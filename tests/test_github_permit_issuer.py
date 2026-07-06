import json
import os
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from integrations.github_deployment import issue_permit
from tests.test_authorization_permit import low_risk_action


class IssueHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["content-length"])))
        self.server.requests.append(
            {
                "path": self.path,
                "authorization": self.headers.get("authorization"),
                "idempotency": self.headers.get("idempotency-key"),
                "payload": payload,
            }
        )
        if self.path == "/v1/language/evaluate":
            response = {"replay_id": "replay-issuer-1001"}
            status = 200
        else:
            response = {"permit_token": "header.payload.signature"}
            status = 201
        encoded = json.dumps(response).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


class PermitIssuerTests(unittest.TestCase):
    def test_endpoint_requires_https_outside_loopback(self):
        self.assertEqual(
            issue_permit.endpoint("http://127.0.0.1:8788", "/v1/permits/issue"),
            "http://127.0.0.1:8788/v1/permits/issue",
        )
        with self.assertRaises(issue_permit.PermitIssueError):
            issue_permit.endpoint("http://smerc.example", "/v1/permits/issue")
        with self.assertRaises(issue_permit.PermitIssueError):
            issue_permit.endpoint("https://user:secret@smerc.example", "/v1/permits/issue")

    @unittest.skipIf(os.name == "nt", "Codex managed Windows workspace denies cleanup; CI verifies on Linux.")
    def test_main_uses_separate_credentials_and_never_prints_permit(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), IssueHandler)
        server.requests = []
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                action_path = root / "action.json"
                permit_path = root / "permit.token"
                action_path.write_text(json.dumps(low_risk_action()), encoding="utf-8")
                argv = [
                    "issue_permit.py",
                    "--api-url", f"http://127.0.0.1:{server.server_address[1]}",
                    "--action-file", str(action_path),
                    "--audience", "github-production-executor",
                    "--output-file", str(permit_path),
                ]
                output = StringIO()
                with patch.dict(
                    os.environ,
                    {
                        "SMERC_PROPOSER_TOKEN": "proposer-secret",
                        "SMERC_ISSUER_TOKEN": "issuer-secret",
                        "GITHUB_RUN_ID": "9001",
                    },
                    clear=False,
                ), patch.object(sys, "argv", argv), redirect_stdout(output):
                    self.assertEqual(issue_permit.main(), 0)
                self.assertEqual(permit_path.read_text(encoding="utf-8"), "header.payload.signature")
                self.assertNotIn("header.payload.signature", output.getvalue())
                self.assertEqual([item["path"] for item in server.requests], [
                    "/v1/language/evaluate", "/v1/permits/issue"
                ])
                self.assertEqual(server.requests[0]["authorization"], "Bearer proposer-secret")
                self.assertEqual(server.requests[1]["authorization"], "Bearer issuer-secret")
                self.assertTrue(server.requests[0]["idempotency"].startswith("deployment-permit-9001-"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()

import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "integrations" / "github_actions" / "run_smerc_gate.py"
LOCAL_SAMPLE = ROOT / "integrations" / "github_actions" / "sample_action_request.json"
DENIED_SAMPLE = ROOT / "integrations" / "github_actions" / "denied_action_request.json"
REMOTE_SAMPLE = ROOT / "examples" / "recoverability_single_action.json"
OUTPUT_DIR = ROOT / "test_outputs" / "github_action_remote"
API_SECRET = "test-secret-01234567890123456789"


def remote_decision(posture="THROTTLE"):
    return {
        "action_id": "AGENT_DEPLOY_PROD_CONFIG",
        "posture": posture,
        "enforcement_state": "constrain",
        "scores": {
            "irreversible_exposure_score": 0.502,
            "reversible_capacity_score": 0.588,
            "confidence_score": 0.686,
        },
        "reason_codes": ["IRREVERSIBLE_EXPOSURE_ELEVATED"],
        "controls": ["limit_scope", "require_rollback_plan"],
        "plain_english_summary": "Action received a constrained remote posture.",
        "replay_id": "replay_remote_1001",
        "replay": {"evaluated_at": "2026-06-28T12:00:00+00:00"},
    }


class FakeSMERCHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length)
        self.server.requests.append(
            {
                "path": self.path,
                "headers": {name.lower(): value for name, value in self.headers.items()},
                "body": json.loads(body.decode("utf-8")),
            }
        )
        status, payload = self.server.responses.pop(0)
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


class FakeSMERCServer(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), FakeSMERCHandler)
        self.requests = []
        self.responses = []


class GitHubActionsIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.server = FakeSMERCServer()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        self.server.requests.clear()
        self.server.responses.clear()
        self.output = OUTPUT_DIR / f"{self._testMethodName}.json"
        self.github_output = OUTPUT_DIR / f"{self._testMethodName}.outputs"
        self.step_summary = OUTPUT_DIR / f"{self._testMethodName}.md"
        self.github_output.write_text("", encoding="utf-8")
        self.step_summary.write_text("", encoding="utf-8")

    @property
    def api_url(self):
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    def run_gate(self, sample, *extra, api_key=None):
        environment = os.environ.copy()
        environment.update(
            {
                "GITHUB_OUTPUT": str(self.github_output),
                "GITHUB_STEP_SUMMARY": str(self.step_summary),
                "GITHUB_RUN_ID": "5001",
                "GITHUB_RUN_ATTEMPT": "1",
                "GITHUB_JOB": "permission-check",
            }
        )
        if api_key is not None:
            environment["SMERC_API_KEY"] = api_key
        else:
            environment.pop("SMERC_API_KEY", None)
        return subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--action-file",
                str(sample),
                "--output-file",
                str(self.output),
                *extra,
            ],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=15,
        )

    def read_report(self):
        return json.loads(self.output.read_text(encoding="utf-8"))

    def test_runner_writes_local_decision_report_in_observe_mode(self):
        result = self.run_gate(LOCAL_SAMPLE, "--mode", "observe")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.read_report()
        self.assertEqual(report["source"], "local")
        self.assertEqual(report["integration_status"], "evaluated")
        self.assertIn(report["decision"]["posture"], {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertFalse(report["enforcement"]["active"])

    def test_local_enforce_mode_fails_on_denied_action(self):
        result = self.run_gate(
            DENIED_SAMPLE,
            "--mode",
            "enforce",
            "--fail-on",
            "DENY,FREEZE",
        )
        self.assertEqual(result.returncode, 1)
        report = self.read_report()
        self.assertEqual(report["decision"]["posture"], "DENY")
        self.assertTrue(report["enforcement"]["would_fail"])

    def test_remote_mode_authenticates_and_normalizes_outputs_without_leaking_secret(self):
        self.server.responses.append((200, remote_decision()))
        result = self.run_gate(
            REMOTE_SAMPLE,
            "--source",
            "remote",
            "--api-url",
            self.api_url,
            "--tenant",
            "platform-team",
            api_key=API_SECRET,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.read_report()
        request = self.server.requests[0]
        self.assertEqual(request["path"], "/v1/evaluate")
        self.assertEqual(request["headers"]["authorization"], f"Bearer {API_SECRET}")
        self.assertEqual(request["headers"]["x-smerc-tenant"], "platform-team")
        self.assertTrue(request["headers"]["idempotency-key"])
        self.assertEqual(request["body"]["action_id"], "AGENT_DEPLOY_PROD_CONFIG")
        self.assertEqual(report["decision"]["posture"], "THROTTLE")
        self.assertIn("risk-score=0.502", self.github_output.read_text(encoding="utf-8"))
        self.assertIn("integration-status=evaluated", self.github_output.read_text(encoding="utf-8"))
        combined = result.stdout + result.stderr + self.output.read_text(encoding="utf-8")
        self.assertNotIn(API_SECRET, combined)

    def test_remote_mode_retries_transient_failure_with_same_idempotency_key(self):
        self.server.responses.extend([(503, {"error": "busy"}), (200, remote_decision())])
        result = self.run_gate(
            REMOTE_SAMPLE,
            "--source",
            "remote",
            "--api-url",
            self.api_url,
            "--max-retries",
            "1",
            api_key=API_SECRET,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.server.requests), 2)
        keys = [request["headers"]["idempotency-key"] for request in self.server.requests]
        self.assertEqual(keys[0], keys[1])

    def test_observe_mode_reports_remote_unavailability_without_fabricating_posture(self):
        result = self.run_gate(
            REMOTE_SAMPLE,
            "--source",
            "remote",
            "--api-url",
            "http://127.0.0.1:1",
            "--request-timeout",
            "1",
            "--max-retries",
            "0",
            api_key=API_SECRET,
        )
        self.assertEqual(result.returncode, 0)
        report = self.read_report()
        self.assertEqual(report["integration_status"], "unavailable")
        self.assertIsNone(report["decision"])
        self.assertIn("posture=UNAVAILABLE", self.github_output.read_text(encoding="utf-8"))

    def test_enforce_mode_fails_closed_when_remote_evaluation_is_unavailable(self):
        result = self.run_gate(
            REMOTE_SAMPLE,
            "--source",
            "remote",
            "--mode",
            "enforce",
            "--api-url",
            "http://127.0.0.1:1",
            "--request-timeout",
            "1",
            "--max-retries",
            "0",
            api_key=API_SECRET,
        )
        self.assertEqual(result.returncode, 2)
        self.assertTrue(self.read_report()["enforcement"]["would_fail"])

    def test_explicit_fail_policy_stops_observe_mode_on_api_error(self):
        result = self.run_gate(
            REMOTE_SAMPLE,
            "--source",
            "remote",
            "--api-url",
            "http://127.0.0.1:1",
            "--api-failure-policy",
            "fail",
            "--request-timeout",
            "1",
            "--max-retries",
            "0",
            api_key=API_SECRET,
        )
        self.assertEqual(result.returncode, 2)

    def test_remote_mode_rejects_insecure_non_loopback_endpoint_before_network_use(self):
        result = self.run_gate(
            REMOTE_SAMPLE,
            "--source",
            "remote",
            "--api-url",
            "http://example.com",
            "--api-failure-policy",
            "fail",
            api_key=API_SECRET,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.read_report()["error"]["code"], "insecure_api_url")

    def test_remote_mode_reports_missing_api_key(self):
        result = self.run_gate(
            REMOTE_SAMPLE,
            "--source",
            "remote",
            "--api-url",
            self.api_url,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.read_report()["error"]["code"], "missing_api_key")
        self.assertEqual(len(self.server.requests), 0)

    def test_remote_mode_rejects_malformed_decision_response(self):
        self.server.responses.append((200, {"posture": "THROTTLE"}))
        result = self.run_gate(
            REMOTE_SAMPLE,
            "--source",
            "remote",
            "--api-url",
            self.api_url,
            api_key=API_SECRET,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.read_report()["error"]["code"], "invalid_api_response")


if __name__ == "__main__":
    unittest.main()

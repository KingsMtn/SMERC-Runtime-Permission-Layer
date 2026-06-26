import json
import threading
import time
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from api_server import SMERCRequestHandler


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = json.loads((ROOT / "examples" / "recoverability_action_requests.json").read_text(encoding="utf-8"))


class APIServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), SMERCRequestHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def get_json(self, path):
        with urlopen(self.url(path), timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def post_json(self, path, payload):
        data = json.dumps(payload).encode("utf-8")
        request = Request(self.url(path), data=data, headers={"content-type": "application/json"}, method="POST")
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def test_health_endpoint(self):
        self.assertEqual(self.get_json("/health")["status"], "ok")

    def test_schema_endpoint_lists_postures(self):
        schema = self.get_json("/schema")
        self.assertIn("reversibility", schema["required_fields"])
        self.assertIn("ESCALATE", schema["postures"])

    def test_evaluate_endpoint_returns_posture(self):
        result = self.post_json("/evaluate", EXAMPLES[0])
        self.assertEqual(result["posture"], "ALLOW")
        self.assertIn("scores", result)

    def test_batch_endpoint_returns_all_records(self):
        result = self.post_json("/batch", EXAMPLES[:2])
        self.assertEqual(len(result), 2)

    def test_bad_request_returns_400(self):
        with self.assertRaises(HTTPError) as ctx:
            self.post_json("/evaluate", {"action_id": "BROKEN"})
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import threading
import unittest
from pathlib import Path

from api_server import create_server
from reference_engine.api_smoke_test import (
    render_markdown,
    run_api_smoke_test,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "examples" / "recoverability_single_action.json").read_text(encoding="utf-8"))
DOC = ROOT / "docs" / "API_Smoke_Test.md"
README = ROOT / "README.md"


class APISmokeTestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={"alpha": "alpha-secret"},
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_smoke_test_exercises_runtime_api_and_operator_status(self):
        report = run_api_smoke_test(
            base_url=self.base_url,
            token="alpha-secret",
            action=EXAMPLE,
            latency_slo_ms=1000,
        )

        self.assertEqual(report["schema"], "smerc.api-smoke-test.v1")
        self.assertTrue(report["passed"])
        self.assertEqual(report["failed_checks"], [])
        self.assertEqual(report["artifacts"]["decision"]["posture"], "THROTTLE")
        self.assertEqual(report["artifacts"]["runtime_health"]["health_status"], "healthy")
        self.assertEqual(report["artifacts"]["operator_status"]["schema"], "smerc.operator-status.v1")
        self.assertIn("does not prove production availability", report["evidence_boundary"])

    def test_smoke_test_reports_failure_without_hiding_boundary(self):
        report = run_api_smoke_test(
            base_url=self.base_url,
            token="wrong-secret",
            action=EXAMPLE,
            latency_slo_ms=1000,
        )

        self.assertFalse(report["passed"])
        self.assertIn("evaluate", report["failed_checks"])
        self.assertIn("production availability", report["evidence_boundary"])

    def test_markdown_and_writers_create_reports(self):
        report = run_api_smoke_test(
            base_url=self.base_url,
            token="alpha-secret",
            action=EXAMPLE,
            latency_slo_ms=1000,
        )
        markdown = render_markdown(report)
        self.assertIn("SMERC API Smoke Test Report", markdown)
        self.assertIn("Evidence Boundary", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "smoke.json"
            markdown_path = Path(directory) / "smoke.md"
            write_outputs(report, json_path=json_path, markdown_path=markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

    def test_docs_and_readme_link_smoke_test(self):
        self.assertIn("python -m reference_engine.api_smoke_test", DOC.read_text(encoding="utf-8"))
        self.assertIn("docs/API_Smoke_Test.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "integrations" / "github_actions" / "run_smerc_gate.py"
SAMPLE = ROOT / "integrations" / "github_actions" / "sample_action_request.json"
DENIED_SAMPLE = ROOT / "integrations" / "github_actions" / "denied_action_request.json"
TEST_OUTPUT = ROOT / "smerc-test-decision.json"


class GitHubActionsIntegrationTests(unittest.TestCase):
    def test_runner_writes_decision_report_in_observe_mode(self):
        result = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--action-file",
                str(SAMPLE),
                "--mode",
                "observe",
                "--output-file",
                str(TEST_OUTPUT),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn('"decision"', result.stdout)
        report = json.loads(TEST_OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(report["mode"], "observe")
        self.assertIn(report["decision"]["posture"], {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertFalse(report["enforcement"]["active"])

    def test_enforce_mode_fails_on_denied_action(self):
        result = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--action-file",
                str(DENIED_SAMPLE),
                "--mode",
                "enforce",
                "--output-file",
                str(TEST_OUTPUT),
                "--fail-on",
                "DENY,FREEZE",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 1)
        report = json.loads(TEST_OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(report["decision"]["posture"], "DENY")
        self.assertTrue(report["enforcement"]["active"])
        self.assertTrue(report["enforcement"]["would_fail"])


if __name__ == "__main__":
    unittest.main()


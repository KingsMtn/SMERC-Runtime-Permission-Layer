import json
import subprocess
import sys
import unittest
from pathlib import Path

from integrations.github_pr_guardian import pr_guardian


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "integrations" / "github_pr_guardian" / "pr_guardian.py"
DECISION_REPORT = ROOT / "test_outputs" / "sample_smerc_decision.json"
ACTION_FILE = ROOT / "integrations" / "github_actions" / "sample_action_request.json"
OUTPUT_DIR = ROOT / "test_outputs" / "github_pr_guardian"


class GitHubPRGuardianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if not DECISION_REPORT.exists():
            subprocess.check_call(
                [
                    sys.executable,
                    str(ROOT / "integrations" / "github_actions" / "run_smerc_gate.py"),
                    "--action-file",
                    str(ACTION_FILE),
                    "--output-file",
                    str(DECISION_REPORT),
                    "--mode",
                    "observe",
                ],
                cwd=ROOT,
            )

    def test_builds_certificate_and_comment_from_decision_report(self):
        report = json.loads(DECISION_REPORT.read_text(encoding="utf-8"))
        action = json.loads(ACTION_FILE.read_text(encoding="utf-8"))
        certificate = pr_guardian.build_certificate(report, action_request=action)
        comment = pr_guardian.render_pr_comment(certificate)
        self.assertEqual(certificate["version"], "smerc.github-pr-guardian-certificate.v1")
        self.assertTrue(certificate["verification"]["valid"])
        self.assertIn("SMERC PR Guardian", comment)
        self.assertIn("**Posture:** `THROTTLE`", comment)
        self.assertIn("Certificate digest", comment)
        self.assertIn("does not replace branch protection", comment)

    def test_certificate_tampering_is_detected(self):
        report = json.loads(DECISION_REPORT.read_text(encoding="utf-8"))
        action = json.loads(ACTION_FILE.read_text(encoding="utf-8"))
        certificate = pr_guardian.build_certificate(report, action_request=action)
        certificate["posture"] = "ALLOW"
        verification = pr_guardian.verify_certificate(certificate)
        self.assertFalse(verification["valid"])
        self.assertIn("certificate digest mismatch", verification["errors"])

    def test_unavailable_decision_comment_does_not_authorize(self):
        certificate = pr_guardian.build_certificate(
            {
                "mode": "observe",
                "source": "remote",
                "integration_status": "unavailable",
                "enforcement": {"active": False, "would_fail": True, "fail_on": ["DENY", "FREEZE"]},
                "decision": None,
                "error": {"code": "api_unavailable", "message": "SMERC API unavailable"},
            }
        )
        comment = pr_guardian.render_pr_comment(certificate)
        self.assertEqual(certificate["posture"], "UNAVAILABLE")
        self.assertIn("No valid SMERC posture was produced", comment)
        self.assertIn("SMERC API unavailable", certificate["summary"])

    def test_cli_writes_comment_and_certificate_files(self):
        comment_path = OUTPUT_DIR / "comment.md"
        certificate_path = OUTPUT_DIR / "certificate.json"
        result = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--decision-report",
                str(DECISION_REPORT),
                "--action-file",
                str(ACTION_FILE),
                "--comment-output",
                str(comment_path),
                "--certificate-output",
                str(certificate_path),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SMERC PR Guardian", comment_path.read_text(encoding="utf-8"))
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        self.assertTrue(certificate["verification"]["valid"])

    def test_example_workflow_contains_pr_comment_path_and_artifacts(self):
        workflow = (ROOT / "examples" / "github_pr_guardian" / "pr_guardian_workflow.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("pull_request", workflow)
        self.assertIn("smerc-pr-comment.md", workflow)
        self.assertIn("smerc-pr-certificate.json", workflow)
        self.assertIn("Post or update SMERC PR comment", workflow)


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.github_actions_pilot_readiness import build_readiness, markdown


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "github_actions_pilot_manifest.json"
QUICKSTART = ROOT / "docs" / "GitHub_Actions_Pilot_Operator_Quickstart.md"
README = ROOT / "README.md"


class GitHubActionsPilotReadinessTests(unittest.TestCase):
    def test_readiness_report_is_ready_for_current_manifest(self):
        report = build_readiness(json.loads(MANIFEST.read_text(encoding="utf-8")), repo_root=ROOT)
        self.assertEqual(report["schema"], "smerc.github-actions-pilot-readiness.v1")
        self.assertTrue(report["ready_for_week_zero"])
        self.assertTrue(report["ready_for_customer_observe"])
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["warnings"], [])
        self.assertIn("reviewer group", " ".join(report["required_setup_items"]))
        self.assertIn("metadata-only", report["first_customer_question"])
        self.assertIn("does not prove production suitability", report["evidence_boundary"])

    def test_missing_repository_evidence_blocks_observe_readiness(self):
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        payload["required_repository_evidence"] = ["missing/pilot/file.md"]
        with tempfile.TemporaryDirectory() as directory:
            report = build_readiness(payload, repo_root=Path(directory))
        self.assertFalse(report["ready_for_week_zero"])
        self.assertFalse(report["ready_for_customer_observe"])
        self.assertIn("missing/pilot/file.md", report["blockers"])

    def test_markdown_contains_operator_decision_and_boundary(self):
        report = build_readiness(json.loads(MANIFEST.read_text(encoding="utf-8")), repo_root=ROOT)
        text = markdown(report)
        self.assertIn("Ready for week-zero qualification", text)
        self.assertIn("Ready for customer observe mode", text)
        self.assertIn("First Customer Question", text)
        self.assertIn("Evidence Boundary", text)

    def test_operator_quickstart_is_specific_and_non_enforcement_first(self):
        text = QUICKSTART.read_text(encoding="utf-8")
        self.assertIn("python -m reference_engine.github_actions_pilot_readiness --pretty", text)
        self.assertIn("Do not use enforcement mode in the first pilot.", text)
        self.assertIn("smerc-decision.json", text)
        self.assertIn("reviewer agreement rate", text)
        self.assertIn("Do not move to enforcement", text)

    def test_readme_links_operator_quickstart(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn("docs/GitHub_Actions_Pilot_Operator_Quickstart.md", text)
        self.assertIn("reference_engine.github_actions_pilot_readiness", text)


if __name__ == "__main__":
    unittest.main()

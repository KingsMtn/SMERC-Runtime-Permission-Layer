import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ThirtyMinuteWorkflowProofTests(unittest.TestCase):
    def test_workflow_proof_is_specific_bounded_and_actionable(self):
        text = (ROOT / "docs" / "Thirty_Minute_Workflow_Proof.md").read_text(encoding="utf-8")

        self.assertIn("30-Minute Workflow Proof", text)
        self.assertIn("GitHub Actions", text)
        self.assertIn("CISO_REVIEW_DEPLOY_CANARY", text)
        self.assertIn("simple allow/deny", text)
        self.assertIn("THROTTLE", text)
        self.assertIn("FREEZE", text)
        self.assertIn("ESCALATE", text)
        self.assertIn("not customer validation", text)
        self.assertIn("not production certification", text)
        self.assertIn("What Would Invalidate The Pilot", text)
        self.assertIn("pilot_package/First_Pilot_Path.md", text)

    def test_readme_and_ciso_quick_review_link_to_workflow_proof(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        quick = (ROOT / "docs" / "CISO_Quick_Review.md").read_text(encoding="utf-8")

        self.assertIn("docs/Thirty_Minute_Workflow_Proof.md", readme)
        self.assertIn("docs/Thirty_Minute_Workflow_Proof.md", quick)
        self.assertIn("one-workflow proof path", quick)


if __name__ == "__main__":
    unittest.main()

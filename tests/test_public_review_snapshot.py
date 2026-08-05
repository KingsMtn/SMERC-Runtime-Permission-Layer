import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicReviewSnapshotTests(unittest.TestCase):
    def test_snapshot_states_status_artifacts_paths_and_limits(self):
        text = (ROOT / "docs" / "Public_Review_Snapshot.md").read_text(encoding="utf-8")

        self.assertIn("Structural Momentum Entropy Range Confidence", text)
        self.assertIn("Recoverability scoring before automated actions execute", text)
        self.assertIn("Level 5 candidate", text)
        self.assertIn("Pilot-ready for bounded shadow-mode evaluation", text)
        self.assertIn("GitHub Actions shadow-mode integration", text)
        self.assertIn("Decision Lifecycle Ledger", text)
        self.assertIn("Model and Agent Fitness Layer", text)
        self.assertIn("pilot_package/First_Pilot_Path.md", text)
        self.assertIn("Do not claim", text)
        self.assertIn("not ready to claim production-certified security platform", text)

    def test_external_review_start_here_references_snapshot(self):
        text = (ROOT / "docs" / "External_Review_Start_Here.md").read_text(encoding="utf-8")

        self.assertIn("docs/Public_Review_Snapshot.md", text)

    def test_readme_references_snapshot(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/Public_Review_Snapshot.md", text)


if __name__ == "__main__":
    unittest.main()

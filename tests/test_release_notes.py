import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseNotesTests(unittest.TestCase):
    def test_public_review_release_notes_are_bounded_and_actionable(self):
        text = (ROOT / "docs" / "Release_Notes_v0_14_Public_Review.md").read_text(encoding="utf-8")

        self.assertIn("Structural Momentum Entropy Range Confidence", text)
        self.assertIn("Recoverability scoring before automated actions execute", text)
        self.assertIn("Level 5 candidate", text)
        self.assertIn("not a production-certified release", text)
        self.assertIn("GitHub Actions shadow-mode scoring", text)
        self.assertIn("python -m reference_engine.first_pilot_packet --pretty", text)
        self.assertIn("Do not claim", text)
        self.assertIn("Evidence Still Needed", text)
        self.assertIn("Ready for technical review and bounded shadow-mode pilot discussion", text)

    def test_readme_and_snapshot_reference_release_notes(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        snapshot = (ROOT / "docs" / "Public_Review_Snapshot.md").read_text(encoding="utf-8")

        self.assertIn("docs/Release_Notes_v0_14_Public_Review.md", readme)
        self.assertIn("docs/Release_Notes_v0_14_Public_Review.md", snapshot)


if __name__ == "__main__":
    unittest.main()

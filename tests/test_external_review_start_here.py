import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "External_Review_Start_Here.md"
README = ROOT / "README.md"


class ExternalReviewStartHereTests(unittest.TestCase):
    def test_readme_links_external_review_front_door(self):
        readme = README.read_text(encoding="utf-8")
        self.assertIn("docs/External_Review_Start_Here.md", readme)

    def test_front_door_routes_major_reviewers(self):
        text = DOC.read_text(encoding="utf-8")
        for phrase in (
            "CISO or security executive",
            "Security architect",
            "Platform engineer",
            "Design partner",
            "Open-source reviewer",
            "YC or startup reviewer",
        ):
            self.assertIn(phrase, text)

    def test_front_door_blocks_overclaims(self):
        text = DOC.read_text(encoding="utf-8")
        required_limits = (
            "production certification",
            "compliance attestation",
            "proven live incident reduction",
            "not customer evidence",
            "bounded shadow-mode pilot",
        )
        for phrase in required_limits:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

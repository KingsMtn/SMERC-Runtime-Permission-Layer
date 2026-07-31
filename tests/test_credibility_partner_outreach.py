import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTREACH = ROOT / "docs" / "Credibility_Partner_Outreach.md"


class CredibilityPartnerOutreachTests(unittest.TestCase):
    def test_outreach_message_contains_links_and_boundary(self):
        text = OUTREACH.read_text(encoding="utf-8")

        self.assertIn("https://admirable-sorbet-9986d5.netlify.app/credibility.html", text)
        self.assertIn("https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer", text)
        self.assertIn("not asking you to treat this as production-ready", text)
        self.assertIn("metadata-only", text)

    def test_outreach_avoids_overclaims(self):
        text = OUTREACH.read_text(encoding="utf-8").lower()

        self.assertIn("do not claim", text)
        self.assertIn("production certification", text)
        self.assertIn("incident reduction", text)


if __name__ == "__main__":
    unittest.main()

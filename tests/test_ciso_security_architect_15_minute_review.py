import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "CISO_Security_Architect_15_Minute_Review.md"
README = ROOT / "README.md"


class CISOSecurityArchitect15MinuteReviewTests(unittest.TestCase):
    def test_doc_exists_and_defines_short_review_path(self):
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("15-Minute Review", text)
        self.assertIn("Is SMERC credible enough to test in shadow mode", text)
        self.assertIn("MCP Governance Gateway", text)
        self.assertIn("GitHub Actions", text)
        self.assertIn("Decision Lifecycle Ledger", text)
        self.assertIn("shadow-mode pilot", text)

    def test_doc_preserves_non_claim_boundary(self):
        text = DOC.read_text(encoding="utf-8")

        for phrase in [
            "not yet ready to claim production certification",
            "compliance attestation",
            "proven live incident reduction",
            "does not implement OAuth",
            "prompt-injection defense",
        ]:
            self.assertIn(phrase, text)

    def test_readme_links_short_review_path(self):
        readme = README.read_text(encoding="utf-8")

        self.assertIn("docs/CISO_Security_Architect_15_Minute_Review.md", readme)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProductReadinessIndexTests(unittest.TestCase):
    def test_product_readiness_index_tracks_project_to_product_gates(self):
        text = (ROOT / "docs" / "Product_Readiness_Index.md").read_text(encoding="utf-8")

        for phrase in [
            "Pilot-grade product candidate",
            "metadata-only shadow-mode review",
            "Core decision engine",
            "AWS shadow-mode lane",
            "Intake friction",
            "Buyer-facing proof packet",
            "Execution-boundary evidence",
            "External credibility",
            "Product Claim Ladder",
        ]:
            self.assertIn(phrase, text)

        for boundary in [
            "Do not claim",
            "production-certified security platform",
            "proven incident reduction",
            "AWS endorsement",
            "enterprise beta",
        ]:
            self.assertIn(boundary, text)

    def test_product_readiness_index_is_linked_from_review_surfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        maturity = (ROOT / "docs" / "Maturity_Model.md").read_text(encoding="utf-8")

        for text in [readme, maturity]:
            self.assertIn("docs/Product_Readiness_Index.md", text)


if __name__ == "__main__":
    unittest.main()

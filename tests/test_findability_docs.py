import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FindabilityDocsTests(unittest.TestCase):
    def test_findability_doc_has_canonical_links_terms_and_boundaries(self):
        text = (ROOT / "docs" / "Findability_And_AI_Discovery.md").read_text(encoding="utf-8")

        self.assertIn("https://admirable-sorbet-9986d5.netlify.app/ai-agent-governance.html", text)
        self.assertIn("https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer", text)
        self.assertIn("AI agent governance", text)
        self.assertIn("Structural Momentum Entropy Range Confidence", text)
        self.assertIn("runtime permission layer", text)
        self.assertIn("recoverability scoring", text)
        self.assertIn("GitHub repository topics", text)
        self.assertIn("Search appearance is not proof of product-market fit", text)

    def test_public_indexing_assets_points_to_findability_doc(self):
        text = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(encoding="utf-8")

        self.assertIn("ai-agent-governance.html", text)
        self.assertIn("Findability_And_AI_Discovery.md", text)

    def test_naming_guide_preserves_brand_category_problem_order(self):
        text = (ROOT / "docs" / "Naming_And_Search_Style_Guide.md").read_text(encoding="utf-8")

        self.assertIn("Brand first, category second, searchable problem third", text)
        self.assertIn("SMERC | Runtime Permission Infrastructure for AI Agents", text)
        self.assertIn("Structural Momentum Entropy Range Confidence", text)
        self.assertIn("Recoverability scoring before automated actions execute", text)
        self.assertIn("Do not overstate", text)


if __name__ == "__main__":
    unittest.main()

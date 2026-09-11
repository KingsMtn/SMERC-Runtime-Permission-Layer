import unittest
import json
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
        self.assertIn("ai-review.json", text)
        self.assertIn("pilot-runbook.json", text)
        self.assertIn("openapi.json", text)
        self.assertIn("AI Reviewer Bundle", text)
        self.assertIn("without relying on founder explanation", text)
        self.assertIn("docs/AI_Readable_Reviewer_Bundle.md", text)
        self.assertIn("examples/ai_reviewer_bundle.json", text)

    def test_naming_guide_preserves_brand_category_problem_order(self):
        text = (ROOT / "docs" / "Naming_And_Search_Style_Guide.md").read_text(encoding="utf-8")

        self.assertIn("Brand first, category second, searchable problem third", text)
        self.assertIn("SMERC | Pre-Execution Recoverability Control", text)
        self.assertIn("Structural Momentum Entropy Range Confidence", text)
        self.assertIn("Pre-execution recoverability control", text)
        self.assertIn("Do not overstate", text)

    def test_repo_ai_reviewer_bundle_has_links_and_boundaries(self):
        bundle = json.loads(
            (ROOT / "examples" / "ai_reviewer_bundle.json").read_text(encoding="utf-8")
        )
        doc = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(bundle["schema_version"], "smerc.ai_reviewer_bundle.v1")
        self.assertIn("https://admirable-sorbet-9986d5.netlify.app/", bundle["canonical_site"])
        self.assertIn("https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer", bundle["canonical_repository"])
        self.assertIn("pre-execution recoverability control", bundle["category"])
        self.assertIn("runtime permission infrastructure", bundle["category"])
        self.assertIn("Recovery Authority Gate for governed unlock after pause", bundle["implemented_surfaces"])
        self.assertIn("customer validation", bundle["current_evidence"]["evidence_boundary"])
        self.assertIn("SMERC is not production-certified.", bundle["non_claims"])
        self.assertIn("docs/AI_Readable_Reviewer_Bundle.md", readme)
        self.assertIn("examples/ai_reviewer_bundle.json", readme)
        self.assertIn("What It Does Not Prove", doc)
        self.assertIn("Impact", doc)

    def test_accelerator_map_preserves_overlap_and_difference(self):
        text = (ROOT / "docs" / "Accelerator_And_Adjacent_Company_Map.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("The market is already active", text)
        self.assertIn("YC has backed companies close to AI-agent authorization", text)
        self.assertIn("recoverability checkpoint", text)
        self.assertIn("MACH37", text)
        self.assertIn("not a competitive legal opinion", text)

    def test_two_tier_valuation_path_is_linked_and_bounded(self):
        text = (ROOT / "docs" / "Two_Tier_Valuation_Path.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        strategic = (ROOT / "docs" / "Strategic_Acquisition_Positioning.md").read_text(
            encoding="utf-8"
        )
        aws = (ROOT / "docs" / "AWS_Deployable_Bot_Readiness_Path.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Tier 1: Public Decision Language And Review Standard", text)
        self.assertIn("Tier 2: Enterprise Cloud Action Governance Package", text)
        self.assertIn("smerc.decision.v1", text)
        self.assertIn("AWS-style metadata adapter", text)
        self.assertIn("postcondition evidence", text)
        self.assertIn("customer-owned metadata", text)
        self.assertIn("Avoid this", text)
        self.assertIn("SMERC is already worth millions", text)
        self.assertIn("docs/Two_Tier_Valuation_Path.md", readme)
        self.assertIn("Two-Tier Valuation Path", strategic)
        self.assertIn("Tier 2 proof path", aws)


if __name__ == "__main__":
    unittest.main()

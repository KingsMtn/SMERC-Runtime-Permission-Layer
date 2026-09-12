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
        self.assertIn(
            "AWS Shadow Mirror Metadata Path for converting sanitized VPC Traffic Mirroring, Network Load Balancer fan-out, and Gateway Load Balancer endpoint summaries into SMERC shadow-mode evidence without packet payloads or live AWS access",
            bundle["implemented_surfaces"],
        )
        self.assertIn("customer validation", bundle["current_evidence"]["evidence_boundary"])
        self.assertIn("aws_shadow_mirror_metadata_path", bundle["current_evidence"])
        self.assertIn("two_tier_valuation_path", bundle["current_evidence"])
        self.assertIn("AWS shadow mirror metadata", bundle["search_and_index_terms"])
        self.assertIn("SMERC is not production-certified.", bundle["non_claims"])
        self.assertIn("docs/AI_Readable_Reviewer_Bundle.md", readme)
        self.assertIn("examples/ai_reviewer_bundle.json", readme)
        self.assertIn("AWS Shadow Mirror Metadata Path", doc)
        self.assertIn("Two-Tier Valuation Path", doc)
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

    def test_aws_tier2_release_note_is_discoverable(self):
        release = (ROOT / "docs" / "Release_Notes_v0_15_AWS_Tier2_Review.md").read_text(
            encoding="utf-8"
        )
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("AWS Tier 2 Review Notes", release)
        self.assertIn("AWS shadow mirror metadata", release)
        self.assertIn("Two_Tier_Valuation_Path.md", release)
        self.assertIn("What This Does Not Prove", release)
        self.assertIn("customer willingness to pay", release)
        self.assertIn("docs/Release_Notes_v0_15_AWS_Tier2_Review.md", indexing)
        self.assertIn("AWS shadow mirror metadata evidence", changelog)

    def test_tier2_aws_reviewer_front_door_is_linked_and_bounded(self):
        front_door = (ROOT / "docs" / "Tier2_AWS_Reviewer_Front_Door.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "Does recoverability before execution change cloud-agent or automation judgment",
            front_door,
        )
        self.assertIn("AWS shadow mirror metadata evidence", front_door)
        self.assertIn("5 to 25 safe AWS-style action summaries", front_door)
        self.assertIn("5 to 25 sanitized mirror-derived summaries", front_door)
        self.assertIn("acquisition-grade Tier 3 evidence", front_door)
        self.assertIn("docs/Tier2_AWS_Reviewer_Front_Door.md", readme)
        self.assertIn("docs/Release_Notes_v0_15_AWS_Tier2_Review.md", readme)

    def test_external_metadata_reviewer_request_is_linked_and_bounded(self):
        request = (ROOT / "docs" / "External_Metadata_Reviewer_Request.md").read_text(
            encoding="utf-8"
        )
        drafts = (ROOT / "docs" / "Public_Outreach_Post_Drafts.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        feedback = (ROOT / "docs" / "Public_Review_And_Feedback.md").read_text(
            encoding="utf-8"
        )
        aws_template = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "aws_metadata_pilot_request.md"
        ).read_text(encoding="utf-8")
        mirror_template = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "aws_shadow_mirror_metadata_request.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "Does recoverability before execution belong as its own control layer",
            request,
        )
        self.assertIn("Share 5 to 25 metadata-only examples", request)
        self.assertIn("Do not share", request)
        self.assertIn("live AWS access", request)
        self.assertIn("reviewer label after seeing SMERC posture", request)
        self.assertIn("Hacker News Draft", drafts)
        self.assertIn("Reddit Or Cloud Forum Draft", drafts)
        self.assertIn("ask reviewers to challenge the control gap", drafts)
        self.assertIn("docs/External_Metadata_Reviewer_Request.md", readme)
        self.assertIn("docs/Public_Outreach_Post_Drafts.md", readme)
        self.assertIn("docs/External_Metadata_Reviewer_Request.md", indexing)
        self.assertIn("docs/Public_Outreach_Post_Drafts.md", indexing)
        self.assertIn("External_Metadata_Reviewer_Request.md", feedback)
        self.assertIn("External_Metadata_Reviewer_Request.md", aws_template)
        self.assertIn("External_Metadata_Reviewer_Request.md", mirror_template)


if __name__ == "__main__":
    unittest.main()

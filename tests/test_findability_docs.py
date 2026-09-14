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
        self.assertIn("aws_ecosystem_entry_path", bundle["current_evidence"])
        self.assertIn("aws_decision_api_surface", bundle["current_evidence"])
        self.assertIn("two_tier_valuation_path", bundle["current_evidence"])
        self.assertIn("AWS shadow mirror metadata", bundle["search_and_index_terms"])
        self.assertIn("AWS ecosystem entry path", bundle["search_and_index_terms"])
        self.assertIn("AWS decision API surface", bundle["search_and_index_terms"])
        self.assertIn("evaluateAwsActionRecoverability", bundle["search_and_index_terms"])
        self.assertIn("SMERC is not production-certified.", bundle["non_claims"])
        self.assertIn("docs/AI_Readable_Reviewer_Bundle.md", readme)
        self.assertIn("examples/ai_reviewer_bundle.json", readme)
        self.assertIn("AWS Shadow Mirror Metadata Path", doc)
        self.assertIn("AWS Ecosystem Entry Path", doc)
        self.assertIn("AWS Decision API Surface", doc)
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

    def test_aws_ecosystem_entry_path_is_linked_and_bounded(self):
        entry = (ROOT / "docs" / "AWS_Ecosystem_Entry_Path.md").read_text(encoding="utf-8")
        quickstart = (ROOT / "docs" / "AWS_Reviewer_Quickstart.md").read_text(encoding="utf-8")
        marketplace = (ROOT / "docs" / "AWS_Marketplace_Validation_Path.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ai_bundle = json.loads((ROOT / "examples" / "ai_reviewer_bundle.json").read_text(encoding="utf-8"))

        self.assertIn("AWS has created a more direct path", entry)
        self.assertIn("AgentCore Gateway", entry)
        self.assertIn("AgentCore Runtime", entry)
        self.assertIn("AWS Marketplace", entry)
        self.assertIn("Partner Agent Factory", entry)
        self.assertIn("not current claims", entry)
        self.assertIn("claim AWS partnership", entry)
        self.assertIn("docs/AWS_Ecosystem_Entry_Path.md", quickstart)
        self.assertIn("docs/AWS_Ecosystem_Entry_Path.md", marketplace)
        self.assertIn("docs/AWS_Ecosystem_Entry_Path.md", readme)
        self.assertIn("aws_ecosystem_entry_path", ai_bundle["current_evidence"])

    def test_external_metadata_reviewer_request_is_linked_and_bounded(self):
        request = (ROOT / "docs" / "External_Metadata_Reviewer_Request.md").read_text(
            encoding="utf-8"
        )
        drafts = (ROOT / "docs" / "Public_Outreach_Post_Drafts.md").read_text(
            encoding="utf-8"
        )
        status = (ROOT / "docs" / "Public_Outreach_Status.md").read_text(
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
        self.assertIn("OpenSSF `ossf/ai-ml-security` issue #50", status)
        self.assertIn("Wait for a response before posting the same ask broadly", status)
        self.assertIn("ask for critique, not adoption", status)
        self.assertIn("docs/External_Metadata_Reviewer_Request.md", readme)
        self.assertIn("docs/Public_Outreach_Post_Drafts.md", readme)
        self.assertIn("docs/Public_Outreach_Status.md", readme)
        self.assertIn("docs/External_Metadata_Reviewer_Request.md", indexing)
        self.assertIn("docs/Public_Outreach_Post_Drafts.md", indexing)
        self.assertIn("docs/Public_Outreach_Status.md", indexing)
        self.assertIn("External_Metadata_Reviewer_Request.md", feedback)
        self.assertIn("Public_Outreach_Status.md", feedback)
        self.assertIn("External_Metadata_Reviewer_Request.md", aws_template)
        self.assertIn("External_Metadata_Reviewer_Request.md", mirror_template)

    def test_premortem_is_linked_and_actionable(self):
        premortem = (ROOT / "docs" / "SMERC_Premortem.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        valuation = (ROOT / "docs" / "Two_Tier_Valuation_Path.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("If SMERC does not get traction", premortem)
        self.assertIn("Failure mode", premortem)
        self.assertIn("Warning signal", premortem)
        self.assertIn("The proof is too synthetic", premortem)
        self.assertIn("The product surface is unclear", premortem)
        self.assertIn("Current Highest-Risk Assumption", premortem)
        self.assertIn("What Failure Would Teach", premortem)
        self.assertIn("docs/SMERC_Premortem.md", readme)
        self.assertIn("docs/SMERC_Premortem.md", indexing)
        self.assertIn("docs/SMERC_Premortem.md", valuation)
        self.assertIn("SMERC premortem", changelog)

    def test_openssf_response_playbook_and_five_row_example_are_linked(self):
        playbook = (ROOT / "docs" / "OpenSSF_Response_Playbook.md").read_text(
            encoding="utf-8"
        )
        example_doc = (ROOT / "docs" / "Five_Row_Metadata_Example.md").read_text(
            encoding="utf-8"
        )
        example_json = json.loads(
            (ROOT / "examples" / "external_metadata_reviewer_5_row_example.json").read_text(
                encoding="utf-8"
            )
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        outreach_status = (ROOT / "docs" / "Public_Outreach_Status.md").read_text(
            encoding="utf-8"
        )
        reviewer_request = (ROOT / "docs" / "External_Metadata_Reviewer_Request.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("If They Say This Is The Wrong Forum", playbook)
        self.assertIn("If They Say Existing Tools Already Cover It", playbook)
        self.assertIn("If They Ask For A Concrete Example", playbook)
        self.assertIn("ask for critique, not adoption", playbook)
        self.assertIn("This is the smallest readable example", example_doc)
        self.assertIn("Agent requests capacity increase during a retry loop", example_doc)
        self.assertIn("examples/external_metadata_reviewer_5_row_example.json", example_doc)
        self.assertEqual(example_json["schema_version"], "smerc.external_metadata_reviewer_example.v1")
        self.assertEqual(len(example_json["rows"]), 5)
        self.assertIn("docs/OpenSSF_Response_Playbook.md", readme)
        self.assertIn("docs/Five_Row_Metadata_Example.md", readme)
        self.assertIn("docs/OpenSSF_Response_Playbook.md", indexing)
        self.assertIn("docs/Five_Row_Metadata_Example.md", indexing)
        self.assertIn("docs/OpenSSF_Response_Playbook.md", outreach_status)
        self.assertIn("docs/Five_Row_Metadata_Example.md", reviewer_request)

    def test_local_source_of_truth_is_linked_and_explicit(self):
        source_note = (ROOT / "docs" / "Local_Source_Of_Truth.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn(".smerc-action-language-publish", source_note)
        self.assertIn("https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer.git", source_note)
        self.assertIn("SMERC-Macro-Language-Model", source_note)
        self.assertIn("SMERC-Runtime-Permission-Layer", source_note)
        self.assertIn("not the active source of truth", source_note)
        self.assertIn("docs/Local_Source_Of_Truth.md", readme)
        self.assertIn("docs/Local_Source_Of_Truth.md", indexing)
        self.assertIn("local source-of-truth note", changelog)

    def test_field_of_use_strategy_is_linked_and_preserves_core(self):
        strategy = (ROOT / "docs" / "SMERC_Field_Of_Use_Strategy.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        commercial = (ROOT / "COMMERCIAL_USE.md").read_text(encoding="utf-8")
        boundary = (
            ROOT / "docs" / "SMERC_Defensible_Moat_And_Commercial_Boundary.md"
        ).read_text(encoding="utf-8")
        valuation = (ROOT / "docs" / "Two_Tier_Valuation_Path.md").read_text(
            encoding="utf-8"
        )
        strategic = (ROOT / "docs" / "Strategic_Acquisition_Positioning.md").read_text(
            encoding="utf-8"
        )
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("SMERC Core", strategy)
        self.assertIn("AWS / Cloud Action Governance", strategy)
        self.assertIn("Reserved Future Fields", strategy)
        self.assertIn("insurance", strategy)
        self.assertIn("SMERC-F", strategy)
        self.assertIn("crypto", strategy)
        self.assertIn("field of use", strategy.lower())
        self.assertIn("not legal advice", strategy)
        self.assertIn("docs/SMERC_Field_Of_Use_Strategy.md", readme)
        self.assertIn("docs/SMERC_Field_Of_Use_Strategy.md", commercial)
        self.assertIn("docs/SMERC_Field_Of_Use_Strategy.md", boundary)
        self.assertIn("docs/SMERC_Field_Of_Use_Strategy.md", valuation)
        self.assertIn("docs/SMERC_Field_Of_Use_Strategy.md", strategic)
        self.assertIn("docs/SMERC_Field_Of_Use_Strategy.md", indexing)
        self.assertIn("field-of-use strategy", changelog)

    def test_public_agent_runtime_incident_learning_is_linked_and_bounded(self):
        learning = (
            ROOT / "docs" / "Public_Agent_Runtime_Incident_Learning.md"
        ).read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        data_map = (ROOT / "docs" / "Runtime_Data_Source_Map.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("Do not use leaked proprietary source", learning)
        self.assertIn("public reporting", learning)
        self.assertIn("More Than Code", learning)
        self.assertIn("AGENT_RUNTIME_PROVENANCE_WEAK", learning)
        self.assertIn("CREDENTIAL_EXFILTRATION_PRESSURE", learning)
        self.assertIn("RECOVERY_PATH_UNPROVEN", learning)
        self.assertIn("POSTCONDITION_EVIDENCE_MISSING", learning)
        self.assertIn("docs/Public_Agent_Runtime_Incident_Learning.md", readme)
        self.assertIn("docs/Public_Agent_Runtime_Incident_Learning.md", indexing)
        self.assertIn("docs/Public_Agent_Runtime_Incident_Learning.md", data_map)
        self.assertIn("public agent-runtime incident learning", changelog)

    def test_try_smerc_on_one_action_is_linked_and_runnable(self):
        try_doc = (ROOT / "docs" / "Try_SMERC_On_One_Action.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        ai_bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.recoverability_engine", try_doc)
        self.assertIn("examples/recoverability_single_action.json", try_doc)
        self.assertIn("POST http://127.0.0.1:8788/v1/evaluate", try_doc)
        self.assertIn("ALLOW", try_doc)
        self.assertIn("THROTTLE", try_doc)
        self.assertIn("FREEZE", try_doc)
        self.assertIn("DENY", try_doc)
        self.assertIn("ESCALATE", try_doc)
        self.assertIn("Do not include secrets", try_doc)
        self.assertIn("docs/Try_SMERC_On_One_Action.md", readme)
        self.assertIn("docs/Try_SMERC_On_One_Action.md", indexing)
        self.assertIn("docs/Try_SMERC_On_One_Action.md", ai_bundle)
        self.assertIn("one-action SMERC front door", changelog)


if __name__ == "__main__":
    unittest.main()

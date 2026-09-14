import json
import unittest
from pathlib import Path

from reference_engine.aws_reviewer_bundle import (
    VERSION,
    build_aws_reviewer_bundle,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class AWSReviewerBundleTests(unittest.TestCase):
    def test_builds_aws_reviewer_bundle(self):
        bundle = build_aws_reviewer_bundle(root=ROOT, requested_actions=12, iterations=1)

        self.assertEqual(bundle["version"], VERSION)
        self.assertIn(bundle["bundle_status"], {"ready_for_limited_aws_review", "ready_for_aws_shadow_mode_discussion"})
        self.assertIn("aws_agent_action_chain", bundle["reports"])
        self.assertIn("aws_decision_api_surface", bundle["reports"])
        self.assertIn("aws_agent_action_chain_postcondition", bundle["reports"])
        self.assertIn("aws_postcondition_evidence", bundle["reports"])
        self.assertIn("aws_shadow_mirror", bundle["reports"])
        self.assertIn("performance", bundle["reports"])
        self.assertIn("aws_customer_owned_metadata_request", bundle["reports"])
        self.assertEqual(bundle["reports"]["aws_shadow_mirror"]["accepted_rows"], 3)
        self.assertEqual(bundle["reports"]["aws_shadow_mirror"]["skipped_rows"], 1)
        self.assertEqual(bundle["reports"]["aws_decision_api_surface"]["status"], "reviewable_aws_decision_surface")
        self.assertEqual(
            bundle["reports"]["aws_decision_api_surface"]["operation_id"],
            "evaluateAwsActionRecoverability",
        )
        self.assertEqual(bundle["reports"]["aws_customer_owned_metadata_request"]["workflow_family"], "aws")
        self.assertIn("metadata-only", bundle["evidence_boundary"])
        self.assertIn("packet payloads", bundle["evidence_boundary"])

    def test_markdown_uses_plain_aws_reviewer_frame(self):
        markdown = render_markdown(build_aws_reviewer_bundle(root=ROOT, iterations=1))

        self.assertIn("# AWS-Style Reviewer Bundle", markdown)
        self.assertIn("Guardrails check content. IAM checks authority. SMERC checks recoverability.", markdown)
        self.assertIn("Shadow mirror metadata tests operational behavior", markdown)
        self.assertIn("AWS decision API surface", markdown)
        self.assertIn("evaluateAwsActionRecoverability", markdown)
        self.assertIn("Included Reports", markdown)
        self.assertIn("AWS shadow mirror metadata", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("Next Action", markdown)

    def test_writes_bundle_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "aws_reviewer_bundle"
        bundle = build_aws_reviewer_bundle(root=ROOT, iterations=1)

        write_outputs(bundle, output_dir=scratch)

        self.assertEqual(
            json.loads((scratch / "aws_reviewer_bundle.json").read_text(encoding="utf-8"))["version"],
            VERSION,
        )
        self.assertIn("AWS-Style Reviewer Bundle", (scratch / "AWS_Reviewer_Bundle.md").read_text(encoding="utf-8"))
        self.assertTrue((scratch / "AWS_Agent_Action_Chain.md").exists())
        self.assertTrue((scratch / "AWS_Decision_API_Surface.md").exists())
        self.assertTrue((scratch / "sample_decision_request.json").exists())
        self.assertTrue((scratch / "sample_decision_response.json").exists())
        self.assertTrue((scratch / "AWS_Agent_Action_Chain_Postcondition_Evidence.md").exists())
        self.assertTrue((scratch / "AWS_Postcondition_Evidence_Report.md").exists())
        self.assertTrue((scratch / "AWS_Shadow_Mirror_Adapter_Report.md").exists())
        self.assertTrue((scratch / "Serious_Report_Performance.md").exists())
        self.assertTrue((scratch / "AWS_Customer_Owned_Metadata_Request.md").exists())

    def test_docs_and_readme_reference_bundle(self):
        docs = (ROOT / "docs" / "AWS_Reviewer_Bundle.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ai_bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.aws_reviewer_bundle", docs)
        self.assertIn("AWS_Decision_API_Surface.md", docs)
        self.assertIn("AWS_Shadow_Mirror_Adapter_Report.md", docs)
        self.assertIn("docs/AWS_Reviewer_Bundle.md", readme)
        self.assertIn("aws-style reviewer bundle", ai_bundle.lower())


if __name__ == "__main__":
    unittest.main()

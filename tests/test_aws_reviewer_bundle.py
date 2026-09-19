import json
import unittest
from pathlib import Path

from reference_engine.aws_reviewer_bundle import (
    VERSION,
    build_aws_reviewer_bundle,
    render_markdown,
    write_outputs,
)
from reference_engine.aws_postcondition_evidence import load_aws_observations
from reference_engine.evidence_provenance import build_ledger, digest


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
        self.assertEqual(bundle["readiness"]["chain_proof_eligible_actions"], 0)
        self.assertEqual(bundle["readiness"]["aws_proof_eligible_actions"], 0)
        self.assertIn("not proof-eligible", " ".join(bundle["readiness"]["warnings"]))
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
        self.assertIn("AWS proof-eligible observations", markdown)

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

    def test_customer_provenance_is_verified_through_bundle(self):
        observations_path = ROOT / "examples" / "aws_customer_postcondition_observations_sample.json"
        observations = load_aws_observations(observations_path)
        provenance_rows = [{"observation_id": row["action_id"], **row} for row in observations]
        artifacts = {row["observation_id"]: digest({"fixture": row["observation_id"]}) for row in provenance_rows}
        key = b"aws-reviewer-bundle-test-key-0123456789"
        ledger = build_ledger(
            provenance_rows,
            program_id="aws-customer-review-test",
            collector_id="customer-test-adapter",
            collection_method="test-fixture",
            artifact_digests=artifacts,
            hmac_key=key,
            recorded_at="2026-09-18T20:00:00+00:00",
        )
        ledger_path = ROOT / "tests" / "_tmp" / "aws_reviewer_bundle" / "customer_provenance.json"
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

        bundle = build_aws_reviewer_bundle(
            root=ROOT,
            iterations=1,
            customer_aws_source_exports="examples/aws_customer_metadata_filled_sample.json",
            customer_aws_observations="examples/aws_customer_postcondition_observations_sample.json",
            customer_aws_provenance_ledger=ledger_path,
            customer_aws_hmac_key=key,
        )

        customer = bundle["reports"]["customer_aws_postcondition_evidence"]
        self.assertEqual(customer["proof_eligible_actions"], customer["observed_actions"])
        self.assertEqual(bundle["readiness"]["customer_proof_eligible_actions"], customer["observed_actions"])
        self.assertNotIn("customer AWS observations are not fully authenticated", bundle["readiness"]["warnings"])

    def test_rejects_hmac_key_without_provenance_ledger(self):
        with self.assertRaisesRegex(ValueError, "HMAC key requires customer AWS provenance ledger"):
            build_aws_reviewer_bundle(
                root=ROOT,
                iterations=1,
                customer_aws_source_exports="examples/aws_customer_metadata_filled_sample.json",
                customer_aws_observations="examples/aws_customer_postcondition_observations_sample.json",
                customer_aws_hmac_key=b"unused-key",
            )

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

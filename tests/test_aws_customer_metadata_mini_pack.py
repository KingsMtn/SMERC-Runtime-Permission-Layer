import json
import unittest
from pathlib import Path

from reference_engine.aws_metadata_adapter import build_adapter_report, load_source_exports
from reference_engine.aws_reviewer_bundle import build_aws_reviewer_bundle, write_outputs


ROOT = Path(__file__).resolve().parents[1]
FILLED_SAMPLE = ROOT / "examples" / "aws_customer_metadata_filled_sample.json"
OBS_SAMPLE = ROOT / "examples" / "aws_customer_postcondition_observations_sample.json"


class AWSCustomerMetadataMiniPackTests(unittest.TestCase):
    def test_templates_are_safe_and_documented(self):
        files = [
            ROOT / "examples" / "aws_bedrock_action_group_metadata_template.json",
            ROOT / "examples" / "aws_cloud_platform_metadata_template.json",
            ROOT / "examples" / "aws_postcondition_observation_template.json",
            ROOT / "examples" / "aws_customer_metadata_filled_sample.json",
            ROOT / "examples" / "aws_customer_postcondition_observations_sample.json",
        ]
        prohibited_keys = {"account_id", "arn", "access_key", "secret", "session_token", "raw_log", "production_command"}

        for path in files:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(payload, list)
            self.assertTrue(payload)
            text = json.dumps(payload).lower()
            self.assertNotIn("AKIA", text)
            self.assertTrue(prohibited_keys.isdisjoint(_keys(payload)))

        doc = (ROOT / "docs" / "AWS_Customer_Metadata_Mini_Pack.md").read_text(encoding="utf-8")
        self.assertIn("5 to 25 safe metadata-only AWS-style action summaries", doc)
        self.assertIn("Do not provide account IDs", doc)
        self.assertIn("python -m reference_engine.aws_reviewer_bundle", doc)

    def test_filled_sample_runs_through_adapter(self):
        report = build_adapter_report(load_source_exports(FILLED_SAMPLE))

        self.assertEqual(report["accepted_rows"], 5)
        self.assertEqual(report["skipped_rows"], 0)
        self.assertEqual(report["customer_evaluation"]["summary"]["total_actions"], 5)
        self.assertIn("agentcore_gateway_tool_call_summary", report["accepted_source_format_counts"])
        self.assertIn("cost_anomaly_action_summary", report["accepted_source_format_counts"])

    def test_reviewer_bundle_accepts_customer_aws_metadata(self):
        bundle = build_aws_reviewer_bundle(
            root=ROOT,
            iterations=1,
            customer_aws_source_exports=FILLED_SAMPLE,
            customer_aws_observations=OBS_SAMPLE,
        )

        self.assertIsNotNone(bundle["reports"]["customer_aws_metadata_review"])
        self.assertIsNotNone(bundle["reports"]["customer_aws_postcondition_evidence"])
        self.assertEqual(bundle["reports"]["customer_aws_metadata_review"]["accepted_rows"], 5)
        self.assertIn("Customer AWS metadata supplied", "\n".join(bundle["readiness"]["takeaways"]))

    def test_bundle_writes_customer_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "aws_customer_mini_pack"
        bundle = build_aws_reviewer_bundle(
            root=ROOT,
            iterations=1,
            customer_aws_source_exports=FILLED_SAMPLE,
            customer_aws_observations=OBS_SAMPLE,
        )

        write_outputs(bundle, output_dir=scratch)

        self.assertTrue((scratch / "Customer_AWS_Metadata_Adapter_Report.md").exists())
        self.assertTrue((scratch / "customer_aws_normalized_customer_actions.json").exists())
        self.assertTrue((scratch / "customer_aws_customer_evaluation_report.json").exists())
        self.assertTrue((scratch / "Customer_AWS_Postcondition_Evidence_Report.md").exists())


def _keys(value):
    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key).lower())
            found.update(_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_keys(child))
    return found


if __name__ == "__main__":
    unittest.main()


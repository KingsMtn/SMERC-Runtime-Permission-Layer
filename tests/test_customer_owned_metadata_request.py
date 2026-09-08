import json
import unittest
from pathlib import Path

from reference_engine.customer_owned_metadata_request import (
    VERSION,
    build_request_report,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class CustomerOwnedMetadataRequestTests(unittest.TestCase):
    def test_builds_aws_request_with_aws_specific_commands_and_boundaries(self):
        report = build_request_report(workflow_family="aws", requested_actions=12)

        self.assertEqual(report["workflow_family"], "aws")
        self.assertIn("AgentCore Runtime", " ".join(report["acceptable_action_types"]))
        self.assertIn("aws_metadata_adapter", report["commands"])
        self.assertIn("aws_postcondition_evidence", report["commands"])
        self.assertIn("cloudtrail_data_event_expected", report["aws_recommended_fields"])
        self.assertIn("gateway_bypass_detected", report["aws_recommended_fields"])
        self.assertIn("server_initiated_elicitation", report["aws_recommended_fields"])
        self.assertIn("AWS account IDs", " ".join(report["excluded_data"]))
        self.assertIn("AWS shadow-mode pilot", " ".join(report["aws_reviewer_questions"]))

    def test_builds_financial_request_without_sensitive_data(self):
        report = build_request_report(workflow_family="financial", requested_actions=12)

        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["workflow_family"], "financial")
        self.assertEqual(report["requested_action_count"], 12)
        self.assertIn("stablecoin", " ".join(report["acceptable_action_types"]))
        self.assertIn("serious_report_performance", report["commands"])
        self.assertIn("not prove customer demand", report["evidence_boundary"])
        self.assertIn("regulated transaction payloads", " ".join(report["excluded_data"]))

    def test_rejects_invalid_request_size(self):
        with self.assertRaisesRegex(ValueError, "between 5 and 25"):
            build_request_report(requested_actions=30)

    def test_markdown_explains_work_result_impact_and_performance(self):
        markdown = render_markdown(build_request_report(workflow_family="cloud", requested_actions=10))

        self.assertIn("# Customer-Owned Metadata Request", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("serious_report_performance", markdown)
        self.assertIn("Do Not Provide", markdown)
        self.assertIn("Reviewer Question", markdown)

        aws_markdown = render_markdown(build_request_report(workflow_family="aws", requested_actions=12))
        self.assertIn("AWS Recommended Metadata Fields", aws_markdown)
        self.assertIn("aws_postcondition_evidence", aws_markdown)
        self.assertIn("AWS Reviewer Questions", aws_markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "customer_owned_metadata_request"
        report = build_request_report(workflow_family="general", requested_actions=10)
        json_path = scratch / "request.json"
        markdown_path = scratch / "request.md"

        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        parsed = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(parsed["version"], VERSION)
        self.assertIn("Customer-Owned Metadata Request", markdown_path.read_text(encoding="utf-8"))

    def test_docs_and_readme_reference_customer_owned_metadata_request(self):
        docs = (ROOT / "docs" / "Customer_Owned_Metadata_Request.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.customer_owned_metadata_request", docs)
        self.assertIn("docs/Customer_Owned_Metadata_Request.md", readme)
        self.assertIn("customer-owned metadata", bundle.lower())


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path

from reference_engine.aws_metadata_adapter import (
    build_adapter_report,
    load_source_exports,
    normalize_source_exports,
    render_markdown,
    write_outputs,
)
from reference_engine.customer_evaluation import load_payload


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "aws_metadata_adapter_source_exports.json"


class AWSMetadataAdapterTests(unittest.TestCase):
    def test_loads_metadata_source_exports(self):
        rows = load_source_exports(INPUTS)

        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row["record_id"] for row in rows}), 8)

    def test_normalizes_safe_rows_and_skips_unsafe_rows(self):
        payload = normalize_source_exports(load_source_exports(INPUTS))

        self.assertEqual(payload["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(payload["adapter_summary"]["accepted_rows"], 6)
        self.assertEqual(payload["adapter_summary"]["skipped_rows"], 2)
        reasons = {item["reason"] for item in payload["adapter_summary"]["skipped"]}
        self.assertIn("prohibited field present: raw_log", reasons)
        self.assertIn("unsupported source_format", reasons)
        for action in payload["actions"]:
            self.assertEqual(action["context"]["domain_profile"], "cloud_admin")
            self.assertEqual(action["tool_plan"]["metadata"]["cloud_provider"], "aws")
            self.assertEqual(action["tool_plan"]["metadata"]["adapter_mode"], "non_executing")
            self.assertIn("postcondition_evidence_expected", action["tool_plan"]["metadata"])
            self.assertIn("session_and_delegated_approval_context", action["tool_plan"]["metadata"])

    def test_preserves_session_and_delegated_approval_context(self):
        payload = normalize_source_exports(load_source_exports(INPUTS))
        by_record = {
            action["tool_plan"]["metadata"]["source_record_id"]: action
            for action in payload["actions"]
        }

        gateway_action = by_record["aws-meta-001"]["tool_plan"]["metadata"]["session_and_delegated_approval_context"]
        self.assertTrue(gateway_action["gateway_only_path"])
        self.assertTrue(gateway_action["delegated_on_behalf_of"])
        self.assertEqual(gateway_action["tool_discovery_method"], "role_filtered_tools_list")
        self.assertEqual(gateway_action["approval_mode"], "required_for_side_effect")

        bypass_action = by_record["aws-meta-004"]
        bypass_context = bypass_action["tool_plan"]["metadata"]["session_and_delegated_approval_context"]
        self.assertTrue(bypass_context["gateway_bypass_detected"])
        self.assertEqual(bypass_context["approval_mode"], "never")
        self.assertGreaterEqual(bypass_action["base_action_risk"], 0.62)

    def test_builds_adapter_report_and_customer_evaluation(self):
        report = build_adapter_report(load_source_exports(INPUTS))

        self.assertEqual(report["version"], "smerc.aws-metadata-adapter.v1")
        self.assertEqual(report["accepted_rows"], 6)
        self.assertEqual(report["skipped_rows"], 2)
        self.assertEqual(report["customer_evaluation"]["summary"]["total_actions"], 6)
        self.assertNotIn("adapter_summary", report["normalized_customer_evaluation"])
        self.assertIn("does not call AWS APIs", report["evidence_boundary"])
        self.assertIn("iam_policy_change_summary", report["accepted_source_format_counts"])
        self.assertEqual(report["session_and_delegated_approval_summary"]["boolean_counts"]["gateway_bypass_detected"], 1)
        self.assertEqual(report["session_and_delegated_approval_summary"]["approval_mode_counts"]["never"], 1)

    def test_markdown_explains_work_result_impact_and_boundary(self):
        markdown = render_markdown(build_adapter_report(load_source_exports(INPUTS)))

        self.assertIn("AWS Metadata Adapter Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("non-executing", markdown)
        self.assertIn("Session and delegated approval summary", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_adapter_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "aws_metadata_adapter"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_adapter_report(load_source_exports(INPUTS))
        normalized = scratch / "normalized.json"
        report_json = scratch / "report.json"
        report_md = scratch / "report.md"
        customer_json = scratch / "customer.json"
        customer_md = scratch / "customer.md"

        write_outputs(
            report,
            normalized_output=normalized,
            json_output=report_json,
            markdown_output=report_md,
            customer_json_output=customer_json,
            customer_markdown_output=customer_md,
        )

        self.assertEqual(len(load_payload(normalized)["actions"]), 6)
        self.assertIn("AWS Metadata Adapter Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(report_json.read_text(encoding="utf-8"))["skipped_rows"], 2)

    def test_docs_and_readme_reference_adapter_contract(self):
        docs = (ROOT / "docs" / "AWS_Metadata_Intake_Contract.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs" / "AWS_Deployable_Bot_Readiness_Path.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("metadata-only", docs)
        self.assertIn("Prohibited Inputs", docs)
        self.assertIn("python -m reference_engine.aws_metadata_adapter", docs)
        self.assertIn("docs/AWS_Metadata_Intake_Contract.md", readiness)
        self.assertIn("docs/AWS_Metadata_Intake_Contract.md", readme)


if __name__ == "__main__":
    unittest.main()

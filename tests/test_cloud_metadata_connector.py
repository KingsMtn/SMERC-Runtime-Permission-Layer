import unittest
from pathlib import Path

from reference_engine.cloud_metadata_connector import (
    build_connector_report,
    load_source_exports,
    normalize_source_exports,
    render_markdown,
    write_outputs,
)
from reference_engine.customer_evaluation import load_payload


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "cloud_admin_source_exports.json"


class CloudMetadataConnectorTests(unittest.TestCase):
    def test_loads_supported_cloud_source_exports(self):
        rows = load_source_exports(INPUTS)

        self.assertEqual(len(rows), 6)
        self.assertEqual(len({row["record_id"] for row in rows}), 6)

    def test_normalizes_exports_to_customer_evaluation_contract(self):
        payload = normalize_source_exports(load_source_exports(INPUTS))

        self.assertEqual(payload["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(len(payload["actions"]), 6)
        for action in payload["actions"]:
            self.assertEqual(action["context"]["domain_profile"], "cloud_admin")
            self.assertIn("source_format", action["context"])
            self.assertIn("ref_gate", action)
            self.assertIn("tool_plan", action)

    def test_builds_connector_report_and_customer_evaluation(self):
        report = build_connector_report(load_source_exports(INPUTS))

        self.assertEqual(report["version"], "smerc.cloud-metadata-connector.v1")
        self.assertEqual(report["source_export_count"], 6)
        self.assertEqual(report["normalized_action_count"], 6)
        self.assertEqual(report["customer_evaluation"]["summary"]["total_actions"], 6)
        self.assertGreaterEqual(report["customer_evaluation"]["summary"]["non_executable_routes"], 2)
        self.assertIn("does not call AWS", report["evidence_boundary"])
        self.assertIn("terraform_plan_change", report["source_format_counts"])

    def test_markdown_explains_work_result_impact_and_boundary(self):
        markdown = render_markdown(build_connector_report(load_source_exports(INPUTS)))

        self.assertIn("Cloud Metadata Connector Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("does not call AWS", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_connector_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "cloud_metadata_connector"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_connector_report(load_source_exports(INPUTS))
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
        self.assertIn("Cloud Metadata Connector Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))

    def test_docs_and_readme_reference_connector(self):
        docs = (ROOT / "docs" / "Cloud_Metadata_Connector.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.cloud_metadata_connector", docs)
        self.assertIn("read-only exported summaries", docs)
        self.assertIn("docs/Cloud_Metadata_Connector.md", readme)


if __name__ == "__main__":
    unittest.main()

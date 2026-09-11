import json
import unittest
from pathlib import Path

from reference_engine.aws_shadow_mirror_adapter import (
    build_adapter_report,
    load_source_exports,
    normalize_source_exports,
    render_markdown,
    write_outputs,
)
from reference_engine.customer_evaluation import load_payload


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "aws_shadow_mirror_source_exports.json"


class AWSShadowMirrorAdapterTests(unittest.TestCase):
    def test_loads_shadow_mirror_source_exports(self):
        rows = load_source_exports(INPUTS)

        self.assertEqual(len(rows), 4)
        self.assertEqual(len({row["record_id"] for row in rows}), 4)

    def test_normalizes_safe_rows_and_skips_payload_rows(self):
        payload = normalize_source_exports(load_source_exports(INPUTS))

        self.assertEqual(payload["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(payload["adapter_summary"]["accepted_rows"], 3)
        self.assertEqual(payload["adapter_summary"]["skipped_rows"], 1)
        self.assertEqual(
            payload["adapter_summary"]["skipped"][0]["reason"],
            "prohibited field present: raw_payload",
        )
        for action in payload["actions"]:
            metadata = action["tool_plan"]["metadata"]
            self.assertEqual(action["context"]["domain_profile"], "cloud_admin")
            self.assertEqual(metadata["cloud_provider"], "aws")
            self.assertEqual(metadata["adapter_mode"], "shadow_observe_only")
            self.assertTrue(metadata["payload_boundary"]["derived_metadata_only"])
            self.assertFalse(metadata["payload_boundary"]["payload_inspected"])
            self.assertFalse(metadata["payload_boundary"]["payload_retained"])

    def test_builds_shadow_mirror_report_and_customer_evaluation(self):
        report = build_adapter_report(load_source_exports(INPUTS))

        self.assertEqual(report["version"], "smerc.aws-shadow-mirror-adapter.v1")
        self.assertEqual(report["accepted_rows"], 3)
        self.assertEqual(report["skipped_rows"], 1)
        self.assertEqual(report["customer_evaluation"]["summary"]["total_actions"], 3)
        self.assertIn("direct_eni_mirroring", report["mirror_method_counts"])
        self.assertIn("gateway_load_balancer_endpoint", report["mirror_method_counts"])
        self.assertEqual(report["high_velocity_flow_count"], 2)
        self.assertEqual(report["sensitive_pattern_flow_count"], 1)
        self.assertIn("does not configure VPC Traffic Mirroring", report["evidence_boundary"])
        self.assertNotIn("adapter_summary", report["normalized_customer_evaluation"])

    def test_high_sensitivity_flow_gets_restrictive_posture(self):
        report = build_adapter_report(load_source_exports(INPUTS))
        records = {
            record["action_id"]: record
            for record in report["customer_evaluation"]["records"]
        }
        high_sensitivity = next(
            record for record in records.values() if "high_volume_egress" in record["action_id"]
        )

        self.assertIn(high_sensitivity["decision"]["posture"], {"FREEZE", "DENY", "ESCALATE"})
        self.assertFalse(high_sensitivity["sparta_route"]["executable"])

    def test_markdown_explains_shadow_mode_boundary(self):
        markdown = render_markdown(build_adapter_report(load_source_exports(INPUTS)))

        self.assertIn("AWS Shadow Mirror Adapter Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("not a firewall path", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_shadow_mirror_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "aws_shadow_mirror"
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

        self.assertEqual(len(load_payload(normalized)["actions"]), 3)
        self.assertIn("AWS Shadow Mirror Adapter Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(report_json.read_text(encoding="utf-8"))["skipped_rows"], 1)

    def test_docs_and_readme_reference_shadow_mirror_path(self):
        docs = (ROOT / "docs" / "AWS_Shadow_Mirror_Metadata_Path.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs" / "AWS_Deployable_Bot_Readiness_Path.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("metadata-only", docs)
        self.assertIn("VPC Traffic Mirroring", docs)
        self.assertIn("Gateway Load Balancer", docs)
        self.assertIn("python -m reference_engine.aws_shadow_mirror_adapter", docs)
        self.assertIn("docs/AWS_Shadow_Mirror_Metadata_Path.md", readiness)
        self.assertIn("docs/AWS_Shadow_Mirror_Metadata_Path.md", readme)


if __name__ == "__main__":
    unittest.main()

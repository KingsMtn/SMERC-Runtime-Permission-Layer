import unittest
from pathlib import Path

from reference_engine.aws_postcondition_evidence import (
    build_aws_postcondition_report,
    load_aws_observations,
    load_json_object,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "reports" / "aws_metadata_adapter" / "customer_evaluation_report.json"
OBSERVATIONS = ROOT / "examples" / "aws_postcondition_observations.json"


class AWSPostconditionEvidenceTests(unittest.TestCase):
    def test_builds_aws_postcondition_report(self):
        report = build_aws_postcondition_report(load_json_object(EVALUATION), load_aws_observations(OBSERVATIONS))

        self.assertEqual(report["version"], "smerc.aws-postcondition-evidence.v1")
        self.assertEqual(report["evaluated_actions"], 6)
        self.assertEqual(report["observed_actions"], 6)
        self.assertGreaterEqual(report["aws_postcondition_status_counts"].get("pass", 0), 4)
        self.assertGreaterEqual(report["aws_postcondition_status_counts"].get("gap", 0), 1)
        self.assertIn("AgentCore Runtime", " ".join(report["aws_official_signal_surfaces_used_as_model"]))
        self.assertIn("metadata-only", report["evidence_boundary"])

    def test_detects_missing_aws_source_and_missing_route_control(self):
        report = build_aws_postcondition_report(load_json_object(EVALUATION), load_aws_observations(OBSERVATIONS))
        by_id = {record["action_id"]: record for record in report["records"]}

        change_set = by_id["AWS_ADAPTER_003_execute_change_set_that_replaces_stateful_resources"]
        self.assertEqual(change_set["aws_postcondition_status"], "gap")
        self.assertIn("cloudwatch_metric_or_log", change_set["missing_aws_evidence_sources"])

        s3_action = by_id["AWS_ADAPTER_005_widen_bucket_object_access_during_failed_data_export"]
        self.assertEqual(s3_action["aws_postcondition_status"], "gap")
        self.assertIn("require_rollback_plan", s3_action["missing_controls"])

    def test_rejects_secret_bearing_observations(self):
        payload = [
            {
                "action_id": "bad",
                "aws_surface": "iam_policy_change_summary",
                "expected_aws_evidence_sources": ["cloudtrail_management_event"],
                "secret": "do-not-accept",
                "observed_controls": [],
                "execution": {
                    "attempted": False,
                    "status": "not_executed",
                    "rollback_performed": False,
                    "rollback_success": None,
                    "notes": "bad",
                },
            }
        ]
        scratch = ROOT / "tests" / "_tmp" / "aws_postcondition_secret.json"
        scratch.parent.mkdir(parents=True, exist_ok=True)
        scratch.write_text(__import__("json").dumps(payload), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_aws_observations(scratch)

    def test_markdown_and_outputs_include_work_result_impact(self):
        report = build_aws_postcondition_report(load_json_object(EVALUATION), load_aws_observations(OBSERVATIONS))
        markdown = render_markdown(report)

        self.assertIn("AWS Postcondition Evidence Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("AWS Signal Surfaces Modeled", markdown)

        scratch = ROOT / "tests" / "_tmp" / "aws_postcondition"
        json_path = scratch / "report.json"
        markdown_path = scratch / "report.md"
        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertIn("aws-postcondition-evidence", json_path.read_text(encoding="utf-8"))
        self.assertIn("AWS Postcondition Evidence Report", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

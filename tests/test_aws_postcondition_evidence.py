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
        self.assertEqual(report["evaluated_actions"], 9)
        self.assertEqual(report["observed_actions"], 9)
        self.assertEqual(report["aws_postcondition_status_counts"].get("pass", 0), 7)
        self.assertEqual(report["aws_postcondition_status_counts"].get("gap", 0), 2)
        self.assertNotIn("unobserved", report["aws_postcondition_status_counts"])
        self.assertEqual(report["evidence_assurance_counts"], {"modeled_unverified": 9})
        self.assertEqual(report["proof_eligible_actions"], 0)
        self.assertGreater(report["route_control_evidence"]["required_control_count"], 0)
        self.assertGreater(report["route_control_evidence"]["route_control_evidence_ratio"], 0.9)
        self.assertEqual(report["agentcore_runtime_postcondition_summary"]["runtime_action_count"], 5)
        self.assertEqual(report["agentcore_runtime_postcondition_summary"]["status_counts"]["pass"], 5)
        self.assertIn(
            "agentcore_runtime_trace_span",
            report["agentcore_runtime_postcondition_summary"]["observed_runtime_source_counts"],
        )
        self.assertIn("AgentCore Runtime", " ".join(report["aws_official_signal_surfaces_used_as_model"]))
        self.assertIn("metadata-only", report["evidence_boundary"])
        self.assertIn("modeled and unverified", report["evidence_boundary"])
        self.assertTrue(all(not record["proof_eligible"] for record in report["records"]))

    def test_detects_missing_aws_source_and_missing_route_control(self):
        report = build_aws_postcondition_report(load_json_object(EVALUATION), load_aws_observations(OBSERVATIONS))
        by_id = {record["action_id"]: record for record in report["records"]}

        change_set = by_id["AWS_ADAPTER_003_execute_change_set_that_replaces_stateful_resources"]
        self.assertEqual(change_set["aws_postcondition_status"], "gap")
        self.assertIn("cloudwatch_metric_or_log", change_set["missing_aws_evidence_sources"])

        s3_action = by_id["AWS_ADAPTER_005_widen_bucket_object_access_during_failed_data_export"]
        self.assertEqual(s3_action["aws_postcondition_status"], "gap")
        self.assertIn("require_rollback_plan", s3_action["missing_controls"])
        self.assertEqual(s3_action["evidence_depth"], "partial_required_control_evidence")
        self.assertLess(s3_action["route_control_evidence_ratio"], 1)

        weak_session = by_id["AWS_ADAPTER_008_invoke_runtime_using_client_supplied_session_identifier_under_shared_bac"]
        self.assertEqual(weak_session["aws_postcondition_status"], "pass")
        self.assertEqual(weak_session["execution_status"], "not_executed")
        self.assertIn("block_execution", weak_session["applied_required_controls"])

        command_shell = by_id["AWS_ADAPTER_009_open_interactive_command_shell_in_runtime_with_broad_execution_role_cred"]
        self.assertEqual(command_shell["aws_postcondition_status"], "pass")
        self.assertIn("agentcore_runtime_trace_span", command_shell["observed_aws_evidence_sources"])

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
        self.assertIn("Route control evidence", markdown)
        self.assertIn("AgentCore runtime postcondition summary", markdown)
        self.assertIn("Evidence ratio", markdown)
        self.assertIn("Evidence assurance counts", markdown)
        self.assertIn("Proof-eligible actions", markdown)

        scratch = ROOT / "tests" / "_tmp" / "aws_postcondition"
        json_path = scratch / "report.json"
        markdown_path = scratch / "report.md"
        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertIn("aws-postcondition-evidence", json_path.read_text(encoding="utf-8"))
        self.assertIn("AWS Postcondition Evidence Report", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

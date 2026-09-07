import unittest
from pathlib import Path

from reference_engine.aws_cloud_action_replay import (
    aws_reason_codes,
    build_report,
    load_payload,
    render_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "aws_cloud_action_replay_actions.json"


class AWSCloudActionReplayTests(unittest.TestCase):
    def test_builds_aws_cloud_action_replay(self):
        report = build_report(load_payload(SAMPLE))

        self.assertEqual(report["version"], "smerc.aws-cloud-action-replay.v1")
        self.assertEqual(report["scenario_count"], 12)
        self.assertEqual(report["summary"]["valid_ledgers"], 12)
        self.assertGreaterEqual(report["summary"]["non_executable_routes"], 3)
        self.assertEqual(report["pilot_fit"]["fit"], "strong")
        self.assertGreaterEqual(len(report["summary"]["posture_counts"]), 3)
        self.assertIn("iam", report["aws_surface_counts"])
        self.assertIn("cloudformation", report["aws_surface_counts"])
        self.assertIn("cost_management", report["aws_surface_counts"])

    def test_records_include_aws_reason_codes_alignment_and_impact(self):
        report = build_report(load_payload(SAMPLE))

        for record in report["records"]:
            self.assertIn("aws_reason_codes", record)
            self.assertIn("aws_reason_labels", record)
            self.assertIn("aws_alignment", record)
            self.assertIn("work_result_impact", record)
            self.assertIn("work", record["work_result_impact"])
            self.assertIn("result", record["work_result_impact"])
            self.assertIn("impact", record["work_result_impact"])

    def test_specific_aws_risks_are_classified(self):
        report = build_report(load_payload(SAMPLE))
        gateway = next(record for record in report["records"] if record["action_id"] == "AWS_AGENTCORE_GATEWAY_BYPASS_002")
        iam = next(record for record in report["records"] if record["action_id"] == "AWS_IAM_ROLE_EXPANSION_003")
        cost = next(record for record in report["records"] if record["action_id"] == "AWS_COST_VELOCITY_SPIKE_010")
        rds = next(record for record in report["records"] if record["action_id"] == "AWS_RDS_CLUSTER_DELETE_008")

        self.assertIn("AGENTCORE_GATEWAY_BYPASS_RISK", gateway["aws_reason_codes"])
        self.assertIn("IAM_SCOPE_EXPANSION", iam["aws_reason_codes"])
        self.assertIn("COST_VELOCITY_SPIKE", cost["aws_reason_codes"])
        self.assertIn("RDS_DATA_PLANE_RECOVERY_RISK", rds["aws_reason_codes"])

    def test_markdown_is_reviewer_readable_and_bounded(self):
        markdown = render_markdown(build_report(load_payload(SAMPLE)))

        self.assertIn("AWS Cloud Action Replay", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("AWS Reason Codes", markdown)
        self.assertIn("not AWS endorsement", markdown)
        self.assertIn("replacement for IAM", markdown)

    def test_docs_reference_aws_cloud_action_replay(self):
        doc = (ROOT / "docs" / "AWS_Cloud_Action_Replay.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.aws_cloud_action_replay", doc)
        self.assertIn("metadata-only", doc)
        self.assertIn("AgentCore", doc)


if __name__ == "__main__":
    unittest.main()

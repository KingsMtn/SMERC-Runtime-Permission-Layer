import unittest
from pathlib import Path

from reference_engine.aws_agent_action_chain import build_report, load_payload, render_markdown


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "aws_agent_action_chain.json"


class AWSAgentActionChainTests(unittest.TestCase):
    def test_builds_agent_action_chain_report(self):
        report = build_report(load_payload(SAMPLE))

        self.assertEqual(report["version"], "smerc.aws-agent-action-chain.v1")
        self.assertEqual(report["scenario_count"], 8)
        self.assertEqual(report["summary"]["valid_ledgers"], 8)
        self.assertIn("pass", report["summary"]["bedrock_guardrail_counts"])
        self.assertIn("iam", report["summary"]["aws_surface_counts"])
        self.assertIn("cloudformation", report["summary"]["aws_surface_counts"])
        self.assertIn("s3_policy", report["summary"]["aws_surface_counts"])
        self.assertIn("cross_account_delegation", report["summary"]["aws_surface_counts"])
        self.assertIn("agent_runtime_retry_loop", report["summary"]["aws_surface_counts"])

    def test_records_show_chain_context(self):
        report = build_report(load_payload(SAMPLE))
        iam_record = next(record for record in report["records"] if record["action_id"] == "AWS_CHAIN_GUARDRAIL_PASS_IAM_WIDE_002")

        self.assertEqual(iam_record["bedrock_guardrail_status"], "pass")
        self.assertTrue(iam_record["iam_authorized"])
        self.assertEqual(iam_record["rollback_checkpoint_state"], "missing")
        self.assertEqual(iam_record["ref_gate_status"], "fail")
        self.assertIn(iam_record["smerc_posture"], {"DENY", "FREEZE", "ESCALATE"})

        retry_record = next(record for record in report["records"] if record["action_id"] == "AWS_CHAIN_AGENT_RETRY_LOOP_008")
        self.assertEqual(retry_record["aws_surface"], "agent_runtime_retry_loop")
        self.assertEqual(retry_record["smerc_posture"], "THROTTLE")

    def test_markdown_is_bounded_and_positioned(self):
        markdown = render_markdown(build_report(load_payload(SAMPLE)))

        self.assertIn("AWS Agent Action Chain", markdown)
        self.assertIn("Bedrock-style Guardrail", markdown)
        self.assertIn("SMERC Recoverability Gate", markdown)
        self.assertIn("does not replace guardrails or IAM", markdown)
        self.assertIn("AWS endorsement", markdown)

    def test_docs_reference_runner_and_boundary(self):
        doc = (ROOT / "docs" / "AWS_Agent_Action_Chain.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.aws_agent_action_chain", doc)
        self.assertIn("metadata-only", doc)
        self.assertIn("Bedrock-style", doc)


if __name__ == "__main__":
    unittest.main()

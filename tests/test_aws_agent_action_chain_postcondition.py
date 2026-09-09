import unittest
from pathlib import Path

from reference_engine.aws_agent_action_chain_postcondition import build_report, render_markdown, write_outputs
from reference_engine.customer_evaluation import load_payload


ROOT = Path(__file__).resolve().parents[1]
ACTIONS = ROOT / "examples" / "aws_agent_action_chain.json"
OBSERVATIONS = ROOT / "examples" / "aws_agent_action_chain_observations.json"


class AWSAgentActionChainPostconditionTests(unittest.TestCase):
    def test_builds_chain_postcondition_report(self):
        report = build_report(load_payload(ACTIONS), OBSERVATIONS)

        self.assertEqual(report["version"], "smerc.aws-agent-action-chain-postcondition.v1")
        self.assertEqual(report["source_chain_version"], "smerc.aws-agent-action-chain.v1")
        self.assertEqual(report["evaluated_actions"], 5)
        self.assertEqual(report["observed_actions"], 5)
        self.assertGreaterEqual(report["aws_postcondition_status_counts"].get("pass", 0), 4)
        self.assertGreaterEqual(report["aws_postcondition_status_counts"].get("gap", 0), 1)

    def test_detects_missing_chain_evidence_source(self):
        report = build_report(load_payload(ACTIONS), OBSERVATIONS)
        by_id = {record["action_id"]: record for record in report["records"]}

        change_set = by_id["AWS_CHAIN_CLOUDFORMATION_REPLACE_003"]
        self.assertEqual(change_set["aws_postcondition_status"], "gap")
        self.assertIn("cloudwatch_metric_or_log", change_set["missing_aws_evidence_sources"])

    def test_markdown_and_outputs_are_reviewer_readable(self):
        report = build_report(load_payload(ACTIONS), OBSERVATIONS)
        markdown = render_markdown(report)

        self.assertIn("AWS Agent Action Chain Postcondition Evidence", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("AWS Signal Surfaces Modeled", markdown)

        scratch = ROOT / "tests" / "_tmp" / "aws_agent_action_chain_postcondition"
        json_path = scratch / "report.json"
        markdown_path = scratch / "report.md"
        write_outputs(report, json_path, markdown_path)

        self.assertIn("aws-agent-action-chain-postcondition", json_path.read_text(encoding="utf-8"))
        self.assertIn("AWS Agent Action Chain Postcondition Evidence", markdown_path.read_text(encoding="utf-8"))

    def test_docs_reference_runner(self):
        doc = (ROOT / "docs" / "AWS_Agent_Action_Chain_Postcondition_Evidence.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.aws_agent_action_chain_postcondition", doc)
        self.assertIn("metadata-only", doc)
        self.assertIn("Postcondition Evidence", doc)


if __name__ == "__main__":
    unittest.main()

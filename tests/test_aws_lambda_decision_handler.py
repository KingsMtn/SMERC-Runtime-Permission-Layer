import json
import unittest
from pathlib import Path

from reference_engine.aws_lambda_decision_handler import EVIDENCE_BOUNDARY, lambda_handler


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "aws_lambda_decision_event.json"


class AWSLambdaDecisionHandlerTests(unittest.TestCase):
    def test_lambda_handler_returns_compact_recoverability_decision(self):
        event = json.loads(SAMPLE.read_text(encoding="utf-8"))

        response = lambda_handler(event)

        self.assertEqual(response["version"], "smerc.aws-lambda-decision-handler.v1")
        self.assertEqual(response["request_id"], "AWS_BEDROCK_ACTION_GROUP_LAMBDA_001")
        self.assertIn(response["posture"], {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertIn("route_state", response)
        self.assertIn("required_controls", response)
        self.assertTrue(response["ledger_valid"])
        self.assertIn("metadata-only", response["evidence_boundary"])
        self.assertIn("does not call AWS", response["evidence_boundary"])

    def test_lambda_handler_accepts_api_gateway_style_json_body(self):
        event = {"body": SAMPLE.read_text(encoding="utf-8")}

        response = lambda_handler(event)

        self.assertEqual(response["request_id"], "AWS_BEDROCK_ACTION_GROUP_LAMBDA_001")
        self.assertEqual(response["evidence_boundary"], EVIDENCE_BOUNDARY)

    def test_aws_docs_reference_handler_and_boundaries(self):
        kill_switch = (ROOT / "docs" / "AWS_Bedrock_Agent_Kill_Switch_Pattern.md").read_text(encoding="utf-8")
        evidence_path = (ROOT / "docs" / "AWS_Security_Ecosystem_Evidence_Path.md").read_text(encoding="utf-8")
        marketplace = (ROOT / "docs" / "AWS_Marketplace_Validation_Path.md").read_text(encoding="utf-8")
        moat = (ROOT / "docs" / "SMERC_Defensible_Moat_And_Commercial_Boundary.md").read_text(encoding="utf-8")

        self.assertIn("reference_engine/aws_lambda_decision_handler.py", kill_switch)
        self.assertIn("Bedrock Agent Action Group", kill_switch)
        self.assertIn("AWS endorsement", kill_switch)
        self.assertIn("Security Lake", evidence_path)
        self.assertIn("EventBridge", evidence_path)
        self.assertIn("Marketplace packaging is a later validation path", marketplace)
        self.assertIn("recoverability-before-execution control model", moat)
        self.assertIn("separate written commercial license", moat)


if __name__ == "__main__":
    unittest.main()


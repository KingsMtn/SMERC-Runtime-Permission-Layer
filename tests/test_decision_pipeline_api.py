import json
import unittest
from pathlib import Path

from reference_engine.decision_pipeline_api import EVIDENCE_BOUNDARY, api_gateway_handler, lambda_handler
from reference_engine.decision_pipeline_contract import VERSION


ROOT = Path(__file__).resolve().parents[1]


def request(record_index=0):
    manifest = json.loads(
        (ROOT / "examples" / "authorization_afterlife_evidence_manifest.json").read_text(encoding="utf-8")
    )
    manifest["records"] = [manifest["records"][record_index]]
    return {
        "version": VERSION,
        "pipeline_id": f"api-pipeline-{record_index}",
        "hard_gates": {
            "identity_valid": True, "delegation_valid": True, "authority_current": True,
            "recovery_capability_present": True, "evidence_non_secret": True,
        },
        "action": {
            "action_id": f"api-action-{record_index}", "description": "Bounded AWS metadata action",
            "tool": "aws-mcp", "actor": "customer-agent", "confidence": 0.95, "harm": 0.1,
            "consent": 0.95, "reversibility": 0.95, "external_effect": False,
            "sensitive_data": False,
        },
        "consequence_manifest": manifest,
    }


class DecisionPipelineAPITests(unittest.TestCase):
    def test_lambda_handler_returns_compact_settlement_decision(self):
        response = lambda_handler(request(0))
        self.assertEqual(response["final_decision"], "SETTLE")
        self.assertTrue(response["should_commit"])
        self.assertEqual(len(response["pipeline_sha256"]), 64)
        self.assertIn("does not call AWS", response["evidence_boundary"])

    def test_api_gateway_body_can_return_compensation(self):
        response = api_gateway_handler({"body": json.dumps(request(2))})
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["final_decision"], "COMPENSATE")
        self.assertFalse(body["should_commit"])

    def test_api_gateway_returns_bounded_validation_error(self):
        response = api_gateway_handler({"body": "{}"})
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertEqual(body["error"], "invalid_request")
        self.assertEqual(body["evidence_boundary"], EVIDENCE_BOUNDARY)


if __name__ == "__main__":
    unittest.main()

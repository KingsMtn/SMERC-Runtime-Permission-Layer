import json
import unittest
from pathlib import Path

from reference_engine.model_fitness import ModelFitnessEngine, evaluate_batch


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "model_agent_routing_examples.json"


class ModelFitnessEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ModelFitnessEngine()
        self.requests = json.loads(EXAMPLES.read_text(encoding="utf-8"))

    def by_id(self, task_id):
        return next(request for request in self.requests if request["task_id"] == task_id)

    def test_allows_low_risk_qualified_executor(self):
        result = self.engine.evaluate(self.by_id("ROUTE_CODE_REVIEW_LOW_RISK"))
        self.assertEqual(result["execution_posture"], "ALLOW")
        self.assertIn(result["recommended_executor"], {"general_llm", "security_review_agent"})
        self.assertIn("QUALIFIED_LOW_RISK_EXECUTOR", result["reason_codes"])

    def test_throttles_high_impact_deployment_to_specialized_agent(self):
        result = self.engine.evaluate(self.by_id("ROUTE_PROD_DEPLOYMENT"))
        self.assertEqual(result["recommended_executor"], "deployment_guardian")
        self.assertEqual(result["execution_posture"], "THROTTLE")
        self.assertIn("require_human_approval_before_external_effect", result["controls"])
        self.assertIn("general_llm", result["blocked_executors"])

    def test_escalates_or_throttles_restricted_finance_transfer_to_control_agent(self):
        result = self.engine.evaluate(self.by_id("ROUTE_RESTRICTED_FINANCE_TRANSFER"))
        self.assertEqual(result["recommended_executor"], "treasury_control_agent")
        self.assertIn(result["execution_posture"], {"THROTTLE", "ESCALATE"})
        self.assertIn("SENSITIVE_DATA_ROUTING", result["reason_codes"])
        self.assertIn("finance_chat_assistant", result["blocked_executors"])

    def test_denies_when_no_candidate_has_required_boundary(self):
        request = self.by_id("ROUTE_RESTRICTED_FINANCE_TRANSFER")
        broken = dict(request)
        broken["candidates"] = [dict(request["candidates"][0])]
        result = self.engine.evaluate(broken)
        self.assertEqual(result["recommended_executor"], None)
        self.assertEqual(result["execution_posture"], "DENY")
        self.assertIn("DATA_BOUNDARY_EXCEEDED", result["reason_codes"])

    def test_batch_evaluation_returns_all_records(self):
        results = evaluate_batch(self.requests)
        self.assertEqual(len(results), len(self.requests))
        self.assertTrue(all("candidate_rankings" in result for result in results))

    def test_validation_rejects_missing_fields(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate({"task_id": "BROKEN"})


if __name__ == "__main__":
    unittest.main()

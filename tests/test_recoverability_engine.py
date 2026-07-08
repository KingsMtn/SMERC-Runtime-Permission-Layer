import json
import unittest
from pathlib import Path

from reference_engine.recoverability_engine import RecoverabilityEngine, evaluate_batch


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "recoverability_action_requests.json"


class RecoverabilityEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = RecoverabilityEngine()
        self.actions = json.loads(EXAMPLES.read_text(encoding="utf-8"))

    def by_id(self, action_id):
        return next(action for action in self.actions if action["action_id"] == action_id)

    def test_allows_recoverable_test_run(self):
        result = self.engine.evaluate(self.by_id("AGENT_RUN_TESTS"))
        self.assertEqual(result["posture"], "ALLOW")
        self.assertEqual(result["enforcement_state"], "release")
        self.assertIn("retain_cancel_handle", result["controls"])

    def test_throttles_production_config_deploy(self):
        result = self.engine.evaluate(self.by_id("AGENT_DEPLOY_PROD_CONFIG"))
        self.assertEqual(result["posture"], "THROTTLE")
        self.assertEqual(result["enforcement_state"], "constrain")
        self.assertIn("rate_limit_external_side_effect", result["controls"])
        self.assertEqual(result["domain_profile"]["profile_id"], "general")
        self.assertIn("score_contributions", result["decision_trace"])
        self.assertIn("threshold_trace", result["decision_trace"])
        self.assertEqual(result["transition_guidance"]["current_posture"], "THROTTLE")

    def test_blocks_or_pauses_low_recovery_action(self):
        result = self.engine.evaluate(self.by_id("AGENT_DELETE_AUDIT_LOGS"))
        self.assertIn(result["posture"], {"FREEZE", "DENY"})
        self.assertIn("RECOVERY_CAPACITY_LOW", result["reason_codes"])
        self.assertIn("rollback test or recovery evidence", result["transition_guidance"]["evidence_needed"])

    def test_denies_high_exposure_customer_data_export(self):
        result = self.engine.evaluate(self.by_id("AGENT_EXPORT_CUSTOMER_DATA"))
        self.assertEqual(result["posture"], "DENY")
        self.assertIn("IRREVERSIBLE_EXPOSURE_HIGH", result["reason_codes"])
        self.assertIn("SENSITIVE_DATA", result["reason_codes"])

    def test_batch_evaluation_returns_all_records(self):
        results = evaluate_batch(self.actions)
        self.assertEqual(len(results), len(self.actions))
        self.assertTrue(all("risk_adjusted_authorization_score" in item["scores"] for item in results))
        self.assertTrue(all("decision_trace" in item for item in results))

    def test_validation_rejects_missing_fields(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate({"action_id": "BROKEN"})

    def test_domain_profile_calibrates_scores_without_hiding_trace(self):
        action = dict(self.by_id("AGENT_EXPORT_CUSTOMER_DATA"))
        general = self.engine.evaluate(action)
        action["context"] = {**action.get("context", {}), "domain_profile": "finance_ops"}
        finance = self.engine.evaluate(action)

        self.assertEqual(finance["domain_profile"]["profile_id"], "finance_ops")
        self.assertGreaterEqual(
            finance["scores"]["irreversible_exposure_score"],
            general["scores"]["irreversible_exposure_score"],
        )
        self.assertIn("profile_multiplier", finance["decision_trace"]["score_contributions"]["irreversible_exposure_score"])
        self.assertTrue(any(step["triggered"] for step in finance["decision_trace"]["threshold_trace"]))

    def test_unknown_domain_profile_is_rejected(self):
        action = dict(self.by_id("AGENT_RUN_TESTS"))
        action["context"] = {"domain_profile": "unknown_profile"}

        with self.assertRaises(ValueError):
            self.engine.evaluate(action)


if __name__ == "__main__":
    unittest.main()

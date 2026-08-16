import json
import unittest
from pathlib import Path

from reference_engine.constraint_eligibility import evaluate_constraint_eligibility


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "constraint_eligibility"


class ConstraintEligibilityTests(unittest.TestCase):
    def load(self, name):
        return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))

    def test_canary_is_constraint_eligible(self):
        result = evaluate_constraint_eligibility(self.load("constraint_eligible_canary.json"))

        self.assertTrue(result["constraint_eligible"])
        self.assertEqual(result["eligibility_labels"], ["constraint_eligible"])
        self.assertEqual(result["recommended_runtime_posture"], "ALLOW")
        self.assertEqual(result["matched_prohibited_patterns"], [])
        self.assertEqual(result["language_version"], "smerc.constraint-eligibility.v1")

    def test_audit_log_delete_is_categorically_prohibited(self):
        result = evaluate_constraint_eligibility(self.load("prohibited_audit_log_delete.json"))

        self.assertFalse(result["constraint_eligible"])
        self.assertEqual(result["recommended_runtime_posture"], "DENY")
        self.assertIn("categorically_prohibited", result["eligibility_labels"])
        self.assertIn("review_required", result["eligibility_labels"])
        self.assertIn("delete_log", result["matched_prohibited_patterns"])
        self.assertTrue(self.rule(result, "PROHIBITED_ACTION_PATTERN")["triggered"])

    def test_weak_authority_transfer_requires_authority(self):
        result = evaluate_constraint_eligibility(self.load("weak_authority_funds_transfer.json"))

        self.assertFalse(result["constraint_eligible"])
        self.assertEqual(result["recommended_runtime_posture"], "DENY")
        self.assertIn("requires_authority", result["eligibility_labels"])
        self.assertIn("recoverability_sensitive", result["eligibility_labels"])
        self.assertTrue(self.rule(result, "LOW_AUTHORITY_CONFIDENCE")["triggered"])
        self.assertTrue(self.rule(result, "RECOVERABILITY_SENSITIVE")["triggered"])

    def test_missing_identity_confidence_type_is_rejected(self):
        payload = self.load("constraint_eligible_canary.json")
        payload["context"]["identity_confidence"] = "high"

        with self.assertRaisesRegex(TypeError, "identity_confidence"):
            evaluate_constraint_eligibility(payload)

    def test_custom_prohibited_pattern_is_supported(self):
        payload = self.load("constraint_eligible_canary.json")
        payload["context"]["prohibited_action_patterns"] = ["deploy_canary"]

        result = evaluate_constraint_eligibility(payload)

        self.assertFalse(result["constraint_eligible"])
        self.assertEqual(result["recommended_runtime_posture"], "DENY")
        self.assertEqual(result["matched_prohibited_patterns"], ["deploy_canary"])

    @staticmethod
    def rule(result, rule_id):
        return next(item for item in result["rule_results"] if item["rule_id"] == rule_id)


if __name__ == "__main__":
    unittest.main()

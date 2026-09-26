import copy
import unittest

from reference_engine.continuing_authority import ContinuingAuthorityError, evaluate_continuing_authority


class ContinuingAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.grant = {
            "contract_id": "authority-001",
            "authority_epoch": 7,
            "authority_lineage": ["human:owner", "agent:coordinator"],
            "issued_at": 100,
            "valid_until": 500,
            "revalidation_triggers": ["policy_changed", "tool_version_changed"],
            "checkpoint_digest": "checkpoint-7",
            "settlement_requirements": ["outcome_verified", "cleanup_verified"],
            "descendant_contract_ids": ["child-1", "child-2"],
        }
        self.runtime = {
            "observed_at": 200,
            "current_authority_epoch": 7,
            "revoked_contract_ids": [],
            "trigger_events": [],
            "active_principals": ["human:owner", "agent:coordinator"],
            "invalidation_acknowledged_by": ["child-1", "child-2"],
            "checkpoint_digest": "checkpoint-7",
            "partial_effects_present": False,
            "satisfied_settlement_requirements": ["outcome_verified", "cleanup_verified"],
        }

    def evaluate(self, *, grant=None, runtime=None, phase="continue"):
        return evaluate_continuing_authority(grant or self.grant, runtime or self.runtime, phase=phase)

    def test_current_authority_can_continue(self):
        result = self.evaluate()
        self.assertEqual(result["decision"], "CONTINUE")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_epoch_change_requires_quarantine(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["current_authority_epoch"] = 8
        result = self.evaluate(runtime=runtime)
        self.assertEqual(result["decision"], "QUARANTINE")
        self.assertIn("authority_epoch_changed", result["reasons"])

    def test_revoked_partial_action_requires_compensation(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["revoked_contract_ids"] = ["authority-001"]
        runtime["partial_effects_present"] = True
        result = self.evaluate(runtime=runtime)
        self.assertEqual(result["decision"], "COMPENSATE")
        self.assertIn("partial_effects_require_compensation", result["reasons"])

    def test_expiry_cannot_be_hidden_by_valid_original_epoch(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["observed_at"] = 500
        result = self.evaluate(runtime=runtime)
        self.assertEqual(result["decision"], "QUARANTINE")
        self.assertIn("authority_lease_expired", result["reasons"])

    def test_missing_accountable_principal_creates_orphan(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["active_principals"] = ["agent:unrelated"]
        self.assertEqual(self.evaluate(runtime=runtime)["decision"], "ORPHANED")

    def test_policy_trigger_and_checkpoint_drift_require_revalidation(self):
        triggered = copy.deepcopy(self.runtime)
        triggered["trigger_events"] = ["policy_changed"]
        self.assertEqual(self.evaluate(runtime=triggered)["decision"], "REVALIDATE")

        checkpoint = copy.deepcopy(self.runtime)
        checkpoint["checkpoint_digest"] = "checkpoint-8"
        result = self.evaluate(runtime=checkpoint)
        self.assertEqual(result["decision"], "REVALIDATE")
        self.assertIn("checkpoint_discontinuity", result["reasons"])

    def test_settlement_requires_current_authority_and_all_evidence(self):
        self.assertEqual(self.evaluate(phase="settle")["decision"], "SETTLE")
        runtime = copy.deepcopy(self.runtime)
        runtime["satisfied_settlement_requirements"] = ["outcome_verified"]
        result = self.evaluate(runtime=runtime, phase="settle")
        self.assertEqual(result["decision"], "REVALIDATE")
        self.assertIn("settlement_missing:cleanup_verified", result["reasons"])

    def test_invalidation_propagation_is_visible(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["current_authority_epoch"] = 8
        runtime["invalidation_acknowledged_by"] = ["child-1"]
        result = self.evaluate(runtime=runtime)
        self.assertFalse(result["propagation"]["complete"])
        self.assertEqual(result["propagation"]["missing_acknowledgements"], ["child-2"])
        self.assertIn("descendant_invalidation_unconfirmed", result["reasons"])

    def test_invalid_contract_shape_fails_closed(self):
        grant = copy.deepcopy(self.grant)
        grant["valid_until"] = 100
        with self.assertRaisesRegex(ContinuingAuthorityError, "after"):
            self.evaluate(grant=grant)


if __name__ == "__main__":
    unittest.main()

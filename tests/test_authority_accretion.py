import copy
import unittest

from reference_engine.authority_accretion import AuthorityAccretionError, evaluate_acquired_authority


class AuthorityAccretionTests(unittest.TestCase):
    def setUp(self):
        self.envelope = {
            "envelope_id": "env-001", "authority_epoch": 7,
            "allowed_resource_kinds": ["credential", "service"],
            "allowed_capabilities": ["s3:GetObject", "logs:PutLogEvents"],
            "allowed_effects": ["read", "append_audit"], "allowed_providers": ["aws"],
            "max_delegation_depth": 1, "max_persistence_seconds": 900, "max_spend_minor": 100,
        }
        self.acquired = {
            "resource_id": "credential-001", "resource_kind": "credential", "provider": "aws",
            "capabilities": ["s3:GetObject"], "effects": ["read"], "delegation_depth": 0,
            "persistence_seconds": 300, "spend_minor": 0, "provenance_digest": "proof-001",
        }
        self.observation = {
            "current_authority_epoch": 7, "resolved_provenance_digest": "proof-001",
            "resolver_version": "aws-resolver-1", "quarantined_before_evaluation": True,
        }

    def evaluate(self, acquired=None, observation=None):
        return evaluate_acquired_authority(
            self.envelope, acquired or self.acquired, observation or self.observation
        )

    def test_bounded_resource_is_only_eligible(self):
        result = self.evaluate()
        self.assertEqual(result["decision"], "ELIGIBLE_FOR_ACTIVATION")
        self.assertFalse(result["should_activate"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_capability_and_effect_expansion_stay_quarantined(self):
        acquired = copy.deepcopy(self.acquired)
        acquired["capabilities"].append("iam:AttachRolePolicy")
        acquired["effects"].append("change_authority")
        result = self.evaluate(acquired)
        self.assertEqual(result["decision"], "QUARANTINE")
        self.assertIn("capability_expansion", result["reasons"])
        self.assertIn("effect_expansion", result["reasons"])

    def test_epoch_and_provenance_are_checked_at_activation(self):
        observation = copy.deepcopy(self.observation)
        observation.update(current_authority_epoch=8, resolved_provenance_digest="different")
        reasons = self.evaluate(observation=observation)["reasons"]
        self.assertIn("authority_epoch_changed", reasons)
        self.assertIn("provenance_resolution_mismatch", reasons)

    def test_budget_delegation_and_persistence_cannot_expand(self):
        acquired = copy.deepcopy(self.acquired)
        acquired.update(delegation_depth=2, persistence_seconds=901, spend_minor=101)
        self.assertEqual(set(self.evaluate(acquired)["reasons"]), {
            "delegation_depth_exceeded", "persistence_limit_exceeded", "spend_limit_exceeded"
        })

    def test_resource_must_arrive_quarantined(self):
        observation = copy.deepcopy(self.observation)
        observation["quarantined_before_evaluation"] = False
        self.assertIn("resource_was_not_quarantined", self.evaluate(observation=observation)["reasons"])

    def test_unknown_kind_fails_closed(self):
        envelope = copy.deepcopy(self.envelope)
        envelope["allowed_resource_kinds"].append("magic")
        with self.assertRaisesRegex(AuthorityAccretionError, "unknown kind"):
            evaluate_acquired_authority(envelope, self.acquired, self.observation)


if __name__ == "__main__":
    unittest.main()

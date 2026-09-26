import copy
import hashlib
import unittest

from reference_engine.consequence_time_reconciliation import reconcile_consequence_time
from reference_engine.delegated_continuance_contract import ContinuanceContractSigner


class ConsequenceTimeReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.intent = hashlib.sha256(b"deploy-reviewed-build").hexdigest()
        self.signer = ContinuanceContractSigner("test-key", b"k" * 32)
        root = self.signer.issue_root(
            tenant_id="tenant-1", originating_user_id="user-1", agent_id="coordinator",
            intent_digest=self.intent, capabilities=["deploy"], resources=["service/api"],
            max_actions=4, max_scope_units=10, max_cost_usd=5, max_delegation_depth=2,
            issued_at=100, expires_at=500, checkpoint_every_actions=2,
            cleanup_obligations=["remove-temporary-credential"],
        )
        self.contract = self.signer.delegate(
            root, agent_id="worker", capabilities=["deploy"], resources=["service/api"],
            max_actions=2, max_scope_units=4, max_cost_usd=2, expires_at=450,
            checkpoint_every_actions=1,
            cleanup_obligations=["remove-temporary-credential"],
        )
        self.action = {
            "capability": "deploy", "resource": "service/api", "intent_digest": self.intent,
            "scope_units": 1, "cost_usd": 0.5, "external_side_effect": True,
            "checkpoint_present": True, "cleanup_plan_present": True,
        }
        self.consumption = {"actions": 0, "scope_units": 0, "cost_usd": 0}
        self.grant = {
            "contract_id": "authority-1", "authority_epoch": 7,
            "authority_lineage": ["user-1", "coordinator"], "issued_at": 100,
            "valid_until": 500, "revalidation_triggers": ["policy_changed"],
            "checkpoint_digest": "checkpoint-7",
            "settlement_requirements": ["outcome_verified", "cleanup_verified"],
            "descendant_contract_ids": ["worker-contract"],
        }
        self.runtime = {
            "observed_at": 200, "current_authority_epoch": 7,
            "revoked_contract_ids": [], "trigger_events": [],
            "active_principals": ["user-1", "coordinator"],
            "invalidation_acknowledged_by": ["worker-contract"],
            "checkpoint_digest": "checkpoint-7",
            "satisfied_settlement_requirements": ["outcome_verified", "cleanup_verified"],
        }
        self.envelope = {
            "envelope_id": "env-1", "authority_epoch": 7,
            "allowed_resource_kinds": ["credential"],
            "allowed_capabilities": ["service:Deploy"], "allowed_effects": ["deploy"],
            "allowed_providers": ["aws"], "max_delegation_depth": 1,
            "max_persistence_seconds": 900, "max_spend_minor": 100,
        }
        self.resource = {
            "resource_id": "credential-1", "resource_kind": "credential", "provider": "aws",
            "capabilities": ["service:Deploy"], "effects": ["deploy"],
            "delegation_depth": 0, "persistence_seconds": 300, "spend_minor": 0,
            "provenance_digest": "proof-1",
        }
        self.observation = {
            "current_authority_epoch": 7, "resolved_provenance_digest": "proof-1",
            "resolver_version": "resolver-1", "quarantined_before_evaluation": True,
        }

    def reconcile(self, **overrides):
        values = {
            "signer": self.signer, "delegated_contract": self.contract,
            "proposed_action": self.action, "consumption": self.consumption,
            "authority_grant": self.grant, "authority_runtime": self.runtime,
            "acquired_envelope": self.envelope, "acquired_resource": self.resource,
            "acquired_observation": self.observation, "now": 200,
            "partial_effects_present": False,
        }
        values.update(overrides)
        return reconcile_consequence_time(**values)

    def test_current_bounded_chain_can_settle(self):
        result = self.reconcile()
        self.assertEqual(result["decision"], "SETTLE")
        self.assertTrue(result["should_commit"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_epoch_change_and_acquired_expansion_quarantine_before_commit(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["current_authority_epoch"] = 8
        observation = copy.deepcopy(self.observation)
        observation["current_authority_epoch"] = 8
        resource = copy.deepcopy(self.resource)
        resource["capabilities"].append("iam:AttachRolePolicy")
        result = self.reconcile(
            authority_runtime=runtime, acquired_observation=observation,
            acquired_resource=resource,
        )
        self.assertEqual(result["decision"], "QUARANTINE")
        self.assertFalse(result["should_commit"])
        self.assertIn("acquired:capability_expansion", result["reasons"])
        self.assertIn("continuing:authority_epoch_changed", result["reasons"])

    def test_revoked_chain_with_partial_effects_requires_compensation(self):
        runtime = copy.deepcopy(self.runtime)
        runtime["revoked_contract_ids"] = ["authority-1"]
        result = self.reconcile(authority_runtime=runtime, partial_effects_present=True)
        self.assertEqual(result["decision"], "COMPENSATE")
        self.assertFalse(result["should_commit"])
        self.assertIn("continuing:partial_effects_require_compensation", result["reasons"])

    def test_consumed_delegated_budget_cannot_be_hidden_by_current_authority(self):
        consumption = {"actions": 2, "scope_units": 0, "cost_usd": 0}
        result = self.reconcile(consumption=consumption)
        self.assertEqual(result["decision"], "QUARANTINE")
        self.assertIn("delegated:action_budget_exhausted", result["reasons"])


if __name__ == "__main__":
    unittest.main()

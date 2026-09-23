import copy
import hashlib
import unittest

from reference_engine.delegated_continuance_contract import (
    ContinuanceContractError,
    ContinuanceContractSigner,
    evaluate_delegated_continuance,
)


class DelegatedContinuanceContractTests(unittest.TestCase):
    def setUp(self):
        self.signer = ContinuanceContractSigner("continuance-key-1", b"delegated-continuance-test-secret-32-bytes")
        self.intent = hashlib.sha256(b"safely inspect and update the bounded deployment").hexdigest()
        self.root = self.signer.issue_root(
            tenant_id="smerc-labs",
            originating_user_id="owner-1",
            agent_id="coordinator",
            intent_digest=self.intent,
            capabilities=["read_deployment", "update_ephemeral_branch"],
            resources=["repo:SMERC", "branch:ephemeral"],
            max_actions=6,
            max_scope_units=20,
            max_cost_usd=1.0,
            max_delegation_depth=2,
            issued_at=100,
            expires_at=1000,
            checkpoint_every_actions=2,
            cleanup_obligations=["delete_ephemeral_branch"],
        )
        self.child = self.signer.delegate(
            self.root,
            agent_id="aws-worker",
            capabilities=["update_ephemeral_branch"],
            resources=["branch:ephemeral"],
            max_actions=3,
            max_scope_units=5,
            max_cost_usd=0.25,
            expires_at=700,
            checkpoint_every_actions=1,
            cleanup_obligations=["delete_ephemeral_branch"],
        )

    def action(self, **overrides):
        value = {
            "intent_digest": self.intent,
            "capability": "update_ephemeral_branch",
            "resource": "branch:ephemeral",
            "scope_units": 1,
            "cost_usd": 0.01,
            "external_side_effect": True,
            "checkpoint_present": True,
            "cleanup_plan_present": True,
        }
        value.update(overrides)
        return value

    def test_child_can_continue_with_attenuated_authority(self):
        result = evaluate_delegated_continuance(
            self.signer,
            self.child,
            self.action(),
            {"actions": 0, "scope_units": 0, "cost_usd": 0},
            now=200,
        )
        self.assertEqual(result["decision"], "CONTINUE")
        self.assertEqual(result["remaining"]["actions"], 2)
        self.assertEqual(result["remaining"]["cost_usd"], 0.24)

    def test_child_cannot_expand_parent_authority(self):
        with self.assertRaisesRegex(ContinuanceContractError, "capability_expansion"):
            self.signer.delegate(
                self.root,
                agent_id="worker",
                capabilities=["delete_production"],
                resources=["branch:ephemeral"],
                max_actions=1,
                max_scope_units=1,
                max_cost_usd=0,
                expires_at=500,
                checkpoint_every_actions=1,
                cleanup_obligations=["delete_ephemeral_branch"],
            )

    def test_scope_expansion_and_expired_resumption_are_blocked(self):
        expanded = evaluate_delegated_continuance(
            self.signer,
            self.child,
            self.action(scope_units=6),
            {"actions": 0, "scope_units": 0, "cost_usd": 0},
            now=200,
        )
        expired = evaluate_delegated_continuance(
            self.signer,
            self.child,
            self.action(),
            {"actions": 0, "scope_units": 0, "cost_usd": 0},
            now=700,
        )
        self.assertEqual(expanded["decision"], "BLOCK")
        self.assertIn("scope_budget_exhausted", expanded["reasons"])
        self.assertEqual(expired["decision"], "EXPIRED")

    def test_checkpoint_and_cleanup_are_preconditions_to_continue(self):
        checkpoint = evaluate_delegated_continuance(
            self.signer,
            self.child,
            self.action(checkpoint_present=False),
            {"actions": 1, "scope_units": 1, "cost_usd": 0.01},
            now=200,
        )
        cleanup = evaluate_delegated_continuance(
            self.signer,
            self.child,
            self.action(cleanup_plan_present=False),
            {"actions": 0, "scope_units": 0, "cost_usd": 0},
            now=200,
        )
        self.assertEqual(checkpoint["decision"], "CHECKPOINT_REQUIRED")
        self.assertEqual(cleanup["decision"], "CLEANUP_REQUIRED")

    def test_tampering_invalidates_contract(self):
        tampered = copy.deepcopy(self.child)
        tampered["contract"]["budget"]["max_cost_usd"] = 10.0
        with self.assertRaisesRegex(ContinuanceContractError, "signature"):
            self.signer.verify(tampered)


if __name__ == "__main__":
    unittest.main()

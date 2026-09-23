import hashlib
import threading
import unittest
from pathlib import Path

from reference_engine.consequence_settlement import (
    ConsequenceLedger,
    ConsequenceReservationError,
    ConsequenceSettlementError,
)
from reference_engine.delegated_continuance_contract import ContinuanceContractSigner


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "test_outputs" / "consequence_settlement_test.sqlite3"


class ConsequenceSettlementTests(unittest.TestCase):
    def setUp(self):
        DB.parent.mkdir(exist_ok=True)
        DB.unlink(missing_ok=True)
        self.ledger = ConsequenceLedger(DB)
        self.signer = ContinuanceContractSigner("settlement-key", b"consequence-settlement-test-secret-32-bytes")
        self.intent = hashlib.sha256(b"bounded shared deployment outcome").hexdigest()
        self.contract = self.signer.issue_root(
            tenant_id="smerc-labs", originating_user_id="owner", agent_id="coordinator",
            intent_digest=self.intent, capabilities=["mutate"], resources=["ephemeral"],
            max_actions=10, max_scope_units=10, max_cost_usd=1, max_delegation_depth=2,
            issued_at=100, expires_at=1000, checkpoint_every_actions=1,
            cleanup_obligations=["remove_ephemeral_state"],
        )
        self.ledger.create_budget(
            budget_id="shared", tenant_id="smerc-labs", intent_digest=self.intent,
            max_cost_usd=1.0, max_scope_units=10, max_mutations=4,
        )

    def tearDown(self):
        self.ledger.close()
        DB.unlink(missing_ok=True)
        Path(str(DB) + "-wal").unlink(missing_ok=True)
        Path(str(DB) + "-shm").unlink(missing_ok=True)

    def reserve(self, operation, task, cost=0.1, scope=1, mutations=1):
        return self.ledger.reserve(
            budget_id="shared", signer=self.signer, contract=self.contract,
            operation_key=operation, task_id=task,
            request={"intent_digest": self.intent, "cost_usd": cost, "scope_units": scope, "mutations": mutations},
            now=200,
        )

    def test_concurrent_agents_cannot_double_spend_capacity(self):
        outcomes = []
        barrier = threading.Barrier(2)

        def attempt(index):
            barrier.wait()
            try:
                outcomes.append(self.reserve(f"op-{index}", f"task-{index}", cost=0.75)["status"])
            except ConsequenceReservationError:
                outcomes.append("BLOCKED")

        threads = [threading.Thread(target=attempt, args=(index,)) for index in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertCountEqual(outcomes, ["RESERVED", "BLOCKED"])

    def test_retry_uses_same_reservation_even_with_new_task_id(self):
        first = self.reserve("stable-operation", "task-1")
        retry = self.reserve("stable-operation", "task-2")
        self.assertEqual(retry["reservation_id"], first["reservation_id"])
        self.assertTrue(retry["idempotent_replay"])
        self.assertEqual(retry["task_id"], "task-1")

    def test_operation_key_cannot_be_rebound_to_larger_request(self):
        self.reserve("stable-operation", "task-1")
        with self.assertRaisesRegex(ConsequenceReservationError, "conflicts"):
            self.reserve("stable-operation", "task-2", scope=5)

    def test_expired_or_intent_mismatched_contract_cannot_reserve(self):
        with self.assertRaisesRegex(ConsequenceReservationError, "expired"):
            self.ledger.reserve(
                budget_id="shared", signer=self.signer, contract=self.contract,
                operation_key="late", task_id="task-late",
                request={"intent_digest": self.intent, "cost_usd": 0, "scope_units": 0, "mutations": 0},
                now=1000,
            )
        with self.assertRaisesRegex(ConsequenceReservationError, "intent"):
            self.ledger.reserve(
                budget_id="shared", signer=self.signer, contract=self.contract,
                operation_key="wrong-intent", task_id="task-wrong",
                request={"intent_digest": "0" * 64, "cost_usd": 0, "scope_units": 0, "mutations": 0},
                now=200,
            )

    def test_recovery_releases_scope_but_not_spend(self):
        reservation = self.reserve("recoverable", "task-1", cost=0.2, scope=3, mutations=1)
        self.ledger.settle(
            reservation["reservation_id"], outcome="RECOVERED", actual_cost_usd=0.2,
            actual_scope_units=3, actual_mutations=1, cleanup_verified=True,
            evidence={"residual_count": 0},
        )
        status = self.ledger.budget_status("shared")
        self.assertEqual(status["committed"], {"cost_usd": 0.2, "scope_units": 0.0, "mutations": 0.0})

    def test_partial_cleanup_remains_unsettled_and_holds_capacity(self):
        reservation = self.reserve("partial-cleanup", "task-1", scope=4, mutations=2)
        self.ledger.settle(
            reservation["reservation_id"], outcome="UNSETTLED", actual_cost_usd=0.1,
            actual_scope_units=1, actual_mutations=1, cleanup_verified=False,
            evidence={"residual_count": 1},
        )
        status = self.ledger.budget_status("shared")
        self.assertEqual(status["committed"]["scope_units"], 4.0)
        self.assertEqual(status["committed"]["mutations"], 2.0)

    def test_recovered_requires_verified_cleanup(self):
        reservation = self.reserve("bad-recovery", "task-1")
        with self.assertRaisesRegex(ConsequenceSettlementError, "verified cleanup"):
            self.ledger.settle(
                reservation["reservation_id"], outcome="RECOVERED", actual_cost_usd=0.1,
                actual_scope_units=1, actual_mutations=1, cleanup_verified=False, evidence={},
            )

    def test_escalated_outcome_holds_larger_observed_consequence(self):
        reservation = self.reserve("escalated", "task-1", scope=1, mutations=1)
        self.ledger.settle(
            reservation["reservation_id"], outcome="ESCALATED", actual_cost_usd=0.1,
            actual_scope_units=3, actual_mutations=2, cleanup_verified=False,
            evidence={"unexpected_dependents": 2},
        )
        status = self.ledger.budget_status("shared")
        self.assertEqual(status["committed"]["scope_units"], 3.0)
        self.assertEqual(status["committed"]["mutations"], 2.0)


if __name__ == "__main__":
    unittest.main()

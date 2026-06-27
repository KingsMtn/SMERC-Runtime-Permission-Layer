import unittest

from reference_engine.audit_store import AuditStore, IdempotencyConflictError


def decision(replay_id="replay_a", posture="THROTTLE"):
    return {
        "action_id": "action-a",
        "posture": posture,
        "replay_id": replay_id,
        "scores": {"irreversible_exposure_score": 0.5},
        "replay": {"evaluated_at": "2026-06-26T12:00:00+00:00"},
    }


class AuditStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = AuditStore(":memory:")

    def tearDown(self):
        self.store.close()

    def test_records_and_reads_decision_within_tenant(self):
        self.store.record("alpha", decision(), "hash-a")
        self.assertEqual(self.store.get("alpha", "replay_a")["posture"], "THROTTLE")
        self.assertIsNone(self.store.get("beta", "replay_a"))

    def test_idempotency_lookup_returns_hash_and_decision(self):
        self.store.record("alpha", decision(), "hash-a", idempotency_key="request-a")
        stored = self.store.get_by_idempotency_key("alpha", "request-a")
        self.assertEqual(stored["request_hash"], "hash-a")
        self.assertEqual(stored["decision"]["replay_id"], "replay_a")

    def test_duplicate_idempotency_write_is_atomic(self):
        original = self.store.record("alpha", decision(), "hash-a", idempotency_key="request-a")
        replayed = self.store.record(
            "alpha",
            decision("replay_b"),
            "hash-a",
            idempotency_key="request-a",
        )
        self.assertEqual(replayed["replay_id"], original["replay_id"])

        with self.assertRaises(IdempotencyConflictError):
            self.store.record(
                "alpha",
                decision("replay_c"),
                "different-hash",
                idempotency_key="request-a",
            )

    def test_list_filters_by_posture_and_reports_count(self):
        self.store.record("alpha", decision("replay_a", "ALLOW"), "hash-a")
        self.store.record("alpha", decision("replay_b", "FREEZE"), "hash-b")
        self.assertEqual(self.store.count("alpha"), 2)
        frozen = self.store.list("alpha", posture="FREEZE")
        self.assertEqual([item["replay_id"] for item in frozen], ["replay_b"])

    def test_ping_confirms_database_readiness(self):
        self.assertTrue(self.store.ping())


if __name__ == "__main__":
    unittest.main()

import unittest

from reference_engine.audit_store import AuditStore, IdempotencyConflictError, ReviewConflictError


def decision(replay_id="replay_a", posture="THROTTLE"):
    return {
        "action_id": "action-a",
        "posture": posture,
        "replay_id": replay_id,
        "scores": {"irreversible_exposure_score": 0.5},
        "replay": {"evaluated_at": "2026-06-26T12:00:00+00:00"},
    }


def review(review_id="review_a", reviewer_id="security-1", verdict="agree", posture="THROTTLE"):
    return {
        "review_id": review_id,
        "tenant_id": "alpha",
        "replay_id": "replay_a",
        "reviewer_id": reviewer_id,
        "verdict": verdict,
        "decision_posture": posture,
        "recommended_posture": None,
        "false_release": False,
        "false_constraint": False,
        "useful_constraint": posture != "ALLOW",
        "review_latency_ms": 1200,
        "comment": None,
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

    def test_review_is_tenant_scoped_and_retry_safe(self):
        self.store.record("alpha", decision(), "hash-a")
        original = self.store.record_review(
            "alpha", "replay_a", review(), "review-hash", idempotency_key="review-request-a"
        )
        replayed = self.store.record_review(
            "alpha",
            "replay_a",
            review(review_id="review_b"),
            "review-hash",
            idempotency_key="review-request-a",
        )
        self.assertEqual(replayed["review_id"], original["review_id"])
        self.assertEqual(len(self.store.list_reviews("alpha", "replay_a")), 1)
        self.assertEqual(self.store.list_reviews("beta", "replay_a"), [])

    def test_one_immutable_review_per_reviewer_and_decision(self):
        self.store.record("alpha", decision(), "hash-a")
        self.store.record_review("alpha", "replay_a", review(), "review-hash-a")
        with self.assertRaises(ReviewConflictError):
            self.store.record_review(
                "alpha",
                "replay_a",
                review(review_id="review_b", verdict="uncertain"),
                "review-hash-b",
            )

    def test_pilot_metrics_disclose_denominators(self):
        self.store.record("alpha", decision("replay_allow", "ALLOW"), "hash-allow")
        self.store.record("alpha", decision("replay_freeze", "FREEZE"), "hash-freeze")
        allow_review = review("review_allow", "security-1", "override", "ALLOW")
        allow_review.update(
            {
                "replay_id": "replay_allow",
                "recommended_posture": "FREEZE",
                "false_release": True,
                "useful_constraint": False,
                "review_latency_ms": 1000,
            }
        )
        freeze_review = review("review_freeze", "security-2", "agree", "FREEZE")
        freeze_review.update({"replay_id": "replay_freeze", "review_latency_ms": 3000})
        self.store.record_review("alpha", "replay_allow", allow_review, "review-hash-allow")
        self.store.record_review("alpha", "replay_freeze", freeze_review, "review-hash-freeze")

        result = self.store.pilot_metrics("alpha")
        self.assertEqual(result["decision_count"], 2)
        self.assertEqual(result["denominators"]["determinate_reviews"], 2)
        self.assertEqual(result["metrics"]["reviewer_agreement_rate"], 0.5)
        self.assertEqual(result["metrics"]["override_rate"], 0.5)
        self.assertEqual(result["metrics"]["false_release_rate"], 1.0)
        self.assertEqual(result["metrics"]["useful_constraint_rate"], 1.0)
        self.assertEqual(result["metrics"]["average_review_latency_ms"], 2000.0)

    def test_review_queue_filters_pending_reviewed_and_posture(self):
        pending = decision("replay_pending", "ALLOW")
        pending["plain_english_summary"] = "Pending action"
        reviewed = decision("replay_reviewed", "FREEZE")
        reviewed["plain_english_summary"] = "Reviewed action"
        self.store.record("alpha", pending, "hash-pending")
        self.store.record("alpha", reviewed, "hash-reviewed")
        reviewed_record = review("review_queue", "security-queue", "agree", "FREEZE")
        reviewed_record.update({"replay_id": "replay_reviewed"})
        self.store.record_review(
            "alpha", "replay_reviewed", reviewed_record, "review-hash-queue"
        )

        pending_queue = self.store.review_queue("alpha", review_status="pending")
        reviewed_queue = self.store.review_queue("alpha", review_status="reviewed")
        frozen_queue = self.store.review_queue("alpha", posture="FREEZE")
        self.assertEqual([item["replay_id"] for item in pending_queue], ["replay_pending"])
        self.assertEqual([item["replay_id"] for item in reviewed_queue], ["replay_reviewed"])
        self.assertEqual(frozen_queue[0]["review_count"], 1)
        self.assertEqual(frozen_queue[0]["verdict_counts"]["agree"], 1)
        self.assertEqual(frozen_queue[0]["description"], "Reviewed action")


if __name__ == "__main__":
    unittest.main()

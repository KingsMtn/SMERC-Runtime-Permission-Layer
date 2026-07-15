import json
import threading
import unittest
from pathlib import Path

from api_server import create_server
from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger, build_example_ledger
from smerc_sdk import SMERCAPIError, SMERCClient


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "examples" / "recoverability_single_action.json").read_text(encoding="utf-8"))
LANGUAGE_EXAMPLE = json.loads(
    (ROOT / "examples" / "action_language" / "production_database_change.json").read_text(encoding="utf-8")
)


def example_ledger_for(tenant_id: str, decision_id: str):
    source = build_example_ledger().to_dict()
    ledger = DecisionLifecycleLedger(decision_id, tenant_id=tenant_id)
    for record in source["records"]:
        ledger.append(
            record["event_type"],
            record["actor"],
            record["payload"],
            recorded_at=record["recorded_at"],
        )
    return ledger


class PythonSDKTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={"alpha": "alpha-secret"},
            max_body_bytes=262144,
            max_batch_size=5,
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def client(self, *, token="alpha-secret"):
        return SMERCClient(self.base_url, token=token, timeout=5)

    def test_health_ready_and_schema_use_public_endpoints(self):
        client = SMERCClient(self.base_url, timeout=5)

        self.assertEqual(client.health()["status"], "ok")
        self.assertEqual(client.ready()["status"], "ready")
        self.assertIn("POST /v1/evaluate", client.schema()["endpoints"])

    def test_evaluate_and_replay_decision(self):
        client = self.client()

        decision = client.evaluate(EXAMPLE, idempotency_key="sdk-evaluate-1001")
        replay = client.get_decision(decision["replay_id"])
        listed = client.list_decisions(limit=5, posture=decision["posture"])

        self.assertEqual(decision["tenant_id"], "alpha")
        self.assertEqual(replay["replay_id"], decision["replay_id"])
        self.assertGreaterEqual(listed["count"], 1)
        self.assertTrue(all(item["posture"] == decision["posture"] for item in listed["decisions"]))

    def test_language_evaluate_and_idempotent_replay(self):
        client = self.client()

        first = client.evaluate_language_action(LANGUAGE_EXAMPLE, idempotency_key="sdk-language-1001")
        second = client.evaluate_language_action(LANGUAGE_EXAMPLE, idempotency_key="sdk-language-1001")

        self.assertEqual(first["language_version"], "smerc.decision.v1")
        self.assertEqual(first["replay_id"], second["replay_id"])

    def test_batch_review_queue_review_and_metrics(self):
        client = self.client()
        batch = client.batch([EXAMPLE], idempotency_key="sdk-batch-1001")
        decision = batch["decisions"][0]
        queue = client.review_queue(limit=10, status="pending")

        self.assertGreaterEqual(queue["count"], 1)
        review = client.review_decision(
            decision["replay_id"],
            {
                "reviewer_id": "security-reviewer-sdk",
                "verdict": "agree",
                "review_latency_ms": 1200,
                "useful_constraint": decision["posture"] != "ALLOW",
            },
            idempotency_key="sdk-review-1001",
        )
        reviews = client.list_reviews(decision["replay_id"])
        metrics = client.pilot_metrics()

        self.assertEqual(review["replay_id"], decision["replay_id"])
        self.assertEqual(reviews["count"], 1)
        self.assertGreaterEqual(metrics["reviewed_decision_count"], 1)

    def test_security_events_are_available_to_authenticated_client(self):
        client = self.client()
        events = client.security_events(limit=5)

        self.assertEqual(events["tenant_id"], "alpha")
        self.assertIn("events", events)

    def test_pilot_evidence_package_flow(self):
        client = self.client()
        ledger = example_ledger_for("alpha", "sdk-dll-001").to_dict()

        stored = client.store_pilot_dll_ledger(ledger)
        decision_id = stored["stored_ledger"]["decision_id"]
        listed = client.list_pilot_dll_ledgers(limit=5)
        fetched = client.get_pilot_dll_ledger(decision_id)
        certificate = client.issue_stored_pilot_dll_certificate(decision_id, issuer="python-sdk-test")
        package = client.pilot_evidence_package(
            decision_id,
            issuer="python-sdk-test",
            security_event_limit=20,
        )

        self.assertEqual(decision_id, "sdk-dll-001")
        self.assertIn(decision_id, {item["decision_id"] for item in listed["ledgers"]})
        self.assertEqual(fetched["ledger"]["decision_id"], decision_id)
        self.assertTrue(certificate["certificate"]["verification"]["valid"])
        self.assertEqual(package["package"]["version"], "smerc.pilot-evidence-package.v1")
        self.assertTrue(package["package"]["certificate_verification"]["valid"])
        self.assertIn("SMERC Pilot Evidence Package", package["package"]["markdown_report"])

    def test_unauthenticated_evaluate_raises_structured_api_error(self):
        client = SMERCClient(self.base_url, timeout=5)

        with self.assertRaises(SMERCAPIError) as ctx:
            client.evaluate(EXAMPLE)

        self.assertEqual(ctx.exception.status, 401)
        self.assertEqual(ctx.exception.code, "authentication_required")

    def test_invalid_replay_identifier_is_rejected_client_side(self):
        client = self.client()

        with self.assertRaises(ValueError):
            client.get_decision("../bad")

        with self.assertRaises(ValueError):
            client.get_pilot_dll_ledger("../bad")


if __name__ == "__main__":
    unittest.main()

import json
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from api_server import create_server, parse_api_keys
from reference_engine.policy import PolicyRegistry, RuntimePolicy


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = json.loads((ROOT / "examples" / "recoverability_action_requests.json").read_text(encoding="utf-8"))
LANGUAGE_EXAMPLE = json.loads(
    (ROOT / "examples" / "action_language" / "production_database_change.json").read_text(encoding="utf-8")
)
POLICY_EXAMPLE = json.loads(
    (ROOT / "examples" / "policies" / "alpha_conservative.json").read_text(encoding="utf-8")
)


class APIServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={"alpha": "alpha-secret", "beta": "beta-secret"},
            max_body_bytes=4096,
            max_batch_size=2,
            cors_origins=["https://console.example"],
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def request_json(self, path, *, method="GET", payload=None, key=None, headers=None):
        request_headers = dict(headers or {})
        if key:
            request_headers["authorization"] = f"Bearer {key}"
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            request_headers.setdefault("content-type", "application/json")
        request = Request(self.url(path), data=data, headers=request_headers, method=method)
        try:
            with urlopen(request, timeout=5) as response:
                response_headers = {name.lower(): value for name, value in response.headers.items()}
                return response.status, response_headers, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            response_headers = {name.lower(): value for name, value in exc.headers.items()}
            return exc.code, response_headers, json.loads(exc.read().decode("utf-8"))

    def test_health_and_ready_do_not_require_authentication(self):
        health = self.request_json("/health")
        ready = self.request_json("/ready")
        self.assertEqual(health[0], 200)
        self.assertEqual(health[2]["version"], "0.11")
        self.assertEqual(health[2]["tenant_policy_count"], 0)
        self.assertEqual(health[2]["permit_signer_count"], 0)
        self.assertEqual(health[2]["api_principal_count"], 2)
        self.assertEqual(health[2]["control_evidence_adapter_count"], 0)
        self.assertFalse(health[2]["short_lived_access_enabled"])
        self.assertEqual(ready[2]["status"], "ready")

    def test_schema_lists_versioned_endpoints_and_postures(self):
        status, _, body = self.request_json("/schema")
        self.assertEqual(status, 200)
        self.assertIn("reversibility", body["required_fields"])
        self.assertIn("ESCALATE", body["postures"])
        self.assertIn("POST /v1/evaluate", body["endpoints"])
        self.assertIn("POST /v1/language/evaluate", body["endpoints"])
        self.assertEqual(body["language_versions"]["action"], "smerc.action.v1")
        self.assertEqual(body["language_versions"]["permit"], "smerc.permit.v1")
        self.assertEqual(
            body["language_versions"]["control_evidence"],
            "smerc.control-evidence.v1",
        )
        self.assertEqual(body["language_versions"]["access_token"], "smerc.access-token.v1")
        self.assertEqual(body["policy_version"], "smerc.policy.v1")
        self.assertIn("POST /v1/decisions/{replay_id}/reviews", body["endpoints"])
        self.assertIn("GET /v1/pilot/metrics", body["endpoints"])
        self.assertIn("GET /v1/review-queue", body["endpoints"])
        self.assertIn("POST /v1/permits/issue", body["endpoints"])
        self.assertIn("POST /v1/permits/consume", body["endpoints"])
        self.assertIn("POST /v1/auth/token", body["endpoints"])
        self.assertIn("GET /v1/security-events", body["endpoints"])
        self.assertIn("permits.consume", body["authorization"]["scopes"])
        self.assertEqual(body["principal_version"], "smerc.principal.v1")
        self.assertEqual(body["security_event_version"], "smerc.security-event.v1")

    def test_evaluate_requires_bearer_authentication(self):
        status, headers, body = self.request_json("/v1/evaluate", method="POST", payload=EXAMPLES[0])
        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "authentication_required")
        self.assertIn("x-request-id", headers)

    def test_invalid_api_key_is_rejected(self):
        status, _, body = self.request_json(
            "/v1/evaluate", method="POST", payload=EXAMPLES[0], key="wrong-secret"
        )
        self.assertEqual(status, 401)
        self.assertEqual(body["error"], "invalid_api_key")

    def test_tenant_header_cannot_override_key_tenant(self):
        status, _, body = self.request_json(
            "/v1/evaluate",
            method="POST",
            payload=EXAMPLES[0],
            key="alpha-secret",
            headers={"x-smerc-tenant": "beta"},
        )
        self.assertEqual(status, 403)
        self.assertEqual(body["error"], "tenant_mismatch")

    def test_evaluate_persists_and_retrieves_a_tenant_decision(self):
        status, _, decision = self.request_json(
            "/v1/evaluate", method="POST", payload=EXAMPLES[0], key="alpha-secret"
        )
        self.assertEqual(status, 200)
        self.assertEqual(decision["tenant_id"], "alpha")
        self.assertEqual(decision["authenticated_principal"]["principal_id"], "legacy-alpha")

        status, _, retrieved = self.request_json(
            f"/v1/decisions/{decision['replay_id']}", key="alpha-secret"
        )
        self.assertEqual(status, 200)
        self.assertEqual(retrieved["replay_id"], decision["replay_id"])

        status, _, _ = self.request_json(f"/v1/decisions/{decision['replay_id']}", key="beta-secret")
        self.assertEqual(status, 404)

    def test_action_language_endpoint_is_authenticated_persisted_and_idempotent(self):
        headers = {"idempotency-key": "language-run-1001"}
        first = self.request_json(
            "/v1/language/evaluate", method="POST", payload=LANGUAGE_EXAMPLE,
            key="alpha-secret", headers=headers
        )
        second = self.request_json(
            "/v1/language/evaluate", method="POST", payload=LANGUAGE_EXAMPLE,
            key="alpha-secret", headers=headers
        )
        self.assertEqual(first[0], 200)
        self.assertEqual(first[2]["language_version"], "smerc.decision.v1")
        self.assertEqual(first[2]["tenant_id"], "alpha")
        self.assertEqual(first[2]["replay_id"], second[2]["replay_id"])
        self.assertEqual(second[1]["x-smerc-idempotent-replay"], "true")

    def test_action_language_endpoint_rejects_invalid_contract(self):
        payload = dict(LANGUAGE_EXAMPLE)
        payload["language_version"] = "unknown"
        status, _, body = self.request_json(
            "/v1/language/evaluate", method="POST", payload=payload, key="alpha-secret"
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "bad_request")

    def test_idempotency_replays_same_decision(self):
        headers = {"idempotency-key": "deploy-run-1001"}
        first = self.request_json(
            "/v1/evaluate", method="POST", payload=EXAMPLES[1], key="alpha-secret", headers=headers
        )
        second = self.request_json(
            "/v1/evaluate", method="POST", payload=EXAMPLES[1], key="alpha-secret", headers=headers
        )
        self.assertEqual(first[2]["replay_id"], second[2]["replay_id"])
        self.assertEqual(second[1]["x-smerc-idempotent-replay"], "true")

    def test_idempotency_key_reuse_with_different_payload_is_a_conflict(self):
        headers = {"idempotency-key": "deploy-run-1002"}
        self.request_json(
            "/v1/evaluate", method="POST", payload=EXAMPLES[0], key="alpha-secret", headers=headers
        )
        status, _, body = self.request_json(
            "/v1/evaluate", method="POST", payload=EXAMPLES[1], key="alpha-secret", headers=headers
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "idempotency_conflict")

    def test_decision_list_is_tenant_scoped_and_filterable(self):
        self.request_json("/v1/evaluate", method="POST", payload=EXAMPLES[0], key="beta-secret")
        status, _, body = self.request_json("/v1/decisions?limit=10&posture=ALLOW", key="beta-secret")
        self.assertEqual(status, 200)
        self.assertEqual(body["tenant_id"], "beta")
        self.assertGreaterEqual(body["count"], 1)
        self.assertTrue(all(item["posture"] == "ALLOW" for item in body["decisions"]))

    def test_versioned_batch_returns_envelope(self):
        status, _, body = self.request_json(
            "/v1/batch", method="POST", payload=EXAMPLES[:2], key="alpha-secret"
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["count"], 2)
        self.assertEqual(len(body["decisions"]), 2)

    def test_legacy_batch_preserves_list_response(self):
        status, _, body = self.request_json(
            "/batch", method="POST", payload=EXAMPLES[:2], key="alpha-secret"
        )
        self.assertEqual(status, 200)
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 2)

    def test_batch_limit_is_enforced(self):
        status, _, body = self.request_json(
            "/v1/batch", method="POST", payload=EXAMPLES[:3], key="alpha-secret"
        )
        self.assertEqual(status, 413)
        self.assertEqual(body["error"], "batch_too_large")

    def test_content_type_and_body_size_are_enforced(self):
        status, _, body = self.request_json(
            "/v1/evaluate",
            method="POST",
            payload=EXAMPLES[0],
            key="alpha-secret",
            headers={"content-type": "text/plain"},
        )
        self.assertEqual(status, 415)
        self.assertEqual(body["error"], "unsupported_media_type")

        oversized = dict(EXAMPLES[0])
        oversized["context"] = {"note": "x" * 5000}
        status, _, body = self.request_json(
            "/v1/evaluate", method="POST", payload=oversized, key="alpha-secret"
        )
        self.assertEqual(status, 413)
        self.assertEqual(body["error"], "body_too_large")

    def test_cors_is_allowlisted_instead_of_wildcarded(self):
        status, headers, _ = self.request_json(
            "/health", headers={"origin": "https://console.example"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(headers["access-control-allow-origin"], "https://console.example")

        status, headers, _ = self.request_json("/health", headers={"origin": "https://untrusted.example"})
        self.assertEqual(status, 200)
        self.assertNotIn("access-control-allow-origin", headers)

    def test_parse_api_keys_validates_tenant_mapping(self):
        alpha = "alpha-secret-012345678901"
        beta = "beta-secret-0123456789012"
        self.assertEqual(parse_api_keys(f"alpha={alpha},beta={beta}"), {"alpha": alpha, "beta": beta})
        with self.assertRaises(ValueError):
            parse_api_keys("missing-separator")
        with self.assertRaises(ValueError):
            parse_api_keys("alpha=short")
        with self.assertRaises(ValueError):
            parse_api_keys(f"alpha={alpha},alpha={beta}")
        with self.assertRaises(ValueError):
            parse_api_keys(f"alpha={alpha},beta={alpha}")


class LocalDevelopmentModeTests(unittest.TestCase):
    def test_server_requires_auth_unless_local_mode_is_explicit(self):
        with self.assertRaises(ValueError):
            create_server("127.0.0.1", 0, audit_db=":memory:", api_keys={})

    def test_server_resolves_tenant_specific_policy_without_cross_tenant_fallback(self):
        policy = RuntimePolicy.from_dict(POLICY_EXAMPLE)
        server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={"alpha": "alpha-secret", "beta": "beta-secret"},
            policy_registry=PolicyRegistry([policy]),
        )
        try:
            alpha = server.engine_for("alpha").evaluate(EXAMPLES[0])
            beta = server.engine_for("beta").evaluate(EXAMPLES[0])
            self.assertEqual(alpha["policy"]["policy_id"], policy.policy_id)
            self.assertEqual(beta["policy"]["policy_id"], "smerc-reference-recoverability")
            self.assertNotEqual(alpha["policy"]["policy_hash"], beta["policy"]["policy_hash"])
        finally:
            server.server_close()


class PilotReviewAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={"alpha": "alpha-secret", "beta": "beta-secret"},
            max_body_bytes=4096,
            max_batch_size=2,
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def request_json(self, path, *, method="GET", payload=None, key=None, headers=None):
        request_headers = dict(headers or {})
        if key:
            request_headers["authorization"] = f"Bearer {key}"
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            request_headers.setdefault("content-type", "application/json")
        request = Request(self.url(path), data=data, headers=request_headers, method=method)
        try:
            with urlopen(request, timeout=5) as response:
                response_headers = {name.lower(): value for name, value in response.headers.items()}
                return response.status, response_headers, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            response_headers = {name.lower(): value for name, value in exc.headers.items()}
            return exc.code, response_headers, json.loads(exc.read().decode("utf-8"))

    def create_decision(self, example_index=0, tenant="alpha"):
        key = f"{tenant}-secret"
        status, _, decision = self.request_json(
            "/v1/evaluate", method="POST", payload=EXAMPLES[example_index], key=key
        )
        self.assertEqual(status, 200)
        return decision

    @staticmethod
    def review_payload(**overrides):
        payload = {
            "reviewer_id": "security-reviewer-1",
            "verdict": "agree",
            "review_latency_ms": 1800,
            "useful_constraint": True,
        }
        payload.update(overrides)
        return payload

    def test_review_lifecycle_is_tenant_scoped_and_idempotent(self):
        decision = self.create_decision(1)
        path = f"/v1/decisions/{decision['replay_id']}/reviews"
        payload = self.review_payload(
            useful_constraint=decision["posture"] != "ALLOW",
            false_release=False,
        )
        headers = {"idempotency-key": "review-run-1001"}
        first = self.request_json(path, method="POST", payload=payload, key="alpha-secret", headers=headers)
        second = self.request_json(path, method="POST", payload=payload, key="alpha-secret", headers=headers)
        self.assertEqual(first[0], 201)
        self.assertEqual(second[0], 200)
        self.assertEqual(second[1]["x-smerc-idempotent-replay"], "true")
        self.assertEqual(first[2]["review_id"], second[2]["review_id"])

        status, _, listed = self.request_json(path, key="alpha-secret")
        self.assertEqual(status, 200)
        self.assertEqual(listed["count"], 1)
        status, _, body = self.request_json(path, key="beta-secret")
        self.assertEqual(status, 404)
        self.assertEqual(body["error"], "decision_not_found")

    def test_review_validation_rejects_incoherent_labels_and_overrides(self):
        decision = self.create_decision(0)
        path = f"/v1/decisions/{decision['replay_id']}/reviews"
        status, _, body = self.request_json(
            path,
            method="POST",
            payload=self.review_payload(verdict="override", recommended_posture=decision["posture"]),
            key="alpha-secret",
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_override")

        status, _, body = self.request_json(
            path,
            method="POST",
            payload=self.review_payload(false_constraint=True, useful_constraint=True),
            key="alpha-secret",
        )
        self.assertEqual(status, 400)
        self.assertIn(body["error"], {"invalid_constraint_label", "conflicting_constraint_labels"})

    def test_metrics_report_rates_with_explicit_denominators(self):
        decision = self.create_decision(1)
        path = f"/v1/decisions/{decision['replay_id']}/reviews"
        payload = self.review_payload(useful_constraint=decision["posture"] != "ALLOW")
        status, _, _ = self.request_json(path, method="POST", payload=payload, key="alpha-secret")
        self.assertEqual(status, 201)

        status, _, metrics = self.request_json("/v1/pilot/metrics", key="alpha-secret")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(metrics["review_count"], 1)
        self.assertGreaterEqual(metrics["denominators"]["determinate_reviews"], 1)
        self.assertIn("reviewer_agreement_rate", metrics["metrics"])
        self.assertIn("average_review_latency_ms", metrics["metrics"])

        status, _, beta_metrics = self.request_json("/v1/pilot/metrics", key="beta-secret")
        self.assertEqual(status, 200)
        self.assertEqual(beta_metrics["review_count"], 0)
        self.assertIsNone(beta_metrics["metrics"]["reviewer_agreement_rate"])

    def test_review_idempotency_and_reviewer_conflicts_are_explicit(self):
        decision = self.create_decision(1)
        path = f"/v1/decisions/{decision['replay_id']}/reviews"
        payload = self.review_payload(
            reviewer_id="security-reviewer-conflict",
            useful_constraint=decision["posture"] != "ALLOW",
        )
        headers = {"idempotency-key": "review-run-conflict"}
        status, _, _ = self.request_json(
            path, method="POST", payload=payload, key="alpha-secret", headers=headers
        )
        self.assertEqual(status, 201)

        changed = dict(payload, review_latency_ms=1900)
        status, _, body = self.request_json(
            path, method="POST", payload=changed, key="alpha-secret", headers=headers
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "idempotency_conflict")

        status, _, body = self.request_json(
            path,
            method="POST",
            payload=changed,
            key="alpha-secret",
            headers={"idempotency-key": "review-run-conflict-2"},
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "review_conflict")

    def test_review_idempotency_key_is_bound_to_replay_id(self):
        first_decision = self.create_decision(1)
        second_decision = self.create_decision(1)
        payload = self.review_payload(
            reviewer_id="security-reviewer-replay-bound",
            useful_constraint=first_decision["posture"] != "ALLOW",
        )
        headers = {"idempotency-key": "review-run-replay-bound"}
        status, _, _ = self.request_json(
            f"/v1/decisions/{first_decision['replay_id']}/reviews",
            method="POST",
            payload=payload,
            key="alpha-secret",
            headers=headers,
        )
        self.assertEqual(status, 201)
        status, _, body = self.request_json(
            f"/v1/decisions/{second_decision['replay_id']}/reviews",
            method="POST",
            payload=payload,
            key="alpha-secret",
            headers=headers,
        )
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "idempotency_conflict")

    def test_review_queue_is_tenant_scoped_and_filterable(self):
        pending = self.create_decision(0)
        reviewed = self.create_decision(1)
        reviewed_path = f"/v1/decisions/{reviewed['replay_id']}/reviews"
        status, _, _ = self.request_json(
            reviewed_path,
            method="POST",
            payload=self.review_payload(
                reviewer_id="security-reviewer-queue",
                useful_constraint=reviewed["posture"] != "ALLOW",
            ),
            key="alpha-secret",
        )
        self.assertEqual(status, 201)

        status, _, pending_queue = self.request_json(
            "/v1/review-queue?status=pending&limit=200", key="alpha-secret"
        )
        self.assertEqual(status, 200)
        self.assertIn(pending["replay_id"], {item["replay_id"] for item in pending_queue["decisions"]})
        self.assertNotIn(reviewed["replay_id"], {item["replay_id"] for item in pending_queue["decisions"]})

        status, _, reviewed_queue = self.request_json(
            f"/v1/review-queue?status=reviewed&posture={reviewed['posture']}", key="alpha-secret"
        )
        self.assertEqual(status, 200)
        queue_item = next(
            item for item in reviewed_queue["decisions"] if item["replay_id"] == reviewed["replay_id"]
        )
        self.assertEqual(queue_item["review_status"], "reviewed")
        self.assertGreaterEqual(queue_item["verdict_counts"]["agree"], 1)

        status, _, beta_queue = self.request_json("/v1/review-queue", key="beta-secret")
        self.assertEqual(status, 200)
        self.assertEqual(beta_queue["count"], 0)

    def test_review_queue_rejects_invalid_status(self):
        status, _, body = self.request_json(
            "/v1/review-queue?status=unknown", key="alpha-secret"
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_review_status")


if __name__ == "__main__":
    unittest.main()

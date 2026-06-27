import json
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from api_server import create_server, parse_api_keys


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = json.loads((ROOT / "examples" / "recoverability_action_requests.json").read_text(encoding="utf-8"))


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
        self.assertEqual(health[2]["version"], "0.2")
        self.assertEqual(ready[2]["status"], "ready")

    def test_schema_lists_versioned_endpoints_and_postures(self):
        status, _, body = self.request_json("/schema")
        self.assertEqual(status, 200)
        self.assertIn("reversibility", body["required_fields"])
        self.assertIn("ESCALATE", body["postures"])
        self.assertIn("POST /v1/evaluate", body["endpoints"])

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

        status, _, retrieved = self.request_json(
            f"/v1/decisions/{decision['replay_id']}", key="alpha-secret"
        )
        self.assertEqual(status, 200)
        self.assertEqual(retrieved["replay_id"], decision["replay_id"])

        status, _, _ = self.request_json(f"/v1/decisions/{decision['replay_id']}", key="beta-secret")
        self.assertEqual(status, 404)

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


if __name__ == "__main__":
    unittest.main()

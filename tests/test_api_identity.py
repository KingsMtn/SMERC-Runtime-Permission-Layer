import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from api_server import create_server
from reference_engine.api_identity import APIPrincipal, PrincipalRegistry, parse_scoped_principals
from reference_engine.authorization_permit import PermitSigner
from reference_engine.policy import PolicyRegistry
from tests.test_authorization_permit import enforce_policy, low_risk_action


def principal(principal_id, secret, *scopes):
    return APIPrincipal(
        tenant_id="alpha",
        principal_id=principal_id,
        secret=secret,
        scopes=frozenset(scopes),
    )


PRINCIPALS = [
    principal("agent-proposer", "proposer-secret-012345678901", "actions.evaluate"),
    principal("backup-proposer", "backup-proposer-secret-012345", "actions.evaluate"),
    principal("permit-issuer", "issuer-secret-01234567890123", "permits.issue"),
    principal("deployment-executor", "executor-secret-012345678901", "permits.consume"),
    principal("security-reviewer", "reviewer-secret-012345678901", "reviews.write", "reviews.read"),
    principal(
        "security-auditor",
        "auditor-secret-0123456789012",
        "audit.read",
        "decisions.read",
        "metrics.read",
    ),
]


class APIIdentityUnitTests(unittest.TestCase):
    def test_parser_and_registry_bind_tenant_principal_and_scopes(self):
        parsed = parse_scoped_principals(
            "alpha:agent-1:actions.evaluate=agent-secret-012345678901,"
            "alpha:auditor-1:audit.read+decisions.read=auditor-secret-0123456789"
        )
        registry = PrincipalRegistry.from_configuration({}, parsed)
        authenticated = registry.authenticate("agent-secret-012345678901")
        self.assertEqual(authenticated.principal_id, "agent-1")
        self.assertEqual(authenticated.public_identity()["identity_version"], "smerc.principal.v1")
        self.assertTrue(authenticated.permits("actions.evaluate"))
        self.assertFalse(authenticated.permits("permits.issue"))
        self.assertNotIn("secret", repr(authenticated))
        self.assertNotIn(authenticated.secret, str(authenticated.public_identity()))

    def test_scoped_configuration_rejects_wildcards_unknowns_duplicates_and_reused_secrets(self):
        with self.assertRaisesRegex(ValueError, "wildcard"):
            parse_scoped_principals("alpha:agent:*=agent-secret-012345678901")
        with self.assertRaisesRegex(ValueError, "unknown"):
            parse_scoped_principals("alpha:agent:root.access=agent-secret-012345678901")
        with self.assertRaisesRegex(ValueError, "repeat"):
            parse_scoped_principals(
                "alpha:agent:actions.evaluate+actions.evaluate=agent-secret-012345678901"
            )
        with self.assertRaisesRegex(ValueError, "distinct secret"):
            PrincipalRegistry.from_configuration(
                {"alpha": "shared-secret-012345678901"},
                [principal("agent", "shared-secret-012345678901", "actions.evaluate")],
            )

    def test_legacy_keys_remain_explicit_all_scope_principals(self):
        registry = PrincipalRegistry.from_configuration({"alpha": "legacy-secret-012345678901"})
        legacy = registry.authenticate("legacy-secret-012345678901")
        self.assertTrue(legacy.legacy)
        self.assertTrue(legacy.permits("permits.issue"))
        self.assertEqual(legacy.scopes, frozenset({"*"}))


class ScopedPrincipalAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={},
            api_principals=PRINCIPALS,
            policy_registry=PolicyRegistry([enforce_policy()]),
            permit_signers={"alpha": PermitSigner("alpha-permit-2026-02", b"b" * 32)},
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path, *, secret, method="GET", payload=None, headers=None):
        request_headers = {"authorization": f"Bearer {secret}", "connection": "close", **(headers or {})}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            request_headers["content-type"] = "application/json"
        request = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            headers=request_headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_separation_of_duties_and_attributed_security_events(self):
        action = low_risk_action()
        status, decision = self.request(
            "/v1/language/evaluate",
            secret="proposer-secret-012345678901",
            method="POST",
            payload=action,
        )
        self.assertEqual(status, 200)
        self.assertEqual(decision["authenticated_principal"]["principal_id"], "agent-proposer")
        self.assertEqual(decision["replay"]["authenticated_principal"], decision["authenticated_principal"])

        status, denied = self.request(
            "/v1/decisions",
            secret="proposer-secret-012345678901",
        )
        self.assertEqual(status, 403)
        self.assertEqual(denied["error"], "insufficient_scope")

        status, denied = self.request(
            "/v1/language/evaluate",
            secret="issuer-secret-01234567890123",
            method="POST",
            payload=action,
        )
        self.assertEqual(status, 403)
        self.assertEqual(denied["error"], "insufficient_scope")

        issue_request = {
            "replay_id": decision["replay_id"],
            "action": action,
            "audience": "deployment-executor",
            "ttl_seconds": 120,
        }
        status, issued = self.request(
            "/v1/permits/issue",
            secret="issuer-secret-01234567890123",
            method="POST",
            payload=issue_request,
        )
        self.assertEqual(status, 201)

        status, denied = self.request(
            "/v1/permits/issue",
            secret="proposer-secret-012345678901",
            method="POST",
            payload=issue_request,
        )
        self.assertEqual(status, 403)
        self.assertEqual(denied["error"], "insufficient_scope")

        prepare_request = {
            "permit_token": issued["permit_token"],
            "action": action,
            "audience": "deployment-executor",
            "execution_id": "identity-test-deployment",
        }
        status, denied = self.request(
            "/v1/permits/prepare",
            secret="issuer-secret-01234567890123",
            method="POST",
            payload=prepare_request,
        )
        self.assertEqual(status, 403)
        self.assertEqual(denied["error"], "insufficient_scope")

        status, prepared = self.request(
            "/v1/permits/prepare",
            secret="executor-secret-012345678901",
            method="POST",
            payload=prepare_request,
        )
        self.assertEqual(status, 200)

        consume_request = {
            "permit_token": issued["permit_token"],
            "action": action,
            "audience": "deployment-executor",
            "preparation_id": prepared["preparation"]["preparation_id"],
            "enforced_controls": ["retain_cancel_handle"],
        }

        status, consumed = self.request(
            "/v1/permits/consume",
            secret="executor-secret-012345678901",
            method="POST",
            payload=consume_request,
        )
        self.assertEqual(status, 200)
        self.assertTrue(consumed["valid"])

        review_payload = {
            "reviewer_id": "reviewer-alias-1",
            "verdict": "agree",
            "review_latency_ms": 800,
            "useful_constraint": False,
        }
        status, review = self.request(
            f"/v1/decisions/{decision['replay_id']}/reviews",
            secret="reviewer-secret-012345678901",
            method="POST",
            payload=review_payload,
        )
        self.assertEqual(status, 201)
        self.assertEqual(review["authenticated_principal"]["principal_id"], "security-reviewer")

        status, audit = self.request(
            "/v1/security-events?limit=20",
            secret="auditor-secret-0123456789012",
        )
        self.assertEqual(status, 200)
        event_pairs = {(item["event_type"], item["principal_id"]) for item in audit["events"]}
        self.assertTrue(all(item["event_version"] == "smerc.security-event.v1" for item in audit["events"]))
        self.assertIn(("permit.issued", "permit-issuer"), event_pairs)
        self.assertIn(("permit.consumed", "deployment-executor"), event_pairs)
        self.assertIn(("review.recorded", "security-reviewer"), event_pairs)
        self.assertNotIn("permit_token", json.dumps(audit))

        status, denied = self.request(
            "/v1/security-events",
            secret="proposer-secret-012345678901",
        )
        self.assertEqual(status, 403)
        self.assertEqual(denied["error"], "insufficient_scope")

    def test_idempotency_key_cannot_cross_authenticated_principals(self):
        headers = {"idempotency-key": "principal-bound-request-1"}
        status, original = self.request(
            "/v1/language/evaluate",
            secret="proposer-secret-012345678901",
            method="POST",
            payload=low_risk_action(),
            headers=headers,
        )
        self.assertEqual(status, 200)
        self.assertEqual(original["authenticated_principal"]["principal_id"], "agent-proposer")

        status, conflict = self.request(
            "/v1/language/evaluate",
            secret="backup-proposer-secret-012345",
            method="POST",
            payload=low_risk_action(),
            headers=headers,
        )
        self.assertEqual(status, 409)
        self.assertEqual(conflict["error"], "idempotency_principal_conflict")


if __name__ == "__main__":
    unittest.main()

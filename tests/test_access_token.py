import base64
import hashlib
import hmac
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from api_server import create_server
from reference_engine.access_token import AccessTokenError, AccessTokenSigner, parse_access_token_signer
from reference_engine.api_identity import SCOPES, APIPrincipal
from reference_engine.authorization_permit import PermitSigner
from reference_engine.control_evidence import ControlEvidenceSigner
from tests.test_authorization_permit import low_risk_action


def bootstrap_principal(*scopes, legacy=False):
    return APIPrincipal(
        tenant_id="alpha",
        principal_id="agent-proposer",
        secret="bootstrap-secret-012345678901",
        scopes=frozenset(scopes or {"actions.evaluate", "decisions.read"}),
        legacy=legacy,
    )


class AccessTokenUnitTests(unittest.TestCase):
    def setUp(self):
        self.signer = AccessTokenSigner("access-key-2026-01", b"s" * 32)

    def test_token_is_short_lived_scope_narrowed_and_session_attributed(self):
        issued = self.signer.issue(
            bootstrap_principal("actions.evaluate", "decisions.read"),
            requested_scopes=["actions.evaluate"],
            ttl_seconds=60,
            now=1_000,
        )
        principal = self.signer.verify(issued["access_token"], now=1_030)
        self.assertEqual(principal.scopes, frozenset({"actions.evaluate"}))
        self.assertEqual(principal.credential_type, "short_lived_access_token")
        self.assertEqual(principal.expires_at, 1_060)
        self.assertTrue(principal.session_id.startswith("session_"))
        self.assertNotIn("secret", str(principal.public_identity()))

    def test_scope_escalation_wildcards_and_excessive_lifetime_are_rejected(self):
        principal = bootstrap_principal("actions.evaluate")
        with self.assertRaisesRegex(AccessTokenError, "exceeds"):
            self.signer.issue(principal, requested_scopes=["decisions.read"], now=1_000)
        with self.assertRaisesRegex(AccessTokenError, "wildcard"):
            self.signer.issue(principal, requested_scopes=["*"], now=1_000)
        with self.assertRaisesRegex(AccessTokenError, "unique"):
            self.signer.issue(
                principal,
                requested_scopes=["actions.evaluate", "actions.evaluate"],
                now=1_000,
            )
        with self.assertRaisesRegex(AccessTokenError, "1 through 900"):
            self.signer.issue(principal, ttl_seconds=901, now=1_000)

    def test_tampering_expiry_and_wrong_signer_fail_closed(self):
        issued = self.signer.issue(bootstrap_principal("actions.evaluate"), now=1_000, ttl_seconds=60)
        token = issued["access_token"]
        header, payload, signature = token.split(".")
        replacement = "A" if signature[0] != "A" else "B"
        corrupted = f"{header}.{payload}.{replacement}{signature[1:]}"
        with self.assertRaisesRegex(AccessTokenError, "signature"):
            self.signer.verify(corrupted, now=1_001)
        with self.assertRaisesRegex(AccessTokenError, "expired"):
            self.signer.verify(token, now=1_060)
        other = AccessTokenSigner("other-key", b"o" * 32)
        with self.assertRaisesRegex(AccessTokenError, "header"):
            other.verify(token, now=1_001)

    def test_legacy_bootstrap_token_expands_to_explicit_scopes_not_wildcard(self):
        issued = self.signer.issue(bootstrap_principal("*", legacy=True), now=1_000)
        principal = self.signer.verify(issued["access_token"], now=1_001)
        self.assertNotIn("*", principal.scopes)
        self.assertEqual(principal.scopes, SCOPES)
        self.assertTrue(principal.legacy)

    def test_unexpired_v1_session_remains_verifiable_during_v2_transition(self):
        issued = self.signer.issue(
            bootstrap_principal("actions.evaluate"), now=1_000, ttl_seconds=60
        )
        encoded_header, encoded_payload, _ = issued["access_token"].split(".")
        payload = json.loads(
            base64.urlsafe_b64decode(encoded_payload + "=" * (-len(encoded_payload) % 4))
        )
        payload["version"] = "smerc.access-token.v1"
        payload.pop("workload_context")
        encoded_payload = base64.urlsafe_b64encode(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).rstrip(b"=").decode("ascii")
        message = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = base64.urlsafe_b64encode(
            hmac.new(self.signer.secret, message, hashlib.sha256).digest()
        ).rstrip(b"=").decode("ascii")
        principal = self.signer.verify(
            f"{encoded_header}.{encoded_payload}.{signature}", now=1_001
        )
        self.assertEqual(principal.scopes, frozenset({"actions.evaluate"}))
        self.assertIsNone(principal.workload_context)

    def test_parser_requires_one_long_signing_secret(self):
        parsed = parse_access_token_signer(
            "access-key-2026-01:access-token-secret-0123456789012345"
        )
        self.assertEqual(parsed.key_id, "access-key-2026-01")
        self.assertIsNone(parse_access_token_signer(""))
        with self.assertRaisesRegex(ValueError, "at least 32"):
            parse_access_token_signer("key:short")

    def test_principal_session_metadata_and_signing_key_separation_are_strict(self):
        with self.assertRaisesRegex(ValueError, "cannot carry"):
            APIPrincipal(
                tenant_id="alpha",
                principal_id="bad-session",
                secret="bad-session-secret",
                scopes=frozenset({"actions.evaluate"}),
                session_id="session_0123456789abcdef0123456789abcdef",
            )
        shared = "shared-secret-01234567890123456789"
        with self.assertRaisesRegex(ValueError, "distinct"):
            create_server(
                "127.0.0.1",
                0,
                audit_db=":memory:",
                api_keys={},
                api_principals=[
                    APIPrincipal(
                        tenant_id="alpha",
                        principal_id="shared-key-principal",
                        secret=shared,
                        scopes=frozenset({"actions.evaluate"}),
                    )
                ],
                access_token_signer=AccessTokenSigner("access-key", shared.encode("utf-8")),
            )

    def test_access_token_key_cannot_be_reused_for_other_signatures(self):
        shared = b"shared-signing-secret-012345678901"
        principal = bootstrap_principal()
        access_signer = AccessTokenSigner("access-key", shared)
        with self.assertRaisesRegex(ValueError, "permit signing keys"):
            create_server(
                "127.0.0.1",
                0,
                audit_db=":memory:",
                api_keys={},
                api_principals=[principal],
                permit_signers={"alpha": PermitSigner("permit-key", shared)},
                access_token_signer=access_signer,
            )
        with self.assertRaisesRegex(ValueError, "control-evidence signing keys"):
            create_server(
                "127.0.0.1",
                0,
                audit_db=":memory:",
                api_keys={},
                api_principals=[principal],
                permit_signers={"alpha": PermitSigner("permit-key", b"p" * 32)},
                control_evidence_signers={
                    ("alpha", "github-actions-prod"): ControlEvidenceSigner(
                        tenant_id="alpha",
                        audience="github-actions-prod",
                        adapter_id="github-actions-adapter",
                        key_id="evidence-key",
                        secret=shared,
                    )
                },
                access_token_signer=access_signer,
            )


class AccessTokenAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.signer = AccessTokenSigner("access-key-2026-01", b"s" * 32)
        cls.server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={},
            api_principals=[bootstrap_principal("actions.evaluate", "decisions.read")],
            access_token_signer=cls.signer,
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path, *, credential, method="GET", payload=None):
        headers = {"authorization": f"Bearer {credential}"}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["content-type"] = "application/json"
        request = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_static_exchange_token_use_scope_enforcement_and_audit(self):
        status, issued = self.request(
            "/v1/auth/token",
            credential="bootstrap-secret-012345678901",
            method="POST",
            payload={"scopes": ["actions.evaluate"], "ttl_seconds": 60},
        )
        self.assertEqual(status, 201)
        token = issued["access_token"]
        self.assertEqual(issued["token_type"], "Bearer")
        self.assertEqual(issued["expires_in"], 60)

        status, decision = self.request(
            "/v1/language/evaluate",
            credential=token,
            method="POST",
            payload=low_risk_action(),
        )
        self.assertEqual(status, 200)
        identity = decision["authenticated_principal"]
        self.assertEqual(identity["credential_type"], "short_lived_access_token")
        self.assertEqual(identity["session_id"], issued["session"]["session_id"])
        self.assertEqual(identity["scopes"], ["actions.evaluate"])

        status, denied = self.request("/v1/decisions", credential=token)
        self.assertEqual(status, 403)
        self.assertEqual(denied["error"], "insufficient_scope")

        status, denied = self.request(
            "/v1/auth/token",
            credential=token,
            method="POST",
            payload={},
        )
        self.assertEqual(status, 401)
        self.assertEqual(denied["error"], "invalid_bootstrap_credential")

        events = self.server.audit_store.list_security_events("alpha")
        issuance = next(event for event in events if event["event_type"] == "access_token.issued")
        self.assertEqual(issuance["resource_id"], issued["session"]["session_id"])
        self.assertEqual(issuance["metadata"]["scopes"], ["actions.evaluate"])
        self.assertNotIn(token, json.dumps(events))

    def test_exchange_cannot_expand_bootstrap_scope(self):
        status, denied = self.request(
            "/v1/auth/token",
            credential="bootstrap-secret-012345678901",
            method="POST",
            payload={"scopes": ["permits.issue"]},
        )
        self.assertEqual(status, 400)
        self.assertEqual(denied["error"], "access_token_scope_escalation")


if __name__ == "__main__":
    unittest.main()

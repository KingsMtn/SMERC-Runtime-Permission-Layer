import base64
import hashlib
import json
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from api_server import create_server
from reference_engine.access_token import AccessTokenSigner
from reference_engine.github_oidc import (
    GITHUB_OIDC_AUDIENCE,
    GITHUB_OIDC_ISSUER,
    GitHubOIDCError,
    GitHubOIDCTrustPolicy,
    GitHubOIDCVerifier,
    SHA256_DIGEST_INFO_PREFIX,
    parse_github_oidc_trust,
)
from tests.test_authorization_permit import low_risk_action


RSA_N = "y5YBOoe37zaJhgyHOjlJPCJpwD9SMFsU7Jykq0KiFdZzU402JTDxjwCnJhovybMYFi_v_oh1qqdD7EXVgPslBSui3OFzbQLd0E003AosHK4Q1zai03SlXnAPAqy5xMaEgAleH_9xg0hBjbV2uM8gpMhzx_yEQ4-ruZ9Z3VuTiQEDlu_BQwZ2kttyRwAvUxiWa--UDXCxoU1m2GJePQf_g9dH46KARJobF_WDLQAGSE5nsE-jI-SNqbfc9J07PjzJpjdtpZ9PgHQhqXe7maCfo4nQ_4WagQm4eGC1SSqdXAOKquLOaCLf4Az2uVMJ-oXLt-MgA99goRRAK3VSPJ6IdQ"
RSA_E = "AQAB"
# Test-only key material with no authority outside this unit-test fixture.
RSA_D = "pXLGlNZu-IyNvs63pu2fQquE3aOYG4wpuRCkEjoYlz6sgp4j_p2D8f9J14E4jOZrELzsgSJM3d8JKB6ooCV5tHX96RufPlwx_3J_HsN1jek37m6MbORC8DiJOlc8sVnTnGoAgGiLy3ERNSTf0tkhYkk1LrVcl7tOh4-k7Gvbvl4Nebf-77bOfOBS0UbV58H50MZwGccZdkJM6RlGCYAASHRakEMIiWOxwSO5ZFL4IYYrIFjWtWgm9z7pzuoE5OGmQjzsoqkpl45FGQo2BwTQSFsExn9j6ZP0GbNCQiY6IPno2pv2aRa9gOp_M3tJBp-Q7piNTvZKdp6Vxz0VEo8DkQ"
KID = "github-test-key"
REPOSITORY = "KingsMtn/SMERC-Runtime-Permission-Layer"
WORKFLOW_REF = f"{REPOSITORY}/.github/workflows/deploy.yml@refs/heads/main"
SUBJECT = f"repo:{REPOSITORY}:environment:production"


def b64(value):
    if isinstance(value, dict):
        value = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def b64_int(value):
    return int.from_bytes(base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)), "big")


def claims(now=1_000, **updates):
    value = {
        "iss": GITHUB_OIDC_ISSUER,
        "aud": GITHUB_OIDC_AUDIENCE,
        "sub": SUBJECT,
        "jti": "github-token-1001",
        "iat": now,
        "nbf": now,
        "exp": now + 600,
        "repository": REPOSITORY,
        "repository_id": "99887766",
        "repository_owner_id": "293280548",
        "workflow_ref": WORKFLOW_REF,
        "workflow_sha": "a" * 40,
        "ref": "refs/heads/main",
        "sha": "b" * 40,
        "run_id": "5001",
        "run_attempt": "1",
        "actor_id": "293280548",
        "event_name": "workflow_dispatch",
        "runner_environment": "github-hosted",
        "environment": "production",
    }
    value.update(updates)
    return value


def sign_token(payload, *, kid=KID):
    header = {"alg": "RS256", "kid": kid, "typ": "JWT"}
    encoded_header = b64(header)
    encoded_payload = b64(payload)
    message = f"{encoded_header}.{encoded_payload}".encode("ascii")
    modulus = b64_int(RSA_N)
    private_exponent = b64_int(RSA_D)
    size = (modulus.bit_length() + 7) // 8
    digest_info = SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(message).digest()
    encoded = b"\x00\x01" + b"\xff" * (size - len(digest_info) - 3) + b"\x00" + digest_info
    signature = pow(int.from_bytes(encoded, "big"), private_exponent, modulus).to_bytes(size, "big")
    return f"{encoded_header}.{encoded_payload}.{b64(signature)}"


def policy():
    return GitHubOIDCTrustPolicy(
        tenant_id="platform-team",
        repository=REPOSITORY,
        repository_id="99887766",
        repository_owner_id="293280548",
        subjects=(SUBJECT,),
        refs=("refs/heads/main",),
        workflow_refs=(WORKFLOW_REF,),
        workflow_shas=("a" * 40,),
        events=("workflow_dispatch",),
        environments=("production",),
        scopes=frozenset({"actions.evaluate"}),
        runner_environments=("github-hosted",),
    )


def verifier():
    return GitHubOIDCVerifier(
        [policy()],
        jwks_fetcher=lambda: {
            "keys": [{"kty": "RSA", "kid": KID, "alg": "RS256", "use": "sig", "n": RSA_N, "e": RSA_E}]
        },
    )


class GitHubOIDCUnitTests(unittest.TestCase):
    def test_verified_token_becomes_scoped_attributed_workload(self):
        verified = verifier().verify(sign_token(claims()), now=1_001)
        self.assertEqual(verified.principal.tenant_id, "platform-team")
        self.assertEqual(verified.principal.principal_id, "github-repo-99887766")
        self.assertEqual(verified.principal.scopes, frozenset({"actions.evaluate"}))
        context = verified.principal.workload_context
        self.assertEqual(context["repository_id"], "99887766")
        self.assertEqual(context["workflow_ref"], WORKFLOW_REF)
        self.assertEqual(context["commit_sha"], "b" * 40)
        self.assertEqual(context["run_id"], "5001")

    def test_signature_audience_activation_and_expiry_fail_closed(self):
        token = sign_token(claims())
        header, payload, signature = token.split(".")
        replacement = "A" if signature[0] != "A" else "B"
        with self.assertRaisesRegex(GitHubOIDCError, "signature"):
            verifier().verify(f"{header}.{payload}.{replacement}{signature[1:]}", now=1_001)
        with self.assertRaisesRegex(GitHubOIDCError, "issuer or audience"):
            verifier().verify(sign_token(claims(aud="wrong-audience")), now=1_001)
        with self.assertRaisesRegex(GitHubOIDCError, "not active"):
            verifier().verify(sign_token(claims(now=1_100)), now=1_000)
        with self.assertRaisesRegex(GitHubOIDCError, "expired"):
            verifier().verify(token, now=1_700)

    def test_repository_ref_workflow_event_environment_and_subject_are_exact(self):
        mutations = {
            "repository": "attacker/repository",
            "repository_id": "1",
            "repository_owner_id": "2",
            "sub": "repo:attacker/repository:ref:refs/heads/main",
            "ref": "refs/heads/untrusted",
            "workflow_ref": f"{REPOSITORY}/.github/workflows/other.yml@refs/heads/main",
            "workflow_sha": "c" * 40,
            "event_name": "pull_request_target",
            "environment": "development",
            "runner_environment": "self-hosted",
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                with self.assertRaisesRegex(GitHubOIDCError, "exactly one"):
                    verifier().verify(sign_token(claims(**{field: value})), now=1_001)

    def test_unknown_key_and_malformed_configuration_are_rejected(self):
        with self.assertRaisesRegex(GitHubOIDCError, "not found"):
            verifier().verify(sign_token(claims(), kid="unknown"), now=1_001)
        encoded = json.dumps(
            [
                {
                    "tenant_id": "platform-team",
                    "repository": REPOSITORY,
                    "repository_id": "99887766",
                    "repository_owner_id": "293280548",
                    "subjects": [SUBJECT],
                    "refs": ["refs/heads/main"],
                    "workflow_refs": [WORKFLOW_REF],
                    "workflow_shas": ["a" * 40],
                    "events": ["workflow_dispatch"],
                    "environments": ["production"],
                    "scopes": ["actions.evaluate"],
                    "runner_environments": ["github-hosted"],
                }
            ]
        )
        self.assertEqual(parse_github_oidc_trust(encoded)[0], policy())
        with self.assertRaisesRegex(ValueError, "wildcard|explicit"):
            parse_github_oidc_trust(encoded.replace('"actions.evaluate"', '"*"'))


class GitHubOIDCAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={},
            access_token_signer=AccessTokenSigner("access-key", b"s" * 32),
            github_oidc_verifier=verifier(),
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path, credential, payload):
        request = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"authorization": f"Bearer {credential}", "content-type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_exchange_evaluate_attribution_replay_and_scope_controls(self):
        now = int(time.time())
        oidc_token = sign_token(claims(now=now, jti="api-token-one"))
        status, issued = self.request(
            "/v1/auth/github", oidc_token, {"scopes": ["actions.evaluate"], "ttl_seconds": 60}
        )
        self.assertEqual(status, 201)
        self.assertEqual(issued["session"]["version"], "smerc.access-token.v2")
        self.assertEqual(issued["session"]["workload_context"]["run_id"], "5001")

        status, decision = self.request("/v1/language/evaluate", issued["access_token"], low_risk_action())
        self.assertEqual(status, 200)
        identity = decision["authenticated_principal"]
        self.assertEqual(identity["credential_type"], "short_lived_access_token")
        self.assertEqual(identity["workload_context"]["repository_id"], "99887766")
        self.assertEqual(identity["workload_context"]["commit_sha"], "b" * 40)

        status, replay = self.request("/v1/auth/github", oidc_token, {})
        self.assertEqual(status, 409)
        self.assertEqual(replay["error"], "github_oidc_replay")
        events = self.server.audit_store.list_security_events("platform-team")
        exchange = next(item for item in events if item["event_type"] == "github_oidc.exchanged")
        self.assertEqual(exchange["metadata"]["run_id"], "5001")
        self.assertNotIn(oidc_token, json.dumps(events))

        short_identity = sign_token(claims(now=now, jti="api-token-short", exp=now + 45))
        status, capped = self.request(
            "/v1/auth/github", short_identity, {"ttl_seconds": 900}
        )
        self.assertEqual(status, 201)
        self.assertLessEqual(capped["expires_at"], now + 45)

        second = sign_token(claims(now=now, jti="api-token-two"))
        status, denied = self.request(
            "/v1/auth/github", second, {"scopes": ["decisions.read"]}
        )
        self.assertEqual(status, 400)
        self.assertEqual(denied["error"], "access_token_scope_escalation")


if __name__ == "__main__":
    unittest.main()

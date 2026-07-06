from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Optional
from urllib.request import Request, urlopen

from reference_engine.api_identity import APIPrincipal, SCOPES


GITHUB_OIDC_VERSION = "smerc.github-oidc.v1"
GITHUB_OIDC_ISSUER = "https://token.actions.githubusercontent.com"
GITHUB_OIDC_JWKS_URL = f"{GITHUB_OIDC_ISSUER}/.well-known/jwks"
GITHUB_OIDC_AUDIENCE = "smerc-runtime-api"
MAX_GITHUB_TOKEN_SECONDS = 900
MAX_GITHUB_TOKEN_BYTES = 16_384
JWKS_CACHE_SECONDS = 300
MIN_JWKS_REFRESH_SECONDS = 30
SHA256_DIGEST_INFO_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


class GitHubOIDCError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _safe_identifier(value: Any, path: str, maximum: int = 64) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        rf"[A-Za-z0-9][A-Za-z0-9._-]{{0,{maximum - 1}}}", value
    ):
        raise ValueError(f"{path} must be a safe identifier of 1 to {maximum} characters.")
    return value


def _bounded_string(value: Any, path: str, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum or any(
        ord(character) < 32 for character in value
    ):
        raise GitHubOIDCError("invalid_github_oidc_claims", f"{path} must be a bounded string.")
    return value


def _claim_string(claims: Mapping[str, Any], name: str, maximum: int = 512) -> str:
    value = claims.get(name)
    if isinstance(value, int) and not isinstance(value, bool):
        value = str(value)
    return _bounded_string(value, name, maximum)


def _timestamp(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise GitHubOIDCError("invalid_github_oidc_claims", f"{path} must be a non-negative integer.")
    return value


def _git_object_id(value: Any, path: str) -> str:
    value = _bounded_string(value, path, 64)
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
        raise GitHubOIDCError("invalid_github_oidc_claims", f"{path} must be a Git object ID.")
    return value


def _decode_base64url(value: str, path: str) -> bytes:
    if not isinstance(value, str) or not value or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise GitHubOIDCError("invalid_github_oidc", f"{path} is not valid base64url.")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (TypeError, ValueError) as exc:
        raise GitHubOIDCError("invalid_github_oidc", f"{path} is not valid base64url.") from exc


def _decode_json(value: str, path: str) -> Mapping[str, Any]:
    try:
        decoded = json.loads(_decode_base64url(value, path).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GitHubOIDCError("invalid_github_oidc", f"{path} must contain a JSON object.") from exc
    if not isinstance(decoded, dict):
        raise GitHubOIDCError("invalid_github_oidc", f"{path} must contain a JSON object.")
    return decoded


def _string_tuple(value: Any, path: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(f"{path} must be {'an' if allow_empty else 'a non-empty'} array of strings.")
    if any(not isinstance(item, str) or not item or len(item) > 512 for item in value):
        raise ValueError(f"{path} entries must be bounded non-empty strings.")
    if len(value) != len(set(value)):
        raise ValueError(f"{path} cannot contain duplicates.")
    return tuple(sorted(value))


@dataclass(frozen=True)
class GitHubOIDCTrustPolicy:
    tenant_id: str
    repository: str
    repository_id: str
    repository_owner_id: str
    subjects: tuple[str, ...]
    refs: tuple[str, ...]
    workflow_refs: tuple[str, ...]
    workflow_shas: tuple[str, ...]
    events: tuple[str, ...]
    environments: tuple[str, ...]
    scopes: frozenset[str]
    runner_environments: tuple[str, ...] = ("github-hosted", "self-hosted")

    def __post_init__(self) -> None:
        _safe_identifier(self.tenant_id, "tenant_id")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.repository):
            raise ValueError("repository must use owner/name format.")
        if not self.repository_id.isdigit() or not self.repository_owner_id.isdigit():
            raise ValueError("repository_id and repository_owner_id must be decimal GitHub IDs.")
        for path, values in (
            ("subjects", self.subjects),
            ("refs", self.refs),
            ("workflow_refs", self.workflow_refs),
            ("workflow_shas", self.workflow_shas),
            ("events", self.events),
            ("runner_environments", self.runner_environments),
        ):
            if not values or len(values) != len(set(values)):
                raise ValueError(f"{path} must contain unique allowed values.")
        if set(self.runner_environments) - {"github-hosted", "self-hosted"}:
            raise ValueError("runner_environments contains an unsupported value.")
        if any(not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value) for value in self.workflow_shas):
            raise ValueError("workflow_shas entries must be Git object IDs.")
        if not self.scopes or set(self.scopes) - SCOPES or "*" in self.scopes:
            raise ValueError("GitHub OIDC policies require explicit recognized scopes.")

    def matches(self, claims: Mapping[str, Any]) -> bool:
        environment = claims.get("environment")
        return all(
            (
                _claim_string(claims, "repository") == self.repository,
                _claim_string(claims, "repository_id") == self.repository_id,
                _claim_string(claims, "repository_owner_id") == self.repository_owner_id,
                _claim_string(claims, "sub") in self.subjects,
                _claim_string(claims, "ref") in self.refs,
                _claim_string(claims, "workflow_ref") in self.workflow_refs,
                _claim_string(claims, "workflow_sha") in self.workflow_shas,
                _claim_string(claims, "event_name") in self.events,
                _claim_string(claims, "runner_environment") in self.runner_environments,
                (
                    environment in self.environments
                    if self.environments
                    else environment is None
                ),
            )
        )


def parse_github_oidc_trust(value: str) -> tuple[GitHubOIDCTrustPolicy, ...]:
    if not value.strip():
        return ()
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError("SMERC_GITHUB_OIDC_TRUST must be a JSON array.") from exc
    if not isinstance(decoded, list) or not decoded:
        raise ValueError("SMERC_GITHUB_OIDC_TRUST must be a non-empty JSON array.")
    policies = []
    expected = {
        "tenant_id", "repository", "repository_id", "repository_owner_id",
        "subjects", "refs", "workflow_refs", "workflow_shas", "events", "environments",
        "scopes", "runner_environments",
    }
    required = expected - {"runner_environments"}
    for index, item in enumerate(decoded):
        if not isinstance(item, dict) or set(item) - expected or required - set(item):
            raise ValueError(f"SMERC_GITHUB_OIDC_TRUST[{index}] fields are incomplete or unknown.")
        scopes = _string_tuple(item["scopes"], f"policy[{index}].scopes")
        policies.append(
            GitHubOIDCTrustPolicy(
                tenant_id=item["tenant_id"],
                repository=item["repository"],
                repository_id=str(item["repository_id"]),
                repository_owner_id=str(item["repository_owner_id"]),
                subjects=_string_tuple(item["subjects"], f"policy[{index}].subjects"),
                refs=_string_tuple(item["refs"], f"policy[{index}].refs"),
                workflow_refs=_string_tuple(item["workflow_refs"], f"policy[{index}].workflow_refs"),
                workflow_shas=_string_tuple(item["workflow_shas"], f"policy[{index}].workflow_shas"),
                events=_string_tuple(item["events"], f"policy[{index}].events"),
                environments=_string_tuple(
                    item["environments"], f"policy[{index}].environments", allow_empty=True
                ),
                scopes=frozenset(scopes),
                runner_environments=_string_tuple(
                    item.get("runner_environments", ["github-hosted", "self-hosted"]),
                    f"policy[{index}].runner_environments",
                ),
            )
        )
    return tuple(policies)


@dataclass(frozen=True)
class VerifiedGitHubWorkload:
    principal: APIPrincipal
    token_id: str
    token_hash: str
    issued_at: int
    expires_at: int


class GitHubOIDCVerifier:
    def __init__(
        self,
        policies: Iterable[GitHubOIDCTrustPolicy],
        *,
        audience: str = GITHUB_OIDC_AUDIENCE,
        jwks_fetcher: Optional[Callable[[], Mapping[str, Any]]] = None,
        clock_skew_seconds: int = 30,
    ) -> None:
        self.policies = tuple(policies)
        if not self.policies:
            raise ValueError("GitHub OIDC verifier requires at least one trust policy.")
        self.audience = _safe_identifier(audience, "GitHub OIDC audience", 128)
        if not 0 <= clock_skew_seconds <= 60:
            raise ValueError("GitHub OIDC clock skew must be from 0 through 60 seconds.")
        self.clock_skew_seconds = clock_skew_seconds
        self._jwks_fetcher = jwks_fetcher or self._fetch_github_jwks
        self._jwks: Optional[Mapping[str, Any]] = None
        self._jwks_loaded_at = 0.0
        self._lock = threading.RLock()

    @property
    def tenant_ids(self) -> frozenset[str]:
        return frozenset(policy.tenant_id for policy in self.policies)

    def verify(self, token: str, *, now: Optional[int] = None) -> VerifiedGitHubWorkload:
        if not isinstance(token, str) or not token or len(token) > MAX_GITHUB_TOKEN_BYTES:
            raise GitHubOIDCError("invalid_github_oidc", "GitHub OIDC token is missing or too large.")
        parts = token.split(".")
        if len(parts) != 3:
            raise GitHubOIDCError("invalid_github_oidc", "GitHub OIDC token must contain three segments.")
        encoded_header, encoded_claims, encoded_signature = parts
        header = _decode_json(encoded_header, "GitHub OIDC header")
        claims = _decode_json(encoded_claims, "GitHub OIDC claims")
        if set(header) - {"alg", "kid", "typ", "x5t"}:
            raise GitHubOIDCError("invalid_github_oidc_header", "GitHub OIDC header contains unsupported fields.")
        if header.get("alg") != "RS256" or header.get("typ") != "JWT":
            raise GitHubOIDCError("invalid_github_oidc_header", "GitHub OIDC token must use RS256 JWT.")
        kid = _bounded_string(header.get("kid"), "kid", 256)
        signature = _decode_base64url(encoded_signature, "GitHub OIDC signature")
        jwk = self._key_for(kid)
        self._verify_rs256(
            f"{encoded_header}.{encoded_claims}".encode("ascii"), signature, jwk
        )
        when = int(time.time()) if now is None else now
        _timestamp(when, "verification time")
        self._validate_standard_claims(claims, when)
        matches = [policy for policy in self.policies if policy.matches(claims)]
        if len(matches) != 1:
            raise GitHubOIDCError(
                "github_oidc_trust_denied",
                "GitHub workload did not match exactly one configured trust policy.",
            )
        policy = matches[0]
        context = self._workload_context(claims)
        principal = APIPrincipal(
            tenant_id=policy.tenant_id,
            principal_id=f"github-repo-{policy.repository_id}",
            secret="verified-github-oidc-workload",
            scopes=policy.scopes,
            credential_type="static_bearer",
            workload_context=context,
        )
        return VerifiedGitHubWorkload(
            principal=principal,
            token_id=context["token_id"],
            token_hash=hashlib.sha256(token.encode("ascii")).hexdigest(),
            issued_at=_timestamp(claims["iat"], "iat"),
            expires_at=_timestamp(claims["exp"], "exp"),
        )

    def _validate_standard_claims(self, claims: Mapping[str, Any], now: int) -> None:
        if claims.get("iss") != GITHUB_OIDC_ISSUER or claims.get("aud") != self.audience:
            raise GitHubOIDCError("invalid_github_oidc_claims", "GitHub issuer or audience is invalid.")
        issued_at = _timestamp(claims.get("iat"), "iat")
        not_before = _timestamp(claims.get("nbf"), "nbf")
        expires_at = _timestamp(claims.get("exp"), "exp")
        if not 1 <= expires_at - issued_at <= MAX_GITHUB_TOKEN_SECONDS:
            raise GitHubOIDCError("invalid_github_oidc_claims", "GitHub token lifetime is invalid.")
        if issued_at > now + self.clock_skew_seconds or not_before > now + self.clock_skew_seconds:
            raise GitHubOIDCError("github_oidc_not_active", "GitHub OIDC token is not active yet.")
        if expires_at <= now - self.clock_skew_seconds:
            raise GitHubOIDCError("github_oidc_expired", "GitHub OIDC token has expired.")
        for claim in (
            "jti", "sub", "repository", "repository_id", "repository_owner_id",
            "workflow_ref", "workflow_sha", "ref", "sha", "run_id", "run_attempt",
            "actor_id", "event_name", "runner_environment",
        ):
            _claim_string(claims, claim)
        _git_object_id(claims["workflow_sha"], "workflow_sha")
        _git_object_id(claims["sha"], "sha")

    @staticmethod
    def _workload_context(claims: Mapping[str, Any]) -> dict[str, str]:
        context = {
            "provider": "github_actions_oidc",
            "subject": _claim_string(claims, "sub"),
            "repository": _claim_string(claims, "repository"),
            "repository_id": _claim_string(claims, "repository_id"),
            "repository_owner_id": _claim_string(claims, "repository_owner_id"),
            "workflow_ref": _claim_string(claims, "workflow_ref"),
            "workflow_sha": _claim_string(claims, "workflow_sha"),
            "ref": _claim_string(claims, "ref"),
            "commit_sha": _claim_string(claims, "sha"),
            "run_id": _claim_string(claims, "run_id"),
            "run_attempt": _claim_string(claims, "run_attempt"),
            "actor_id": _claim_string(claims, "actor_id"),
            "event_name": _claim_string(claims, "event_name"),
            "runner_environment": _claim_string(claims, "runner_environment"),
            "token_id": _claim_string(claims, "jti"),
        }
        for optional in ("environment", "job_workflow_ref"):
            if claims.get(optional) is not None:
                context[optional] = _claim_string(claims, optional)
        return context

    def _key_for(self, kid: str) -> Mapping[str, Any]:
        for attempt in range(2):
            keys = self._load_jwks(force=attempt == 1).get("keys")
            if not isinstance(keys, list):
                raise GitHubOIDCError("github_oidc_jwks_unavailable", "GitHub JWKS is malformed.")
            matches = [item for item in keys if isinstance(item, dict) and item.get("kid") == kid]
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                raise GitHubOIDCError("github_oidc_jwks_unavailable", "GitHub JWKS repeats a key ID.")
            with self._lock:
                cache_age = time.monotonic() - self._jwks_loaded_at
            if attempt == 0 and cache_age < MIN_JWKS_REFRESH_SECONDS:
                break
        raise GitHubOIDCError("github_oidc_unknown_key", "GitHub OIDC signing key was not found.")

    def _load_jwks(self, *, force: bool) -> Mapping[str, Any]:
        with self._lock:
            now = time.monotonic()
            if not force and self._jwks is not None and now - self._jwks_loaded_at < JWKS_CACHE_SECONDS:
                return self._jwks
            try:
                jwks = self._jwks_fetcher()
            except GitHubOIDCError:
                raise
            except Exception as exc:
                raise GitHubOIDCError(
                    "github_oidc_jwks_unavailable", "GitHub signing keys could not be loaded."
                ) from exc
            if not isinstance(jwks, dict):
                raise GitHubOIDCError("github_oidc_jwks_unavailable", "GitHub JWKS is malformed.")
            self._jwks = jwks
            self._jwks_loaded_at = now
            return jwks

    @staticmethod
    def _fetch_github_jwks() -> Mapping[str, Any]:
        request = Request(
            GITHUB_OIDC_JWKS_URL,
            headers={"Accept": "application/json", "User-Agent": "SMERC-OIDC-Verifier/1.0"},
        )
        with urlopen(request, timeout=5) as response:
            if response.headers.get_content_type() != "application/json":
                raise GitHubOIDCError("github_oidc_jwks_unavailable", "GitHub JWKS must use JSON.")
            raw = response.read(262_145)
            if len(raw) > 262_144:
                raise GitHubOIDCError("github_oidc_jwks_unavailable", "GitHub JWKS is too large.")
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GitHubOIDCError("github_oidc_jwks_unavailable", "GitHub JWKS is invalid JSON.") from exc

    @staticmethod
    def _verify_rs256(message: bytes, signature: bytes, jwk: Mapping[str, Any]) -> None:
        if (
            jwk.get("kty") != "RSA"
            or jwk.get("alg") not in {None, "RS256"}
            or jwk.get("use") not in {None, "sig"}
        ):
            raise GitHubOIDCError("invalid_github_oidc_key", "GitHub signing key is not an RS256 key.")
        modulus = int.from_bytes(_decode_base64url(jwk.get("n", ""), "JWK modulus"), "big")
        exponent = int.from_bytes(_decode_base64url(jwk.get("e", ""), "JWK exponent"), "big")
        size = (modulus.bit_length() + 7) // 8
        if modulus.bit_length() < 2048 or exponent < 3 or exponent % 2 == 0 or len(signature) != size:
            raise GitHubOIDCError("invalid_github_oidc_key", "GitHub RSA key parameters are invalid.")
        encoded = pow(int.from_bytes(signature, "big"), exponent, modulus).to_bytes(size, "big")
        digest_info = SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(message).digest()
        padding_length = size - len(digest_info) - 3
        expected = b"\x00\x01" + b"\xff" * padding_length + b"\x00" + digest_info
        if padding_length < 8 or not hmac.compare_digest(encoded, expected):
            raise GitHubOIDCError("invalid_github_oidc_signature", "GitHub OIDC signature is invalid.")

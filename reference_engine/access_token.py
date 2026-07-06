from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional
from uuid import uuid4

from reference_engine.api_identity import ALL_SCOPES, APIPrincipal, SCOPES


ACCESS_TOKEN_VERSION = "smerc.access-token.v2"
LEGACY_ACCESS_TOKEN_VERSION = "smerc.access-token.v1"
ACCESS_TOKEN_TYPE = "SMERC-ACCESS"
ACCESS_TOKEN_ALGORITHM = "HS256"
ACCESS_TOKEN_ISSUER = "smerc-pilot-api"
ACCESS_TOKEN_AUDIENCE = "smerc-runtime-api"
DEFAULT_ACCESS_TOKEN_TTL_SECONDS = 300
MAX_ACCESS_TOKEN_TTL_SECONDS = 900


class AccessTokenError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str, path: str) -> bytes:
    if not value or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise AccessTokenError("invalid_access_token", f"{path} is not valid base64url.")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (TypeError, ValueError) as exc:
        raise AccessTokenError("invalid_access_token", f"{path} is not valid base64url.") from exc


def _identifier(value: Any, path: str, maximum: int = 64) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,%d}" % (maximum - 1), value):
        raise AccessTokenError(
            "invalid_access_token",
            f"{path} must be a safe identifier of 1 to {maximum} characters.",
        )
    return value


def _timestamp(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AccessTokenError("invalid_access_token", f"{path} must be a non-negative integer.")
    return value


def _scopes(values: Any) -> list[str]:
    if not isinstance(values, list) or not values or len(values) > len(SCOPES):
        raise AccessTokenError("invalid_access_token_scope", "Access token must contain explicit API scopes.")
    if any(not isinstance(value, str) for value in values):
        raise AccessTokenError("invalid_access_token_scope", "Access token scopes must be strings.")
    if len(values) != len(set(values)) or set(values) - SCOPES or ALL_SCOPES in values:
        raise AccessTokenError(
            "invalid_access_token_scope",
            "Access token scopes must be unique, recognized, and cannot use wildcard authority.",
        )
    if values != sorted(values):
        raise AccessTokenError("invalid_access_token_scope", "Access token scopes must use canonical order.")
    return values


@dataclass(frozen=True)
class AccessTokenSigner:
    key_id: str
    secret: bytes

    def __post_init__(self) -> None:
        _identifier(self.key_id, "key_id")
        if not isinstance(self.secret, bytes) or len(self.secret) < 32:
            raise ValueError("Access-token signing secrets must contain at least 32 bytes.")

    def issue(
        self,
        principal: APIPrincipal,
        *,
        requested_scopes: Optional[Iterable[str]] = None,
        ttl_seconds: int = DEFAULT_ACCESS_TOKEN_TTL_SECONDS,
        now: Optional[int] = None,
    ) -> Dict[str, Any]:
        issued_at = int(time.time()) if now is None else now
        _timestamp(issued_at, "issued_at")
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or not 1 <= ttl_seconds <= MAX_ACCESS_TOKEN_TTL_SECONDS:
            raise AccessTokenError(
                "invalid_access_token_ttl",
                f"ttl_seconds must be an integer from 1 through {MAX_ACCESS_TOKEN_TTL_SECONDS}.",
            )
        allowed = set(SCOPES) if ALL_SCOPES in principal.scopes else set(principal.scopes)
        selected = sorted(allowed) if requested_scopes is None else sorted(list(requested_scopes))
        _scopes(selected)
        unauthorized = sorted(set(selected) - allowed)
        if unauthorized:
            raise AccessTokenError(
                "access_token_scope_escalation",
                f"Requested scope exceeds bootstrap principal authority: {', '.join(unauthorized)}.",
            )
        payload = {
            "version": ACCESS_TOKEN_VERSION,
            "session_id": f"session_{uuid4().hex}",
            "issuer": ACCESS_TOKEN_ISSUER,
            "audience": ACCESS_TOKEN_AUDIENCE,
            "tenant_id": principal.tenant_id,
            "principal_id": principal.principal_id,
            "scopes": selected,
            "source_legacy": principal.legacy,
            "issued_at": issued_at,
            "not_before": issued_at,
            "expires_at": issued_at + ttl_seconds,
            "workload_context": (
                None if principal.workload_context is None else dict(principal.workload_context)
            ),
        }
        header = {"alg": ACCESS_TOKEN_ALGORITHM, "kid": self.key_id, "typ": ACCESS_TOKEN_TYPE}
        encoded_header = _encode(_canonical_json(header))
        encoded_payload = _encode(_canonical_json(payload))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = _encode(hmac.new(self.secret, signing_input, hashlib.sha256).digest())
        return {
            "access_token": f"{encoded_header}.{encoded_payload}.{signature}",
            "token_type": "Bearer",
            "expires_in": ttl_seconds,
            "expires_at": payload["expires_at"],
            "session": payload,
        }

    def verify(self, token: str, *, now: Optional[int] = None) -> APIPrincipal:
        if not isinstance(token, str) or len(token) > 16_384:
            raise AccessTokenError(
                "invalid_access_token",
                "Access token must be a string no larger than 16384 characters.",
            )
        parts = token.split(".")
        if len(parts) != 3:
            raise AccessTokenError("invalid_access_token", "Access token must contain three segments.")
        encoded_header, encoded_payload, encoded_signature = parts
        try:
            header = json.loads(_decode(encoded_header, "access-token header").decode("utf-8"))
            payload = json.loads(_decode(encoded_payload, "access-token payload").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AccessTokenError("invalid_access_token", "Access token must contain valid JSON.") from exc
        expected_header = {"alg": ACCESS_TOKEN_ALGORITHM, "kid": self.key_id, "typ": ACCESS_TOKEN_TYPE}
        if header != expected_header:
            raise AccessTokenError("invalid_access_token_header", "Access-token header is not supported.")
        expected_signature = hmac.new(
            self.secret,
            f"{encoded_header}.{encoded_payload}".encode("ascii"),
            hashlib.sha256,
        ).digest()
        supplied_signature = _decode(encoded_signature, "access-token signature")
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise AccessTokenError("invalid_access_token_signature", "Access-token signature is invalid.")
        self._validate_payload(payload)
        when = int(time.time()) if now is None else now
        _timestamp(when, "verification time")
        if when < payload["not_before"]:
            raise AccessTokenError("access_token_not_active", "Access token is not active yet.")
        if when >= payload["expires_at"]:
            raise AccessTokenError("access_token_expired", "Access token has expired.")
        return APIPrincipal(
            tenant_id=payload["tenant_id"],
            principal_id=payload["principal_id"],
            secret="verified-access-token",
            scopes=frozenset(payload["scopes"]),
            legacy=payload["source_legacy"],
            credential_type="short_lived_access_token",
            session_id=payload["session_id"],
            expires_at=payload["expires_at"],
            workload_context=payload.get("workload_context"),
        )

    @staticmethod
    def _validate_payload(payload: Any) -> None:
        base_fields = {
            "version", "session_id", "issuer", "audience", "tenant_id",
            "principal_id", "scopes", "source_legacy", "issued_at",
            "not_before", "expires_at",
        }
        if not isinstance(payload, dict):
            raise AccessTokenError("invalid_access_token", "Access-token claims must be an object.")
        version = payload.get("version")
        fields = (
            base_fields
            if version == LEGACY_ACCESS_TOKEN_VERSION
            else base_fields | {"workload_context"}
        )
        if set(payload) != fields:
            raise AccessTokenError("invalid_access_token", "Access-token claims are incomplete or unknown.")
        if (
            version not in {LEGACY_ACCESS_TOKEN_VERSION, ACCESS_TOKEN_VERSION}
            or payload["issuer"] != ACCESS_TOKEN_ISSUER
            or payload["audience"] != ACCESS_TOKEN_AUDIENCE
        ):
            raise AccessTokenError("invalid_access_token", "Access-token version, issuer, or audience is invalid.")
        if not isinstance(payload["session_id"], str) or not re.fullmatch(r"session_[0-9a-f]{32}", payload["session_id"]):
            raise AccessTokenError("invalid_access_token", "session_id is invalid.")
        _identifier(payload["tenant_id"], "tenant_id")
        _identifier(payload["principal_id"], "principal_id")
        _scopes(payload["scopes"])
        if not isinstance(payload["source_legacy"], bool):
            raise AccessTokenError("invalid_access_token", "source_legacy must be boolean.")
        if version == ACCESS_TOKEN_VERSION and payload["workload_context"] is not None:
            try:
                APIPrincipal(
                    tenant_id=payload["tenant_id"],
                    principal_id=payload["principal_id"],
                    secret="workload-context-validation",
                    scopes=frozenset(payload["scopes"]),
                    credential_type="short_lived_access_token",
                    session_id=payload["session_id"],
                    expires_at=payload["expires_at"],
                    workload_context=payload["workload_context"],
                )
            except ValueError as exc:
                raise AccessTokenError("invalid_access_token", str(exc)) from exc
        issued_at = _timestamp(payload["issued_at"], "issued_at")
        not_before = _timestamp(payload["not_before"], "not_before")
        expires_at = _timestamp(payload["expires_at"], "expires_at")
        if not_before != issued_at:
            raise AccessTokenError("invalid_access_token", "not_before must equal issued_at.")
        if not 1 <= expires_at - issued_at <= MAX_ACCESS_TOKEN_TTL_SECONDS:
            raise AccessTokenError("invalid_access_token", "Access-token lifetime exceeds the supported range.")


def parse_access_token_signer(value: str) -> Optional[AccessTokenSigner]:
    if not value.strip():
        return None
    key_id, separator, secret = value.strip().partition(":")
    if separator != ":" or not key_id or len(secret) < 32:
        raise ValueError("SMERC_ACCESS_TOKEN_KEY must use key-id:secret with at least 32 secret characters.")
    return AccessTokenSigner(key_id=key_id, secret=secret.encode("utf-8"))

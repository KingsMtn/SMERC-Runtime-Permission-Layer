from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional
from uuid import uuid4


CONTROL_EVIDENCE_VERSION = "smerc.control-evidence.v1"
CONTROL_EVIDENCE_TYPE = "SMERC-CONTROL-EVIDENCE"
CONTROL_EVIDENCE_ALGORITHM = "HS256"
MAX_CONTROL_EVIDENCE_TTL_SECONDS = 120
MAX_CONTROL_RESULTS = 64


class ControlEvidenceError(ValueError):
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
        raise ControlEvidenceError("invalid_control_evidence", f"{path} is not valid base64url.")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, TypeError) as exc:
        raise ControlEvidenceError("invalid_control_evidence", f"{path} is not valid base64url.") from exc


def _identifier(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,%d}" % (maximum - 1), value):
        raise ControlEvidenceError(
            "invalid_control_evidence",
            f"{path} must be a safe identifier of 1 to {maximum} characters.",
        )
    return value


def _digest(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ControlEvidenceError("invalid_control_evidence", f"{path} must be a lowercase SHA-256 digest.")
    return value


def _bounded_text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= maximum or any(ord(char) < 32 for char in value):
        raise ControlEvidenceError(
            "invalid_control_evidence",
            f"{path} must contain 1 to {maximum} printable characters.",
        )
    return value


def _timestamp(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ControlEvidenceError("invalid_control_evidence", f"{path} must be a non-negative integer.")
    return value


def _control_results(values: Any, issued_at: int) -> list[Dict[str, Any]]:
    if not isinstance(values, list) or len(values) > MAX_CONTROL_RESULTS:
        raise ControlEvidenceError(
            "invalid_control_evidence",
            f"controls must be a list containing at most {MAX_CONTROL_RESULTS} results.",
        )
    normalized = []
    seen = set()
    expected_fields = {"control_id", "outcome", "mechanism", "evidence_ref", "observed_at"}
    for index, item in enumerate(values):
        if not isinstance(item, Mapping) or set(item) != expected_fields:
            raise ControlEvidenceError(
                "invalid_control_evidence",
                f"controls[{index}] fields are incomplete or unknown.",
            )
        control_id = _identifier(item["control_id"], f"controls[{index}].control_id")
        if control_id in seen:
            raise ControlEvidenceError("invalid_control_evidence", "Control results must be unique.")
        if item["outcome"] != "applied":
            raise ControlEvidenceError("control_not_applied", f"Control {control_id} was not applied.")
        observed_at = _timestamp(item["observed_at"], f"controls[{index}].observed_at")
        if observed_at > issued_at or issued_at - observed_at > MAX_CONTROL_EVIDENCE_TTL_SECONDS:
            raise ControlEvidenceError(
                "stale_control_evidence",
                f"Control {control_id} was not observed within the supported freshness window.",
            )
        normalized.append(
            {
                "control_id": control_id,
                "outcome": "applied",
                "mechanism": _bounded_text(item["mechanism"], f"controls[{index}].mechanism", 128),
                "evidence_ref": _bounded_text(item["evidence_ref"], f"controls[{index}].evidence_ref", 256),
                "observed_at": observed_at,
            }
        )
        seen.add(control_id)
    return sorted(normalized, key=lambda item: item["control_id"])


@dataclass(frozen=True)
class ControlEvidenceSigner:
    tenant_id: str
    audience: str
    adapter_id: str
    key_id: str
    secret: bytes

    def __post_init__(self) -> None:
        _identifier(self.tenant_id, "tenant_id")
        _identifier(self.audience, "audience")
        _identifier(self.adapter_id, "adapter_id")
        _identifier(self.key_id, "key_id", 64)
        if not isinstance(self.secret, bytes) or len(self.secret) < 32:
            raise ValueError("Control-evidence signing secrets must contain at least 32 bytes.")

    def issue(
        self,
        permit: Mapping[str, Any],
        controls: Iterable[Mapping[str, Any]],
        *,
        ttl_seconds: int = 60,
        now: Optional[int] = None,
    ) -> Dict[str, Any]:
        issued_at = int(time.time()) if now is None else now
        _timestamp(issued_at, "issued_at")
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or not 1 <= ttl_seconds <= MAX_CONTROL_EVIDENCE_TTL_SECONDS:
            raise ControlEvidenceError(
                "invalid_control_evidence_ttl",
                f"ttl_seconds must be an integer from 1 through {MAX_CONTROL_EVIDENCE_TTL_SECONDS}.",
            )
        if permit.get("tenant_id") != self.tenant_id or permit.get("audience") != self.audience:
            raise ControlEvidenceError("control_evidence_binding_mismatch", "Permit tenant or audience is not assigned to this adapter.")
        results = _control_results(list(controls), issued_at)
        applied = {item["control_id"] for item in results}
        required_controls = permit.get("required_controls")
        if not isinstance(required_controls, list):
            raise ControlEvidenceError(
                "invalid_control_evidence",
                "Permit required_controls must be a list.",
            )
        required = {
            _identifier(value, "permit.required_controls")
            for value in required_controls
        }
        missing = sorted(required - applied)
        if missing:
            raise ControlEvidenceError(
                "required_control_evidence_missing",
                f"Receipt is missing required control evidence: {', '.join(missing)}.",
            )
        payload = {
            "version": CONTROL_EVIDENCE_VERSION,
            "evidence_id": f"control_evidence_{uuid4().hex}",
            "tenant_id": self.tenant_id,
            "audience": self.audience,
            "adapter_id": self.adapter_id,
            "permit_id": _identifier(permit.get("permit_id"), "permit_id", 192),
            "action_hash": _digest(permit.get("action_hash"), "action_hash"),
            "controls": results,
            "issued_at": issued_at,
            "expires_at": issued_at + ttl_seconds,
        }
        header = {
            "alg": CONTROL_EVIDENCE_ALGORITHM,
            "kid": self.key_id,
            "typ": CONTROL_EVIDENCE_TYPE,
        }
        encoded_header = _encode(_canonical_json(header))
        encoded_payload = _encode(_canonical_json(payload))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = _encode(hmac.new(self.secret, signing_input, hashlib.sha256).digest())
        return {
            "control_evidence_token": f"{encoded_header}.{encoded_payload}.{signature}",
            "control_evidence": payload,
        }

    def verify(
        self,
        token: str,
        *,
        tenant_id: str,
        audience: str,
        action_hash: str,
        now: Optional[int] = None,
    ) -> Dict[str, Any]:
        tenant_id = _identifier(tenant_id, "tenant_id")
        audience = _identifier(audience, "audience")
        action_hash = _digest(action_hash, "action_hash")
        if not isinstance(token, str) or len(token) > 32_768:
            raise ControlEvidenceError(
                "invalid_control_evidence",
                "Control-evidence token must be a string no larger than 32768 characters.",
            )
        parts = token.split(".")
        if len(parts) != 3:
            raise ControlEvidenceError("invalid_control_evidence", "Control-evidence token must contain three segments.")
        encoded_header, encoded_payload, encoded_signature = parts
        try:
            header = json.loads(_decode(encoded_header, "control-evidence header").decode("utf-8"))
            payload = json.loads(_decode(encoded_payload, "control-evidence payload").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ControlEvidenceError("invalid_control_evidence", "Control-evidence token must contain valid JSON.") from exc
        expected_header = {
            "alg": CONTROL_EVIDENCE_ALGORITHM,
            "kid": self.key_id,
            "typ": CONTROL_EVIDENCE_TYPE,
        }
        if header != expected_header:
            raise ControlEvidenceError("invalid_control_evidence_header", "Control-evidence header is not supported.")
        expected_signature = hmac.new(
            self.secret,
            f"{encoded_header}.{encoded_payload}".encode("ascii"),
            hashlib.sha256,
        ).digest()
        supplied_signature = _decode(encoded_signature, "control-evidence signature")
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise ControlEvidenceError("invalid_control_evidence_signature", "Control-evidence signature is invalid.")
        self._validate_payload(payload)
        when = int(time.time()) if now is None else now
        _timestamp(when, "verification time")
        if when < payload["issued_at"]:
            raise ControlEvidenceError("control_evidence_not_active", "Control evidence is not active yet.")
        if when >= payload["expires_at"]:
            raise ControlEvidenceError("control_evidence_expired", "Control evidence has expired.")
        if (
            payload["tenant_id"] != self.tenant_id
            or payload["audience"] != self.audience
            or payload["adapter_id"] != self.adapter_id
        ):
            raise ControlEvidenceError(
                "control_evidence_binding_mismatch",
                "Control evidence does not match the configured adapter binding.",
            )
        if payload["tenant_id"] != tenant_id or payload["audience"] != audience:
            raise ControlEvidenceError("control_evidence_binding_mismatch", "Control evidence tenant or audience does not match.")
        if payload["action_hash"] != action_hash:
            raise ControlEvidenceError("control_evidence_action_mismatch", "Control evidence is not bound to this action.")
        return payload

    @staticmethod
    def applied_controls(payload: Mapping[str, Any]) -> list[str]:
        return sorted(item["control_id"] for item in payload["controls"] if item["outcome"] == "applied")

    @staticmethod
    def _validate_payload(payload: Any) -> None:
        expected_fields = {
            "version", "evidence_id", "tenant_id", "audience", "adapter_id",
            "permit_id", "action_hash", "controls", "issued_at", "expires_at",
        }
        if not isinstance(payload, dict) or set(payload) != expected_fields:
            raise ControlEvidenceError("invalid_control_evidence", "Control-evidence payload fields are incomplete or unknown.")
        if payload["version"] != CONTROL_EVIDENCE_VERSION:
            raise ControlEvidenceError("invalid_control_evidence", "Control-evidence version is unsupported.")
        if not isinstance(payload["evidence_id"], str) or not re.fullmatch(r"control_evidence_[0-9a-f]{32}", payload["evidence_id"]):
            raise ControlEvidenceError("invalid_control_evidence", "evidence_id is invalid.")
        _identifier(payload["tenant_id"], "tenant_id")
        _identifier(payload["audience"], "audience")
        _identifier(payload["adapter_id"], "adapter_id")
        _identifier(payload["permit_id"], "permit_id", 192)
        _digest(payload["action_hash"], "action_hash")
        issued_at = _timestamp(payload["issued_at"], "issued_at")
        expires_at = _timestamp(payload["expires_at"], "expires_at")
        if not 1 <= expires_at - issued_at <= MAX_CONTROL_EVIDENCE_TTL_SECONDS:
            raise ControlEvidenceError("invalid_control_evidence", "Control-evidence lifetime exceeds the supported range.")
        if payload["controls"] != _control_results(payload["controls"], issued_at):
            raise ControlEvidenceError(
                "invalid_control_evidence",
                "Control results must use canonical control_id order.",
            )


def parse_control_evidence_signers(value: str) -> Dict[tuple[str, str], ControlEvidenceSigner]:
    """Parse tenant:audience=adapter-id:key-id:secret entries."""
    signers: Dict[tuple[str, str], ControlEvidenceSigner] = {}
    key_ids = set()
    secrets = set()
    if not value.strip():
        return signers
    for entry in value.split(","):
        binding, separator, key_spec = entry.strip().partition("=")
        binding_parts = binding.split(":")
        key_parts = key_spec.split(":", 2)
        if separator != "=" or len(binding_parts) != 2 or len(key_parts) != 3:
            raise ValueError(
                "SMERC_CONTROL_EVIDENCE_KEYS entries must use tenant:audience=adapter-id:key-id:secret format."
            )
        tenant_id, audience = binding_parts
        adapter_id, key_id, secret = key_parts
        if len(secret) < 32:
            raise ValueError("SMERC_CONTROL_EVIDENCE_KEYS secrets must contain at least 32 characters.")
        signer = ControlEvidenceSigner(tenant_id, audience, adapter_id, key_id, secret.encode("utf-8"))
        binding_key = (tenant_id, audience)
        if binding_key in signers:
            raise ValueError(f"Duplicate control-evidence binding: {tenant_id}/{audience}")
        if key_id in key_ids or secret in secrets:
            raise ValueError("Each control-evidence adapter must use a distinct key ID and secret.")
        signers[binding_key] = signer
        key_ids.add(key_id)
        secrets.add(secret)
    return signers

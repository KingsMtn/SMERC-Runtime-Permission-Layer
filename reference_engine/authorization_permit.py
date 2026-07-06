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

from reference_engine.action_language import action_hash


PERMIT_VERSION = "smerc.permit.v1"
PERMIT_TYPE = "SMERC-PERMIT"
PERMIT_ALGORITHM = "HS256"
MAX_PERMIT_TTL_SECONDS = 300
PERMIT_POSTURES = {"ALLOW": "release", "THROTTLE": "constrain"}


class PermitError(ValueError):
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
        raise PermitError("invalid_permit", f"{path} is not valid base64url.")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, TypeError) as exc:
        raise PermitError("invalid_permit", f"{path} is not valid base64url.") from exc


def _identifier(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,%d}" % (maximum - 1), value):
        raise PermitError("invalid_permit_request", f"{path} must be a safe identifier of 1 to {maximum} characters.")
    return value


def _controls(values: Iterable[Any], path: str) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise PermitError("invalid_permit", f"{path} must be a list of control identifiers.")
    result = []
    for value in values:
        result.append(_identifier(value, path, 128))
    if len(result) != len(set(result)):
        raise PermitError("invalid_permit", f"{path} must not contain duplicates.")
    return sorted(result)


@dataclass(frozen=True)
class PermitSigner:
    key_id: str
    secret: bytes

    def __post_init__(self) -> None:
        _identifier(self.key_id, "key_id", 64)
        if not isinstance(self.secret, bytes) or len(self.secret) < 32:
            raise ValueError("Permit signing secrets must contain at least 32 bytes.")

    def issue(
        self,
        decision: Mapping[str, Any],
        action: Mapping[str, Any],
        *,
        tenant_id: str,
        audience: str,
        ttl_seconds: int = 60,
        now: Optional[int] = None,
    ) -> Dict[str, Any]:
        tenant_id = _identifier(tenant_id, "tenant_id")
        audience = _identifier(audience, "audience")
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or not 1 <= ttl_seconds <= MAX_PERMIT_TTL_SECONDS:
            raise PermitError(
                "invalid_permit_ttl",
                f"ttl_seconds must be an integer from 1 through {MAX_PERMIT_TTL_SECONDS}.",
            )
        posture = decision.get("posture")
        if posture not in PERMIT_POSTURES:
            raise PermitError("posture_not_permittable", "Only ALLOW and THROTTLE decisions can produce a permit.")
        if decision.get("enforcement_state") != PERMIT_POSTURES[posture]:
            raise PermitError("decision_incoherent", "Decision posture and enforcement state do not agree.")
        if decision.get("tenant_id") != tenant_id:
            raise PermitError("tenant_mismatch", "Decision tenant does not match the permit tenant.")

        digest = action_hash(dict(action))
        if decision.get("action_hash") != digest:
            raise PermitError("action_mismatch", "Decision is not bound to this action envelope.")
        replay_id = _identifier(decision.get("replay_id"), "decision.replay_id", 192)

        policy = decision.get("policy")
        if not isinstance(policy, Mapping):
            raise PermitError("decision_incoherent", "Decision is missing policy metadata.")
        if policy.get("tenant_id") not in {tenant_id, "*"}:
            raise PermitError("tenant_mismatch", "Decision policy is not valid for the permit tenant.")
        if policy.get("mode") != "ENFORCE":
            raise PermitError("policy_not_enforceable", "Permits require an ENFORCE policy.")
        if policy.get("evidence_ceiling") not in {"LIMITED_ENFORCE", "CALIBRATED_ENFORCE"}:
            raise PermitError("evidence_not_enforceable", "Policy evidence ceiling does not authorize enforcement.")
        policy_claim = {
            "policy_id": _identifier(policy.get("policy_id"), "decision.policy.policy_id"),
            "policy_revision": _identifier(policy.get("policy_revision"), "decision.policy.policy_revision", 64),
            "policy_hash": self._digest(policy.get("policy_hash"), "decision.policy.policy_hash"),
            "mode": "ENFORCE",
            "evidence_ceiling": policy["evidence_ceiling"],
        }

        decision_controls = decision.get("controls")
        if not isinstance(decision_controls, list):
            raise PermitError("decision_incoherent", "Decision controls must be a list.")
        required_controls = _controls(
            [item for item in decision_controls if item not in {"execute", "record_replay"}],
            "decision.controls",
        )
        issued_at = int(time.time()) if now is None else now
        if isinstance(issued_at, bool) or not isinstance(issued_at, int) or issued_at < 0:
            raise PermitError("invalid_permit_time", "Permit issuance time must be a non-negative integer.")
        payload = {
            "version": PERMIT_VERSION,
            "permit_id": f"permit_{uuid4().hex}",
            "tenant_id": tenant_id,
            "audience": audience,
            "action_hash": digest,
            "replay_id": replay_id,
            "posture": posture,
            "authorization": PERMIT_POSTURES[posture],
            "required_controls": required_controls,
            "policy": policy_claim,
            "issued_at": issued_at,
            "not_before": issued_at,
            "expires_at": issued_at + ttl_seconds,
            "max_uses": 1,
        }
        header = {"alg": PERMIT_ALGORITHM, "kid": self.key_id, "typ": PERMIT_TYPE}
        encoded_header = _encode(_canonical_json(header))
        encoded_payload = _encode(_canonical_json(payload))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = _encode(hmac.new(self.secret, signing_input, hashlib.sha256).digest())
        return {"permit_token": f"{encoded_header}.{encoded_payload}.{signature}", "permit": payload}

    def verify(
        self,
        token: str,
        action: Mapping[str, Any],
        *,
        tenant_id: str,
        audience: str,
        enforced_controls: Iterable[str],
        now: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload = self.verify_claims(
            token,
            action,
            tenant_id=tenant_id,
            audience=audience,
            now=now,
        )
        applied = set(_controls(enforced_controls, "enforced_controls"))
        missing = sorted(set(payload["required_controls"]) - applied)
        if missing:
            raise PermitError(
                "required_controls_missing",
                f"Consuming adapter did not declare required control(s): {', '.join(missing)}.",
            )
        return payload

    def verify_claims(
        self,
        token: str,
        action: Mapping[str, Any],
        *,
        tenant_id: str,
        audience: str,
        now: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Authenticate permit claims without asserting that controls have run."""
        tenant_id = _identifier(tenant_id, "tenant_id")
        audience = _identifier(audience, "audience")
        if not isinstance(token, str) or len(token) > 16_384:
            raise PermitError("invalid_permit", "Permit token must be a string no larger than 16384 characters.")
        parts = token.split(".")
        if len(parts) != 3:
            raise PermitError("invalid_permit", "Permit token must contain three segments.")
        encoded_header, encoded_payload, encoded_signature = parts
        try:
            header = json.loads(_decode(encoded_header, "permit header").decode("utf-8"))
            payload = json.loads(_decode(encoded_payload, "permit payload").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PermitError("invalid_permit", "Permit header and payload must contain valid JSON.") from exc
        if header != {"alg": PERMIT_ALGORITHM, "kid": self.key_id, "typ": PERMIT_TYPE}:
            raise PermitError("invalid_permit_header", "Permit header is not supported by this verifier.")
        expected = hmac.new(
            self.secret,
            f"{encoded_header}.{encoded_payload}".encode("ascii"),
            hashlib.sha256,
        ).digest()
        supplied = _decode(encoded_signature, "permit signature")
        if not hmac.compare_digest(supplied, expected):
            raise PermitError("invalid_permit_signature", "Permit signature is invalid.")
        self._validate_payload(payload)

        when = int(time.time()) if now is None else now
        if when < payload["not_before"]:
            raise PermitError("permit_not_active", "Permit is not active yet.")
        if when >= payload["expires_at"]:
            raise PermitError("permit_expired", "Permit has expired.")
        if payload["tenant_id"] != tenant_id:
            raise PermitError("tenant_mismatch", "Permit tenant does not match the authenticated tenant.")
        if payload["audience"] != audience:
            raise PermitError("audience_mismatch", "Permit audience does not match the consuming executor.")
        if payload["action_hash"] != action_hash(dict(action)):
            raise PermitError("action_mismatch", "Permit is not valid for this action envelope.")
        return payload

    @staticmethod
    def _digest(value: Any, path: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise PermitError("decision_incoherent", f"{path} must be a lowercase SHA-256 digest.")
        return value

    @classmethod
    def _validate_payload(cls, payload: Any) -> None:
        fields = {
            "version", "permit_id", "tenant_id", "audience", "action_hash", "replay_id",
            "posture", "authorization", "required_controls", "policy", "issued_at",
            "not_before", "expires_at", "max_uses",
        }
        if not isinstance(payload, dict) or set(payload) != fields:
            raise PermitError("invalid_permit", "Permit payload fields are incomplete or unknown.")
        if payload["version"] != PERMIT_VERSION or payload["posture"] not in PERMIT_POSTURES:
            raise PermitError("invalid_permit", "Permit version or posture is invalid.")
        if payload["authorization"] != PERMIT_POSTURES[payload["posture"]] or payload["max_uses"] != 1:
            raise PermitError("invalid_permit", "Permit authorization or use limit is invalid.")
        _identifier(payload["permit_id"], "permit.permit_id", 192)
        _identifier(payload["tenant_id"], "permit.tenant_id")
        _identifier(payload["audience"], "permit.audience")
        _identifier(payload["replay_id"], "permit.replay_id", 192)
        cls._digest(payload["action_hash"], "permit.action_hash")
        if not isinstance(payload["required_controls"], list):
            raise PermitError("invalid_permit", "Permit required_controls must be a list.")
        _controls(payload["required_controls"], "permit.required_controls")
        for field in ("issued_at", "not_before", "expires_at"):
            if isinstance(payload[field], bool) or not isinstance(payload[field], int) or payload[field] < 0:
                raise PermitError("invalid_permit", f"Permit {field} must be a non-negative integer.")
        if payload["not_before"] != payload["issued_at"]:
            raise PermitError("invalid_permit", "Permit not_before must equal issued_at.")
        ttl = payload["expires_at"] - payload["issued_at"]
        if not 1 <= ttl <= MAX_PERMIT_TTL_SECONDS:
            raise PermitError("invalid_permit", "Permit lifetime exceeds the supported range.")
        policy = payload["policy"]
        expected_policy_fields = {"policy_id", "policy_revision", "policy_hash", "mode", "evidence_ceiling"}
        if not isinstance(policy, dict) or set(policy) != expected_policy_fields:
            raise PermitError("invalid_permit", "Permit policy claim is invalid.")
        _identifier(policy["policy_id"], "permit.policy.policy_id")
        _identifier(policy["policy_revision"], "permit.policy.policy_revision", 64)
        cls._digest(policy["policy_hash"], "permit.policy.policy_hash")
        if policy["mode"] != "ENFORCE" or policy["evidence_ceiling"] not in {
            "LIMITED_ENFORCE", "CALIBRATED_ENFORCE"
        }:
            raise PermitError("invalid_permit", "Permit policy claim is not enforceable.")


def parse_permit_signers(value: str) -> Dict[str, PermitSigner]:
    signers: Dict[str, PermitSigner] = {}
    if not value.strip():
        return signers
    for entry in value.split(","):
        tenant, separator, key_spec = entry.strip().partition("=")
        key_id, key_separator, secret = key_spec.partition(":")
        if separator != "=" or key_separator != ":" or not tenant or not key_id or not secret:
            raise ValueError("SMERC_PERMIT_KEYS entries must use tenant=key-id:secret format.")
        _identifier(tenant, "permit key tenant", 64)
        if tenant in signers:
            raise ValueError(f"Duplicate tenant in SMERC_PERMIT_KEYS: {tenant}")
        signer = PermitSigner(key_id=key_id, secret=secret.encode("utf-8"))
        if any(item.key_id == signer.key_id for item in signers.values()):
            raise ValueError("Each SMERC_PERMIT_KEYS tenant must use a distinct key ID.")
        if any(item.secret == signer.secret for item in signers.values()):
            raise ValueError("Each SMERC_PERMIT_KEYS tenant must use a distinct signing secret.")
        signers[tenant] = signer
    return signers

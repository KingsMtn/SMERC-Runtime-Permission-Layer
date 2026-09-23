from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from uuid import uuid4


VERSION = "smerc.deferred-effect-provenance.v1"
REVIEW_VERSION = "smerc.deferred-effect-review.v1"
AUTHORITY_RANK = {"OBSERVE": 0, "READ": 1, "BOUNDED_WRITE": 2, "PRODUCTION_WRITE": 3, "IRREVERSIBLE": 4}


class DeferredEffectError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def content_digest(content: bytes) -> str:
    if not isinstance(content, bytes):
        raise TypeError("artifact content must be bytes")
    return hashlib.sha256(content).hexdigest()


def _identifier(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{0,191}", value):
        raise DeferredEffectError(f"{path} must be a safe identifier")
    return value


def _identifiers(values: Iterable[Any], path: str) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise DeferredEffectError(f"{path} must be a list")
    result = sorted(_identifier(value, path) for value in values)
    if len(result) != len(set(result)):
        raise DeferredEffectError(f"{path} must not contain duplicates")
    return result


@dataclass(frozen=True)
class DeferredEffectSigner:
    key_id: str
    secret: bytes

    def __post_init__(self) -> None:
        _identifier(self.key_id, "key_id")
        if not isinstance(self.secret, bytes) or len(self.secret) < 32:
            raise ValueError("provenance signing secrets must contain at least 32 bytes")

    def attest_origin(
        self,
        content: bytes,
        *,
        artifact_id: str,
        artifact_type: str,
        tenant_id: str,
        originating_agent_id: str,
        originating_contract_sha256: str,
        intent_digest: str,
        authority_ceiling: str,
        allowed_effects: Iterable[str],
        prohibited_effects: Iterable[str],
        obligations: Iterable[str],
        issued_at: int,
        expires_at: int,
        review_required: bool,
    ) -> dict[str, Any]:
        body = {
            "version": VERSION,
            "attestation_id": f"dep_{uuid4().hex}",
            "artifact_id": _identifier(artifact_id, "artifact_id"),
            "artifact_type": _identifier(artifact_type, "artifact_type"),
            "content_sha256": content_digest(content),
            "parent_attestation_sha256": [],
            "tenant_id": _identifier(tenant_id, "tenant_id"),
            "originating_agent_ids": [_identifier(originating_agent_id, "originating_agent_id")],
            "originating_contract_sha256": self._sha(originating_contract_sha256, "originating_contract_sha256"),
            "intent_digests": [self._sha(intent_digest, "intent_digest")],
            "authority_ceiling": self._authority(authority_ceiling),
            "allowed_effects": _identifiers(allowed_effects, "allowed_effects"),
            "prohibited_effects": _identifiers(prohibited_effects, "prohibited_effects"),
            "obligations": _identifiers(obligations, "obligations"),
            "issued_at": self._time(issued_at, "issued_at"),
            "expires_at": self._time(expires_at, "expires_at"),
            "review_required": self._boolean(review_required, "review_required"),
        }
        self._validate_semantics(body)
        return self._sign(body)

    def derive(
        self,
        content: bytes,
        parents: Iterable[Mapping[str, Any]],
        *,
        artifact_id: str,
        artifact_type: str,
        issued_at: int,
    ) -> dict[str, Any]:
        parent_envelopes = list(parents)
        verified = [self.verify(parent) for parent in parent_envelopes]
        if not verified:
            raise DeferredEffectError("at least one parent attestation is required")
        tenant_ids = {item["tenant_id"] for item in verified}
        contract_hashes = {item["originating_contract_sha256"] for item in verified}
        if len(tenant_ids) != 1:
            raise DeferredEffectError("cross-tenant derivation requires explicit reauthorization")
        if len(contract_hashes) != 1:
            raise DeferredEffectError("mixed originating contracts require explicit reauthorization")
        allowed = set(verified[0]["allowed_effects"])
        for item in verified[1:]:
            allowed &= set(item["allowed_effects"])
        prohibited = set().union(*(set(item["prohibited_effects"]) for item in verified))
        allowed -= prohibited
        ceiling = min(verified, key=lambda item: AUTHORITY_RANK[item["authority_ceiling"]])["authority_ceiling"]
        body = {
            "version": VERSION,
            "attestation_id": f"dep_{uuid4().hex}",
            "artifact_id": _identifier(artifact_id, "artifact_id"),
            "artifact_type": _identifier(artifact_type, "artifact_type"),
            "content_sha256": content_digest(content),
            "parent_attestation_sha256": sorted(_digest(parent) for parent in parent_envelopes),
            "tenant_id": next(iter(tenant_ids)),
            "originating_agent_ids": sorted(set().union(*(set(item["originating_agent_ids"]) for item in verified))),
            "originating_contract_sha256": next(iter(contract_hashes)),
            "intent_digests": sorted(set().union(*(set(item["intent_digests"]) for item in verified))),
            "authority_ceiling": ceiling,
            "allowed_effects": sorted(allowed),
            "prohibited_effects": sorted(prohibited),
            "obligations": sorted(set().union(*(set(item["obligations"]) for item in verified))),
            "issued_at": self._time(issued_at, "issued_at"),
            "expires_at": min(item["expires_at"] for item in verified),
            "review_required": any(item["review_required"] for item in verified),
        }
        self._validate_semantics(body)
        return self._sign(body)

    def review(
        self,
        attestation: Mapping[str, Any],
        content: bytes,
        *,
        reviewer_id: str,
        approved_effects: Iterable[str],
        satisfied_obligations: Iterable[str],
        reviewed_at: int,
    ) -> dict[str, Any]:
        body = self.verify(attestation)
        if content_digest(content) != body["content_sha256"]:
            raise DeferredEffectError("review content does not match attestation")
        if reviewed_at < body["issued_at"] or reviewed_at >= body["expires_at"]:
            raise DeferredEffectError("review must occur during the attestation lifetime")
        effects = _identifiers(approved_effects, "approved_effects")
        obligations = _identifiers(satisfied_obligations, "satisfied_obligations")
        if not set(effects) <= set(body["allowed_effects"]):
            raise DeferredEffectError("review cannot expand inherited effects")
        if not set(obligations) <= set(body["obligations"]):
            raise DeferredEffectError("review names unknown obligations")
        review = {
            "version": REVIEW_VERSION,
            "review_id": f"der_{uuid4().hex}",
            "attestation_sha256": _digest(attestation),
            "content_sha256": body["content_sha256"],
            "reviewer_id": _identifier(reviewer_id, "reviewer_id"),
            "approved_effects": effects,
            "satisfied_obligations": obligations,
            "reviewed_at": self._time(reviewed_at, "reviewed_at"),
        }
        return self._sign(review)

    def verify(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "verification"}:
            raise DeferredEffectError("signed envelope fields are invalid")
        payload = envelope["payload"]
        verification = envelope["verification"]
        if not isinstance(payload, Mapping) or not isinstance(verification, Mapping):
            raise DeferredEffectError("signed envelope is invalid")
        if verification.get("method") != "hmac_sha256" or verification.get("key_id") != self.key_id:
            raise DeferredEffectError("verification metadata is invalid")
        expected = hmac.new(self.secret, _canonical(payload), hashlib.sha256).hexdigest()
        if not isinstance(verification.get("signature"), str) or not hmac.compare_digest(
            verification["signature"], expected
        ):
            raise DeferredEffectError("signature is invalid")
        if payload.get("version") == VERSION:
            self._validate_attestation(payload)
        elif payload.get("version") == REVIEW_VERSION:
            self._validate_review(payload)
        else:
            raise DeferredEffectError("signed payload version is invalid")
        return dict(payload)

    def _sign(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "payload": dict(payload),
            "verification": {
                "method": "hmac_sha256",
                "key_id": self.key_id,
                "signature": hmac.new(self.secret, _canonical(payload), hashlib.sha256).hexdigest(),
            },
        }

    def _validate_attestation(self, body: Mapping[str, Any]) -> None:
        fields = {
            "version", "attestation_id", "artifact_id", "artifact_type", "content_sha256",
            "parent_attestation_sha256", "tenant_id", "originating_agent_ids",
            "originating_contract_sha256", "intent_digests", "authority_ceiling", "allowed_effects",
            "prohibited_effects", "obligations", "issued_at", "expires_at", "review_required",
        }
        if set(body) != fields:
            raise DeferredEffectError("attestation fields are invalid")
        for field in ("attestation_id", "artifact_id", "artifact_type", "tenant_id"):
            _identifier(body[field], field)
        self._sha(body["content_sha256"], "content_sha256")
        for value in body["parent_attestation_sha256"]:
            self._sha(value, "parent_attestation_sha256")
        _identifiers(body["originating_agent_ids"], "originating_agent_ids")
        self._sha(body["originating_contract_sha256"], "originating_contract_sha256")
        for value in body["intent_digests"]:
            self._sha(value, "intent_digests")
        self._authority(body["authority_ceiling"])
        _identifiers(body["allowed_effects"], "allowed_effects")
        _identifiers(body["prohibited_effects"], "prohibited_effects")
        _identifiers(body["obligations"], "obligations")
        self._time(body["issued_at"], "issued_at")
        self._time(body["expires_at"], "expires_at")
        self._boolean(body["review_required"], "review_required")
        self._validate_semantics(body)

    def _validate_review(self, review: Mapping[str, Any]) -> None:
        fields = {
            "version", "review_id", "attestation_sha256", "content_sha256", "reviewer_id",
            "approved_effects", "satisfied_obligations", "reviewed_at",
        }
        if set(review) != fields:
            raise DeferredEffectError("review fields are invalid")
        _identifier(review["review_id"], "review_id")
        _identifier(review["reviewer_id"], "reviewer_id")
        self._sha(review["attestation_sha256"], "attestation_sha256")
        self._sha(review["content_sha256"], "content_sha256")
        _identifiers(review["approved_effects"], "approved_effects")
        _identifiers(review["satisfied_obligations"], "satisfied_obligations")
        self._time(review["reviewed_at"], "reviewed_at")

    @staticmethod
    def _validate_semantics(body: Mapping[str, Any]) -> None:
        if body["expires_at"] <= body["issued_at"]:
            raise DeferredEffectError("expires_at must be after issued_at")
        overlap = set(body["allowed_effects"]) & set(body["prohibited_effects"])
        if overlap:
            raise DeferredEffectError("an effect cannot be both allowed and prohibited")

    @staticmethod
    def _sha(value: Any, path: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise DeferredEffectError(f"{path} must be a lowercase SHA-256 digest")
        return value

    @staticmethod
    def _authority(value: Any) -> str:
        if value not in AUTHORITY_RANK:
            raise DeferredEffectError("authority_ceiling is invalid")
        return value

    @staticmethod
    def _time(value: Any, path: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise DeferredEffectError(f"{path} must be a non-negative integer")
        return value

    @staticmethod
    def _boolean(value: Any, path: str) -> bool:
        if not isinstance(value, bool):
            raise DeferredEffectError(f"{path} must be a boolean")
        return value


def authorize_deferred_effect(
    signer: DeferredEffectSigner,
    attestation: Mapping[str, Any],
    content: bytes,
    *,
    effect: str,
    required_authority: str,
    now: int,
    review: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    body = signer.verify(attestation)
    effect = _identifier(effect, "effect")
    required_authority = signer._authority(required_authority)
    reasons = []
    if content_digest(content) != body["content_sha256"]:
        reasons.append("artifact_content_changed")
    if now >= body["expires_at"]:
        reasons.append("provenance_expired")
    if effect not in body["allowed_effects"] or effect in body["prohibited_effects"]:
        reasons.append("effect_not_in_inherited_authority")
    if AUTHORITY_RANK[required_authority] > AUTHORITY_RANK[body["authority_ceiling"]]:
        reasons.append("required_authority_exceeds_ceiling")
    satisfied = set()
    if review is not None:
        review_body = signer.verify(review)
        if review_body["attestation_sha256"] != _digest(attestation):
            reasons.append("review_not_bound_to_attestation")
        if review_body["content_sha256"] != body["content_sha256"]:
            reasons.append("review_not_bound_to_content")
        if review_body["reviewed_at"] > now or review_body["reviewed_at"] >= body["expires_at"]:
            reasons.append("review_time_invalid")
        if effect not in review_body["approved_effects"]:
            reasons.append("effect_not_approved_by_review")
        satisfied = set(review_body["satisfied_obligations"])
    elif body["review_required"]:
        reasons.append("material_review_required")
    missing = sorted(set(body["obligations"]) - satisfied)
    if missing:
        reasons.append("artifact_obligations_unresolved")
    decision = "BLOCK" if reasons else "ALLOW"
    return {
        "version": VERSION,
        "decision": decision,
        "reasons": reasons,
        "artifact_id": body["artifact_id"],
        "effect": effect,
        "authority_ceiling": body["authority_ceiling"],
        "missing_obligations": missing,
        "evidence": {
            "attestation_sha256": _digest(attestation),
            "content_sha256": content_digest(content),
            "review_sha256": _digest(review) if review is not None else None,
        },
    }

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

VERSION = "smerc.authority-accretion.v1"
RESOURCE_KINDS = {"credential", "account", "service", "agent", "compute", "tool"}


class AuthorityAccretionError(ValueError):
    pass


def _digest(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AuthorityAccretionError(f"{path} must be a non-empty string")
    return value.strip()


def _integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AuthorityAccretionError(f"{path} must be a non-negative integer")
    return value


def _string_set(value: Any, path: str) -> set[str]:
    if not isinstance(value, list):
        raise AuthorityAccretionError(f"{path} must be a list")
    result = {_text(item, path) for item in value}
    if len(result) != len(value):
        raise AuthorityAccretionError(f"{path} must not contain duplicates")
    return result


def evaluate_acquired_authority(
    envelope: Mapping[str, Any], acquired: Mapping[str, Any], observation: Mapping[str, Any]
) -> dict[str, Any]:
    """Check whether a resource acquired during a task remains inside its authority envelope."""
    envelope_id = _text(envelope.get("envelope_id"), "envelope.envelope_id")
    epoch = _integer(envelope.get("authority_epoch"), "envelope.authority_epoch")
    kinds = _string_set(envelope.get("allowed_resource_kinds", []), "envelope.allowed_resource_kinds")
    if not kinds <= RESOURCE_KINDS:
        raise AuthorityAccretionError("envelope.allowed_resource_kinds contains an unknown kind")
    capabilities = _string_set(envelope.get("allowed_capabilities", []), "envelope.allowed_capabilities")
    effects = _string_set(envelope.get("allowed_effects", []), "envelope.allowed_effects")
    providers = _string_set(envelope.get("allowed_providers", []), "envelope.allowed_providers")
    limits = {
        "delegation": _integer(envelope.get("max_delegation_depth"), "envelope.max_delegation_depth"),
        "persistence": _integer(envelope.get("max_persistence_seconds"), "envelope.max_persistence_seconds"),
        "spend": _integer(envelope.get("max_spend_minor"), "envelope.max_spend_minor"),
    }

    resource_id = _text(acquired.get("resource_id"), "acquired.resource_id")
    kind = _text(acquired.get("resource_kind"), "acquired.resource_kind")
    provider = _text(acquired.get("provider"), "acquired.provider")
    acquired_capabilities = _string_set(acquired.get("capabilities", []), "acquired.capabilities")
    acquired_effects = _string_set(acquired.get("effects", []), "acquired.effects")
    depth = _integer(acquired.get("delegation_depth"), "acquired.delegation_depth")
    persistence = _integer(acquired.get("persistence_seconds"), "acquired.persistence_seconds")
    spend = _integer(acquired.get("spend_minor"), "acquired.spend_minor")
    provenance = _text(acquired.get("provenance_digest"), "acquired.provenance_digest")

    observed_epoch = _integer(observation.get("current_authority_epoch"), "observation.current_authority_epoch")
    resolved_provenance = _text(
        observation.get("resolved_provenance_digest"), "observation.resolved_provenance_digest"
    )
    resolver_version = _text(observation.get("resolver_version"), "observation.resolver_version")
    quarantined = observation.get("quarantined_before_evaluation")
    if not isinstance(quarantined, bool):
        raise AuthorityAccretionError("observation.quarantined_before_evaluation must be a boolean")

    reasons: list[str] = []
    checks = [
        (not quarantined, "resource_was_not_quarantined"),
        (observed_epoch != epoch, "authority_epoch_changed"),
        (resolved_provenance != provenance, "provenance_resolution_mismatch"),
        (kind not in kinds, "resource_kind_not_authorized"),
        (bool(providers) and provider not in providers, "provider_not_authorized"),
        (bool(acquired_capabilities - capabilities), "capability_expansion"),
        (bool(acquired_effects - effects), "effect_expansion"),
        (depth > limits["delegation"], "delegation_depth_exceeded"),
        (persistence > limits["persistence"], "persistence_limit_exceeded"),
        (spend > limits["spend"], "spend_limit_exceeded"),
    ]
    reasons.extend(reason for failed, reason in checks if failed)

    return {
        "version": VERSION,
        "decision": "ELIGIBLE_FOR_ACTIVATION" if not reasons else "QUARANTINE",
        "reasons": reasons,
        "authority_effect": "NONE",
        "should_activate": False,
        "envelope_id": envelope_id,
        "resource_id": resource_id,
        "resolver_version": resolver_version,
        "evidence": {
            "envelope_sha256": _digest(envelope),
            "acquired_resource_sha256": _digest(acquired),
            "observation_sha256": _digest(observation),
        },
    }

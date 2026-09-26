from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


VERSION = "smerc.continuing-authority.v1"
DECISIONS = {"CONTINUE", "REVALIDATE", "QUARANTINE", "COMPENSATE", "SETTLE", "ORPHANED"}


class ContinuingAuthorityError(ValueError):
    pass


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContinuingAuthorityError(f"{path} must be a non-empty string")
    return value.strip()


def _integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContinuingAuthorityError(f"{path} must be a non-negative integer")
    return value


def _string_set(value: Any, path: str) -> set[str]:
    if not isinstance(value, list):
        raise ContinuingAuthorityError(f"{path} must be a list")
    result = {_text(item, path) for item in value}
    if len(result) != len(value):
        raise ContinuingAuthorityError(f"{path} must not contain duplicates")
    return result


def evaluate_continuing_authority(
    grant: Mapping[str, Any],
    runtime: Mapping[str, Any],
    *,
    phase: str = "continue",
) -> dict[str, Any]:
    """Reconcile an earlier authority grant with current runtime facts.

    The result is advisory evidence and never creates or expands authority.
    """
    if phase not in {"continue", "settle"}:
        raise ContinuingAuthorityError("phase must be continue or settle")

    contract_id = _text(grant.get("contract_id"), "grant.contract_id")
    granted_epoch = _integer(grant.get("authority_epoch"), "grant.authority_epoch")
    issued_at = _integer(grant.get("issued_at"), "grant.issued_at")
    valid_until = _integer(grant.get("valid_until"), "grant.valid_until")
    if valid_until <= issued_at:
        raise ContinuingAuthorityError("grant.valid_until must be after grant.issued_at")

    lineage = _string_set(grant.get("authority_lineage"), "grant.authority_lineage")
    if not lineage:
        raise ContinuingAuthorityError("grant.authority_lineage must not be empty")
    triggers = _string_set(grant.get("revalidation_triggers", []), "grant.revalidation_triggers")
    settlement_requirements = _string_set(
        grant.get("settlement_requirements", []), "grant.settlement_requirements"
    )
    expected_descendants = _string_set(
        grant.get("descendant_contract_ids", []), "grant.descendant_contract_ids"
    )
    checkpoint_digest = _text(grant.get("checkpoint_digest"), "grant.checkpoint_digest")

    observed_at = _integer(runtime.get("observed_at"), "runtime.observed_at")
    current_epoch = _integer(runtime.get("current_authority_epoch"), "runtime.current_authority_epoch")
    revoked = _string_set(runtime.get("revoked_contract_ids", []), "runtime.revoked_contract_ids")
    observed_triggers = _string_set(runtime.get("trigger_events", []), "runtime.trigger_events")
    active_principals = _string_set(runtime.get("active_principals", []), "runtime.active_principals")
    acknowledged_descendants = _string_set(
        runtime.get("invalidation_acknowledged_by", []), "runtime.invalidation_acknowledged_by"
    )
    satisfied_requirements = _string_set(
        runtime.get("satisfied_settlement_requirements", []),
        "runtime.satisfied_settlement_requirements",
    )
    current_checkpoint = _text(runtime.get("checkpoint_digest"), "runtime.checkpoint_digest")
    partial_effects = runtime.get("partial_effects_present")
    if not isinstance(partial_effects, bool):
        raise ContinuingAuthorityError("runtime.partial_effects_present must be a boolean")

    stale_reasons: list[str] = []
    if observed_at >= valid_until:
        stale_reasons.append("authority_lease_expired")
    if contract_id in revoked:
        stale_reasons.append("contract_revoked")
    if current_epoch != granted_epoch:
        stale_reasons.append("authority_epoch_changed")

    reasons: list[str] = []
    accountable_principals = lineage & active_principals
    if not accountable_principals:
        decision = "ORPHANED"
        reasons.append("no_accountable_principal_active")
    elif stale_reasons:
        reasons.extend(stale_reasons)
        missing_acks = expected_descendants - acknowledged_descendants
        if missing_acks:
            reasons.append("descendant_invalidation_unconfirmed")
        if partial_effects:
            decision = "COMPENSATE"
            reasons.append("partial_effects_require_compensation")
        else:
            decision = "QUARANTINE"
    else:
        matched_triggers = triggers & observed_triggers
        if matched_triggers:
            decision = "REVALIDATE"
            reasons.extend(f"trigger:{trigger}" for trigger in sorted(matched_triggers))
        elif current_checkpoint != checkpoint_digest:
            decision = "REVALIDATE"
            reasons.append("checkpoint_discontinuity")
        elif phase == "settle":
            missing_requirements = settlement_requirements - satisfied_requirements
            if missing_requirements:
                decision = "REVALIDATE"
                reasons.extend(f"settlement_missing:{item}" for item in sorted(missing_requirements))
            else:
                decision = "SETTLE"
        else:
            decision = "CONTINUE"

    missing_acknowledgements = sorted(expected_descendants - acknowledged_descendants)
    return {
        "version": VERSION,
        "decision": decision,
        "reasons": reasons,
        "authority_effect": "NONE",
        "contract_id": contract_id,
        "phase": phase,
        "authority": {
            "granted_epoch": granted_epoch,
            "current_epoch": current_epoch,
            "valid_until": valid_until,
            "observed_at": observed_at,
            "accountable_principals": sorted(accountable_principals),
        },
        "propagation": {
            "expected_descendants": sorted(expected_descendants),
            "missing_acknowledgements": missing_acknowledgements,
            "complete": not missing_acknowledgements,
        },
        "evidence": {
            "grant_sha256": _digest(grant),
            "runtime_sha256": _digest(runtime),
            "reconciled_at": observed_at,
        },
    }

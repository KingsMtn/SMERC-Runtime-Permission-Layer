from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from reference_engine.authority_accretion import evaluate_acquired_authority
from reference_engine.continuing_authority import evaluate_continuing_authority
from reference_engine.delegated_continuance_contract import (
    ContinuanceContractSigner,
    evaluate_delegated_continuance,
)


VERSION = "smerc.consequence-time-reconciliation.v1"


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def reconcile_consequence_time(
    *,
    signer: ContinuanceContractSigner,
    delegated_contract: Mapping[str, Any],
    proposed_action: Mapping[str, Any],
    consumption: Mapping[str, Any],
    authority_grant: Mapping[str, Any],
    authority_runtime: Mapping[str, Any],
    acquired_envelope: Mapping[str, Any],
    acquired_resource: Mapping[str, Any],
    acquired_observation: Mapping[str, Any],
    now: int,
    partial_effects_present: bool,
) -> dict[str, Any]:
    """Reconcile delegated, acquired, and continuing authority before consequence."""
    delegated = evaluate_delegated_continuance(
        signer, delegated_contract, proposed_action, consumption, now=now
    )
    acquired = evaluate_acquired_authority(
        acquired_envelope, acquired_resource, acquired_observation
    )
    continuing_runtime = dict(authority_runtime)
    continuing_runtime["partial_effects_present"] = partial_effects_present
    continuing = evaluate_continuing_authority(
        authority_grant, continuing_runtime, phase="settle"
    )

    reasons: list[str] = []
    if delegated["decision"] != "CONTINUE":
        reasons.extend(f"delegated:{reason}" for reason in delegated["reasons"])
    if acquired["decision"] != "ELIGIBLE_FOR_ACTIVATION":
        reasons.extend(f"acquired:{reason}" for reason in acquired["reasons"])
    if continuing["decision"] != "SETTLE":
        reasons.extend(f"continuing:{reason}" for reason in continuing["reasons"])

    if continuing["decision"] == "COMPENSATE":
        decision = "COMPENSATE"
    elif reasons:
        decision = "QUARANTINE"
    else:
        decision = "SETTLE"

    return {
        "version": VERSION,
        "decision": decision,
        "reasons": reasons,
        "authority_effect": "NONE",
        "should_commit": decision == "SETTLE",
        "checkpoints": {
            "delegated_continuance": delegated,
            "authority_accretion": acquired,
            "continuing_authority": continuing,
        },
        "evidence": {
            "delegated_sha256": _digest(delegated),
            "acquired_sha256": _digest(acquired),
            "continuing_sha256": _digest(continuing),
            "reconciled_at": now,
        },
    }

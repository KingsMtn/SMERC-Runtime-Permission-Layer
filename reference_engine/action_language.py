from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List

from reference_engine.recoverability_engine import RecoverabilityEngine, evaluate_action


ACTION_VERSION = "smerc.action.v1"
DECISION_VERSION = "smerc.decision.v1"
MAX_CONTEXT_BYTES = 16_384

ROOT_FIELDS = {"language_version", "action", "signals", "recoverability", "effects", "context"}
ACTION_FIELDS = {"id", "description", "actor", "tool", "type", "target", "authority"}
TARGET_FIELDS = {"resource", "environment"}
AUTHORITY_FIELDS = {"basis", "confidence"}
SIGNAL_FIELDS = {"base_action_risk", "evidence_validity", "anomaly_pressure", "impact_scope"}
RECOVERY_FIELDS = {
    "reversibility", "containment_strength", "rollback_latency", "cancel_reliability", "rollback_method"
}
EFFECT_FIELDS = {"external_side_effect", "sensitive_data"}

REASON_TITLES = {
    "IRREVERSIBLE_EXPOSURE_HIGH": "Irreversible exposure is high",
    "IRREVERSIBLE_EXPOSURE_ELEVATED": "Irreversible exposure is elevated",
    "RECOVERY_CAPACITY_LOW": "Recovery capacity is low",
    "ROLLBACK_LATENCY_HIGH": "Rollback latency is high",
    "CANCEL_RELIABILITY_WEAK": "Cancellation is unreliable",
    "CONTAINMENT_WEAK": "Containment is weak",
    "EVIDENCE_VALIDITY_LOW": "Evidence validity is low",
    "AUTHORIZATION_CONFIDENCE_LOW": "Authority confidence is low",
    "ANOMALY_PRESSURE_HIGH": "Anomaly pressure is high",
    "IMPACT_SCOPE_WIDE": "Impact scope is wide",
    "EXTERNAL_SIDE_EFFECT": "Action has an external side effect",
    "SENSITIVE_DATA": "Action involves sensitive data",
    "RECOVERABILITY_ACCEPTABLE": "Recoverability is acceptable",
}

CONTROL_TITLES = {
    "execute": "Execute the action",
    "record_replay": "Record a replayable decision",
    "retain_cancel_handle": "Retain an effective cancellation handle",
    "limit_scope": "Limit action scope",
    "preview_before_execution": "Preview before execution",
    "require_rollback_plan": "Require a tested rollback plan",
    "rate_limit_external_side_effect": "Rate-limit external effects",
    "checkpoint_before_execution": "Create a recovery checkpoint",
    "pause_execution": "Pause execution",
    "collect_more_evidence": "Collect additional evidence",
    "snapshot_current_state": "Snapshot current state",
    "preserve_replay": "Preserve the decision replay",
    "block_execution": "Block execution",
    "explain_denial": "Explain the denial",
    "require_new_request": "Require a materially new request",
    "route_to_accountable_reviewer": "Route to an accountable reviewer",
    "require_explicit_approval": "Require explicit approval",
    "document_override_if_approved": "Document any approved override",
}


def _condition(code: str, field: str, operator: str, value: Any, description: str) -> Dict[str, Any]:
    return {"code": code, "field": field, "operator": operator, "value": value, "description": description}


TRANSITION_CONDITIONS = {
    "limit_scope": _condition("IMPACT_SCOPE_REDUCED", "signals.impact_scope", "lte", 0.45, "Reduce impact scope to 0.45 or lower."),
    "preview_before_execution": _condition("PREVIEW_APPROVED", "evidence.preview_approved", "eq", True, "Approve an execution preview."),
    "require_rollback_plan": _condition("ROLLBACK_PLAN_VERIFIED", "evidence.rollback_plan_verified", "eq", True, "Verify the rollback plan."),
    "rate_limit_external_side_effect": _condition("EXTERNAL_RATE_LIMIT_SET", "controls.external_rate_limit", "present", True, "Set an external-effect rate limit."),
    "checkpoint_before_execution": _condition("CHECKPOINT_CREATED", "evidence.checkpoint_created", "eq", True, "Create a recovery checkpoint."),
    "collect_more_evidence": _condition("EVIDENCE_VALIDITY_RESTORED", "signals.evidence_validity", "gte", 0.65, "Raise evidence validity to at least 0.65."),
    "snapshot_current_state": _condition("STATE_SNAPSHOT_CREATED", "evidence.state_snapshot_created", "eq", True, "Create a current-state snapshot."),
    "route_to_accountable_reviewer": _condition("REVIEWER_ASSIGNED", "review.accountable_reviewer", "present", True, "Assign an accountable reviewer."),
    "require_explicit_approval": _condition("APPROVAL_RECORDED", "review.explicit_approval", "eq", True, "Record explicit approval."),
    "document_override_if_approved": _condition("OVERRIDE_RATIONALE_RECORDED", "review.override_rationale", "present", True, "Record the override rationale when applicable."),
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    return value


def _required(value: Dict[str, Any], fields: Iterable[str], path: str) -> None:
    missing = sorted(set(fields) - set(value))
    if missing:
        raise ValueError(f"{path} is missing required field(s): {', '.join(missing)}")


def _strict(value: Dict[str, Any], fields: Iterable[str], path: str) -> None:
    unknown = sorted(set(value) - set(fields))
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _text(value: Any, path: str, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value.strip()


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    if not 0 <= value <= 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return float(value)


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def validate_action_envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    root = deepcopy(_object(payload, "request"))
    _required(root, ROOT_FIELDS, "request")
    _strict(root, ROOT_FIELDS, "request")
    if root["language_version"] != ACTION_VERSION:
        raise ValueError(f"language_version must be {ACTION_VERSION}")

    action = _object(root["action"], "action")
    signals = _object(root["signals"], "signals")
    recovery = _object(root["recoverability"], "recoverability")
    effects = _object(root["effects"], "effects")
    context = _object(root["context"], "context")
    for value, fields, path in (
        (action, ACTION_FIELDS, "action"), (signals, SIGNAL_FIELDS, "signals"),
        (recovery, RECOVERY_FIELDS, "recoverability"), (effects, EFFECT_FIELDS, "effects"),
    ):
        _required(value, fields, path)
        _strict(value, fields, path)

    target = _object(action["target"], "action.target")
    authority = _object(action["authority"], "action.authority")
    _required(target, TARGET_FIELDS, "action.target")
    _strict(target, TARGET_FIELDS, "action.target")
    _required(authority, AUTHORITY_FIELDS, "action.authority")
    _strict(authority, AUTHORITY_FIELDS, "action.authority")

    for field in ("id", "description", "actor", "tool", "type"):
        action[field] = _text(action[field], f"action.{field}")
    for field in TARGET_FIELDS:
        target[field] = _text(target[field], f"action.target.{field}", 256)
    authority["basis"] = _text(authority["basis"], "action.authority.basis", 256)
    authority["confidence"] = _score(authority["confidence"], "action.authority.confidence")
    for field in SIGNAL_FIELDS:
        signals[field] = _score(signals[field], f"signals.{field}")
    for field in RECOVERY_FIELDS - {"rollback_method"}:
        recovery[field] = _score(recovery[field], f"recoverability.{field}")
    recovery["rollback_method"] = _text(recovery["rollback_method"], "recoverability.rollback_method", 512)
    for field in EFFECT_FIELDS:
        effects[field] = _boolean(effects[field], f"effects.{field}")
    try:
        context_size = len(canonical_json(context).encode("utf-8"))
    except (TypeError, ValueError) as exc:
        raise TypeError("context must contain JSON-serializable values") from exc
    if context_size > MAX_CONTEXT_BYTES:
        raise ValueError(f"context must not exceed {MAX_CONTEXT_BYTES} canonical JSON bytes")
    return root


def action_hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(validate_action_envelope(payload)).encode("utf-8")).hexdigest()


def compile_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    envelope = validate_action_envelope(payload)
    action, signals = envelope["action"], envelope["signals"]
    recovery, effects = envelope["recoverability"], envelope["effects"]
    compiled_context = deepcopy(envelope["context"])
    compiled_context["smerc_language"] = {
        "version": ACTION_VERSION,
        "action_hash": hashlib.sha256(canonical_json(envelope).encode("utf-8")).hexdigest(),
        "target": action["target"],
        "authority_basis": action["authority"]["basis"],
        "rollback_method": recovery["rollback_method"],
    }
    return {
        "action_id": action["id"], "description": action["description"], "actor": action["actor"],
        "tool": action["tool"], "action_type": action["type"], **signals,
        "reversibility": recovery["reversibility"], "containment_strength": recovery["containment_strength"],
        "rollback_latency": recovery["rollback_latency"], "cancel_reliability": recovery["cancel_reliability"],
        "authorization_confidence": action["authority"]["confidence"], **effects, "context": compiled_context,
    }


def transition_for(posture: str, controls: List[str]) -> Dict[str, Any]:
    target = {"ALLOW": "ALLOW", "THROTTLE": "ALLOW", "FREEZE": "THROTTLE", "DENY": None, "ESCALATE": "THROTTLE"}[posture]
    conditions = [deepcopy(TRANSITION_CONDITIONS[control]) for control in controls if control in TRANSITION_CONDITIONS]
    if posture == "DENY":
        conditions.append(_condition("MATERIAL_NEW_REQUEST_REQUIRED", "request.action_hash", "changed", True, "Submit a materially new action request."))
    return {
        "mode": "maintain" if posture == "ALLOW" else "conditional",
        "eligible_target_posture": target,
        "requires_new_request": posture == "DENY",
        "conditions": conditions,
    }


def evaluate_language_action(
    payload: Dict[str, Any],
    engine: RecoverabilityEngine | None = None,
) -> Dict[str, Any]:
    normalized = validate_action_envelope(payload)
    digest = hashlib.sha256(canonical_json(normalized).encode("utf-8")).hexdigest()
    compiled = compile_action(normalized)
    decision = engine.evaluate(compiled) if engine is not None else evaluate_action(compiled)
    decision.update({
        "language_version": DECISION_VERSION, "action_language_version": ACTION_VERSION, "action_hash": digest,
        "reasons": [{"code": code, "title": REASON_TITLES.get(code, code.replace("_", " ").title())} for code in decision["reason_codes"]],
        "structured_controls": [{"code": code, "title": CONTROL_TITLES.get(code, code.replace("_", " ").title())} for code in decision["controls"]],
        "transition": transition_for(decision["posture"], decision["controls"]),
    })
    decision["replay"]["language_version"] = DECISION_VERSION
    decision["replay"]["action_hash"] = digest
    decision["replay"]["transition"] = decision["transition"]
    return decision


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a SMERC Action Language v1 envelope")
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate_language_action(json.loads(args.request.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()

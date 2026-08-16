from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from reference_engine.action_language import action_hash, validate_action_envelope


ELIGIBILITY_VERSION = "smerc.constraint-eligibility.v1"
DEFAULT_PROHIBITED_PATTERNS = (
    "disable_audit",
    "delete_audit",
    "delete_log",
    "delete_logs",
    "delete_backup",
    "delete_backups",
    "export_secret",
    "export_private_key",
    "exfiltrate",
    "bypass_auth",
    "disable_mfa",
    "disable_security_control",
    "weaken_audit",
    "privilege_escalation",
)
CRITICAL_ENVIRONMENTS = {"production", "prod", "financial_rail", "regulated", "safety_critical"}


def evaluate_constraint_eligibility(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify whether a SMERC action may use constrained authorization.

    Recoverability can only modify an action that is allowed in principle. This
    module fails closed on missing authority, categorical prohibitions, severe
    identity/evidence gaps, and high-impact sensitive actions.
    """

    envelope = validate_action_envelope(dict(payload))
    action = envelope["action"]
    signals = envelope["signals"]
    recovery = envelope["recoverability"]
    effects = envelope["effects"]
    context = deepcopy(envelope.get("context", {}))

    rule_results: List[Dict[str, Any]] = []
    labels: List[str] = []
    recommended_posture = "constraint_eligible"

    def add_rule(rule_id: str, triggered: bool, severity: str, reason: str, posture: str | None = None) -> None:
        nonlocal recommended_posture
        rule_results.append(
            {
                "rule_id": rule_id,
                "triggered": bool(triggered),
                "severity": severity,
                "reason": reason,
                "recommended_posture": posture,
            }
        )
        if triggered and posture:
            recommended_posture = _more_restrictive(recommended_posture, posture)

    action_text = " ".join(
        [
            action["id"],
            action["description"],
            action["tool"],
            action["type"],
            action["target"]["resource"],
            action["authority"]["basis"],
        ]
    ).lower()
    configured_patterns = _list_of_text(context.get("prohibited_action_patterns"), "context.prohibited_action_patterns")
    prohibited_patterns = tuple(configured_patterns or DEFAULT_PROHIBITED_PATTERNS)
    matched_patterns = [pattern for pattern in prohibited_patterns if pattern.lower() in action_text]

    authority_confidence = action["authority"]["confidence"]
    environment = action["target"]["environment"].strip().lower()
    identity_confidence = _score_from_context(context, "identity_confidence", 1.0)
    legal_hold = _bool_from_context(context, "legal_or_regulatory_hold", False)
    actor_authorized = _bool_from_context(context, "actor_authorized", True)
    approved_goal_consistent = _bool_from_context(context, "approved_goal_consistent", True)
    control_availability = _score_from_context(context, "control_availability", 1.0)
    adversarial_pressure = _score_from_context(context, "adversarial_pressure", signals["anomaly_pressure"])
    emergency_containment = _bool_from_context(context, "emergency_containment_action", False)

    add_rule(
        "PROHIBITED_ACTION_PATTERN",
        bool(matched_patterns),
        "hard_deny",
        "Action text matches a configured prohibited-action pattern.",
        "categorically_prohibited",
    )
    add_rule(
        "ACTOR_NOT_AUTHORIZED",
        not actor_authorized,
        "hard_deny",
        "Actor is not authorized to request this action type.",
        "requires_authority",
    )
    add_rule(
        "LOW_AUTHORITY_CONFIDENCE",
        authority_confidence < 0.40,
        "hard_deny",
        "Authority confidence is too weak for constrained execution.",
        "requires_authority",
    )
    add_rule(
        "LOW_IDENTITY_CONFIDENCE",
        identity_confidence < 0.50,
        "hard_deny",
        "Actor or workload identity is not strong enough for constrained execution.",
        "requires_authority",
    )
    add_rule(
        "GOAL_INCONSISTENT",
        not approved_goal_consistent,
        "hard_deny",
        "Requested action does not match the approved task or operating goal.",
        "review_required",
    )
    add_rule(
        "REGULATORY_HOLD",
        legal_hold,
        "hard_deny",
        "Legal, regulatory, or contractual hold requires explicit review.",
        "review_required",
    )
    add_rule(
        "CRITICAL_ENV_WIDE_SENSITIVE_EFFECT",
        environment in CRITICAL_ENVIRONMENTS
        and effects["sensitive_data"]
        and effects["external_side_effect"]
        and signals["impact_scope"] >= 0.70,
        "hard_deny",
        "Critical-environment sensitive external action has wide impact.",
        "review_required",
    )
    add_rule(
        "SEVERE_ADVERSARIAL_PRESSURE",
        adversarial_pressure >= 0.85 and not emergency_containment,
        "freeze",
        "Adversarial pressure is too high to treat the action as constraint-eligible.",
        "review_required",
    )
    add_rule(
        "EVIDENCE_TOO_WEAK",
        signals["evidence_validity"] < 0.35,
        "freeze",
        "Evidence validity is too weak for constrained execution.",
        "review_required",
    )
    add_rule(
        "NO_AVAILABLE_CONTROLS",
        control_availability < 0.30,
        "freeze",
        "No credible control path is currently available.",
        "review_required",
    )
    add_rule(
        "RECOVERABILITY_SENSITIVE",
        recovery["reversibility"] < 0.45
        or recovery["containment_strength"] < 0.45
        or recovery["rollback_latency"] > 0.65,
        "modifier",
        "Action remains sensitive to recoverability if it passes hard eligibility checks.",
        None,
    )

    if matched_patterns:
        labels.append("categorically_prohibited")
    if not actor_authorized or authority_confidence < 0.40 or identity_confidence < 0.50:
        labels.append("requires_authority")
    if legal_hold or not approved_goal_consistent or recommended_posture == "review_required":
        labels.append("review_required")
    if any(item["rule_id"] == "RECOVERABILITY_SENSITIVE" and item["triggered"] for item in rule_results):
        labels.append("recoverability_sensitive")
    if not labels:
        labels.append("constraint_eligible")

    if "categorically_prohibited" in labels:
        eligible = False
        recommended_runtime_posture = "DENY"
    elif "requires_authority" in labels:
        eligible = False
        recommended_runtime_posture = "DENY"
    elif "review_required" in labels:
        eligible = False
        recommended_runtime_posture = "ESCALATE"
    else:
        eligible = True
        recommended_runtime_posture = "THROTTLE" if "recoverability_sensitive" in labels else "ALLOW"

    return {
        "language_version": ELIGIBILITY_VERSION,
        "action_hash": action_hash(envelope),
        "action_id": action["id"],
        "constraint_eligible": eligible,
        "eligibility_labels": sorted(set(labels)),
        "recommended_runtime_posture": recommended_runtime_posture,
        "matched_prohibited_patterns": matched_patterns,
        "modifier_inputs": {
            "authority_confidence": round(authority_confidence, 3),
            "identity_confidence": round(identity_confidence, 3),
            "actor_authorized": actor_authorized,
            "approved_goal_consistent": approved_goal_consistent,
            "environment": action["target"]["environment"],
            "impact_scope": round(signals["impact_scope"], 3),
            "evidence_validity": round(signals["evidence_validity"], 3),
            "adversarial_pressure": round(adversarial_pressure, 3),
            "control_availability": round(control_availability, 3),
            "sensitive_data": effects["sensitive_data"],
            "external_side_effect": effects["external_side_effect"],
            "reversibility": round(recovery["reversibility"], 3),
            "containment_strength": round(recovery["containment_strength"], 3),
            "rollback_latency": round(recovery["rollback_latency"], 3),
        },
        "rule_results": rule_results,
        "plain_english_summary": _summary(action["id"], eligible, sorted(set(labels)), recommended_runtime_posture),
    }


def _more_restrictive(current: str, candidate: str) -> str:
    rank = {
        "constraint_eligible": 0,
        "recoverability_sensitive": 1,
        "review_required": 2,
        "requires_authority": 3,
        "categorically_prohibited": 4,
    }
    return candidate if rank[candidate] > rank[current] else current


def _score_from_context(context: Mapping[str, Any], key: str, default: float) -> float:
    value = context.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"context.{key} must be a number between 0.0 and 1.0")
    if not 0 <= value <= 1:
        raise ValueError(f"context.{key} must be between 0.0 and 1.0")
    return float(value)


def _bool_from_context(context: Mapping[str, Any], key: str, default: bool) -> bool:
    value = context.get(key, default)
    if not isinstance(value, bool):
        raise TypeError(f"context.{key} must be a boolean")
    return value


def _list_of_text(value: Any, path: str) -> Sequence[str]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise TypeError(f"{path} must be a list of strings")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise TypeError(f"{path}[{index}] must be a non-empty string")
    return tuple(item.strip() for item in value)


def _summary(action_id: str, eligible: bool, labels: List[str], posture: str) -> str:
    if eligible:
        return (
            f"Action '{action_id}' is eligible for recoverability-aware runtime scoring. "
            f"Recommended starting posture is {posture}."
        )
    return (
        f"Action '{action_id}' is not eligible for constrained authorization. "
        f"Labels: {', '.join(labels)}. Recommended runtime posture is {posture}."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate SMERC constraint eligibility for an action envelope.")
    parser.add_argument("request", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    result = evaluate_constraint_eligibility(json.loads(args.request.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

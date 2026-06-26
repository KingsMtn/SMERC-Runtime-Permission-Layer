from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class RuntimePosture(str, Enum):
    ALLOW = "ALLOW"
    THROTTLE = "THROTTLE"
    FREEZE = "FREEZE"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


class EnforcementState(str, Enum):
    RELEASE = "release"
    CONSTRAIN = "constrain"
    PAUSE = "pause"
    BLOCK = "block"
    REVIEW = "review"


@dataclass(frozen=True)
class RecoverabilityAction:
    action_id: str
    description: str
    actor: str
    tool: str
    action_type: str
    base_action_risk: float
    reversibility: float
    containment_strength: float
    rollback_latency: float
    evidence_validity: float
    anomaly_pressure: float
    impact_scope: float
    cancel_reliability: float
    authorization_confidence: float
    external_side_effect: bool
    sensitive_data: bool
    context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RecoverabilityAction":
        required = [
            "action_id",
            "description",
            "actor",
            "tool",
            "action_type",
            "base_action_risk",
            "reversibility",
            "containment_strength",
            "rollback_latency",
            "evidence_validity",
            "anomaly_pressure",
            "impact_scope",
            "cancel_reliability",
            "authorization_confidence",
            "external_side_effect",
            "sensitive_data",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Missing required recoverability field(s): {', '.join(missing)}")

        for key in ["action_id", "description", "actor", "tool", "action_type"]:
            if not isinstance(payload[key], str) or not payload[key].strip():
                raise TypeError(f"{key} must be a non-empty string")

        values: Dict[str, float] = {}
        for key in [
            "base_action_risk",
            "reversibility",
            "containment_strength",
            "rollback_latency",
            "evidence_validity",
            "anomaly_pressure",
            "impact_scope",
            "cancel_reliability",
            "authorization_confidence",
        ]:
            value = payload[key]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{key} must be a number between 0.0 and 1.0")
            if value < 0 or value > 1:
                raise ValueError(f"{key} must be between 0.0 and 1.0")
            values[key] = float(value)

        for key in ["external_side_effect", "sensitive_data"]:
            if not isinstance(payload[key], bool):
                raise TypeError(f"{key} must be a boolean")

        context = payload.get("context", {})
        if not isinstance(context, dict):
            raise TypeError("context must be an object when provided")

        return cls(
            action_id=payload["action_id"],
            description=payload["description"],
            actor=payload["actor"],
            tool=payload["tool"],
            action_type=payload["action_type"],
            base_action_risk=values["base_action_risk"],
            reversibility=values["reversibility"],
            containment_strength=values["containment_strength"],
            rollback_latency=values["rollback_latency"],
            evidence_validity=values["evidence_validity"],
            anomaly_pressure=values["anomaly_pressure"],
            impact_scope=values["impact_scope"],
            cancel_reliability=values["cancel_reliability"],
            authorization_confidence=values["authorization_confidence"],
            external_side_effect=payload["external_side_effect"],
            sensitive_data=payload["sensitive_data"],
            context=context,
        )


class RecoverabilityEngine:
    """Recoverability-aware runtime permission engine for automated actions."""

    def evaluate(self, payload: Dict[str, Any] | RecoverabilityAction) -> Dict[str, Any]:
        action = payload if isinstance(payload, RecoverabilityAction) else RecoverabilityAction.from_dict(payload)
        scores = self._scores(action)
        reason_codes = self._reason_codes(action, scores)
        posture = self._posture(action, scores)
        enforcement_state = self._enforcement_state(posture)
        controls = self._controls(action, posture, scores)
        replay_id = f"replay_{action.action_id}_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        summary = self._summary(action, posture, scores, controls)
        evaluated_at = datetime.now(timezone.utc).isoformat()

        return {
            "action_id": action.action_id,
            "posture": posture.value,
            "enforcement_state": enforcement_state.value,
            "scores": {key: round(value, 3) for key, value in scores.items()},
            "reason_codes": reason_codes,
            "controls": controls,
            "plain_english_summary": summary,
            "replay_id": replay_id,
            "replay": {
                "replay_id": replay_id,
                "evaluated_at": evaluated_at,
                "actor": action.actor,
                "tool": action.tool,
                "action_type": action.action_type,
                "posture": posture.value,
                "enforcement_state": enforcement_state.value,
                "scores": {key: round(value, 3) for key, value in scores.items()},
                "reason_codes": reason_codes,
                "controls": controls,
                "context": action.context,
            },
        }

    @staticmethod
    def _scores(action: RecoverabilityAction) -> Dict[str, float]:
        irreversibility = 1 - action.reversibility
        rollback_risk = action.rollback_latency
        containment_gap = 1 - action.containment_strength
        cancel_gap = 1 - action.cancel_reliability
        evidence_gap = 1 - action.evidence_validity
        confidence_gap = 1 - action.authorization_confidence
        side_effect = 1.0 if action.external_side_effect else 0.0
        data_risk = 1.0 if action.sensitive_data else 0.0

        irreversible_exposure = clamp(
            action.base_action_risk * 0.18
            + irreversibility * 0.24
            + rollback_risk * 0.17
            + containment_gap * 0.13
            + action.impact_scope * 0.12
            + side_effect * 0.08
            + data_risk * 0.08
        )
        reversible_capacity = clamp(
            action.reversibility * 0.31
            + action.containment_strength * 0.24
            + (1 - action.rollback_latency) * 0.19
            + action.cancel_reliability * 0.16
            + action.evidence_validity * 0.10
        )
        confidence_score = clamp(
            action.evidence_validity * 0.40
            + action.authorization_confidence * 0.34
            + (1 - action.anomaly_pressure) * 0.18
            + action.containment_strength * 0.08
        )
        operational_stress = clamp(
            action.base_action_risk * 0.20
            + action.anomaly_pressure * 0.20
            + action.impact_scope * 0.18
            + evidence_gap * 0.14
            + confidence_gap * 0.12
            + rollback_risk * 0.10
            + cancel_gap * 0.06
        )
        authorization_score = clamp(
            reversible_capacity * 0.45
            + confidence_score * 0.30
            + (1 - irreversible_exposure) * 0.25
        )
        return {
            "irreversible_exposure_score": irreversible_exposure,
            "reversible_capacity_score": reversible_capacity,
            "confidence_score": confidence_score,
            "operational_stress_score": operational_stress,
            "risk_adjusted_authorization_score": authorization_score,
            "cancel_reliability_score": action.cancel_reliability,
        }

    @staticmethod
    def _reason_codes(action: RecoverabilityAction, scores: Dict[str, float]) -> List[str]:
        reasons: List[str] = []
        if scores["irreversible_exposure_score"] >= 0.68:
            reasons.append("IRREVERSIBLE_EXPOSURE_HIGH")
        elif scores["irreversible_exposure_score"] >= 0.48:
            reasons.append("IRREVERSIBLE_EXPOSURE_ELEVATED")
        if scores["reversible_capacity_score"] < 0.42:
            reasons.append("RECOVERY_CAPACITY_LOW")
        if action.rollback_latency >= 0.70:
            reasons.append("ROLLBACK_LATENCY_HIGH")
        if action.cancel_reliability < 0.45:
            reasons.append("CANCEL_RELIABILITY_WEAK")
        if action.containment_strength < 0.45:
            reasons.append("CONTAINMENT_WEAK")
        if action.evidence_validity < 0.50:
            reasons.append("EVIDENCE_VALIDITY_LOW")
        if action.authorization_confidence < 0.50:
            reasons.append("AUTHORIZATION_CONFIDENCE_LOW")
        if action.anomaly_pressure >= 0.65:
            reasons.append("ANOMALY_PRESSURE_HIGH")
        if action.impact_scope >= 0.70:
            reasons.append("IMPACT_SCOPE_WIDE")
        if action.external_side_effect:
            reasons.append("EXTERNAL_SIDE_EFFECT")
        if action.sensitive_data:
            reasons.append("SENSITIVE_DATA")
        return reasons or ["RECOVERABILITY_ACCEPTABLE"]

    @staticmethod
    def _posture(action: RecoverabilityAction, scores: Dict[str, float]) -> RuntimePosture:
        exposure = scores["irreversible_exposure_score"]
        capacity = scores["reversible_capacity_score"]
        confidence = scores["confidence_score"]
        auth = scores["risk_adjusted_authorization_score"]
        stress = scores["operational_stress_score"]

        if exposure >= 0.78 and (capacity < 0.42 or confidence < 0.48):
            return RuntimePosture.DENY
        if action.cancel_reliability < 0.30 and exposure >= 0.62:
            return RuntimePosture.DENY
        if stress >= 0.70 and (action.external_side_effect or action.sensitive_data):
            return RuntimePosture.ESCALATE
        if confidence < 0.45 or capacity < 0.36:
            return RuntimePosture.FREEZE
        if auth < 0.62 or exposure >= 0.45 or action.external_side_effect:
            return RuntimePosture.THROTTLE
        return RuntimePosture.ALLOW

    @staticmethod
    def _enforcement_state(posture: RuntimePosture) -> EnforcementState:
        return {
            RuntimePosture.ALLOW: EnforcementState.RELEASE,
            RuntimePosture.THROTTLE: EnforcementState.CONSTRAIN,
            RuntimePosture.FREEZE: EnforcementState.PAUSE,
            RuntimePosture.DENY: EnforcementState.BLOCK,
            RuntimePosture.ESCALATE: EnforcementState.REVIEW,
        }[posture]

    @staticmethod
    def _controls(action: RecoverabilityAction, posture: RuntimePosture, scores: Dict[str, float]) -> List[str]:
        if posture == RuntimePosture.ALLOW:
            return ["execute", "record_replay", "retain_cancel_handle"]
        if posture == RuntimePosture.THROTTLE:
            controls = ["limit_scope", "preview_before_execution", "record_replay"]
            if action.rollback_latency >= 0.45:
                controls.append("require_rollback_plan")
            if action.external_side_effect:
                controls.append("rate_limit_external_side_effect")
            if scores["reversible_capacity_score"] < 0.60:
                controls.append("checkpoint_before_execution")
            return controls
        if posture == RuntimePosture.FREEZE:
            return ["pause_execution", "collect_more_evidence", "snapshot_current_state", "preserve_replay"]
        if posture == RuntimePosture.DENY:
            return ["block_execution", "explain_denial", "preserve_replay", "require_new_request"]
        return ["route_to_accountable_reviewer", "require_explicit_approval", "preserve_replay", "document_override_if_approved"]

    @staticmethod
    def _summary(
        action: RecoverabilityAction,
        posture: RuntimePosture,
        scores: Dict[str, float],
        controls: List[str],
    ) -> str:
        return (
            f"Action '{action.action_id}' received {posture.value}. "
            f"Irreversible exposure is {scores['irreversible_exposure_score']:.3f}, "
            f"reversible capacity is {scores['reversible_capacity_score']:.3f}, and "
            f"authorization score is {scores['risk_adjusted_authorization_score']:.3f}. "
            f"Controls: {', '.join(controls)}."
        )


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def evaluate_action(payload: Dict[str, Any] | RecoverabilityAction) -> Dict[str, Any]:
    return RecoverabilityEngine().evaluate(payload)


def evaluate_batch(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    engine = RecoverabilityEngine()
    return [engine.evaluate(item) for item in items]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate automated actions with the SMERC recoverability engine.")
    parser.add_argument("path", help="Path to a JSON action request or JSON list of requests.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    result = evaluate_batch(payload) if isinstance(payload, list) else evaluate_action(payload)
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

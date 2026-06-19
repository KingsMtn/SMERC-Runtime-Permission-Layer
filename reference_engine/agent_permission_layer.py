from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class PermissionPosture(str, Enum):
    ALLOW = "ALLOW"
    THROTTLE = "THROTTLE"
    FREEZE = "FREEZE"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class AgentActionRequest:
    action_id: str
    description: str
    tool: str
    actor: str
    confidence: float
    harm: float
    consent: float
    reversibility: float
    external_effect: bool
    sensitive_data: bool
    context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "AgentActionRequest":
        required = [
            "action_id",
            "description",
            "tool",
            "actor",
            "confidence",
            "harm",
            "consent",
            "reversibility",
            "external_effect",
            "sensitive_data",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Missing required action field(s): {', '.join(missing)}")

        for key in ["action_id", "description", "tool", "actor"]:
            if not isinstance(payload[key], str) or not payload[key].strip():
                raise TypeError(f"{key} must be a non-empty string")

        values: Dict[str, float] = {}
        for key in ["confidence", "harm", "consent", "reversibility"]:
            value = payload[key]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{key} must be a number between 0.0 and 1.0")
            if value < 0 or value > 1:
                raise ValueError(f"{key} must be between 0.0 and 1.0")
            values[key] = float(value)

        for key in ["external_effect", "sensitive_data"]:
            if not isinstance(payload[key], bool):
                raise TypeError(f"{key} must be a boolean")

        context = payload.get("context", {})
        if not isinstance(context, dict):
            raise TypeError("context must be an object when provided")

        return cls(
            action_id=payload["action_id"],
            description=payload["description"],
            tool=payload["tool"],
            actor=payload["actor"],
            confidence=values["confidence"],
            harm=values["harm"],
            consent=values["consent"],
            reversibility=values["reversibility"],
            external_effect=payload["external_effect"],
            sensitive_data=payload["sensitive_data"],
            context=context,
        )


@dataclass(frozen=True)
class PermissionDecision:
    posture: PermissionPosture
    risk_score: float
    confidence_score: float
    replay_id: str
    constraints: List[str]
    reason_codes: List[str]
    plain_english_summary: str
    replay: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "posture": self.posture.value,
            "risk_score": round(self.risk_score, 3),
            "confidence_score": round(self.confidence_score, 3),
            "replay_id": self.replay_id,
            "constraints": list(self.constraints),
            "reason_codes": list(self.reason_codes),
            "plain_english_summary": self.plain_english_summary,
            "replay": dict(self.replay),
        }


class RuntimePermissionEngine:
    """Runtime permission infrastructure for proposed AI-agent actions."""

    def evaluate(self, payload: Dict[str, Any] | AgentActionRequest) -> Dict[str, Any]:
        request = payload if isinstance(payload, AgentActionRequest) else AgentActionRequest.from_dict(payload)
        risk_score = self._risk_score(request)
        confidence_score = self._confidence_score(request)
        reason_codes = self._reason_codes(request, risk_score, confidence_score)
        posture = self._posture(request, risk_score, confidence_score)
        constraints = self._constraints(posture, request)
        replay_id = f"replay_{request.action_id}_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        summary = self._summary(request, posture, risk_score, constraints)
        replay = {
            "replay_id": replay_id,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "action_id": request.action_id,
            "actor": request.actor,
            "tool": request.tool,
            "posture": posture.value,
            "risk_score": round(risk_score, 3),
            "confidence_score": round(confidence_score, 3),
            "reason_codes": list(reason_codes),
            "constraints": list(constraints),
        }
        return PermissionDecision(
            posture=posture,
            risk_score=risk_score,
            confidence_score=confidence_score,
            replay_id=replay_id,
            constraints=constraints,
            reason_codes=reason_codes,
            plain_english_summary=summary,
            replay=replay,
        ).to_dict()

    @staticmethod
    def _risk_score(request: AgentActionRequest) -> float:
        confidence_risk = 1 - request.confidence
        consent_risk = 1 - request.consent
        irreversibility = 1 - request.reversibility
        risk = (
            request.harm * 0.36
            + confidence_risk * 0.17
            + consent_risk * 0.17
            + irreversibility * 0.18
            + (0.07 if request.external_effect else 0)
            + (0.05 if request.sensitive_data else 0)
        )
        return max(0.0, min(1.0, risk))

    @staticmethod
    def _confidence_score(request: AgentActionRequest) -> float:
        score = (
            request.confidence * 0.42
            + request.consent * 0.28
            + request.reversibility * 0.20
            + (1 - request.harm) * 0.10
        )
        return max(0.0, min(1.0, score))

    @staticmethod
    def _reason_codes(request: AgentActionRequest, risk_score: float, confidence_score: float) -> List[str]:
        reasons: List[str] = []
        if request.external_effect:
            reasons.append("EXTERNAL_SIDE_EFFECT")
        if request.sensitive_data:
            reasons.append("SENSITIVE_DATA_ACCESS")
        if request.harm >= 0.80:
            reasons.append("HIGH_HARM_POTENTIAL")
        elif request.harm >= 0.45:
            reasons.append("MODERATE_HARM_POTENTIAL")
        if request.confidence < 0.50:
            reasons.append("LOW_MODEL_CONFIDENCE")
        if request.consent < 0.50:
            reasons.append("CONSENT_OR_AUTHORIZATION_WEAK")
        if request.reversibility < 0.30:
            reasons.append("LOW_REVERSIBILITY")
        if risk_score >= 0.70:
            reasons.append("RISK_SCORE_HIGH")
        if confidence_score < 0.45:
            reasons.append("CONFIDENCE_SCORE_LOW")
        return reasons or ["LOW_RISK_REPLAYABLE_ACTION"]

    @staticmethod
    def _posture(
        request: AgentActionRequest,
        risk_score: float,
        confidence_score: float,
    ) -> PermissionPosture:
        if request.harm >= 0.90 and (request.consent < 0.45 or request.reversibility < 0.20):
            return PermissionPosture.DENY

        if request.harm >= 0.72 and request.external_effect and request.sensitive_data:
            return PermissionPosture.ESCALATE

        if confidence_score < 0.42 and (request.external_effect or request.sensitive_data):
            return PermissionPosture.FREEZE

        if risk_score >= 0.46 or request.external_effect:
            return PermissionPosture.THROTTLE

        return PermissionPosture.ALLOW

    @staticmethod
    def _constraints(posture: PermissionPosture, request: AgentActionRequest) -> List[str]:
        if posture == PermissionPosture.ALLOW:
            return ["execute", "log_replay"]
        if posture == PermissionPosture.THROTTLE:
            controls = ["limit_scope", "preview_before_execution", "log_replay"]
            if request.external_effect:
                controls.append("rate_limit_external_effect")
            if request.reversibility < 0.50:
                controls.append("require_recovery_path")
            return controls
        if posture == PermissionPosture.FREEZE:
            return ["pause_execution", "collect_more_context", "preserve_replay"]
        if posture == PermissionPosture.DENY:
            return ["reject_action", "preserve_replay", "explain_denial"]
        return ["route_to_human_review", "preserve_replay", "require_explicit_approval"]

    @staticmethod
    def _summary(
        request: AgentActionRequest,
        posture: PermissionPosture,
        risk_score: float,
        constraints: List[str],
    ) -> str:
        return (
            f"Action '{request.action_id}' by {request.actor} using {request.tool} received {posture.value}. "
            f"Risk score is {risk_score:.3f}. Constraints: {', '.join(constraints)}."
        )


def evaluate_action(payload: Dict[str, Any] | AgentActionRequest) -> Dict[str, Any]:
    return RuntimePermissionEngine().evaluate(payload)


def evaluate_batch(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    engine = RuntimePermissionEngine()
    return [engine.evaluate(item) for item in items]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate AI-agent actions with SMERC runtime permission postures.")
    parser.add_argument("path", help="Path to a JSON action request or JSON list of action requests.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    result = evaluate_batch(payload) if isinstance(payload, list) else evaluate_action(payload)
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()


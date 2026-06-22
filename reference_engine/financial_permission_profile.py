from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SIGNAL_WEIGHTS = {
    "liquidity_concentration": 0.14,
    "collateral_stress": 0.15,
    "settlement_anomaly": 0.13,
    "stablecoin_imbalance": 0.12,
    "counterparty_concentration": 0.12,
    "market_instability": 0.11,
    "model_disagreement": 0.10,
    "agent_velocity": 0.13,
}

DRIVER_CODES = {
    "liquidity_concentration": "LIQUIDITY_CONCENTRATION",
    "collateral_stress": "COLLATERAL_STRESS",
    "settlement_anomaly": "SETTLEMENT_ANOMALY",
    "stablecoin_imbalance": "STABLECOIN_IMBALANCE",
    "counterparty_concentration": "COUNTERPARTY_CONCENTRATION",
    "market_instability": "MARKET_INSTABILITY",
    "model_disagreement": "MODEL_DISAGREEMENT",
    "agent_velocity": "AGENT_VELOCITY",
}


@dataclass(frozen=True)
class FinancialActionRequest:
    action_id: str
    description: str
    action_type: str
    actor: str
    authorization_support: float
    evidence_validity: float
    reversibility: float
    liquidity_concentration: float
    collateral_stress: float
    settlement_anomaly: float
    stablecoin_imbalance: float
    counterparty_concentration: float
    market_instability: float
    model_disagreement: float
    agent_velocity: float

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "FinancialActionRequest":
        text_fields = ["action_id", "description", "action_type", "actor"]
        signal_fields = [
            "authorization_support",
            "evidence_validity",
            "reversibility",
            *SIGNAL_WEIGHTS.keys(),
        ]
        missing = [key for key in [*text_fields, *signal_fields] if key not in payload]
        if missing:
            raise ValueError(f"Missing required financial action field(s): {', '.join(missing)}")

        for key in text_fields:
            if not isinstance(payload[key], str) or not payload[key].strip():
                raise TypeError(f"{key} must be a non-empty string")

        values: Dict[str, float] = {}
        for key in signal_fields:
            value = payload[key]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{key} must be a number between 0.0 and 1.0")
            if value < 0 or value > 1:
                raise ValueError(f"{key} must be between 0.0 and 1.0")
            values[key] = float(value)

        return cls(
            action_id=payload["action_id"],
            description=payload["description"],
            action_type=payload["action_type"],
            actor=payload["actor"],
            **values,
        )


class FinancialPermissionProfile:
    """Reference SMERC profile for proposed autonomous-capital actions."""

    def evaluate(self, payload: Dict[str, Any] | FinancialActionRequest) -> Dict[str, Any]:
        request = payload if isinstance(payload, FinancialActionRequest) else FinancialActionRequest.from_dict(payload)
        signal_risk = self._signal_risk(request)
        confidence = self._confidence(request)
        irreversible_exposure = min(1.0, signal_risk * 0.62 + (1 - request.reversibility) * 0.38)
        reversible_capacity = min(
            1.0,
            request.reversibility * 0.60
            + request.evidence_validity * 0.24
            + request.authorization_support * 0.16,
        )

        drivers = self._drivers(request)
        state = self._state(request, signal_risk, confidence, irreversible_exposure)
        controls = self._controls(state)
        replay_id = f"smerc_f_{request.action_id}_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

        return {
            "profile": "SMERC-F",
            "state": state,
            "confidence": round(confidence, 3),
            "signal_risk": round(signal_risk, 3),
            "irreversible_exposure": round(irreversible_exposure, 3),
            "reversible_capacity": round(reversible_capacity, 3),
            "drivers": drivers,
            "controls": controls,
            "recommended_action": self._recommended_action(state),
            "replay_id": replay_id,
            "plain_english_summary": (
                f"Financial action '{request.action_id}' received {state}. "
                f"Irreversible exposure is {irreversible_exposure:.3f}; "
                f"reversible capacity is {reversible_capacity:.3f}."
            ),
        }

    @staticmethod
    def _signal_risk(request: FinancialActionRequest) -> float:
        return sum(getattr(request, key) * weight for key, weight in SIGNAL_WEIGHTS.items())

    @staticmethod
    def _confidence(request: FinancialActionRequest) -> float:
        return min(1.0, request.evidence_validity * 0.68 + (1 - request.model_disagreement) * 0.32)

    @staticmethod
    def _drivers(request: FinancialActionRequest) -> List[str]:
        ranked = sorted(
            ((key, getattr(request, key)) for key in SIGNAL_WEIGHTS),
            key=lambda item: item[1],
            reverse=True,
        )
        drivers = [DRIVER_CODES[key] for key, value in ranked if value >= 0.55]
        if request.authorization_support < 0.55:
            drivers.append("AUTHORIZATION_SUPPORT_WEAK")
        if request.evidence_validity < 0.55:
            drivers.append("EVIDENCE_VALIDITY_WEAK")
        if request.reversibility < 0.40:
            drivers.append("LOW_REVERSIBILITY")
        return drivers or ["LOW_STRESS_REPLAYABLE_ACTION"]

    @staticmethod
    def _state(
        request: FinancialActionRequest,
        signal_risk: float,
        confidence: float,
        irreversible_exposure: float,
    ) -> str:
        if request.authorization_support < 0.25:
            return "DENY"
        if irreversible_exposure >= 0.82 and request.reversibility < 0.25:
            return "DENY"
        if request.model_disagreement >= 0.75:
            return "FREEZE"
        if irreversible_exposure >= 0.68 and (confidence < 0.62 or request.reversibility < 0.45):
            return "FREEZE"
        if request.authorization_support < 0.60 or request.evidence_validity < 0.58:
            return "ESCALATE"
        if signal_risk >= 0.40 or request.agent_velocity >= 0.55:
            return "THROTTLE"
        return "ALLOW"

    @staticmethod
    def _controls(state: str) -> List[str]:
        return {
            "ALLOW": ["execute", "retain_reversal_path", "log_replay"],
            "THROTTLE": ["reduce_transaction_size", "lower_velocity", "require_dual_approval", "log_replay"],
            "FREEZE": ["pause_automation", "preserve_state", "secondary_validation", "supervisor_review"],
            "DENY": ["block_action", "emergency_escalation", "executive_override_required", "preserve_replay"],
            "ESCALATE": ["route_to_accountable_reviewer", "require_explicit_approval", "preserve_replay"],
        }[state]

    @staticmethod
    def _recommended_action(state: str) -> str:
        return {
            "ALLOW": "Proceed with normal monitoring and retain a reversal path.",
            "THROTTLE": "Reduce exposure and transaction velocity; require dual approval.",
            "FREEZE": "Pause financial automation pending secondary validation and supervisor review.",
            "DENY": "Block automated progression; require emergency escalation for any override.",
            "ESCALATE": "Route the proposed action to an accountable financial-risk reviewer.",
        }[state]


def evaluate_financial_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    return FinancialPermissionProfile().evaluate(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate proposed financial actions with the SMERC-F profile.")
    parser.add_argument("path", help="Path to a JSON financial action request or list of requests.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    profile = FinancialPermissionProfile()
    result = [profile.evaluate(item) for item in payload] if isinstance(payload, list) else profile.evaluate(payload)
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()


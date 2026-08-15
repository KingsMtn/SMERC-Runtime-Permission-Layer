from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List


class ExecutorPosture(str, Enum):
    ALLOW = "ALLOW"
    THROTTLE = "THROTTLE"
    FREEZE = "FREEZE"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


AUTHORITY_ORDER = {
    "recommend_only": 0,
    "read_only": 1,
    "write_limited": 2,
    "execute_external": 3,
    "admin": 4,
}

DATA_ORDER = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3,
}

TIER_SCORE = {
    "low": 1.0,
    "medium": 0.65,
    "high": 0.30,
}


@dataclass(frozen=True)
class ExecutorCandidate:
    executor_id: str
    display_name: str
    provider: str
    capabilities: List[str]
    allowed_data_classes: List[str]
    max_tool_authority: str
    cost_tier: str
    latency_tier: str
    reliability_score: float
    domain_fit: float
    safety_history: float
    tool_reliability: float
    data_boundary_score: float
    context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ExecutorCandidate":
        required = [
            "executor_id",
            "display_name",
            "provider",
            "capabilities",
            "allowed_data_classes",
            "max_tool_authority",
            "cost_tier",
            "latency_tier",
            "reliability_score",
            "domain_fit",
            "safety_history",
            "tool_reliability",
            "data_boundary_score",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Missing required executor field(s): {', '.join(missing)}")

        for key in ["executor_id", "display_name", "provider", "max_tool_authority", "cost_tier", "latency_tier"]:
            if not isinstance(payload[key], str) or not payload[key].strip():
                raise TypeError(f"{key} must be a non-empty string")

        if payload["max_tool_authority"] not in AUTHORITY_ORDER:
            raise ValueError(f"max_tool_authority must be one of: {', '.join(AUTHORITY_ORDER)}")

        for key in ["cost_tier", "latency_tier"]:
            if payload[key] not in TIER_SCORE:
                raise ValueError(f"{key} must be one of: {', '.join(TIER_SCORE)}")

        for key in ["capabilities", "allowed_data_classes"]:
            values = payload[key]
            if not isinstance(values, list) or not all(isinstance(item, str) and item.strip() for item in values):
                raise TypeError(f"{key} must be a list of non-empty strings")

        for data_class in payload["allowed_data_classes"]:
            if data_class not in DATA_ORDER:
                raise ValueError(f"allowed_data_classes contains unsupported class: {data_class}")

        scores: Dict[str, float] = {}
        for key in ["reliability_score", "domain_fit", "safety_history", "tool_reliability", "data_boundary_score"]:
            scores[key] = _bounded_float(payload[key], key)

        context = payload.get("context", {})
        if not isinstance(context, dict):
            raise TypeError("context must be an object when provided")

        return cls(
            executor_id=payload["executor_id"],
            display_name=payload["display_name"],
            provider=payload["provider"],
            capabilities=list(payload["capabilities"]),
            allowed_data_classes=list(payload["allowed_data_classes"]),
            max_tool_authority=payload["max_tool_authority"],
            cost_tier=payload["cost_tier"],
            latency_tier=payload["latency_tier"],
            reliability_score=scores["reliability_score"],
            domain_fit=scores["domain_fit"],
            safety_history=scores["safety_history"],
            tool_reliability=scores["tool_reliability"],
            data_boundary_score=scores["data_boundary_score"],
            context=context,
        )


@dataclass(frozen=True)
class ExecutorSelectionRequest:
    task_id: str
    description: str
    task_type: str
    required_capabilities: List[str]
    risk_level: float
    reversibility: float
    evidence_validity: float
    data_sensitivity: str
    required_tool_authority: str
    latency_requirement: str
    cost_sensitivity: str
    impact_scope: float
    anomaly_pressure: float
    candidates: List[ExecutorCandidate]
    context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ExecutorSelectionRequest":
        required = [
            "task_id",
            "description",
            "task_type",
            "required_capabilities",
            "risk_level",
            "reversibility",
            "evidence_validity",
            "data_sensitivity",
            "required_tool_authority",
            "latency_requirement",
            "cost_sensitivity",
            "impact_scope",
            "anomaly_pressure",
            "candidates",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Missing required model fitness field(s): {', '.join(missing)}")

        for key in ["task_id", "description", "task_type", "data_sensitivity", "required_tool_authority", "latency_requirement", "cost_sensitivity"]:
            if not isinstance(payload[key], str) or not payload[key].strip():
                raise TypeError(f"{key} must be a non-empty string")

        if payload["data_sensitivity"] not in DATA_ORDER:
            raise ValueError(f"data_sensitivity must be one of: {', '.join(DATA_ORDER)}")
        if payload["required_tool_authority"] not in AUTHORITY_ORDER:
            raise ValueError(f"required_tool_authority must be one of: {', '.join(AUTHORITY_ORDER)}")
        for key in ["latency_requirement", "cost_sensitivity"]:
            if payload[key] not in TIER_SCORE:
                raise ValueError(f"{key} must be one of: {', '.join(TIER_SCORE)}")

        capabilities = payload["required_capabilities"]
        if not isinstance(capabilities, list) or not all(isinstance(item, str) and item.strip() for item in capabilities):
            raise TypeError("required_capabilities must be a list of non-empty strings")

        candidates_payload = payload["candidates"]
        if not isinstance(candidates_payload, list):
            raise TypeError("candidates must be a list")

        context = payload.get("context", {})
        if not isinstance(context, dict):
            raise TypeError("context must be an object when provided")

        return cls(
            task_id=payload["task_id"],
            description=payload["description"],
            task_type=payload["task_type"],
            required_capabilities=list(capabilities),
            risk_level=_bounded_float(payload["risk_level"], "risk_level"),
            reversibility=_bounded_float(payload["reversibility"], "reversibility"),
            evidence_validity=_bounded_float(payload["evidence_validity"], "evidence_validity"),
            data_sensitivity=payload["data_sensitivity"],
            required_tool_authority=payload["required_tool_authority"],
            latency_requirement=payload["latency_requirement"],
            cost_sensitivity=payload["cost_sensitivity"],
            impact_scope=_bounded_float(payload["impact_scope"], "impact_scope"),
            anomaly_pressure=_bounded_float(payload["anomaly_pressure"], "anomaly_pressure"),
            candidates=[ExecutorCandidate.from_dict(candidate) for candidate in candidates_payload],
            context=context,
        )


class ModelFitnessEngine:
    """Selects the safest qualified model or agent executor for a proposed action."""

    def evaluate(self, payload: Dict[str, Any] | ExecutorSelectionRequest) -> Dict[str, Any]:
        request = payload if isinstance(payload, ExecutorSelectionRequest) else ExecutorSelectionRequest.from_dict(payload)
        evaluated = [self._candidate_record(request, candidate) for candidate in request.candidates]
        evaluated.sort(key=lambda item: item["scores"]["model_fitness_score"], reverse=True)

        qualified = [item for item in evaluated if not item["blocking_reasons"]]
        best = qualified[0] if qualified else None
        posture = self._posture(request, best, evaluated)
        controls = self._controls(request, posture, best)
        reason_codes = self._reason_codes(request, posture, best, evaluated)
        replay_id = f"model_route_{request.task_id}_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

        allowed = [item["executor_id"] for item in evaluated if not item["blocking_reasons"] and item["scores"]["model_fitness_score"] >= 0.55]
        blocked = [item["executor_id"] for item in evaluated if item["blocking_reasons"]]

        return {
            "task_id": request.task_id,
            "recommended_executor": best["executor_id"] if best else None,
            "allowed_executors": allowed,
            "blocked_executors": blocked,
            "execution_posture": posture.value,
            "reason_codes": reason_codes,
            "controls": controls,
            "candidate_rankings": evaluated,
            "plain_english_summary": self._summary(request, posture, best),
            "replay_id": replay_id,
            "replay": {
                "replay_id": replay_id,
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "task_id": request.task_id,
                "task_type": request.task_type,
                "data_sensitivity": request.data_sensitivity,
                "required_tool_authority": request.required_tool_authority,
                "execution_posture": posture.value,
                "recommended_executor": best["executor_id"] if best else None,
                "reason_codes": reason_codes,
                "controls": controls,
                "candidate_rankings": evaluated,
                "context": request.context,
            },
        }

    @staticmethod
    def _candidate_record(request: ExecutorSelectionRequest, candidate: ExecutorCandidate) -> Dict[str, Any]:
        required = set(request.required_capabilities)
        available = set(candidate.capabilities)
        capability_coverage = 1.0 if not required else len(required.intersection(available)) / len(required)
        task_fit = clamp(capability_coverage * 0.62 + candidate.domain_fit * 0.38)

        authority_fit = 1.0 if AUTHORITY_ORDER[candidate.max_tool_authority] >= AUTHORITY_ORDER[request.required_tool_authority] else 0.0
        data_fit = 1.0 if DATA_ORDER[request.data_sensitivity] <= max(DATA_ORDER[item] for item in candidate.allowed_data_classes) else 0.0
        data_boundary_fit = clamp(data_fit * 0.60 + candidate.data_boundary_score * 0.40)
        recoverability_fit = clamp(request.reversibility * 0.55 + candidate.tool_reliability * 0.25 + candidate.safety_history * 0.20)
        reliability_fit = clamp(candidate.reliability_score * 0.45 + candidate.safety_history * 0.35 + request.evidence_validity * 0.20)
        cost_fit = TIER_SCORE[candidate.cost_tier] if request.cost_sensitivity == "high" else 0.70 + (TIER_SCORE[candidate.cost_tier] * 0.30)
        latency_fit = TIER_SCORE[candidate.latency_tier] if request.latency_requirement == "high" else 0.70 + (TIER_SCORE[candidate.latency_tier] * 0.30)

        risk_pressure = clamp(request.risk_level * 0.35 + request.impact_scope * 0.30 + request.anomaly_pressure * 0.20 + (1 - request.reversibility) * 0.15)
        model_fitness_score = clamp(
            task_fit * 0.24
            + authority_fit * 0.17
            + data_boundary_fit * 0.17
            + recoverability_fit * 0.16
            + reliability_fit * 0.16
            + cost_fit * 0.05
            + latency_fit * 0.05
        )
        risk_adjusted_executor_score = clamp(model_fitness_score * (1 - (risk_pressure * 0.35)))

        blocking_reasons: List[str] = []
        if authority_fit == 0:
            blocking_reasons.append("INSUFFICIENT_TOOL_AUTHORITY")
        if data_fit == 0:
            blocking_reasons.append("DATA_BOUNDARY_EXCEEDED")
        if capability_coverage < 0.65:
            blocking_reasons.append("REQUIRED_CAPABILITY_GAP")
        if request.risk_level >= 0.75 and candidate.safety_history < 0.60:
            blocking_reasons.append("SAFETY_HISTORY_TOO_WEAK_FOR_RISK")

        return {
            "executor_id": candidate.executor_id,
            "display_name": candidate.display_name,
            "provider": candidate.provider,
            "scores": {
                "task_fit": round(task_fit, 3),
                "authority_fit": round(authority_fit, 3),
                "data_boundary_fit": round(data_boundary_fit, 3),
                "recoverability_fit": round(recoverability_fit, 3),
                "reliability_fit": round(reliability_fit, 3),
                "cost_fit": round(cost_fit, 3),
                "latency_fit": round(latency_fit, 3),
                "risk_pressure": round(risk_pressure, 3),
                "model_fitness_score": round(model_fitness_score, 3),
                "risk_adjusted_executor_score": round(risk_adjusted_executor_score, 3),
            },
            "blocking_reasons": blocking_reasons,
        }

    @staticmethod
    def _posture(
        request: ExecutorSelectionRequest,
        best: Dict[str, Any] | None,
        evaluated: List[Dict[str, Any]],
    ) -> ExecutorPosture:
        if not evaluated:
            return ExecutorPosture.ESCALATE
        if best is None:
            if request.risk_level >= 0.70 or request.data_sensitivity == "restricted":
                return ExecutorPosture.DENY
            return ExecutorPosture.FREEZE

        score = best["scores"]["risk_adjusted_executor_score"]
        if request.anomaly_pressure >= 0.80 and request.impact_scope >= 0.60:
            return ExecutorPosture.FREEZE
        if score >= 0.76 and request.risk_level < 0.55 and request.impact_scope < 0.60:
            return ExecutorPosture.ALLOW
        if score >= 0.56:
            return ExecutorPosture.THROTTLE
        if request.risk_level >= 0.70:
            return ExecutorPosture.ESCALATE
        return ExecutorPosture.FREEZE

    @staticmethod
    def _controls(
        request: ExecutorSelectionRequest,
        posture: ExecutorPosture,
        best: Dict[str, Any] | None,
    ) -> List[str]:
        if best is None:
            return ["do_not_execute", "route_to_human_owner", "record_executor_gap"]
        if posture == ExecutorPosture.ALLOW:
            return ["route_to_selected_executor", "record_model_route", "retain_replay_record"]
        if posture == ExecutorPosture.THROTTLE:
            controls = ["route_to_selected_executor", "limit_tool_scope", "require_preview_before_execution", "retain_replay_record"]
            if request.risk_level >= 0.55 or request.data_sensitivity in {"confidential", "restricted"}:
                controls.append("require_human_approval_before_external_effect")
            return controls
        if posture == ExecutorPosture.FREEZE:
            return ["pause_execution", "request_additional_evidence", "recompute_executor_ranking", "retain_replay_record"]
        if posture == ExecutorPosture.DENY:
            return ["block_executor_assignment", "document_unqualified_executor_set", "require_new_candidate_or_lower_authority"]
        return ["escalate_to_system_owner", "require_security_review", "retain_replay_record"]

    @staticmethod
    def _reason_codes(
        request: ExecutorSelectionRequest,
        posture: ExecutorPosture,
        best: Dict[str, Any] | None,
        evaluated: List[Dict[str, Any]],
    ) -> List[str]:
        reasons: List[str] = []
        if best is None:
            missing = sorted({reason for item in evaluated for reason in item["blocking_reasons"]})
            return missing or ["NO_EXECUTOR_CANDIDATES"]
        if request.data_sensitivity in {"confidential", "restricted"}:
            reasons.append("SENSITIVE_DATA_ROUTING")
        if request.required_tool_authority in {"execute_external", "admin"}:
            reasons.append("HIGH_TOOL_AUTHORITY")
        if request.risk_level >= 0.65:
            reasons.append("HIGH_TASK_RISK")
        if request.reversibility < 0.45:
            reasons.append("LOW_RECOVERABILITY")
        if request.evidence_validity < 0.60:
            reasons.append("INCOMPLETE_EVIDENCE")
        if posture == ExecutorPosture.THROTTLE:
            reasons.append("QUALIFIED_EXECUTOR_WITH_CONTROLS")
        elif posture == ExecutorPosture.ALLOW:
            reasons.append("QUALIFIED_LOW_RISK_EXECUTOR")
        elif posture == ExecutorPosture.FREEZE:
            reasons.append("EXECUTOR_SELECTION_PAUSED")
        elif posture == ExecutorPosture.ESCALATE:
            reasons.append("OWNER_REVIEW_REQUIRED")
        return reasons or ["QUALIFIED_EXECUTOR_SELECTED"]

    @staticmethod
    def _summary(
        request: ExecutorSelectionRequest,
        posture: ExecutorPosture,
        best: Dict[str, Any] | None,
    ) -> str:
        if best is None:
            return (
                f"No candidate executor is qualified for '{request.description}' under the requested "
                f"data sensitivity and tool authority. SMERC recommends {posture.value}."
            )
        return (
            f"SMERC recommends {best['display_name']} for '{request.description}' with posture "
            f"{posture.value}. The route is based on task fit, data boundaries, tool authority, "
            "recoverability, reliability history, cost, and latency."
        )


def evaluate_batch(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    engine = ModelFitnessEngine()
    return [engine.evaluate(record) for record in records]


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _bounded_float(value: Any, field_name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{field_name} must be a number between 0.0 and 1.0")
    if value < 0 or value > 1:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0")
    return float(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate SMERC model and agent fitness routing.")
    parser.add_argument("input", type=Path, help="JSON file containing one request object or a list of requests")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    engine = ModelFitnessEngine()
    result = evaluate_batch(payload) if isinstance(payload, list) else engine.evaluate(payload)
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

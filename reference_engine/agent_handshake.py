from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from reference_engine.beacon import validate_beacon
from reference_engine.model_fitness import AUTHORITY_ORDER, DATA_ORDER, ModelFitnessEngine
from reference_engine.recoverability_engine import RecoverabilityEngine


HANDSHAKE_VERSION = "smerc.agent_handshake.v1"


@dataclass(frozen=True)
class AgentDeclaration:
    agent_id: str
    display_name: str
    provider: str
    capabilities: List[str]
    requested_tool_authority: str
    requested_data_access: List[str]
    callback_url: str | None = None
    context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "AgentDeclaration":
        required = [
            "agent_id",
            "display_name",
            "provider",
            "capabilities",
            "requested_tool_authority",
            "requested_data_access",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Missing required agent declaration field(s): {', '.join(missing)}")

        for key in ["agent_id", "display_name", "provider", "requested_tool_authority"]:
            _require_non_empty_string(payload[key], key)
        if payload["requested_tool_authority"] not in AUTHORITY_ORDER:
            raise ValueError(f"requested_tool_authority must be one of: {', '.join(AUTHORITY_ORDER)}")

        capabilities = _string_list(payload["capabilities"], "capabilities", min_items=1)
        requested_data_access = _string_list(payload["requested_data_access"], "requested_data_access", min_items=1)
        for item in requested_data_access:
            if item not in DATA_ORDER:
                raise ValueError(f"requested_data_access contains unsupported data class: {item}")

        callback_url = payload.get("callback_url")
        if callback_url is not None:
            _require_non_empty_string(callback_url, "callback_url")
            if not callback_url.startswith("https://"):
                raise ValueError("callback_url must be an https URL when provided")

        context = payload.get("context", {})
        if not isinstance(context, dict):
            raise TypeError("context must be an object when provided")

        return cls(
            agent_id=payload["agent_id"],
            display_name=payload["display_name"],
            provider=payload["provider"],
            capabilities=capabilities,
            requested_tool_authority=payload["requested_tool_authority"],
            requested_data_access=requested_data_access,
            callback_url=callback_url,
            context=context,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "provider": self.provider,
            "capabilities": list(self.capabilities),
            "requested_tool_authority": self.requested_tool_authority,
            "requested_data_access": list(self.requested_data_access),
            "callback_url": self.callback_url,
            "context": dict(self.context),
        }


@dataclass(frozen=True)
class AgentHandshakeRequest:
    handshake_id: str
    beacon: Dict[str, Any]
    agent: AgentDeclaration
    task_route: Dict[str, Any]
    action_request: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "AgentHandshakeRequest":
        if not isinstance(payload, dict):
            raise TypeError("handshake request must be an object")
        if payload.get("schema_version") != HANDSHAKE_VERSION:
            raise ValueError(f"schema_version must be {HANDSHAKE_VERSION}")
        required = ["handshake_id", "beacon", "agent", "task_route", "action_request"]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Missing required handshake field(s): {', '.join(missing)}")
        _require_non_empty_string(payload["handshake_id"], "handshake_id")
        if not isinstance(payload["beacon"], dict):
            raise TypeError("beacon must be an object")
        if not isinstance(payload["task_route"], dict):
            raise TypeError("task_route must be an object")
        if not isinstance(payload["action_request"], dict):
            raise TypeError("action_request must be an object")
        context = payload.get("context", {})
        if not isinstance(context, dict):
            raise TypeError("context must be an object when provided")
        return cls(
            handshake_id=payload["handshake_id"],
            beacon=payload["beacon"],
            agent=AgentDeclaration.from_dict(payload["agent"]),
            task_route=dict(payload["task_route"]),
            action_request=dict(payload["action_request"]),
            context=context,
        )


class AgentHandshakeEngine:
    """Connects beacon discovery, executor fitness, and action posture evaluation."""

    def __init__(
        self,
        fitness_engine: ModelFitnessEngine | None = None,
        recoverability_engine: RecoverabilityEngine | None = None,
    ) -> None:
        self.fitness_engine = fitness_engine or ModelFitnessEngine()
        self.recoverability_engine = recoverability_engine or RecoverabilityEngine()

    def evaluate(self, payload: Dict[str, Any] | AgentHandshakeRequest) -> Dict[str, Any]:
        request = payload if isinstance(payload, AgentHandshakeRequest) else AgentHandshakeRequest.from_dict(payload)
        beacon_summary = validate_beacon(request.beacon)
        agent_issues = self._agent_issues(request)
        fitness_result = self.fitness_engine.evaluate(request.task_route)
        action_result = self.recoverability_engine.evaluate(request.action_request)
        posture = self._combined_posture(agent_issues, fitness_result, action_result)
        controls = self._combined_controls(agent_issues, fitness_result, action_result)
        reason_codes = self._combined_reasons(agent_issues, fitness_result, action_result)
        replay_id = f"handshake_{request.handshake_id}_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{uuid4().hex[:10]}"

        return {
            "schema_version": HANDSHAKE_VERSION,
            "handshake_id": request.handshake_id,
            "handshake_posture": posture,
            "agent_id": request.agent.agent_id,
            "beacon_valid": beacon_summary["valid"],
            "agent_issues": agent_issues,
            "recommended_executor": fitness_result["recommended_executor"],
            "executor_posture": fitness_result["execution_posture"],
            "action_posture": action_result["posture"],
            "reason_codes": reason_codes,
            "controls": controls,
            "fitness": fitness_result,
            "action_evaluation": action_result,
            "plain_english_summary": self._summary(request, posture, fitness_result, action_result, agent_issues),
            "replay_id": replay_id,
            "replay": {
                "replay_id": replay_id,
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "schema_version": HANDSHAKE_VERSION,
                "handshake_id": request.handshake_id,
                "agent": request.agent.to_dict(),
                "beacon": beacon_summary,
                "handshake_posture": posture,
                "recommended_executor": fitness_result["recommended_executor"],
                "executor_posture": fitness_result["execution_posture"],
                "action_posture": action_result["posture"],
                "reason_codes": reason_codes,
                "controls": controls,
                "fitness_replay_id": fitness_result["replay_id"],
                "action_replay_id": action_result["replay_id"],
                "context": request.context,
            },
        }

    @staticmethod
    def _agent_issues(request: AgentHandshakeRequest) -> List[str]:
        issues: List[str] = []
        required = set(request.task_route.get("required_capabilities", []))
        declared = set(request.agent.capabilities)
        if required and len(required.intersection(declared)) / len(required) < 0.65:
            issues.append("AGENT_DECLARED_CAPABILITY_GAP")

        required_authority = request.task_route.get("required_tool_authority")
        if required_authority in AUTHORITY_ORDER:
            if AUTHORITY_ORDER[request.agent.requested_tool_authority] < AUTHORITY_ORDER[required_authority]:
                issues.append("AGENT_REQUESTED_AUTHORITY_TOO_LOW")
        else:
            issues.append("TASK_ROUTE_AUTHORITY_UNKNOWN")

        data_sensitivity = request.task_route.get("data_sensitivity")
        if data_sensitivity in DATA_ORDER:
            max_agent_data = max(DATA_ORDER[item] for item in request.agent.requested_data_access)
            if DATA_ORDER[data_sensitivity] > max_agent_data:
                issues.append("AGENT_DATA_ACCESS_TOO_NARROW")
        else:
            issues.append("TASK_ROUTE_DATA_CLASS_UNKNOWN")

        return issues

    @staticmethod
    def _combined_posture(
        agent_issues: List[str],
        fitness_result: Dict[str, Any],
        action_result: Dict[str, Any],
    ) -> str:
        if "DATA_BOUNDARY_EXCEEDED" in fitness_result["reason_codes"]:
            return "DENY"
        if agent_issues:
            return "FREEZE"
        postures = [fitness_result["execution_posture"], action_result["posture"]]
        severity = {"ALLOW": 0, "THROTTLE": 1, "FREEZE": 2, "ESCALATE": 3, "DENY": 4}
        return max(postures, key=lambda item: severity[item])

    @staticmethod
    def _combined_controls(
        agent_issues: List[str],
        fitness_result: Dict[str, Any],
        action_result: Dict[str, Any],
    ) -> List[str]:
        controls = ["record_agent_handshake", "retain_replay_record"]
        controls.extend(fitness_result.get("controls", []))
        controls.extend(action_result.get("controls", []))
        if agent_issues:
            controls.extend(["pause_agent_execution", "resolve_agent_declaration"])
        deduped: List[str] = []
        for control in controls:
            if control not in deduped:
                deduped.append(control)
        return deduped

    @staticmethod
    def _combined_reasons(
        agent_issues: List[str],
        fitness_result: Dict[str, Any],
        action_result: Dict[str, Any],
    ) -> List[str]:
        reasons = ["BEACON_VALIDATED", "AGENT_HANDSHAKE_EVALUATED"]
        reasons.extend(agent_issues)
        reasons.extend(fitness_result.get("reason_codes", []))
        reasons.extend(action_result.get("reason_codes", []))
        deduped: List[str] = []
        for reason in reasons:
            if reason not in deduped:
                deduped.append(reason)
        return deduped

    @staticmethod
    def _summary(
        request: AgentHandshakeRequest,
        posture: str,
        fitness_result: Dict[str, Any],
        action_result: Dict[str, Any],
        agent_issues: List[str],
    ) -> str:
        if agent_issues:
            return (
                f"SMERC validated the beacon but froze the handshake for agent {request.agent.agent_id} "
                f"because the declaration has unresolved issue(s): {', '.join(agent_issues)}."
            )
        return (
            f"SMERC validated the beacon, evaluated agent {request.agent.agent_id}, selected "
            f"{fitness_result['recommended_executor']}, and returned handshake posture {posture}. "
            f"The underlying action posture is {action_result['posture']}."
        )


def _require_non_empty_string(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{field_name} must be a non-empty string")


def _string_list(value: Any, field_name: str, min_items: int) -> List[str]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list")
    if len(value) < min_items:
        raise ValueError(f"{field_name} must contain at least {min_items} item(s)")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise TypeError(f"{field_name} must contain only non-empty strings")
    return list(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a SMERC agent handshake request.")
    parser.add_argument("input", type=Path, help="Path to a smerc.agent_handshake.v1 JSON request")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = AgentHandshakeEngine().evaluate(payload)
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

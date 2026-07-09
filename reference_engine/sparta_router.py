from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping
from uuid import uuid4


SPARTA_PLAN_VERSION = "smerc.sparta-plan.v1"
SPARTA_ROUTE_VERSION = "smerc.sparta-route.v1"
SUPPORTED_POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}
SIDE_EFFECT_LEVELS = {"none", "internal", "external", "financial", "destructive"}

PLAN_FIELDS = {
    "version",
    "plan_id",
    "tool",
    "action",
    "requested_capability",
    "supports_dry_run",
    "supports_scope_limit",
    "supports_checkpoint",
    "supports_rollback",
    "supports_human_approval",
    "max_scope_units",
    "requested_scope_units",
    "side_effect_level",
    "metadata",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _strict_object(value: Any, fields: set[str], path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    missing = sorted(fields - set(value))
    if missing:
        raise ValueError(f"{path} is missing required field(s): {', '.join(missing)}")
    unknown = sorted(set(value) - fields)
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")
    return dict(value)


def _identifier(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,%d}" % (maximum - 1), value):
        raise ValueError(f"{path} must be a safe identifier of 1 to {maximum} characters")
    return value


def _text(value: Any, path: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value.strip()


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _positive_int(value: Any, path: str, maximum: int = 1_000_000) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if value < 1 or value > maximum:
        raise ValueError(f"{path} must be between 1 and {maximum}")
    return value


def _metadata(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("metadata must be an object")
    encoded = _canonical_json(value)
    if len(encoded.encode("utf-8")) > 4096:
        raise ValueError("metadata must be no larger than 4096 bytes")
    return dict(value)


def _decision_controls(decision: Mapping[str, Any]) -> list[str]:
    controls = decision.get("controls", [])
    if controls is None:
        return []
    if not isinstance(controls, list) or any(not isinstance(item, str) for item in controls):
        raise TypeError("decision.controls must be a list of strings when provided")
    return sorted(set(controls))


def _decision_digest(decision: Mapping[str, Any]) -> str:
    selected = {
        "posture": decision.get("posture"),
        "replay_id": decision.get("replay_id"),
        "reason_codes": decision.get("reason_codes", []),
        "controls": decision.get("controls", []),
        "policy": decision.get("policy", {}),
    }
    return hashlib.sha256(_canonical_json(selected).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ToolPlan:
    plan_id: str
    tool: str
    action: str
    requested_capability: str
    supports_dry_run: bool
    supports_scope_limit: bool
    supports_checkpoint: bool
    supports_rollback: bool
    supports_human_approval: bool
    max_scope_units: int
    requested_scope_units: int
    side_effect_level: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ToolPlan":
        plan = _strict_object(dict(payload), PLAN_FIELDS, "plan")
        if plan["version"] != SPARTA_PLAN_VERSION:
            raise ValueError(f"plan.version must be {SPARTA_PLAN_VERSION}")
        side_effect_level = _text(plan["side_effect_level"], "plan.side_effect_level", 32)
        if side_effect_level not in SIDE_EFFECT_LEVELS:
            raise ValueError(f"plan.side_effect_level must be one of {', '.join(sorted(SIDE_EFFECT_LEVELS))}")
        max_scope_units = _positive_int(plan["max_scope_units"], "plan.max_scope_units")
        requested_scope_units = _positive_int(plan["requested_scope_units"], "plan.requested_scope_units")
        if requested_scope_units > max_scope_units:
            raise ValueError("plan.requested_scope_units cannot exceed plan.max_scope_units")
        return cls(
            plan_id=_identifier(plan["plan_id"], "plan.plan_id"),
            tool=_identifier(plan["tool"], "plan.tool"),
            action=_identifier(plan["action"], "plan.action"),
            requested_capability=_identifier(plan["requested_capability"], "plan.requested_capability"),
            supports_dry_run=_boolean(plan["supports_dry_run"], "plan.supports_dry_run"),
            supports_scope_limit=_boolean(plan["supports_scope_limit"], "plan.supports_scope_limit"),
            supports_checkpoint=_boolean(plan["supports_checkpoint"], "plan.supports_checkpoint"),
            supports_rollback=_boolean(plan["supports_rollback"], "plan.supports_rollback"),
            supports_human_approval=_boolean(plan["supports_human_approval"], "plan.supports_human_approval"),
            max_scope_units=max_scope_units,
            requested_scope_units=requested_scope_units,
            side_effect_level=side_effect_level,
            metadata=_metadata(plan["metadata"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": SPARTA_PLAN_VERSION,
            "plan_id": self.plan_id,
            "tool": self.tool,
            "action": self.action,
            "requested_capability": self.requested_capability,
            "supports_dry_run": self.supports_dry_run,
            "supports_scope_limit": self.supports_scope_limit,
            "supports_checkpoint": self.supports_checkpoint,
            "supports_rollback": self.supports_rollback,
            "supports_human_approval": self.supports_human_approval,
            "max_scope_units": self.max_scope_units,
            "requested_scope_units": self.requested_scope_units,
            "side_effect_level": self.side_effect_level,
            "metadata": dict(self.metadata),
        }


class SPARTaRouter:
    """Route one SMERC decision into an execution posture for one declared tool plan."""

    def route(self, decision: Mapping[str, Any], plan: ToolPlan | Mapping[str, Any]) -> Dict[str, Any]:
        parsed_plan = plan if isinstance(plan, ToolPlan) else ToolPlan.from_dict(plan)
        posture = decision.get("posture")
        if posture not in SUPPORTED_POSTURES:
            raise ValueError(f"decision.posture must be one of {', '.join(sorted(SUPPORTED_POSTURES))}")
        replay_id = _identifier(decision.get("replay_id"), "decision.replay_id", 192)
        controls = _decision_controls(decision)

        routed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        route_id = f"sparta_{parsed_plan.plan_id}_{uuid4().hex[:12]}"
        route = self._route_for_posture(posture, controls, parsed_plan)
        return {
            "version": SPARTA_ROUTE_VERSION,
            "route_id": route_id,
            "routed_at": routed_at,
            "plan_id": parsed_plan.plan_id,
            "decision_replay_id": replay_id,
            "decision_digest": _decision_digest(decision),
            "source_posture": posture,
            "route_state": route["route_state"],
            "executable": route["executable"],
            "effective_scope_units": route["effective_scope_units"],
            "applied_controls": route["applied_controls"],
            "blocked_controls": route["blocked_controls"],
            "reason_codes": route["reason_codes"],
            "plain_english_summary": route["plain_english_summary"],
            "recommended_next_action": route["recommended_next_action"],
            "tool_plan": parsed_plan.to_dict(),
        }

    def _route_for_posture(self, posture: str, controls: list[str], plan: ToolPlan) -> Dict[str, Any]:
        if posture == "ALLOW":
            return self._allow_route(plan)
        if posture == "THROTTLE":
            return self._throttle_route(controls, plan)
        if posture == "FREEZE":
            return self._freeze_route(plan)
        if posture == "DENY":
            return self._deny_route(plan)
        return self._escalate_route(plan)

    def _allow_route(self, plan: ToolPlan) -> Dict[str, Any]:
        applied = ["execute", "record_execution_report"]
        if plan.supports_checkpoint and plan.side_effect_level in {"external", "financial", "destructive"}:
            applied.append("checkpoint_before_execution")
        return {
            "route_state": "EXECUTE",
            "executable": True,
            "effective_scope_units": plan.requested_scope_units,
            "applied_controls": applied,
            "blocked_controls": [],
            "reason_codes": ["SPARTA_ALLOW_DIRECT_EXECUTION"],
            "plain_english_summary": "SPARTa routed the action for execution because SMERC allowed it and the declared plan can preserve an execution report.",
            "recommended_next_action": "Execute through the configured adapter and retain the route report with the SMERC replay.",
        }

    def _throttle_route(self, controls: list[str], plan: ToolPlan) -> Dict[str, Any]:
        required_features = []
        if "limit_scope" in controls or plan.side_effect_level in {"external", "financial", "destructive"}:
            required_features.append(("scope_limit", plan.supports_scope_limit))
        if "preview_before_execution" in controls:
            required_features.append(("dry_run", plan.supports_dry_run))
        if "checkpoint_before_execution" in controls or "require_rollback_plan" in controls:
            required_features.append(("checkpoint_or_rollback", plan.supports_checkpoint or plan.supports_rollback))
        unsupported = [name for name, supported in required_features if not supported]
        if unsupported:
            return {
                "route_state": "REVIEW_REQUIRED",
                "executable": False,
                "effective_scope_units": 0,
                "applied_controls": ["record_execution_report", "preserve_replay"],
                "blocked_controls": unsupported,
                "reason_codes": ["SPARTA_CANNOT_CONSTRAIN_TOOL"],
                "plain_english_summary": "SMERC throttled the action, but the declared tool plan cannot apply the required native constraints.",
                "recommended_next_action": "Route to a reviewer or replace the tool plan with one that supports scope limits, dry runs, checkpoints, or rollback.",
            }

        effective_scope = plan.requested_scope_units
        applied = ["record_execution_report", "preserve_replay"]
        if plan.supports_scope_limit:
            effective_scope = min(plan.requested_scope_units, max(1, math.ceil(plan.max_scope_units * 0.25)))
            applied.append("limit_scope")
        if plan.supports_dry_run:
            applied.append("preview_before_execution")
        if plan.supports_checkpoint:
            applied.append("checkpoint_before_execution")
        if plan.supports_rollback:
            applied.append("require_rollback_plan")
        return {
            "route_state": "CONSTRAINED_EXECUTE",
            "executable": True,
            "effective_scope_units": effective_scope,
            "applied_controls": sorted(set(applied)),
            "blocked_controls": [],
            "reason_codes": ["SPARTA_THROTTLE_WITH_NATIVE_CONTROLS"],
            "plain_english_summary": "SPARTa converted the throttled SMERC posture into a constrained execution route with smaller scope and recovery controls.",
            "recommended_next_action": "Execute only through an adapter that enforces the listed controls and records control evidence.",
        }

    def _freeze_route(self, plan: ToolPlan) -> Dict[str, Any]:
        applied = ["pause_execution", "preserve_replay", "snapshot_current_state"]
        if plan.supports_checkpoint:
            applied.append("checkpoint_before_execution")
        return {
            "route_state": "PAUSE",
            "executable": False,
            "effective_scope_units": 0,
            "applied_controls": applied,
            "blocked_controls": ["execute"],
            "reason_codes": ["SPARTA_FREEZE_PAUSES_AUTOMATION"],
            "plain_english_summary": "SPARTa paused execution because SMERC returned FREEZE, indicating instability or unacceptable deployment risk.",
            "recommended_next_action": "Preserve the replay, snapshot current state, and require accountable review before a new request.",
        }

    def _deny_route(self, plan: ToolPlan) -> Dict[str, Any]:
        return {
            "route_state": "BLOCK",
            "executable": False,
            "effective_scope_units": 0,
            "applied_controls": ["block_execution", "preserve_replay", "explain_denial"],
            "blocked_controls": ["execute"],
            "reason_codes": ["SPARTA_DENY_BLOCKS_EXECUTION"],
            "plain_english_summary": "SPARTa blocked execution because SMERC determined the action is not structurally defensible.",
            "recommended_next_action": "Do not execute this plan. Submit a materially safer action with stronger evidence or reduced impact.",
        }

    def _escalate_route(self, plan: ToolPlan) -> Dict[str, Any]:
        if plan.supports_human_approval:
            return {
                "route_state": "REVIEW_REQUIRED",
                "executable": False,
                "effective_scope_units": 0,
                "applied_controls": ["route_to_accountable_reviewer", "require_explicit_approval", "preserve_replay"],
                "blocked_controls": ["execute"],
                "reason_codes": ["SPARTA_ESCALATE_TO_ACCOUNTABLE_REVIEWER"],
                "plain_english_summary": "SPARTa routed the action to accountable human review because SMERC required escalation.",
                "recommended_next_action": "Assign a reviewer, document the decision, and issue a new request if approval changes the posture.",
            }
        return {
            "route_state": "BLOCKED_ESCALATION_UNAVAILABLE",
            "executable": False,
            "effective_scope_units": 0,
            "applied_controls": ["preserve_replay", "block_execution"],
            "blocked_controls": ["route_to_accountable_reviewer", "execute"],
            "reason_codes": ["SPARTA_ESCALATION_PATH_MISSING"],
            "plain_english_summary": "SMERC required escalation, but the declared plan has no accountable approval path.",
            "recommended_next_action": "Do not execute until the integration provides a human-review route.",
        }


def route_decision(decision: Mapping[str, Any], plan: Mapping[str, Any] | ToolPlan) -> Dict[str, Any]:
    return SPARTaRouter().route(decision, plan)


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a SMERC decision through a SPARTa tool plan.")
    parser.add_argument("--decision", required=True, type=Path, help="Path to a SMERC decision JSON object.")
    parser.add_argument("--plan", required=True, type=Path, help="Path to a SPARTa tool-plan JSON object.")
    parser.add_argument("--pretty", action="store_true", help="Print indented JSON.")
    args = parser.parse_args()

    report = route_decision(load_json(args.decision), load_json(args.plan))
    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_canonical_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

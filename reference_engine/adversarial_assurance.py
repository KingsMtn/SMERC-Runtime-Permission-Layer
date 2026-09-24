from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping


VERSION = "smerc.adversarial-assurance.v1"
REPORT_VERSION = "smerc.assurance-evidence-pack.v1"
OUTCOMES = {"CONTROL_HELD", "CONTROL_MISSED", "STOPPED", "INCONCLUSIVE"}


class AdversarialAssuranceError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise AdversarialAssuranceError(f"{path} must be non-empty text")
    return value.strip()


def _number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise AdversarialAssuranceError(f"{path} must be a non-negative number")
    return float(value)


def _strings(values: Any, path: str) -> list[str]:
    if not isinstance(values, list) or not values:
        raise AdversarialAssuranceError(f"{path} must be a non-empty list")
    result = sorted({_text(value, path) for value in values})
    if len(result) != len(values):
        raise AdversarialAssuranceError(f"{path} must not contain duplicates")
    return result


@dataclass(frozen=True)
class ContainmentEnvelope:
    environment_id: str
    authorized_by: str
    allowed_actions: tuple[str, ...]
    prohibited_targets: tuple[str, ...]
    max_cost_usd: float
    max_scope_units: float
    max_mutations: float
    max_steps: int
    stop_conditions: tuple[str, ...]
    expires_at: int
    production_access: bool = False

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ContainmentEnvelope":
        if not isinstance(value, Mapping):
            raise AdversarialAssuranceError("containment must be an object")
        max_steps = value.get("max_steps")
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
            raise AdversarialAssuranceError("containment.max_steps must be a positive integer")
        if value.get("production_access") is not False:
            raise AdversarialAssuranceError("adversarial assurance cannot target production")
        envelope = cls(
            environment_id=_text(value.get("environment_id"), "containment.environment_id"),
            authorized_by=_text(value.get("authorized_by"), "containment.authorized_by"),
            allowed_actions=tuple(_strings(value.get("allowed_actions"), "containment.allowed_actions")),
            prohibited_targets=tuple(_strings(value.get("prohibited_targets"), "containment.prohibited_targets")),
            max_cost_usd=_number(value.get("max_cost_usd"), "containment.max_cost_usd"),
            max_scope_units=_number(value.get("max_scope_units"), "containment.max_scope_units"),
            max_mutations=_number(value.get("max_mutations"), "containment.max_mutations"),
            max_steps=max_steps,
            stop_conditions=tuple(_strings(value.get("stop_conditions"), "containment.stop_conditions")),
            expires_at=value.get("expires_at"),
            production_access=False,
        )
        if not isinstance(envelope.expires_at, int) or isinstance(envelope.expires_at, bool) or envelope.expires_at <= 0:
            raise AdversarialAssuranceError("containment.expires_at must be a positive integer")
        required_stops = {"cost_ceiling", "scope_ceiling", "unexpected_target", "operator_stop"}
        if not required_stops <= set(envelope.stop_conditions):
            raise AdversarialAssuranceError("containment is missing mandatory stop conditions")
        return envelope


def validate_scenario(value: Mapping[str, Any], *, now: int) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("version") != VERSION:
        raise AdversarialAssuranceError(f"scenario.version must be {VERSION}")
    if not isinstance(now, int) or isinstance(now, bool) or now < 0:
        raise AdversarialAssuranceError("now must be a non-negative integer")
    containment = ContainmentEnvelope.from_mapping(value.get("containment"))
    if now >= containment.expires_at:
        raise AdversarialAssuranceError("containment envelope has expired")
    steps = value.get("steps")
    if not isinstance(steps, list) or not steps:
        raise AdversarialAssuranceError("scenario.steps must be a non-empty list")
    if len(steps) > containment.max_steps:
        raise AdversarialAssuranceError("scenario exceeds the contained step ceiling")
    normalized_steps = []
    totals = {"cost_usd": 0.0, "scope_units": 0.0, "mutations": 0.0}
    for index, raw in enumerate(steps):
        if not isinstance(raw, Mapping):
            raise AdversarialAssuranceError(f"steps[{index}] must be an object")
        action = _text(raw.get("action"), f"steps[{index}].action")
        if action not in containment.allowed_actions:
            raise AdversarialAssuranceError(f"steps[{index}] action is outside containment")
        target = _text(raw.get("target"), f"steps[{index}].target")
        if any(target == item or target.startswith(item + ":") for item in containment.prohibited_targets):
            raise AdversarialAssuranceError(f"steps[{index}] targets a prohibited boundary")
        expected = _text(raw.get("expected_control"), f"steps[{index}].expected_control")
        estimate = {
            "cost_usd": _number(raw.get("cost_usd", 0), f"steps[{index}].cost_usd"),
            "scope_units": _number(raw.get("scope_units", 0), f"steps[{index}].scope_units"),
            "mutations": _number(raw.get("mutations", 0), f"steps[{index}].mutations"),
        }
        for key in totals:
            totals[key] += estimate[key]
        normalized_steps.append({
            "step_id": _text(raw.get("step_id"), f"steps[{index}].step_id"),
            "action": action,
            "target": target,
            "expected_control": expected,
            **estimate,
        })
    ceilings = {
        "cost_usd": containment.max_cost_usd,
        "scope_units": containment.max_scope_units,
        "mutations": containment.max_mutations,
    }
    exceeded = [key for key, total in totals.items() if total > ceilings[key]]
    if exceeded:
        raise AdversarialAssuranceError("scenario exceeds containment ceilings: " + ", ".join(exceeded))
    scenario = {
        "version": VERSION,
        "scenario_id": _text(value.get("scenario_id"), "scenario_id"),
        "objective": _text(value.get("objective"), "objective"),
        "control_under_test": _text(value.get("control_under_test"), "control_under_test"),
        "containment": {
            "environment_id": containment.environment_id,
            "authorized_by": containment.authorized_by,
            "allowed_actions": list(containment.allowed_actions),
            "prohibited_targets": list(containment.prohibited_targets),
            "max_cost_usd": containment.max_cost_usd,
            "max_scope_units": containment.max_scope_units,
            "max_mutations": containment.max_mutations,
            "max_steps": containment.max_steps,
            "stop_conditions": list(containment.stop_conditions),
            "expires_at": containment.expires_at,
            "production_access": False,
        },
        "steps": normalized_steps,
        "estimated_consequence": totals,
    }
    scenario["scenario_sha256"] = _digest(scenario)
    return scenario


def run_scenario(
    scenario: Mapping[str, Any],
    executor: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]],
    *,
    now: int,
    operator_stop: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    plan = validate_scenario(scenario, now=now)
    observations = []
    consumed = {"cost_usd": 0.0, "scope_units": 0.0, "mutations": 0.0}
    stopped_reason = None
    for step in plan["steps"]:
        if operator_stop is not None and operator_stop():
            stopped_reason = "operator_stop"
            break
        observation = executor(dict(step), dict(plan["containment"]))
        if not isinstance(observation, Mapping):
            raise AdversarialAssuranceError("executor observations must be objects")
        target = _text(observation.get("target"), "observation.target")
        if target != step["target"]:
            stopped_reason = "unexpected_target"
            observations.append(_observation(step, observation, "STOPPED"))
            break
        actual = {
            "cost_usd": _number(observation.get("cost_usd", 0), "observation.cost_usd"),
            "scope_units": _number(observation.get("scope_units", 0), "observation.scope_units"),
            "mutations": _number(observation.get("mutations", 0), "observation.mutations"),
        }
        for key in consumed:
            consumed[key] += actual[key]
        ceilings = plan["containment"]
        if consumed["cost_usd"] > ceilings["max_cost_usd"]:
            stopped_reason = "cost_ceiling"
        elif consumed["scope_units"] > ceilings["max_scope_units"] or consumed["mutations"] > ceilings["max_mutations"]:
            stopped_reason = "scope_ceiling"
        outcome = _text(observation.get("outcome"), "observation.outcome")
        if outcome not in OUTCOMES:
            raise AdversarialAssuranceError("observation.outcome is invalid")
        observations.append(_observation(step, observation, "STOPPED" if stopped_reason else outcome))
        if stopped_reason:
            break
    held = sum(item["outcome"] == "CONTROL_HELD" for item in observations)
    missed = sum(item["outcome"] == "CONTROL_MISSED" for item in observations)
    completed = len(observations) == len(plan["steps"]) and stopped_reason is None
    verdict = "PASS" if completed and missed == 0 and held == len(observations) else "FAIL" if missed else "INCOMPLETE"
    report = {
        "version": REPORT_VERSION,
        "scenario_id": plan["scenario_id"],
        "scenario_sha256": plan["scenario_sha256"],
        "environment_id": plan["containment"]["environment_id"],
        "verdict": verdict,
        "stopped_reason": stopped_reason,
        "steps_planned": len(plan["steps"]),
        "steps_observed": len(observations),
        "controls_held": held,
        "controls_missed": missed,
        "actual_consequence": consumed,
        "observations": observations,
        "evidence_boundary": "Authorized non-production scenario evidence; not proof of production security or permission to test third-party systems.",
    }
    report["report_sha256"] = _digest(report)
    return report


def _observation(step: Mapping[str, Any], value: Mapping[str, Any], outcome: str) -> dict[str, Any]:
    return {
        "step_id": step["step_id"],
        "expected_control": step["expected_control"],
        "target": value.get("target"),
        "outcome": outcome,
        "reason_code": _text(value.get("reason_code"), "observation.reason_code"),
        "evidence": dict(value.get("evidence", {})) if isinstance(value.get("evidence", {}), Mapping) else {},
    }


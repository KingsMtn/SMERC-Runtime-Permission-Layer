from __future__ import annotations

import argparse
import copy
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.autonomy_budget import evaluate_autonomy_budget
from reference_engine.earned_autonomy import budget_context_for_tier
from reference_engine.mcp_proxy_runner import run_mcp_proxy


MCP_GOVERNANCE_GATEWAY_VERSION = "smerc.mcp-governance-gateway.v1"
REGISTRY_VERSION = "smerc.mcp-tool-registry.v1"
SESSION_VERSION = "smerc.mcp-gateway-session.v1"
MODES = {"shadow", "enforce"}
REF_GATE_FIELDS = {
    "typed_contract_valid": "typed_contract_invalid",
    "attestation_valid": "attestation_invalid",
    "least_privilege_confirmed": "least_privilege_unconfirmed",
    "object_shape_expected": "object_shape_unexpected",
}


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate_gateway_session(
    *,
    registry: Mapping[str, Any],
    session: Mapping[str, Any],
    mode: str = "shadow",
) -> Dict[str, Any]:
    if mode not in MODES:
        raise ValueError(f"mode must be one of: {', '.join(sorted(MODES))}")
    _require_version(registry, REGISTRY_VERSION, "registry")
    _require_version(session, SESSION_VERSION, "session")
    tools = _registry_by_key(registry)
    requests = session.get("requests")
    if not isinstance(requests, list) or not requests:
        raise ValueError("session.requests must be a non-empty list")

    observed_counts: dict[str, int] = defaultdict(int)
    observed_agent_counts: dict[str, int] = defaultdict(int)
    cumulative_cost_units = 0.0
    gateway_decisions = []

    for index, request in enumerate(requests, start=1):
        if not isinstance(request, Mapping):
            raise TypeError("each session request must be an object")
        tool_key = _tool_key(request)
        tool_policy = tools.get(tool_key)
        if tool_policy is None:
            tool_policy = _unknown_tool_policy(request)
        observed_counts[tool_key] += 1
        observed_agent_counts[str(request["agent"]["agent_id"])] += 1
        cumulative_cost_units += float(tool_policy.get("cost_units", 1.0))
        gateway_pressure = _gateway_pressure(
            request=request,
            tool_policy=tool_policy,
            observed_tool_count=observed_counts[tool_key],
            observed_agent_count=observed_agent_counts[str(request["agent"]["agent_id"])],
            cumulative_cost_units=cumulative_cost_units,
            session_budget=float(session.get("session_budget_units", 100.0)),
        )
        ref_gate = _ref_gate(request, tool_policy)
        gateway_pressure = _merge_ref_gate_pressure(gateway_pressure, ref_gate)
        enriched_request = _enrich_request(request, tool_policy, gateway_pressure, ref_gate)
        proxy_report = run_mcp_proxy(enriched_request, mode=mode)
        gateway_decisions.append(
            {
                "sequence": index,
                "mcp_request_id": proxy_report["mcp_request_id"],
                "agent_id": proxy_report["agent_id"],
                "server_name": proxy_report["server_name"],
                "tool_name": proxy_report["tool_name"],
                "profile": str(tool_policy.get("profile", "general")),
                "risk_tier": str(tool_policy.get("risk_tier", "unknown")),
                "requested_scope_units": request["tool_call"].get("requested_scope_units", 1),
                "mode": mode,
                "ref_gate": ref_gate,
                "gateway_pressure": gateway_pressure,
                "proxy_action": proxy_report["proxy_response"]["proxy_action"],
                "should_forward_tool_call": proxy_report["proxy_response"]["should_forward_tool_call"],
                "posture": proxy_report["governance_report"]["decision"]["posture"],
                "route_state": proxy_report["governance_report"]["sparta_route"]["route_state"],
                "recommended_mcp_result": proxy_report["governance_report"]["recommended_mcp_result"],
                "replay_id": proxy_report["governance_report"]["decision"]["replay_id"],
                "reason_codes": list(proxy_report["governance_report"]["decision"].get("reason_codes", [])),
                "controls": list(proxy_report["governance_report"]["sparta_route"].get("applied_controls", [])),
            }
        )

    posture_counts = _counts(item["posture"] for item in gateway_decisions)
    proxy_action_counts = _counts(item["proxy_action"] for item in gateway_decisions)
    forwarded_count = sum(1 for item in gateway_decisions if item["should_forward_tool_call"])
    blocked_or_held_count = len(gateway_decisions) - forwarded_count
    earned_autonomy = _earned_autonomy_context(session)
    autonomy_budget = evaluate_autonomy_budget(
        decisions=gateway_decisions,
        initial_state=earned_autonomy["budget_context"]["initial_state"] if earned_autonomy else "HEALTHY",
        budget_overrides=earned_autonomy["budget_context"]["budget_overrides"] if earned_autonomy else None,
        earned_autonomy=earned_autonomy,
    )
    return {
        "version": MCP_GOVERNANCE_GATEWAY_VERSION,
        "generated_at": _now(),
        "mode": mode,
        "session_id": str(session.get("session_id", "mcp_gateway_session")),
        "registry_id": str(registry.get("registry_id", "mcp_tool_registry")),
        "request_count": len(gateway_decisions),
        "registered_tool_count": len(tools),
        "cumulative_cost_units": round(cumulative_cost_units, 3),
        "forwarded_count": forwarded_count,
        "blocked_or_held_count": blocked_or_held_count,
        "ref_gate_failure_count": sum(1 for item in gateway_decisions if item["ref_gate"]["status"] == "fail"),
        "posture_counts": posture_counts,
        "proxy_action_counts": proxy_action_counts,
        "highest_pressure_calls": _highest_pressure(gateway_decisions),
        "earned_autonomy": earned_autonomy,
        "autonomy_budget": autonomy_budget,
        "decisions": gateway_decisions,
        "commercial_boundary": (
            "This gateway package demonstrates MCP tool registry governance, deterministic pre-execution metadata "
            "checks, repeated-call pressure, cost metering, and SMERC posture routing. It does not implement OAuth, "
            "mTLS, native MCP transport, payment rails, x402, wallet settlement, prompt-injection defense, "
            "sandboxing, SIEM export, or production billing."
        ),
        "recommended_next_action": (
            "Use this gateway in shadow mode against one typed MCP tool family, require explicit trusted metadata "
            "for contract, attestation, privilege, and object-shape checks, then compare SMERC posture, ref-gate "
            "failures, loop pressure, and reviewer labels before any enforcement or monetization work."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC MCP Governance Gateway Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Session: `{report['session_id']}`",
        f"- Registry: `{report['registry_id']}`",
        f"- Requests evaluated: `{report['request_count']}`",
        f"- Registered tools: `{report['registered_tool_count']}`",
        f"- Cumulative cost units: `{report['cumulative_cost_units']}`",
        f"- Forwarded calls: `{report['forwarded_count']}`",
        f"- Blocked or held calls: `{report['blocked_or_held_count']}`",
        f"- Ref gate failures: `{report['ref_gate_failure_count']}`",
        f"- Earned autonomy tier: `{report['earned_autonomy']['earned_tier'] if report.get('earned_autonomy') else 'not_supplied'}`",
        f"- Autonomy state: `{report['autonomy_budget']['autonomy_state']}`",
        f"- Remaining actions: `{report['autonomy_budget']['remaining']['actions']}`",
        f"- Remaining risk spend: `{report['autonomy_budget']['remaining']['risk_spend']}`",
        "",
        "## Posture Distribution",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in sorted(report["posture_counts"].items()))
    lines.extend(["", "## Proxy Actions", ""])
    lines.extend(f"- `{key}`: `{value}`" for key, value in sorted(report["proxy_action_counts"].items()))
    lines.extend(
        [
            "",
            "## Autonomy Budget",
            "",
            f"- Earned tier: `{report['earned_autonomy']['earned_tier'] if report.get('earned_autonomy') else 'not_supplied'}`",
            f"- State: `{report['autonomy_budget']['autonomy_state']}`",
            f"- Actions spent: `{report['autonomy_budget']['spent']['actions']}` of `{report['autonomy_budget']['budget']['max_actions']}`",
            f"- Scope units spent: `{report['autonomy_budget']['spent']['scope_units']}` of `{report['autonomy_budget']['budget']['max_scope_units']}`",
            f"- Risk spend: `{report['autonomy_budget']['spent']['risk_spend']}` of `{report['autonomy_budget']['budget']['max_risk_spend']}`",
            f"- Review triggers: `{', '.join(report['autonomy_budget']['review_triggers']) or 'none'}`",
            "",
            str(report["autonomy_budget"]["plain_english_summary"]),
        ]
    )
    lines.extend(
        [
            "",
            "## Highest Pressure Calls",
            "",
            "| Request | Tool | Profile | Ref Gate | Pressure | Posture | Proxy Action | Drivers |",
            "| --- | --- | --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for item in report["highest_pressure_calls"]:
        drivers = ", ".join(item["gateway_pressure"]["drivers"]) or "none"
        lines.append(
            f"| `{item['mcp_request_id']}` | `{item['server_name']}.{item['tool_name']}` | "
            f"`{item['profile']}` | `{item['ref_gate']['status']}` | {item['gateway_pressure']['score']} | `{item['posture']}` | "
            f"`{item['proxy_action']}` | {drivers} |"
        )
    lines.extend(
        [
            "",
            "## Decision Table",
            "",
            "| # | Request | Tool | Profile | Ref Gate | Posture | Route | Proxy Action | Forward |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["decisions"]:
        lines.append(
            f"| {item['sequence']} | `{item['mcp_request_id']}` | `{item['server_name']}.{item['tool_name']}` | "
            f"`{item['profile']}` | `{item['ref_gate']['status']}` | `{item['posture']}` | `{item['route_state']}` | "
            f"`{item['proxy_action']}` | `{str(item['should_forward_tool_call']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Commercial Boundary",
            "",
            str(report["commercial_boundary"]),
            "",
            "## Recommended Next Action",
            "",
            str(report["recommended_next_action"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _require_version(payload: Mapping[str, Any], version: str, name: str) -> None:
    if payload.get("version") != version:
        raise ValueError(f"{name} must have version {version}")


def _registry_by_key(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    tools = registry.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ValueError("registry.tools must be a non-empty list")
    result = {}
    for tool in tools:
        if not isinstance(tool, Mapping):
            raise TypeError("registry tool entries must be objects")
        key = f"{tool['server_name']}::{tool['tool_name']}"
        result[key] = tool
    return result


def _tool_key(request: Mapping[str, Any]) -> str:
    return f"{request['server']['name']}::{request['tool_call']['tool_name']}"


def _unknown_tool_policy(request: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "server_name": request["server"]["name"],
        "tool_name": request["tool_call"]["tool_name"],
        "profile": "unknown",
        "risk_tier": "unregistered",
        "cost_units": 1.0,
        "max_calls_per_session": 1,
        "max_agent_calls_per_session": 3,
        "risk_pressure": 0.35,
        "required_metadata": ["registered_tool_policy"],
    }


def _earned_autonomy_context(session: Mapping[str, Any]) -> Dict[str, Any] | None:
    supplied = session.get("earned_autonomy")
    if not isinstance(supplied, Mapping):
        return None
    tier = str(supplied.get("earned_tier", "TIER_2_CONSTRAINED"))
    return {
        "subject_id": str(supplied.get("subject_id", "unknown_subject")),
        "earned_tier": tier,
        "source": str(supplied.get("source", "supplied_session_profile")),
        "budget_context": budget_context_for_tier(tier),
    }


def _gateway_pressure(
    *,
    request: Mapping[str, Any],
    tool_policy: Mapping[str, Any],
    observed_tool_count: int,
    observed_agent_count: int,
    cumulative_cost_units: float,
    session_budget: float,
) -> Dict[str, Any]:
    drivers = []
    pressure = float(tool_policy.get("risk_pressure", 0.0))
    if observed_tool_count > int(tool_policy.get("max_calls_per_session", 3)):
        pressure += 0.18
        drivers.append("tool_loop_pressure")
    if observed_agent_count > int(tool_policy.get("max_agent_calls_per_session", 6)):
        pressure += 0.12
        drivers.append("agent_velocity_pressure")
    if cumulative_cost_units > session_budget:
        pressure += 0.16
        drivers.append("session_budget_pressure")
    if request["tool_call"].get("requested_scope_units", 1) > int(tool_policy.get("max_scope_units", 1_000_000)):
        pressure += 0.2
        drivers.append("scope_exceeds_registry_limit")
    if str(tool_policy.get("risk_tier", "")).lower() in {"critical", "financial", "destructive"}:
        pressure += 0.08
        drivers.append("high_risk_tool_tier")
    return {
        "score": round(min(1.0, pressure), 3),
        "drivers": drivers,
        "observed_tool_count": observed_tool_count,
        "observed_agent_count": observed_agent_count,
        "cumulative_cost_units": round(cumulative_cost_units, 3),
        "session_budget_units": session_budget,
    }


def _ref_gate(request: Mapping[str, Any], tool_policy: Mapping[str, Any]) -> Dict[str, Any]:
    tool_call = request["tool_call"]
    required = bool(tool_policy.get("requires_ref_gate", False))
    checks: dict[str, Any] = {}
    drivers = []
    for field, driver in REF_GATE_FIELDS.items():
        if field in tool_call:
            value = bool(tool_call[field])
            source = "explicit"
        else:
            value = not required
            source = "missing"
        checks[field] = {"value": value, "source": source}
        if not value:
            drivers.append(driver if source == "explicit" else f"{field}_missing")
    return {
        "pattern": "deterministic_pre_execution_ref_gate",
        "status": "fail" if drivers else "pass",
        "required": required,
        "drivers": drivers,
        "checks": checks,
    }


def _merge_ref_gate_pressure(gateway_pressure: Mapping[str, Any], ref_gate: Mapping[str, Any]) -> Dict[str, Any]:
    merged = copy.deepcopy(dict(gateway_pressure))
    if ref_gate["status"] == "fail":
        drivers = list(merged["drivers"])
        drivers.extend(driver for driver in ref_gate["drivers"] if driver not in drivers)
        merged["score"] = 1.0
        merged["drivers"] = drivers
    return merged


def _enrich_request(
    request: Mapping[str, Any],
    tool_policy: Mapping[str, Any],
    gateway_pressure: Mapping[str, Any],
    ref_gate: Mapping[str, Any],
) -> Dict[str, Any]:
    enriched = copy.deepcopy(dict(request))
    signals = dict(enriched["risk_signals"])
    pressure = float(gateway_pressure["score"])
    signals["base_action_risk"] = _clamp(max(float(signals["base_action_risk"]), pressure))
    signals["anomaly_pressure"] = _clamp(max(float(signals["anomaly_pressure"]), pressure))
    if "tool_loop_pressure" in gateway_pressure["drivers"] or "session_budget_pressure" in gateway_pressure["drivers"]:
        signals["authorization_confidence"] = _clamp(min(float(signals["authorization_confidence"]), 1.0 - pressure / 2))
        signals["evidence_validity"] = _clamp(min(float(signals["evidence_validity"]), 1.0 - pressure / 3))
    if ref_gate["status"] == "fail":
        signals["base_action_risk"] = 1.0
        signals["anomaly_pressure"] = 1.0
        signals["authorization_confidence"] = _clamp(min(float(signals["authorization_confidence"]), 0.12))
        signals["evidence_validity"] = _clamp(min(float(signals["evidence_validity"]), 0.12))
        signals["containment_strength"] = _clamp(min(float(signals["containment_strength"]), 0.25))
    enriched["risk_signals"] = signals
    enriched["tool_call"] = dict(enriched["tool_call"])
    if "domain_profile" not in enriched["tool_call"] and tool_policy.get("domain_profile"):
        enriched["tool_call"]["domain_profile"] = tool_policy["domain_profile"]
    return enriched


def _highest_pressure(decisions: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(decisions, key=lambda item: item["gateway_pressure"]["score"], reverse=True)[:5]


def _counts(values: Iterable[str]) -> Dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        result[value] = result.get(value, 0) + 1
    return result


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an MCP session through the SMERC Governance Gateway.")
    parser.add_argument("--registry", default="examples/mcp/governance_gateway_registry.json")
    parser.add_argument("--session", default="examples/mcp/governance_gateway_session.json")
    parser.add_argument("--mode", default="shadow", choices=sorted(MODES))
    parser.add_argument("--json-output", default="reports/mcp_governance_gateway_report.json")
    parser.add_argument("--markdown-output", default="reports/MCP_Governance_Gateway_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = evaluate_gateway_session(registry=load_json(args.registry), session=load_json(args.session), mode=args.mode)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

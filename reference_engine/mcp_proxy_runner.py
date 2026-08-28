from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.dll_intelligence import analyze_ledgers
from reference_engine.mcp_tool_governance import evaluate_mcp_tool_call, load_json, render_markdown as render_governance_markdown


MCP_PROXY_RUNNER_VERSION = "smerc.mcp-proxy-runner.v1"
PROXY_MODES = {"shadow", "enforce"}


def run_mcp_proxy(
    payload: Mapping[str, Any],
    *,
    mode: str = "shadow",
    require_agent_identity: bool = False,
) -> Dict[str, Any]:
    if mode not in PROXY_MODES:
        raise ValueError(f"mode must be one of: {', '.join(sorted(PROXY_MODES))}")
    governance = evaluate_mcp_tool_call(payload, require_agent_identity=require_agent_identity)
    proxy_action = _proxy_action(governance["recommended_mcp_result"], mode)
    response = _proxy_response(payload, governance, proxy_action, mode)
    ledger = _build_ledger(payload, governance, response)
    ledger_data = ledger.to_dict()
    return {
        "version": MCP_PROXY_RUNNER_VERSION,
        "generated_at": _now(),
        "mode": mode,
        "require_agent_identity": require_agent_identity,
        "mcp_request_id": governance["mcp_request_id"],
        "agent_id": governance["agent_id"],
        "server_name": governance["server_name"],
        "tool_name": governance["tool_name"],
        "governance_report": governance,
        "proxy_response": response,
        "decision_lifecycle_ledger": ledger_data,
        "dll_intelligence": analyze_ledgers([ledger_data]),
        "evidence_boundary": (
            "MCP Proxy Runner v1 is a local reference proxy loop. It evaluates supplied MCP-style metadata, "
            "returns a proxy action, and records DLL evidence. It does not implement MCP transport, OAuth, "
            "enterprise identity, prompt-injection defense, sandboxing, native tool execution, or production policy distribution."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    response = report["proxy_response"]
    governance = report["governance_report"]
    lines = [
        "# SMERC MCP Proxy Runner Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Proxy Decision",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Agent identity required: `{str(report['require_agent_identity']).lower()}`",
        f"- MCP request: `{report['mcp_request_id']}`",
        f"- Agent: `{report['agent_id']}`",
        f"- Server: `{report['server_name']}`",
        f"- Tool: `{report['tool_name']}`",
        f"- Proxy action: `{response['proxy_action']}`",
        f"- Should forward tool call: `{str(response['should_forward_tool_call']).lower()}`",
        f"- SMERC posture: `{governance['decision']['posture']}`",
        f"- SPARTa route: `{governance['sparta_route']['route_state']}`",
        f"- Identity gate: `{governance['identity_gate']['status']}`",
        f"- Replay ID: `{governance['decision']['replay_id']}`",
        "",
        "## Proxy Instructions",
        "",
    ]
    lines.extend(f"- {item}" for item in response["proxy_instructions"])
    lines.extend(
        [
            "",
            "## Governance Report",
            "",
            render_governance_markdown(governance),
            "",
            "## Decision Lifecycle Ledger",
            "",
            f"- Valid hash chain: `{str(report['decision_lifecycle_ledger']['verification']['valid']).lower()}`",
            f"- Record count: `{report['decision_lifecycle_ledger']['record_count']}`",
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _proxy_action(recommended_result: str, mode: str) -> str:
    if mode == "shadow":
        return "observe_and_forward_tool_call"
    return {
        "call_tool": "forward_tool_call",
        "call_tool_with_constraints": "forward_constrained_tool_call",
        "require_approval_before_tool_call": "hold_for_approval",
        "pause_tool_call": "pause_tool_call",
        "block_tool_call": "block_tool_call",
    }[recommended_result]


def _proxy_response(
    payload: Mapping[str, Any],
    governance: Mapping[str, Any],
    proxy_action: str,
    mode: str,
) -> Dict[str, Any]:
    route = governance["sparta_route"]
    decision = governance["decision"]
    should_forward = proxy_action in {"observe_and_forward_tool_call", "forward_tool_call", "forward_constrained_tool_call"}
    constrained = proxy_action == "forward_constrained_tool_call"
    instructions = _instructions(proxy_action, route)
    return {
        "version": "smerc.mcp-proxy-response.v1",
        "mode": mode,
        "proxy_action": proxy_action,
        "should_forward_tool_call": should_forward,
        "constraint_applied": constrained,
        "tool_call": dict(payload["tool_call"]),
        "forwarding_plan": {
            "server": dict(payload["server"]),
            "tool_name": payload["tool_call"]["tool_name"],
            "effective_scope_units": route["effective_scope_units"],
            "required_controls": list(route.get("applied_controls", [])),
            "blocked_controls": list(route.get("blocked_controls", [])),
        },
        "decision_reference": {
            "replay_id": decision["replay_id"],
            "posture": decision["posture"],
            "route_state": route["route_state"],
            "recommended_mcp_result": governance["recommended_mcp_result"],
        },
        "proxy_instructions": instructions,
        "plain_english_summary": (
            f"MCP proxy mode `{mode}` selected `{proxy_action}` for tool `{payload['tool_call']['tool_name']}` "
            f"after SMERC posture {decision['posture']} and SPARTa route {route['route_state']}."
        ),
    }


def _instructions(proxy_action: str, route: Mapping[str, Any]) -> list[str]:
    if proxy_action == "observe_and_forward_tool_call":
        return [
            "Forward the tool call because proxy is in shadow mode.",
            "Record the SMERC posture, SPARTa route, and replay ID for reviewer comparison.",
            "Do not claim enforcement occurred.",
        ]
    if proxy_action == "forward_tool_call":
        return ["Forward the tool call and preserve the replay and route evidence."]
    if proxy_action == "forward_constrained_tool_call":
        return [
            "Forward only if the caller can apply the listed controls.",
            f"Use effective scope units {route['effective_scope_units']} instead of the requested scope.",
            "Preserve control evidence after forwarding.",
        ]
    if proxy_action == "hold_for_approval":
        return [
            "Do not forward the tool call yet.",
            "Route to accountable approval and preserve reviewer rationale.",
        ]
    if proxy_action == "pause_tool_call":
        return [
            "Pause the tool call.",
            "Collect more evidence or wait for instability to resolve before submitting a new request.",
        ]
    return [
        "Block the tool call.",
        "Preserve the replay and explain the denial.",
        "Require a materially safer new request before execution.",
    ]


def _build_ledger(
    payload: Mapping[str, Any],
    governance: Mapping[str, Any],
    response: Mapping[str, Any],
) -> DecisionLifecycleLedger:
    decision = governance["decision"]
    route = governance["sparta_route"]
    ledger = DecisionLifecycleLedger(
        f"dll_mcp_{decision['replay_id']}",
        tenant_id="mcp-proxy-runner",
    )
    ledger.append(
        "REQUEST",
        str(payload["agent"]["agent_id"]),
        {
            "initiated_by": str(payload["agent"]["agent_id"]),
            "requested_operation": str(payload["tool_call"]["description"]),
            "environment": str(payload["server"]["trust_boundary"]),
            "risk_profile": f"mcp_{payload['tool_call']['operation_class']}",
        },
    )
    ledger.append(
        "EVIDENCE",
        "mcp-proxy-runner",
        {
            "available_evidence": [
                "agent_metadata",
                "agent_identity_gate",
                "mcp_server_metadata",
                "tool_call_metadata",
                "risk_signals",
                "sparta_route",
            ],
            "confidence_score": float(decision["scores"]["confidence_score"]),
            "missing_evidence": ["live_mcp_transport_result", "customer_reviewer_label"],
            "external_dependencies": ["mcp_client", "mcp_server", "agent_runtime"],
            "model_version": "metadata-only-mcp-proxy-runner",
            "policy_version": "default-reference-policy",
        },
    )
    ledger.append(
        "EVALUATION",
        "smerc-mcp-governance",
        {
            "structural_state": f"MCP proxy produced {response['proxy_action']} before tool execution.",
            "entropy_indicators": list(decision.get("reason_codes", [])),
            "recoverability_score": float(decision["scores"]["reversible_capacity_score"]),
            "authorization_recommendation": str(decision["posture"]),
            "reason_codes": list(decision.get("reason_codes", [])),
            "recommended_safeguards": list(route.get("applied_controls", [])),
        },
    )
    ledger.append(
        "HUMAN_INTERACTION",
        "mcp-proxy-runner",
        {
            "interaction": "accepted",
            "reviewer_id": "mcp-proxy-runner",
            "original_recommendation": str(decision["posture"]),
            "final_recommendation": str(decision["posture"]),
            "rationale": "Synthetic MCP proxy runner accepts the generated posture to produce a complete review artifact.",
        },
    )
    execution_status = "succeeded" if response["should_forward_tool_call"] else "blocked"
    ledger.append(
        "EXECUTION",
        "mcp-proxy-runner",
        {
            "executed_operation": response["plain_english_summary"],
            "execution_status": execution_status,
            "started_at": _now(),
            "duration_ms": 0,
            "rollback_performed": False,
            "rollback_success": None,
        },
    )
    ledger.append(
        "OUTCOME",
        "mcp-proxy-runner",
        {
            "judged_correct": True,
            "unexpected_consequences": False,
            "controls_sufficient": True,
            "cost_incurred": 0,
            "time_to_recover_minutes": 0,
            "customer_impact": "none; local metadata-only proxy runner",
            "security_impact": "none; local metadata-only proxy runner",
            "financial_impact": "none; local metadata-only proxy runner",
        },
    )
    ledger.append(
        "LEARNING_RECOMMENDATION",
        "dll-intelligence",
        {
            "expected_outcome": "MCP proxy runner exposes the pre-execution decision and response action.",
            "actual_outcome": "Proxy response, SPARTa route, and DLL evidence were generated.",
            "prediction_error": "not measured in local metadata-only runner",
            "human_override_effectiveness": "not measured in local metadata-only runner",
            "recommended_policy_updates": ["Collect live customer MCP call metadata before tuning thresholds."],
            "confidence_calibration_changes": ["Do not calibrate from synthetic MCP examples."],
            "suggested_rule_modifications": ["Connect to a real MCP client/server only after reviewer agreement is measured."],
            "activation_status": "requires_review",
        },
    )
    return ledger


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local SMERC MCP proxy loop against one MCP-style tool call.")
    parser.add_argument("--request", default="examples/mcp/tool_call_delete_customer_records.json")
    parser.add_argument("--mode", choices=sorted(PROXY_MODES), default="shadow")
    parser.add_argument("--require-agent-identity", action="store_true")
    parser.add_argument("--json-output", default="reports/mcp_proxy_runner_report.json")
    parser.add_argument("--markdown-output", default="reports/MCP_Proxy_Runner_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = run_mcp_proxy(load_json(args.request), mode=args.mode, require_agent_identity=args.require_agent_identity)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

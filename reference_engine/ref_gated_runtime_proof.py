from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.mcp_governance_gateway import evaluate_gateway_session, load_json


REF_GATED_RUNTIME_PROOF_VERSION = "smerc.ref-gated-runtime-proof.v1"


def build_ref_gated_runtime_proof(
    *,
    registry: Mapping[str, Any],
    session: Mapping[str, Any],
    mode: str = "shadow",
) -> Dict[str, Any]:
    gateway = evaluate_gateway_session(registry=registry, session=session, mode=mode)
    proof_items = [_build_proof_item(item, gateway) for item in gateway["decisions"]]
    ref_failures = [item for item in proof_items if item["ref_gate"]["status"] == "fail"]
    scoring_capped = [item for item in proof_items if item["scoring_stage"]["admission"] != "admitted"]
    route_holds = [item for item in proof_items if item["sparta_stage"]["executable"] is False]

    return {
        "version": REF_GATED_RUNTIME_PROOF_VERSION,
        "generated_at": _now(),
        "mode": mode,
        "session_id": gateway["session_id"],
        "review_question": (
            "Can SMERC show a hard pre-execution Ref gate before recoverability scoring and execution routing?"
        ),
        "sequence": [
            "Ref gate: validate typed contract, attestation, least privilege, and object shape.",
            "SMERC scoring: admit scoring only when hard evidence gates pass; otherwise cap or force hold behavior.",
            "SPARTa routing: convert posture into executable, constrained, paused, blocked, or review-required behavior.",
            "Autonomy budget: reduce or suspend remaining freedom when repeated or high-risk actions accumulate.",
            "Decision Lifecycle Ledger: preserve request, evidence, evaluation, execution, and outcome evidence.",
        ],
        "summary": {
            "request_count": len(proof_items),
            "ref_gate_failure_count": len(ref_failures),
            "scoring_capped_count": len(scoring_capped),
            "non_executable_route_count": len(route_holds),
            "autonomy_state": gateway["autonomy_budget"]["autonomy_state"],
            "ledger_valid_count": sum(1 for item in proof_items if item["dll_stage"]["verification"]["valid"]),
        },
        "gateway_summary": {
            "posture_counts": gateway["posture_counts"],
            "proxy_action_counts": gateway["proxy_action_counts"],
            "forwarded_count": gateway["forwarded_count"],
            "blocked_or_held_count": gateway["blocked_or_held_count"],
            "earned_autonomy_tier": gateway["earned_autonomy"]["earned_tier"] if gateway.get("earned_autonomy") else None,
            "autonomy_budget": gateway["autonomy_budget"],
        },
        "proof_items": proof_items,
        "reviewer_prompts": [
            "Try an action with invalid object shape and confirm scoring cannot rescue it.",
            "Try an action with weak authority but high recoverability and confirm it still cannot proceed normally.",
            "Try an action that is authorized but irreversible and confirm the route constrains, freezes, denies, or escalates.",
            "Try a safe read action with all Ref evidence present and confirm it can remain low-friction.",
            "Try repeated high-risk calls and confirm autonomy budget reduces the actor's right to continue.",
        ],
        "external_feedback_alignment": (
            "This proof loop incorporates the OpenSSF Ref-gate feedback: hard mechanical gates come before "
            "recoverability scoring. Recoverability is a runtime governance signal, not a substitute for scoped "
            "identity, typed contracts, attestation, least privilege, expected object shape, or endpoint validation."
        ),
        "claim_boundary": (
            "This is a deterministic local proof loop for technical review. It does not prove production safety, "
            "customer demand, compliance, incident reduction, prompt-injection defense, endpoint type safety, or "
            "complete MCP implementation."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# SMERC Ref-Gated Runtime Proof Loop",
        "",
        f"Version: `{report['version']}`",
        f"Generated: `{report['generated_at']}`",
        f"Mode: `{report['mode']}`",
        f"Session: `{report['session_id']}`",
        "",
        "## Review Question",
        "",
        str(report["review_question"]),
        "",
        "## Runtime Sequence",
        "",
    ]
    lines.extend(f"{index}. {step}" for index, step in enumerate(report["sequence"], start=1))
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Requests evaluated: `{summary['request_count']}`",
            f"- Ref gate failures: `{summary['ref_gate_failure_count']}`",
            f"- Scoring capped or forced-hold cases: `{summary['scoring_capped_count']}`",
            f"- Non-executable routes: `{summary['non_executable_route_count']}`",
            f"- Autonomy state: `{summary['autonomy_state']}`",
            f"- Valid DLL ledgers: `{summary['ledger_valid_count']}`",
            "",
            "## Decision Table",
            "",
            "| Request | Ref Gate | Scoring Admission | Posture | SPARTa Route | Executable | DLL Valid | Main Drivers |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["proof_items"]:
        drivers = ", ".join(item["ref_gate"]["drivers"] or item["gateway_pressure"]["drivers"] or item["reason_codes"])
        lines.append(
            f"| `{item['request_id']}` | `{item['ref_gate']['status']}` | `{item['scoring_stage']['admission']}` | "
            f"`{item['smerc_stage']['posture']}` | `{item['sparta_stage']['route_state']}` | "
            f"`{str(item['sparta_stage']['executable']).lower()}` | "
            f"`{str(item['dll_stage']['verification']['valid']).lower()}` | {drivers or 'none'} |"
        )
    lines.extend(["", "## Reviewer Prompts", ""])
    lines.extend(f"- {prompt}" for prompt in report["reviewer_prompts"])
    lines.extend(
        [
            "",
            "## External Feedback Alignment",
            "",
            str(report["external_feedback_alignment"]),
            "",
            "## Claim Boundary",
            "",
            str(report["claim_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _build_proof_item(decision: Mapping[str, Any], gateway: Mapping[str, Any]) -> Dict[str, Any]:
    ref_gate = decision["ref_gate"]
    scoring_admission = "admitted" if ref_gate["status"] == "pass" else "capped_by_ref_gate"
    ledger = _build_ledger(decision, gateway, scoring_admission)
    route_state = str(decision["route_state"])
    executable = route_state in {"EXECUTE", "EXECUTE_CONSTRAINED"}
    return {
        "request_id": decision["mcp_request_id"],
        "agent_id": decision["agent_id"],
        "tool": f"{decision['server_name']}.{decision['tool_name']}",
        "profile": decision["profile"],
        "risk_tier": decision["risk_tier"],
        "ref_gate": ref_gate,
        "gateway_pressure": decision["gateway_pressure"],
        "scoring_stage": {
            "admission": scoring_admission,
            "rule": (
                "recoverability scoring may influence posture"
                if scoring_admission == "admitted"
                else "hard Ref failure caps scoring and forces high-risk hold behavior"
            ),
        },
        "smerc_stage": {
            "posture": decision["posture"],
            "reason_codes": decision["reason_codes"],
            "replay_id": decision["replay_id"],
        },
        "sparta_stage": {
            "route_state": route_state,
            "executable": executable,
            "proxy_action": decision["proxy_action"],
            "should_forward_tool_call": decision["should_forward_tool_call"],
            "controls": decision["controls"],
        },
        "dll_stage": {
            "decision_id": ledger["decision_id"],
            "record_count": ledger["record_count"],
            "verification": ledger["verification"],
            "latest_record_hash": ledger["records"][-1]["record_hash"],
        },
        "reason_codes": decision["reason_codes"],
    }


def _build_ledger(decision: Mapping[str, Any], gateway: Mapping[str, Any], scoring_admission: str) -> Dict[str, Any]:
    ledger = DecisionLifecycleLedger(decision_id=f"ref-proof:{decision['mcp_request_id']}", tenant_id="strategic-review")
    ref_gate = decision["ref_gate"]
    ref_fields = [field for field, check in ref_gate["checks"].items() if check["value"]]
    missing_or_failed = [field for field, check in ref_gate["checks"].items() if not check["value"]]
    confidence = 0.92 if ref_gate["status"] == "pass" else 0.12
    ledger.append(
        "REQUEST",
        decision["agent_id"],
        {
            "initiated_by": decision["agent_id"],
            "requested_operation": decision["tool_name"],
            "environment": decision["profile"],
            "risk_profile": {"risk_tier": decision["risk_tier"], "requested_scope_units": decision["requested_scope_units"]},
        },
    )
    ledger.append(
        "EVIDENCE",
        "ref_gate",
        {
            "available_evidence": ref_fields or ["none"],
            "confidence_score": confidence,
            "missing_evidence": missing_or_failed,
            "external_dependencies": [decision["server_name"]],
            "model_version": "not_applicable_ref_gate_is_mechanical",
            "policy_version": gateway["version"],
        },
    )
    ledger.append(
        "EVALUATION",
        "smerc_runtime",
        {
            "structural_state": scoring_admission,
            "entropy_indicators": decision["gateway_pressure"]["drivers"] or ["none"],
            "recoverability_score": max(0.0, round(1.0 - float(decision["gateway_pressure"]["score"]), 3)),
            "authorization_recommendation": decision["posture"],
            "reason_codes": decision["reason_codes"] or ["none"],
            "recommended_safeguards": decision["controls"] or ["continue_monitoring"],
        },
    )
    ledger.append(
        "EXECUTION",
        "sparta_router",
        {
            "executed_operation": decision["tool_name"],
            "execution_status": "not_executed" if not decision["should_forward_tool_call"] else "succeeded",
            "started_at": _now(),
            "duration_ms": 0,
            "rollback_performed": False,
            "rollback_success": None,
        },
    )
    ledger.append(
        "OUTCOME",
        "strategic_review",
        {
            "judged_correct": True,
            "unexpected_consequences": False,
            "controls_sufficient": decision["posture"] != "ALLOW" or ref_gate["status"] == "pass",
            "cost_incurred": 0,
            "time_to_recover_minutes": 0,
            "customer_impact": "not_measured_synthetic_review",
            "security_impact": "not_measured_synthetic_review",
            "financial_impact": "not_measured_synthetic_review",
        },
    )
    payload = ledger.to_dict()
    payload["verification"] = ledger.verify()
    return payload


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the SMERC Ref-gated runtime proof loop.")
    parser.add_argument("--registry", default="examples/mcp/governance_gateway_registry.json")
    parser.add_argument("--session", default="examples/mcp/governance_gateway_session.json")
    parser.add_argument("--mode", default="shadow", choices=["shadow", "enforce"])
    parser.add_argument("--json-output", default="reports/ref_gated_runtime_proof.json")
    parser.add_argument("--markdown-output", default="reports/Ref_Gated_Runtime_Proof.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_ref_gated_runtime_proof(
        registry=load_json(args.registry),
        session=load_json(args.session),
        mode=args.mode,
    )
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

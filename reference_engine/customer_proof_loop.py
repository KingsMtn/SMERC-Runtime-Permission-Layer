from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.recoverability_engine import evaluate_action
from reference_engine.runtime_admission_gate import (
    RUNTIME_ADMISSION_GATE_VERSION,
    evaluate_runtime_admission_gate,
)
from reference_engine.sparta_router import SPARTaRouter


CUSTOMER_PROOF_LOOP_VERSION = "smerc.customer-proof-loop.v1"
CUSTOMER_PROOF_LOOP_INPUT_VERSION = "smerc.customer-proof-loop-input.v1"


def build_customer_proof_loop(payload: Mapping[str, Any]) -> Dict[str, Any]:
    data = _object(payload, "customer_proof_loop")
    if data.get("version") != CUSTOMER_PROOF_LOOP_INPUT_VERSION:
        raise ValueError(f"customer_proof_loop.version must be {CUSTOMER_PROOF_LOOP_INPUT_VERSION}")

    generated_at = _now()
    tenant_id = _text(data.get("tenant_id", "customer-proof"), "tenant_id", 128)
    action = _object(data.get("action"), "action")
    plan = _object(data.get("sparta_plan"), "sparta_plan")
    admission = evaluate_runtime_admission_gate(_object(data.get("admission"), "admission"))

    admitted = admission["decision"] == "ADMIT"
    if admitted:
        recoverability_decision = evaluate_action(action, domain_profile=data.get("domain_profile", "general"))
        recoverability_stage = {
            "skipped": False,
            "reason": "runtime_admission_passed",
        }
    else:
        recoverability_decision = _fail_closed_decision(admission, action)
        recoverability_stage = {
            "skipped": True,
            "reason": "runtime_admission_failed_or_escalated",
        }

    route = SPARTaRouter().route(recoverability_decision, plan)
    ledger = _build_ledger(
        tenant_id=tenant_id,
        admission=admission,
        action=action,
        plan=plan,
        decision=recoverability_decision,
        route=route,
        generated_at=generated_at,
    )
    ledger_dict = ledger.to_dict()

    summary = _summary(admission, recoverability_decision, route, ledger_dict, recoverability_stage)
    report = {
        "version": CUSTOMER_PROOF_LOOP_VERSION,
        "generated_at": generated_at,
        "tenant_id": tenant_id,
        "summary": summary,
        "admission": admission,
        "recoverability_stage": recoverability_stage,
        "recoverability_decision": recoverability_decision,
        "sparta_route": route,
        "decision_lifecycle_ledger": ledger_dict,
    }
    report["markdown_report"] = render_markdown_report(report)
    return report


def write_customer_proof_loop(report: Mapping[str, Any], output_dir: str | Path) -> Dict[str, str]:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    json_path = path / "customer_proof_loop.json"
    markdown_path = path / "Customer_Proof_Loop_Report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(str(report["markdown_report"]), encoding="utf-8")
    return {
        "json": str(json_path),
        "markdown": str(markdown_path),
    }


def render_markdown_report(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    admission = report["admission"]
    decision = report["recoverability_decision"]
    route = report["sparta_route"]
    ledger = report["decision_lifecycle_ledger"]
    return "\n".join(
        [
            "# SMERC Customer Proof Loop Report",
            "",
            f"Generated: `{report['generated_at']}`",
            f"Tenant: `{report['tenant_id']}`",
            "",
            "## Result",
            "",
            f"- Overall status: **{summary['overall_status']}**",
            f"- Runtime admission: **{admission['decision']}**",
            f"- Recoverability posture: **{decision['posture']}**",
            f"- SPARTa route: **{route['route_state']}**",
            f"- Ledger valid: **{ledger['verification']['valid']}**",
            "",
            "## Pass/Fail Checks",
            "",
            "| Check | Result |",
            "| --- | --- |",
            f"| Hard runtime gates passed | `{summary['hard_gates_passed']}` |",
            f"| Recoverability permits progression | `{summary['recoverability_permits_progression']}` |",
            f"| Route executable | `{summary['route_executable']}` |",
            f"| Ledger valid | `{summary['ledger_valid']}` |",
            "",
            "## Reason Codes",
            "",
            *[f"- `{code}`" for code in summary["reason_codes"]],
            "",
            "## Controls",
            "",
            *[f"- `{control}`" for control in summary["controls"]],
            "",
            "## Plain English",
            "",
            summary["plain_english_summary"],
            "",
            "## Evidence Artifacts",
            "",
            "- Full JSON evidence bundle: `customer_proof_loop.json`",
            "- Replayable lifecycle chain: `decision_lifecycle_ledger` inside the JSON bundle",
            "",
        ]
    )


def _build_ledger(
    *,
    tenant_id: str,
    admission: Mapping[str, Any],
    action: Mapping[str, Any],
    plan: Mapping[str, Any],
    decision: Mapping[str, Any],
    route: Mapping[str, Any],
    generated_at: str,
) -> DecisionLifecycleLedger:
    metadata = _object(plan.get("metadata", {}), "sparta_plan.metadata")
    scores = _object(decision.get("scores", {}), "decision.scores")
    action_id = _text(str(action.get("action_id", "unknown-action")), "action.action_id", 160)
    ledger = DecisionLifecycleLedger(
        decision_id=f"customer-proof:{admission['request_id']}",
        tenant_id=tenant_id,
    )
    ledger.append(
        "REQUEST",
        actor=_text(str(action.get("actor", "unknown-actor")), "action.actor", 128),
        payload={
            "initiated_by": str(action.get("actor", "unknown-actor")),
            "requested_operation": str(action.get("action_type", plan.get("action", action_id))),
            "environment": str(metadata.get("environment", "unknown")),
            "risk_profile": {
                "action_id": action_id,
                "base_action_risk": action.get("base_action_risk"),
                "impact_scope": action.get("impact_scope"),
                "admission_decision": admission["decision"],
            },
        },
    )
    ledger.append(
        "EVIDENCE",
        actor="smerc.runtime_admission_gate",
        payload={
            "available_evidence": [
                check
                for check, result in admission["checks"].items()
                if result["value"] and result["source"] == "explicit"
            ],
            "confidence_score": float(scores.get("confidence_score", 0.0 if admission["decision"] != "ADMIT" else 1.0)),
            "missing_evidence": admission["missing_required_checks"] + admission["failed_required_checks"],
            "external_dependencies": [str(action.get("tool", "unknown_tool")), str(plan.get("tool", "unknown_plan"))],
            "model_version": "deterministic_reference_engine",
            "policy_version": RUNTIME_ADMISSION_GATE_VERSION,
        },
    )
    ledger.append(
        "EVALUATION",
        actor="smerc.customer_proof_loop",
        payload={
            "structural_state": "runtime_admitted" if admission["decision"] == "ADMIT" else "runtime_not_admitted",
            "entropy_indicators": list(decision.get("reason_codes", [])),
            "recoverability_score": float(scores.get("reversible_capacity_score", 0.0)),
            "authorization_recommendation": decision["posture"],
            "reason_codes": list(decision.get("reason_codes", [])),
            "recommended_safeguards": list(decision.get("controls", [])),
        },
    )
    ledger.append(
        "EXECUTION",
        actor="smerc.sparta_router",
        payload={
            "executed_operation": str(plan.get("action", "unknown_action")),
            "execution_status": "not_executed" if route["executable"] else "blocked",
            "started_at": generated_at,
            "duration_ms": 0,
            "rollback_performed": False,
            "rollback_success": None,
        },
    )
    return ledger


def _summary(
    admission: Mapping[str, Any],
    decision: Mapping[str, Any],
    route: Mapping[str, Any],
    ledger: Mapping[str, Any],
    recoverability_stage: Mapping[str, Any],
) -> Dict[str, Any]:
    hard_gates_passed = admission["decision"] == "ADMIT"
    recoverability_permits_progression = decision["posture"] in {"ALLOW", "THROTTLE"}
    route_executable = bool(route["executable"])
    ledger_valid = bool(ledger["verification"]["valid"])
    overall_status = (
        "PASS"
        if hard_gates_passed and recoverability_permits_progression and route_executable and ledger_valid
        else "REVIEW"
    )
    reason_codes = list(admission["reason_codes"]) + list(decision.get("reason_codes", [])) + list(route["reason_codes"])
    controls = list(admission["required_controls"]) + list(decision.get("controls", [])) + list(route["applied_controls"])
    skipped = " Recoverability scoring was skipped because admission did not pass." if recoverability_stage["skipped"] else ""
    return {
        "overall_status": overall_status,
        "hard_gates_passed": hard_gates_passed,
        "recoverability_permits_progression": recoverability_permits_progression,
        "route_executable": route_executable,
        "ledger_valid": ledger_valid,
        "reason_codes": sorted(set(reason_codes)),
        "controls": sorted(set(controls)),
        "plain_english_summary": (
            f"Runtime admission returned {admission['decision']}. "
            f"SMERC posture is {decision['posture']}. "
            f"SPARTa route is {route['route_state']}. "
            f"The lifecycle ledger is valid: {ledger_valid}."
            f"{skipped}"
        ),
    }


def _fail_closed_decision(admission: Mapping[str, Any], action: Mapping[str, Any]) -> Dict[str, Any]:
    action_id = str(action.get("action_id", "admission_failed_action"))
    return {
        "action_id": action_id,
        "replay_id": f"admission_gate_{admission['request_id']}",
        "posture": admission["max_recommended_posture"],
        "enforcement_state": "block" if admission["max_recommended_posture"] == "DENY" else "pause",
        "scores": {
            "irreversible_exposure_score": 1.0,
            "reversible_capacity_score": 0.0,
            "confidence_score": 0.0,
            "operational_stress_score": 1.0,
            "risk_adjusted_authorization_score": 0.0,
            "cancel_reliability_score": 0.0,
        },
        "reason_codes": list(admission["reason_codes"]),
        "controls": list(admission["required_controls"]),
        "plain_english_summary": admission["plain_english_summary"],
        "decision_trace": {
            "runtime_admission_gate": admission,
            "recoverability_scoring": "skipped_fail_closed",
        },
    }


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    return dict(value)


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SMERC one-command customer proof loop.")
    parser.add_argument("input", type=Path, help="Path to a customer proof loop JSON input.")
    parser.add_argument("--output-dir", type=Path, default=Path("reports/customer_proof_loop"))
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the evidence bundle to stdout.")
    args = parser.parse_args()

    report = build_customer_proof_loop(json.loads(args.input.read_text(encoding="utf-8")))
    paths = write_customer_proof_loop(report, args.output_dir)
    stdout = {"summary": report["summary"], "written": paths}
    print(json.dumps(stdout if not args.pretty else {**stdout, "report": report}, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

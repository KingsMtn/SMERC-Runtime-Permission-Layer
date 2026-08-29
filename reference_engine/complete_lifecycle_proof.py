from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.action_language import action_hash, evaluate_language_action
from reference_engine.authorization_permit import PermitSigner
from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.policy import PolicyThresholds, RuntimePolicy
from reference_engine.recoverability_engine import RecoverabilityEngine
from reference_engine.recovery_authority_gate import evaluate_recovery_authority
from reference_engine.runtime_admission_gate import evaluate_runtime_admission_gate
from reference_engine.sparta_router import SPARTaRouter


COMPLETE_LIFECYCLE_PROOF_VERSION = "smerc.complete-lifecycle-proof.v1"
COMPLETE_LIFECYCLE_INPUT_VERSION = "smerc.complete-lifecycle-input.v1"


def load_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_complete_lifecycle_proof(payload: Mapping[str, Any]) -> Dict[str, Any]:
    data = _object(payload, "complete_lifecycle")
    if data.get("version") != COMPLETE_LIFECYCLE_INPUT_VERSION:
        raise ValueError(f"complete_lifecycle.version must be {COMPLETE_LIFECYCLE_INPUT_VERSION}")

    generated_at = _now()
    tenant_id = _text(data.get("tenant_id", "alpha"), "tenant_id", 128)
    audience = _text(data.get("executor_audience", "github-actions-deployer"), "executor_audience", 128)
    admission = evaluate_runtime_admission_gate(_object(data["admission"], "admission"))
    proposed_action = _object(data["proposed_action"], "proposed_action")
    continuation_action = _object(data["continuation_action"], "continuation_action")
    initial_plan = _object(data["initial_sparta_plan"], "initial_sparta_plan")
    continuation_plan = _object(data["continuation_sparta_plan"], "continuation_sparta_plan")

    policy = _enforcement_policy(tenant_id)
    engine = RecoverabilityEngine(policy)

    if admission["decision"] == "ADMIT":
        initial_decision = evaluate_language_action(copy.deepcopy(proposed_action), engine)
        admission_skipped_scoring = False
    else:
        initial_decision = _admission_fail_closed_decision(admission, proposed_action, tenant_id, policy)
        admission_skipped_scoring = True
    initial_decision["tenant_id"] = tenant_id
    initial_route = SPARTaRouter().route(initial_decision, initial_plan)

    unlock_case = _unlock_case(
        data=data,
        paused_decision=initial_decision,
        proposed_action=proposed_action,
    )
    unlock_report = evaluate_recovery_authority(unlock_case)

    if unlock_report["recovery_authority"]["state"] in {"UNLOCK", "UNLOCK_CONSTRAINED"}:
        continuation_decision = evaluate_language_action(copy.deepcopy(continuation_action), engine)
        continuation_decision["tenant_id"] = tenant_id
        continuation_route = SPARTaRouter().route(continuation_decision, continuation_plan)
        permit = _issue_and_verify_permit(
            decision=continuation_decision,
            action=continuation_action,
            tenant_id=tenant_id,
            audience=audience,
            controls=sorted(
                set(continuation_decision["controls"])
                | set(continuation_route["applied_controls"])
            ),
        )
        execution = _execution_result(continuation_route, permit["permit"]["permit_id"], generated_at)
    else:
        continuation_decision = None
        continuation_route = None
        permit = None
        execution = _blocked_execution(unlock_report, generated_at)

    ledger = _build_ledger(
        tenant_id=tenant_id,
        admission=admission,
        proposed_action=proposed_action,
        initial_decision=initial_decision,
        initial_route=initial_route,
        unlock_report=unlock_report,
        continuation_decision=continuation_decision,
        continuation_route=continuation_route,
        permit=permit,
        execution=execution,
        generated_at=generated_at,
    )
    ledger_dict = ledger.to_dict()

    summary = _summary(
        admission=admission,
        initial_decision=initial_decision,
        initial_route=initial_route,
        unlock_report=unlock_report,
        continuation_decision=continuation_decision,
        continuation_route=continuation_route,
        permit=permit,
        execution=execution,
        ledger=ledger_dict,
        admission_skipped_scoring=admission_skipped_scoring,
    )
    report = {
        "version": COMPLETE_LIFECYCLE_PROOF_VERSION,
        "generated_at": generated_at,
        "tenant_id": tenant_id,
        "summary": summary,
        "runtime_admission": admission,
        "initial_decision": initial_decision,
        "initial_sparta_route": initial_route,
        "recovery_authority_gate": unlock_report,
        "continuation_decision": continuation_decision,
        "continuation_sparta_route": continuation_route,
        "action_bound_permit": permit,
        "execution_result": execution,
        "decision_lifecycle_ledger": ledger_dict,
    }
    report["markdown_report"] = render_markdown(report)
    return report


def write_outputs(report: Mapping[str, Any], output_dir: str | Path) -> Dict[str, str]:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    json_path = path / "complete_lifecycle_proof.json"
    markdown_path = path / "Complete_Lifecycle_Proof_Report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(str(report["markdown_report"]), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    return "\n".join(
        [
            "# SMERC Complete Lifecycle Proof Report",
            "",
            f"Generated: `{report['generated_at']}`",
            f"Tenant: `{report['tenant_id']}`",
            "",
            "## Work / Result / Impact",
            "",
            "Work: run one proposed automated action through runtime admission, recoverability scoring, SPARTa routing, Recovery Authority Gate, action-bound permit issuance, execution simulation, and Decision Lifecycle Ledger evidence.",
            "",
            f"Result: `{summary['overall_status']}` with initial posture `{summary['initial_posture']}`, unlock state `{summary['unlock_state']}`, continuation posture `{summary['continuation_posture']}`, and ledger validity `{summary['ledger_valid']}`.",
            "",
            "Impact: reviewers can inspect SMERC as a connected lifecycle instead of scattered modules. The proof shows that a paused action cannot unlock itself; continuation requires separate authority, fresh recovery evidence, a bounded route, a short-lived permit, and a replayable ledger.",
            "",
            "## Lifecycle",
            "",
            "| Stage | State |",
            "| --- | --- |",
            f"| Runtime admission | `{summary['runtime_admission']}` |",
            f"| Initial SMERC posture | `{summary['initial_posture']}` |",
            f"| Initial SPARTa route | `{summary['initial_route']}` |",
            f"| Recovery Authority Gate | `{summary['unlock_state']}` |",
            f"| Continuation SMERC posture | `{summary['continuation_posture']}` |",
            f"| Continuation SPARTa route | `{summary['continuation_route']}` |",
            f"| Permit issued | `{summary['permit_issued']}` |",
            f"| Permit verified | `{summary['permit_verified']}` |",
            f"| Execution status | `{summary['execution_status']}` |",
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
            "## Boundary",
            "",
            "This is a deterministic, metadata-only lifecycle proof. It does not execute production commands, prove production safety, certify compliance, validate customer demand, or prove incident reduction.",
            "",
        ]
    )


def _unlock_case(
    *,
    data: Mapping[str, Any],
    paused_decision: Mapping[str, Any],
    proposed_action: Mapping[str, Any],
) -> Dict[str, Any]:
    supplied = _object(data["recovery_authority"], "recovery_authority")
    result = copy.deepcopy(supplied)
    result["paused_decision"] = {
        "posture": paused_decision["posture"],
        "replay_id": paused_decision["replay_id"],
        "action_hash": paused_decision["action_hash"],
        "proposing_actor_id": proposed_action["action"]["actor"],
    }
    return result


def _issue_and_verify_permit(
    *,
    decision: Mapping[str, Any],
    action: Mapping[str, Any],
    tenant_id: str,
    audience: str,
    controls: list[str],
) -> Dict[str, Any]:
    signer = PermitSigner("complete-lifecycle-demo", b"c" * 32)
    issued = signer.issue(decision, action, tenant_id=tenant_id, audience=audience, ttl_seconds=120, now=1_000)
    verified = signer.verify(
        issued["permit_token"],
        action,
        tenant_id=tenant_id,
        audience=audience,
        enforced_controls=controls,
        now=1_030,
    )
    return {
        "permit": issued["permit"],
        "verified": True,
        "verification": {
            "permit_id": verified["permit_id"],
            "audience": verified["audience"],
            "authorization": verified["authorization"],
            "required_controls": verified["required_controls"],
        },
    }


def _execution_result(route: Mapping[str, Any], permit_id: str, generated_at: str) -> Dict[str, Any]:
    return {
        "execution_status": "succeeded" if route["executable"] else "blocked",
        "executed_operation": route["tool_plan"]["action"],
        "started_at": generated_at,
        "duration_ms": 37,
        "permit_id": permit_id,
        "rollback_performed": False,
        "rollback_success": None,
        "notes": "Synthetic execution result for lifecycle proof only.",
    }


def _blocked_execution(unlock_report: Mapping[str, Any], generated_at: str) -> Dict[str, Any]:
    return {
        "execution_status": "blocked",
        "executed_operation": "none",
        "started_at": generated_at,
        "duration_ms": 0,
        "permit_id": None,
        "rollback_performed": False,
        "rollback_success": None,
        "notes": f"Continuation blocked by Recovery Authority Gate: {unlock_report['recovery_authority']['state']}.",
    }


def _build_ledger(
    *,
    tenant_id: str,
    admission: Mapping[str, Any],
    proposed_action: Mapping[str, Any],
    initial_decision: Mapping[str, Any],
    initial_route: Mapping[str, Any],
    unlock_report: Mapping[str, Any],
    continuation_decision: Mapping[str, Any] | None,
    continuation_route: Mapping[str, Any] | None,
    permit: Mapping[str, Any] | None,
    execution: Mapping[str, Any],
    generated_at: str,
) -> DecisionLifecycleLedger:
    action = proposed_action["action"]
    scores = initial_decision.get("scores", {})
    final_posture = (
        continuation_decision["posture"]
        if continuation_decision is not None
        else initial_decision["posture"]
    )
    ledger = DecisionLifecycleLedger(
        decision_id=f"complete-lifecycle:{admission['request_id']}",
        tenant_id=tenant_id,
    )
    ledger.append(
        "REQUEST",
        actor=action["actor"],
        payload={
            "initiated_by": action["actor"],
            "requested_operation": action["type"],
            "environment": action["target"]["environment"],
            "risk_profile": {
                "action_id": action["id"],
                "target": action["target"],
                "admission_decision": admission["decision"],
            },
        },
    )
    ledger.append(
        "EVIDENCE",
        actor="smerc.runtime_admission_gate",
        payload={
            "available_evidence": [
                key
                for key, result in admission["checks"].items()
                if result["value"] and result["source"] == "explicit"
            ],
            "confidence_score": float(scores.get("confidence_score", 0.0)),
            "missing_evidence": admission["missing_required_checks"] + admission["failed_required_checks"],
            "external_dependencies": [action["tool"], initial_route["tool_plan"]["tool"]],
            "model_version": "deterministic_reference_engine",
            "policy_version": "smerc.complete-lifecycle-proof.v1",
        },
    )
    ledger.append(
        "EVALUATION",
        actor="smerc.complete_lifecycle_proof",
        payload={
            "structural_state": f"{admission['decision']}->{initial_route['route_state']}->{unlock_report['recovery_authority']['state']}",
            "entropy_indicators": list(initial_decision.get("reason_codes", [])),
            "recoverability_score": float(scores.get("reversible_capacity_score", 0.0)),
            "authorization_recommendation": initial_decision["posture"],
            "reason_codes": list(initial_decision.get("reason_codes", [])),
            "recommended_safeguards": list(initial_decision.get("controls", [])),
        },
    )
    ledger.append(
        "HUMAN_INTERACTION",
        actor="smerc.recovery_authority_gate",
        payload={
            "interaction": "modified",
            "reviewer_id": unlock_report["unlock_actor"]["actor_id"],
            "original_recommendation": initial_decision["posture"],
            "final_recommendation": final_posture,
            "rationale": f"Recovery Authority Gate returned {unlock_report['recovery_authority']['state']}.",
        },
    )
    ledger.append(
        "EXECUTION",
        actor="smerc.execution_adapter.synthetic",
        payload={
            "executed_operation": execution["executed_operation"],
            "execution_status": execution["execution_status"],
            "started_at": generated_at,
            "duration_ms": execution["duration_ms"],
            "rollback_performed": execution["rollback_performed"],
            "rollback_success": execution["rollback_success"],
        },
    )
    ledger.append(
        "OUTCOME",
        actor="smerc.complete_lifecycle_proof",
        payload={
            "judged_correct": True,
            "unexpected_consequences": False,
            "controls_sufficient": bool(permit and permit.get("verified")),
            "cost_incurred": 0,
            "time_to_recover_minutes": 0,
            "customer_impact": "none_synthetic",
            "security_impact": "paused_then_verified_unlock",
            "financial_impact": "none_synthetic",
        },
    )
    ledger.append(
        "LEARNING_RECOMMENDATION",
        actor="smerc.dll",
        payload={
            "expected_outcome": "paused action continues only through separate unlock authority",
            "actual_outcome": f"unlock={unlock_report['recovery_authority']['state']}; execution={execution['execution_status']}",
            "prediction_error": "not_measured_synthetic",
            "human_override_effectiveness": "requires_real_reviewer_labels",
            "recommended_policy_updates": ["Require Recovery Authority Gate before permitting paused actions."],
            "confidence_calibration_changes": ["Collect real reviewer labels before changing thresholds."],
            "suggested_rule_modifications": ["Keep self-unlock attempts as DENY_UNLOCK."],
            "activation_status": "requires_review",
        },
    )
    return ledger


def _summary(
    *,
    admission: Mapping[str, Any],
    initial_decision: Mapping[str, Any],
    initial_route: Mapping[str, Any],
    unlock_report: Mapping[str, Any],
    continuation_decision: Mapping[str, Any] | None,
    continuation_route: Mapping[str, Any] | None,
    permit: Mapping[str, Any] | None,
    execution: Mapping[str, Any],
    ledger: Mapping[str, Any],
    admission_skipped_scoring: bool,
) -> Dict[str, Any]:
    permit_issued = permit is not None
    permit_verified = bool(permit and permit.get("verified"))
    ledger_valid = bool(ledger["verification"]["valid"])
    complete = (
        admission["decision"] == "ADMIT"
        and initial_decision["posture"] in {"FREEZE", "ESCALATE"}
        and unlock_report["recovery_authority"]["state"] in {"UNLOCK", "UNLOCK_CONSTRAINED"}
        and continuation_decision is not None
        and continuation_decision["posture"] in {"ALLOW", "THROTTLE"}
        and continuation_route is not None
        and continuation_route["executable"]
        and permit_issued
        and permit_verified
        and execution["execution_status"] == "succeeded"
        and ledger_valid
    )
    reason_codes = (
        list(admission["reason_codes"])
        + list(initial_decision.get("reason_codes", []))
        + list(initial_route["reason_codes"])
        + list(unlock_report["recovery_authority"]["drivers"])
        + ([] if continuation_decision is None else list(continuation_decision.get("reason_codes", [])))
        + ([] if continuation_route is None else list(continuation_route["reason_codes"]))
    )
    controls = (
        list(admission["required_controls"])
        + list(initial_decision.get("controls", []))
        + list(initial_route["applied_controls"])
        + ([] if continuation_decision is None else list(continuation_decision.get("controls", [])))
        + ([] if continuation_route is None else list(continuation_route["applied_controls"]))
    )
    return {
        "overall_status": "COMPLETE" if complete else "REVIEW",
        "runtime_admission": admission["decision"],
        "admission_skipped_scoring": admission_skipped_scoring,
        "initial_posture": initial_decision["posture"],
        "initial_route": initial_route["route_state"],
        "unlock_state": unlock_report["recovery_authority"]["state"],
        "continuation_posture": continuation_decision["posture"] if continuation_decision else "none",
        "continuation_route": continuation_route["route_state"] if continuation_route else "none",
        "permit_issued": permit_issued,
        "permit_verified": permit_verified,
        "execution_status": execution["execution_status"],
        "ledger_valid": ledger_valid,
        "reason_codes": sorted(set(reason_codes)) or ["none"],
        "controls": sorted(set(controls)) or ["none"],
    }


def _admission_fail_closed_decision(
    admission: Mapping[str, Any],
    action: Mapping[str, Any],
    tenant_id: str,
    policy: RuntimePolicy,
) -> Dict[str, Any]:
    return {
        "action_id": action["action"]["id"],
        "replay_id": f"admission_gate_{admission['request_id']}",
        "tenant_id": tenant_id,
        "action_hash": action_hash(dict(action)),
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
        "policy": policy.decision_metadata(),
    }


def _enforcement_policy(tenant_id: str) -> RuntimePolicy:
    return RuntimePolicy(
        tenant_id=tenant_id,
        policy_id="complete-lifecycle-proof-policy",
        policy_revision="1.0.0",
        mode="ENFORCE",
        evidence_program_id="complete-lifecycle-proof",
        evidence_ceiling="LIMITED_ENFORCE",
        fail_behavior="fail_closed",
        approved_by_role="security-architecture",
        effective_at="2026-08-29T00:00:00Z",
        thresholds=PolicyThresholds(),
    )


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
    parser = argparse.ArgumentParser(description="Run the complete SMERC lifecycle proof.")
    parser.add_argument("--case", default="examples/complete_lifecycle/lifecycle_case.json")
    parser.add_argument("--output-dir", default="reports/complete_lifecycle")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_complete_lifecycle_proof(load_json(args.case))
    paths = write_outputs(report, args.output_dir)
    stdout = {"summary": report["summary"], "written": paths}
    print(json.dumps(stdout if not args.pretty else {**stdout, "report": report}, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

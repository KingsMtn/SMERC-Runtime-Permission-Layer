from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, TypeVar

from reference_engine.action_language import evaluate_language_action
from reference_engine.constraint_eligibility import evaluate_constraint_eligibility
from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.dll_intelligence import analyze_ledgers
from reference_engine.spark_intake import build_intake_report
from reference_engine.sparta_router import route_decision, route_report_digest
from reference_engine.timing_evidence import build_timing_report


PILOT_INSTALLER_VERSION = "smerc.github-actions-pilot-installer.v1"
T = TypeVar("T")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPARK_EVIDENCE = ROOT / "examples" / "spark" / "github_actions_spark_evidence.json"
DEFAULT_SPARTA_PLAN = ROOT / "examples" / "sparta" / "github_actions_deploy_plan.json"
DEFAULT_TIMING_EVIDENCE = ROOT / "examples" / "timing" / "github_actions_timing_evidence.json"


def build_pilot_package(
    *,
    spark_evidence: Mapping[str, Any],
    sparta_plan: Mapping[str, Any],
    timing_evidence: Mapping[str, Any],
) -> Dict[str, Any]:
    started = time.perf_counter()
    spark_report, spark_latency_ms = _measure(lambda: build_intake_report(spark_evidence))
    action_language = spark_report["action_language"]
    eligibility, eligibility_latency_ms = _measure(lambda: evaluate_constraint_eligibility(action_language))
    raw_decision, decision_latency_ms = _measure(lambda: evaluate_language_action(action_language))
    effective_decision = apply_eligibility_gate(raw_decision, eligibility)
    route_report, route_latency_ms = _measure(lambda: route_decision(_decision_for_sparta(effective_decision), sparta_plan))
    ledger, ledger_latency_ms = _measure(
        lambda: build_pilot_ledger(
            spark_report=spark_report,
            eligibility=eligibility,
            decision=effective_decision,
            route_report=route_report,
        )
    )
    ledger_data = ledger.to_dict()
    dll_intelligence, dll_latency_ms = _measure(lambda: analyze_ledgers([ledger_data]))
    timing_report, timing_latency_ms = _measure(lambda: build_timing_report(timing_evidence))
    total_generation_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "version": PILOT_INSTALLER_VERSION,
        "generated_at": _now(),
        "mode": "shadow_mode_demo_package",
        "primary_workflow": "GitHub Actions",
        "package_summary": {
            "action_id": action_language["action"]["id"],
            "constraint_eligible": eligibility["constraint_eligible"],
            "eligibility_labels": eligibility["eligibility_labels"],
            "raw_engine_posture": raw_decision["posture"],
            "effective_posture": effective_decision["posture"],
            "route_state": route_report["route_state"],
            "route_executable": route_report["executable"],
            "timing_status": timing_report["operational_status"],
            "ledger_valid": ledger_data["verification"]["valid"],
        },
        "artifacts": {
            "spark_intake_report": spark_report,
            "constraint_eligibility": eligibility,
            "raw_decision": raw_decision,
            "effective_decision": effective_decision,
            "sparta_route": {
                "route_report": route_report,
                "route_report_digest": route_report_digest(route_report),
            },
            "decision_lifecycle_ledger": ledger_data,
            "dll_intelligence": dll_intelligence,
            "timing_report": timing_report,
        },
        "pilot_runbook": [
            "Select one GitHub Actions workflow with real side effects and existing review expectations.",
            "Run SMERC in observe mode first; do not block production workflow execution.",
            "Collect non-secret SPARK evidence from repository, workflow, policy, identity, and rollback context.",
            "Evaluate constraint eligibility before recoverability scoring.",
            "Compare raw SMERC posture, eligibility-adjusted posture, SPARTa route, and existing reviewer judgment.",
            "Record timing, unavailable evaluations, reviewer agreement, false release candidates, false constraint candidates, and useful constraint examples.",
            "Move to recommend or enforce only after reviewer agreement and latency evidence justify it.",
        ],
        "customer_success_metrics": {
            "minimum_sample_size_before_claims": 25,
            "reviewer_agreement_rate": "measured during pilot",
            "false_release_rate": "measured during pilot",
            "false_constraint_rate": "measured during pilot",
            "useful_constraint_rate": "measured during pilot",
            "median_decision_latency_ms": "measured during pilot",
            "p95_decision_latency_ms": "measured during pilot",
            "workflow_overhead_ms": "measured during pilot",
            "unavailable_evaluation_rate": "measured during pilot",
        },
        "local_generation_latency": {
            "version": "smerc.pilot-installer-latency.v1",
            "unit": "milliseconds",
            "spark_intake_ms": spark_latency_ms,
            "constraint_eligibility_ms": eligibility_latency_ms,
            "decision_ms": decision_latency_ms,
            "sparta_route_ms": route_latency_ms,
            "ledger_ms": ledger_latency_ms,
            "dll_intelligence_ms": dll_latency_ms,
            "timing_report_ms": timing_latency_ms,
            "total_generation_ms": total_generation_ms,
            "boundary": "Local artifact generation time only. Customer workflow pilots must measure real runner, API, storage, and reviewer latency.",
        },
        "evidence_boundary": [
            "This package is a runnable pilot artifact generator, not production certification.",
            "The default examples are synthetic and metadata-only.",
            "A customer pilot must replace examples with customer-approved non-secret workflow evidence.",
            "SMERC must remain in observe mode until customer reviewer agreement, latency, and failure-mode evidence justify stronger operation.",
        ],
    }


def apply_eligibility_gate(decision: Mapping[str, Any], eligibility: Mapping[str, Any]) -> Dict[str, Any]:
    result = dict(decision)
    result["constraint_eligibility"] = {
        "language_version": eligibility["language_version"],
        "constraint_eligible": eligibility["constraint_eligible"],
        "eligibility_labels": eligibility["eligibility_labels"],
        "recommended_runtime_posture": eligibility["recommended_runtime_posture"],
    }
    recommended = str(eligibility["recommended_runtime_posture"])
    if not eligibility["constraint_eligible"] and _posture_rank(recommended) > _posture_rank(str(decision["posture"])):
        result["raw_posture_before_eligibility"] = decision["posture"]
        result["posture"] = recommended
        result["reason_codes"] = sorted(
            set(list(decision.get("reason_codes", [])) + ["CONSTRAINT_ELIGIBILITY_GATE"])
        )
        result["controls"] = _controls_for_posture(recommended)
        result["plain_english_summary"] = (
            f"Constraint Eligibility overrode raw posture {decision['posture']} to {recommended}. "
            f"Labels: {', '.join(eligibility['eligibility_labels'])}."
        )
    return result


def build_pilot_ledger(
    *,
    spark_report: Mapping[str, Any],
    eligibility: Mapping[str, Any],
    decision: Mapping[str, Any],
    route_report: Mapping[str, Any],
) -> DecisionLifecycleLedger:
    action = spark_report["action_language"]["action"]
    controls = [str(item) for item in decision.get("controls", [])]
    reason_codes = [str(item) for item in decision.get("reason_codes", [])]
    ledger = DecisionLifecycleLedger(
        f"dll_{decision['replay_id']}",
        tenant_id="github-actions-pilot-installer",
    )
    ledger.append(
        "REQUEST",
        action["actor"],
        {
            "initiated_by": action["actor"],
            "requested_operation": action["description"],
            "environment": action["target"]["environment"],
            "risk_profile": "github_actions_shadow_mode",
        },
    )
    ledger.append(
        "EVIDENCE",
        "spark-intake",
        {
            "available_evidence": list(spark_report["source_systems"]),
            "confidence_score": float(decision.get("confidence_score", 0.0)),
            "missing_evidence": list(spark_report["evidence_gaps"]),
            "external_dependencies": ["github_actions", "repository_metadata", "deployment_workflow"],
            "model_version": "metadata-only-pilot",
            "policy_version": "default-reference-policy",
        },
    )
    ledger.append(
        "EVALUATION",
        "smerc-runtime",
        {
            "structural_state": (
                f"Constraint eligibility labels {eligibility['eligibility_labels']} produced posture "
                f"{decision['posture']} before workflow execution."
            ),
            "entropy_indicators": reason_codes,
            "recoverability_score": float(decision["scores"]["reversible_capacity_score"]),
            "authorization_recommendation": decision["posture"],
            "reason_codes": reason_codes,
            "recommended_safeguards": controls,
        },
    )
    ledger.append(
        "HUMAN_INTERACTION",
        "shadow-mode-reviewer",
        {
            "interaction": "accepted",
            "reviewer_id": "shadow-mode-reviewer",
            "original_recommendation": decision["posture"],
            "final_recommendation": decision["posture"],
            "rationale": "Synthetic installer package accepts the posture so the review artifact is complete.",
        },
    )
    ledger.append(
        "EXECUTION",
        "sparta-router",
        {
            "executed_operation": f"SPARTa routed GitHub Actions plan into {route_report['route_state']}.",
            "execution_status": "succeeded" if route_report["executable"] else "blocked",
            "started_at": _now(),
            "duration_ms": 0,
            "rollback_performed": False,
            "rollback_success": None,
        },
    )
    ledger.append(
        "OUTCOME",
        "pilot-installer",
        {
            "judged_correct": True,
            "unexpected_consequences": False,
            "controls_sufficient": True,
            "cost_incurred": 0,
            "time_to_recover_minutes": 0,
            "customer_impact": "none; synthetic installer package",
            "security_impact": "none; synthetic installer package",
            "financial_impact": "none; synthetic installer package",
        },
    )
    ledger.append(
        "LEARNING_RECOMMENDATION",
        "dll-intelligence",
        {
            "expected_outcome": "Reviewer can inspect a complete GitHub Actions shadow-mode package.",
            "actual_outcome": "SPARK, eligibility, decision, SPARTa, DLL, timing, and report artifacts were generated.",
            "prediction_error": "not measured in synthetic package",
            "human_override_effectiveness": "not measured in synthetic package",
            "recommended_policy_updates": ["Collect customer reviewer labels before changing thresholds."],
            "confidence_calibration_changes": ["Do not calibrate from synthetic examples."],
            "suggested_rule_modifications": ["Replace default examples with customer-approved non-secret workflow evidence."],
            "activation_status": "requires_review",
        },
    )
    return ledger


def render_markdown(package: Mapping[str, Any]) -> str:
    summary = package["package_summary"]
    latency = package["local_generation_latency"]
    lines = [
        "# SMERC GitHub Actions Pilot Package",
        "",
        f"Generated: `{package['generated_at']}`",
        "",
        "## What This Is",
        "",
        "A self-contained shadow-mode package showing where SMERC sits in a GitHub Actions workflow before action execution.",
        "",
        "## Result",
        "",
        f"- Action: `{summary['action_id']}`",
        f"- Constraint eligible: `{summary['constraint_eligible']}`",
        f"- Eligibility labels: `{summary['eligibility_labels']}`",
        f"- Raw engine posture: `{summary['raw_engine_posture']}`",
        f"- Effective posture: `{summary['effective_posture']}`",
        f"- SPARTa route: `{summary['route_state']}`",
        f"- Route executable: `{summary['route_executable']}`",
        f"- Timing status: `{summary['timing_status']}`",
        f"- DLL valid: `{summary['ledger_valid']}`",
        "",
        "## Runtime Flow",
        "",
        "```text",
        "SPARK evidence -> Action Language -> Constraint Eligibility -> SMERC decision -> SPARTa route -> DLL -> Timing Evidence",
        "```",
        "",
        "## Pilot Runbook",
        "",
    ]
    lines.extend(f"{index}. {item}" for index, item in enumerate(package["pilot_runbook"], start=1))
    lines.extend(
        [
            "",
            "## Metrics To Collect In A Real Pilot",
            "",
        ]
    )
    for key, value in package["customer_success_metrics"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Local Generation Latency",
            "",
            f"- SPARK intake: `{latency['spark_intake_ms']}` ms",
            f"- Constraint eligibility: `{latency['constraint_eligibility_ms']}` ms",
            f"- SMERC decision: `{latency['decision_ms']}` ms",
            f"- SPARTa route: `{latency['sparta_route_ms']}` ms",
            f"- DLL: `{latency['ledger_ms']}` ms",
            f"- DLL Intelligence: `{latency['dll_intelligence_ms']}` ms",
            f"- Timing report: `{latency['timing_report_ms']}` ms",
            f"- Total generation: `{latency['total_generation_ms']}` ms",
            "",
            "## Evidence Boundary",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in package["evidence_boundary"])
    lines.append("")
    return "\n".join(lines)


def write_pilot_package(package: Mapping[str, Any], output_dir: str | Path) -> Dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "pilot_package": package,
        "spark_intake_report": package["artifacts"]["spark_intake_report"],
        "constraint_eligibility": package["artifacts"]["constraint_eligibility"],
        "effective_decision": package["artifacts"]["effective_decision"],
        "sparta_route": package["artifacts"]["sparta_route"]["route_report"],
        "decision_lifecycle_ledger": package["artifacts"]["decision_lifecycle_ledger"],
        "dll_intelligence": package["artifacts"]["dll_intelligence"],
        "timing_report": package["artifacts"]["timing_report"],
    }
    paths: Dict[str, str] = {}
    for name, payload in artifacts.items():
        path = out / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths[name] = str(path)
    briefing = out / "README.md"
    briefing.write_text(render_markdown(package), encoding="utf-8")
    paths["briefing"] = str(briefing)
    return paths


def _decision_for_sparta(decision: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "posture": decision["posture"],
        "replay_id": decision["replay_id"],
        "reason_codes": list(decision.get("reason_codes", [])),
        "controls": list(decision.get("controls", [])),
        "policy": {"source": "github_actions_pilot_installer"},
    }


def _posture_rank(posture: str) -> int:
    return {"ALLOW": 0, "THROTTLE": 1, "FREEZE": 2, "ESCALATE": 3, "DENY": 4}[posture]


def _controls_for_posture(posture: str) -> list[str]:
    return {
        "ALLOW": ["execute", "record_replay", "retain_cancel_handle"],
        "THROTTLE": ["limit_scope", "preview_before_execution", "record_replay", "require_rollback_plan"],
        "FREEZE": ["pause_execution", "collect_more_evidence", "snapshot_current_state", "preserve_replay"],
        "ESCALATE": ["route_to_accountable_reviewer", "require_explicit_approval", "preserve_replay"],
        "DENY": ["block_execution", "explain_denial", "preserve_replay", "require_new_request"],
    }[posture]


def _measure(callback: Callable[[], T]) -> tuple[T, float]:
    started = time.perf_counter()
    result = callback()
    return result, round((time.perf_counter() - started) * 1000, 3)


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a self-contained SMERC GitHub Actions pilot package.")
    parser.add_argument("--spark-evidence", type=Path, default=DEFAULT_SPARK_EVIDENCE)
    parser.add_argument("--sparta-plan", type=Path, default=DEFAULT_SPARTA_PLAN)
    parser.add_argument("--timing-evidence", type=Path, default=DEFAULT_TIMING_EVIDENCE)
    parser.add_argument("--output-dir", type=Path, default=Path("reports") / "github_actions_pilot_package")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    package = build_pilot_package(
        spark_evidence=_load_json(args.spark_evidence),
        sparta_plan=_load_json(args.sparta_plan),
        timing_evidence=_load_json(args.timing_evidence),
    )
    paths = write_pilot_package(package, args.output_dir)
    result = {
        "version": "smerc.github-actions-pilot-installer-cli.v1",
        "output_dir": str(args.output_dir),
        "paths": paths,
        "summary": package["package_summary"],
    }
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger


DLL_INTELLIGENCE_VERSION = "smerc.dll-intelligence.v1"


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 3)


def _records_by_type(ledger: Mapping[str, Any], event_type: str) -> list[Mapping[str, Any]]:
    return [record for record in ledger.get("records", []) if record.get("event_type") == event_type]


def _first_payload(ledger: Mapping[str, Any], event_type: str) -> Mapping[str, Any] | None:
    records = _records_by_type(ledger, event_type)
    if not records:
        return None
    payload = records[0].get("payload")
    return payload if isinstance(payload, dict) else None


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def load_ledgers(paths: Iterable[str | Path]) -> list[Dict[str, Any]]:
    ledgers: list[Dict[str, Any]] = []
    for path_value in paths:
        path = Path(path_value)
        payload = _load_json(path)
        if payload.get("version") == "smerc.decision-lifecycle-ledger.v1":
            ledgers.append(payload)
        elif payload.get("version") == "smerc.dll-example-bundle.v1":
            bundled = payload.get("ledgers")
            if not isinstance(bundled, list):
                raise ValueError(f"{path} example bundle is missing ledgers")
            ledgers.extend(item for item in bundled if isinstance(item, dict))
        elif payload.get("version") == "smerc.pilot-ledger-intake-result.v1":
            ledger = payload.get("ledger")
            if not isinstance(ledger, dict):
                raise ValueError(f"{path} pilot intake result is missing ledger")
            ledgers.append(ledger)
        else:
            raise ValueError(f"{path} must contain a DLL, DLL example bundle, or pilot intake result")
    if not ledgers:
        raise ValueError("at least one ledger is required")
    return ledgers


def _decision_row(ledger_payload: Mapping[str, Any]) -> Dict[str, Any]:
    ledger = DecisionLifecycleLedger.from_dict(ledger_payload)
    data = ledger.to_dict()
    request = _first_payload(data, "REQUEST") or {}
    evidence = _first_payload(data, "EVIDENCE") or {}
    evaluation = _first_payload(data, "EVALUATION") or {}
    human = _first_payload(data, "HUMAN_INTERACTION") or {}
    execution = _first_payload(data, "EXECUTION") or {}
    outcome = _first_payload(data, "OUTCOME") or {}
    learning = _first_payload(data, "LEARNING_RECOMMENDATION") or {}

    initial_posture = str(evaluation.get("authorization_recommendation", "UNKNOWN"))
    final_posture = str(human.get("final_recommendation", initial_posture))
    execution_status = execution.get("execution_status")
    rollback_performed = bool(execution.get("rollback_performed", False))
    rollback_success = execution.get("rollback_success")
    unexpected = bool(outcome.get("unexpected_consequences", False))
    controls_sufficient = outcome.get("controls_sufficient")
    judged_correct = outcome.get("judged_correct")
    interaction = human.get("interaction")

    constrained_or_escalated = final_posture in {"THROTTLE", "FREEZE", "ESCALATE", "DENY"}
    failed_but_recovered = execution_status == "failed" and rollback_performed and rollback_success is True
    near_miss = bool(constrained_or_escalated and (failed_but_recovered or not unexpected))
    recovery_failure = bool(
        (rollback_performed and rollback_success is False)
        or (unexpected and float(outcome.get("time_to_recover_minutes", 0) or 0) > 0)
    )
    override_helpful = bool(
        interaction == "overrode"
        and judged_correct is True
        and unexpected is False
        and controls_sufficient is True
    )
    override_harmful = bool(
        interaction == "overrode"
        and (judged_correct is False or unexpected is True or controls_sufficient is False)
    )

    return {
        "decision_id": data["decision_id"],
        "tenant_id": data["tenant_id"],
        "requested_operation": request.get("requested_operation"),
        "environment": request.get("environment"),
        "risk_profile": request.get("risk_profile"),
        "confidence_score": evidence.get("confidence_score"),
        "missing_evidence": _as_list(evidence.get("missing_evidence")),
        "initial_posture": initial_posture,
        "final_posture": final_posture,
        "reason_codes": _as_list(evaluation.get("reason_codes")),
        "recommended_safeguards": _as_list(evaluation.get("recommended_safeguards")),
        "interaction": interaction,
        "execution_status": execution_status,
        "rollback_performed": rollback_performed,
        "rollback_success": rollback_success,
        "judged_correct": judged_correct,
        "unexpected_consequences": unexpected,
        "controls_sufficient": controls_sufficient,
        "cost_incurred": float(outcome.get("cost_incurred", 0) or 0),
        "time_to_recover_minutes": float(outcome.get("time_to_recover_minutes", 0) or 0),
        "near_miss": near_miss,
        "recovery_failure": recovery_failure,
        "override_helpful": override_helpful,
        "override_harmful": override_harmful,
        "learning_recommendations": {
            "recommended_policy_updates": _as_list(learning.get("recommended_policy_updates")),
            "confidence_calibration_changes": _as_list(learning.get("confidence_calibration_changes")),
            "suggested_rule_modifications": _as_list(learning.get("suggested_rule_modifications")),
            "activation_status": learning.get("activation_status"),
        },
        "head_record_hash": data["head_record_hash"],
    }


def analyze_ledgers(ledger_payloads: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    rows = [_decision_row(payload) for payload in ledger_payloads]
    if not rows:
        raise ValueError("at least one ledger is required")

    posture_counts = Counter(row["initial_posture"] for row in rows)
    final_posture_counts = Counter(row["final_posture"] for row in rows)
    reason_counts: Counter[str] = Counter()
    missing_evidence_counts: Counter[str] = Counter()
    safeguard_counts: Counter[str] = Counter()
    policy_queue: list[Dict[str, Any]] = []
    for row in rows:
        reason_counts.update(row["reason_codes"])
        missing_evidence_counts.update(row["missing_evidence"])
        safeguard_counts.update(row["recommended_safeguards"])
        recommendations = row["learning_recommendations"]
        if recommendations["activation_status"] == "requires_review":
            for item in recommendations["recommended_policy_updates"]:
                policy_queue.append(
                    {
                        "source_decision_id": row["decision_id"],
                        "recommendation_type": "policy_update",
                        "recommendation": item,
                        "activation_status": "requires_review",
                    }
                )
            for item in recommendations["suggested_rule_modifications"]:
                policy_queue.append(
                    {
                        "source_decision_id": row["decision_id"],
                        "recommendation_type": "rule_modification",
                        "recommendation": item,
                        "activation_status": "requires_review",
                    }
                )

    total = len(rows)
    human_reviewed = sum(1 for row in rows if row["interaction"])
    overrides = sum(1 for row in rows if row["interaction"] == "overrode")
    executed = sum(1 for row in rows if row["execution_status"])
    rollbacks = sum(1 for row in rows if row["rollback_performed"])
    rollback_success = sum(1 for row in rows if row["rollback_success"] is True)
    outcomes = sum(1 for row in rows if row["judged_correct"] is not None)
    judged_correct = sum(1 for row in rows if row["judged_correct"] is True)
    unexpected = sum(1 for row in rows if row["unexpected_consequences"])
    controls_sufficient = sum(1 for row in rows if row["controls_sufficient"] is True)
    near_misses = [row for row in rows if row["near_miss"]]
    recovery_failures = [row for row in rows if row["recovery_failure"]]
    override_helpful = sum(1 for row in rows if row["override_helpful"])
    override_harmful = sum(1 for row in rows if row["override_harmful"])

    generated_recommendations: list[Dict[str, Any]] = []
    for evidence_name, count in missing_evidence_counts.most_common(5):
        if count >= 2:
            generated_recommendations.append(
                {
                    "recommendation_type": "recurring_missing_evidence",
                    "recommendation": f"Require or explain missing evidence item: {evidence_name}",
                    "supporting_count": count,
                    "activation_status": "requires_review",
                }
            )
    for reason_code, count in reason_counts.most_common(5):
        if count >= 2:
            generated_recommendations.append(
                {
                    "recommendation_type": "recurring_reason_code",
                    "recommendation": f"Review policy threshold or control mapping for reason code: {reason_code}",
                    "supporting_count": count,
                    "activation_status": "requires_review",
                }
            )

    drift_signals = []
    override_rate = _rate(overrides, human_reviewed)
    unexpected_rate = _rate(unexpected, outcomes)
    rollback_success_rate = _rate(rollback_success, rollbacks)
    if override_rate is not None and override_rate > 0.25:
        drift_signals.append("reviewers_override_more_than_25_percent_of_reviewed_actions")
    if unexpected_rate is not None and unexpected_rate > 0.10:
        drift_signals.append("unexpected_consequences_above_10_percent_of_outcome_reviewed_actions")
    if rollback_success_rate is not None and rollback_success_rate < 0.80:
        drift_signals.append("rollback_success_below_80_percent_when_rollback_attempted")
    if missing_evidence_counts and sum(missing_evidence_counts.values()) / total > 1.5:
        drift_signals.append("multiple_missing_evidence_items_per_decision_on_average")

    return {
        "version": DLL_INTELLIGENCE_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "summary": {
            "ledger_count": total,
            "human_reviewed_count": human_reviewed,
            "override_count": overrides,
            "override_rate": override_rate,
            "override_helpful_count": override_helpful,
            "override_harmful_count": override_harmful,
            "executed_count": executed,
            "rollback_performed_count": rollbacks,
            "rollback_success_count": rollback_success,
            "rollback_success_rate": rollback_success_rate,
            "outcome_reviewed_count": outcomes,
            "judged_correct_count": judged_correct,
            "judged_correct_rate": _rate(judged_correct, outcomes),
            "unexpected_consequence_count": unexpected,
            "unexpected_consequence_rate": unexpected_rate,
            "controls_sufficient_count": controls_sufficient,
            "controls_sufficient_rate": _rate(controls_sufficient, outcomes),
            "near_miss_count": len(near_misses),
            "recovery_failure_count": len(recovery_failures),
            "initial_posture_counts": dict(sorted(posture_counts.items())),
            "final_posture_counts": dict(sorted(final_posture_counts.items())),
        },
        "top_reason_codes": dict(reason_counts.most_common(10)),
        "top_missing_evidence": dict(missing_evidence_counts.most_common(10)),
        "top_safeguards": dict(safeguard_counts.most_common(10)),
        "near_miss_decisions": [
            {
                "decision_id": row["decision_id"],
                "operation": row["requested_operation"],
                "final_posture": row["final_posture"],
                "reason_codes": row["reason_codes"],
            }
            for row in near_misses
        ],
        "recovery_failure_decisions": [
            {
                "decision_id": row["decision_id"],
                "operation": row["requested_operation"],
                "rollback_success": row["rollback_success"],
                "time_to_recover_minutes": row["time_to_recover_minutes"],
            }
            for row in recovery_failures
        ],
        "policy_review_queue": policy_queue + generated_recommendations,
        "governance_drift_signals": drift_signals,
        "decision_rows": rows,
        "evidence_boundary": [
            "DLL Intelligence summarizes supplied lifecycle records; it does not prove incident reduction by itself.",
            "Synthetic or analyst-assigned ledgers must be labeled before external use.",
            "Policy and calibration recommendations require human review before activation.",
        ],
        "recommended_next_action": recommended_next_action(
            total=total,
            outcomes=outcomes,
            drift_signals=drift_signals,
            recovery_failures=len(recovery_failures),
        ),
    }


def recommended_next_action(
    *,
    total: int,
    outcomes: int,
    drift_signals: list[str],
    recovery_failures: int,
) -> str:
    if total < 30:
        return "Collect at least 30 customer-context DLL records before presenting rates as pilot evidence."
    if outcomes / total < 0.5:
        return "Increase delayed outcome labeling before using DLL Intelligence for policy calibration."
    if recovery_failures:
        return "Review rollback design and containment controls before moving from shadow mode to enforcement."
    if drift_signals:
        return "Review governance drift signals with security owners and approve any policy changes manually."
    return "Use DLL Intelligence as pilot evidence while continuing to collect outcome-labeled decisions."


def _append_common(
    ledger: DecisionLifecycleLedger,
    *,
    actor: str,
    operation: str,
    environment: str,
    risk_profile: str,
    evidence_score: float,
    missing_evidence: list[str],
    posture: str,
    final_posture: str,
    interaction: str,
    execution_status: str,
    rollback_performed: bool,
    rollback_success: bool | None,
    judged_correct: bool,
    unexpected: bool,
    controls_sufficient: bool,
    reason_codes: list[str],
    safeguards: list[str],
    time_to_recover_minutes: float = 0,
    cost_incurred: float = 0,
) -> None:
    ledger.append(
        "REQUEST",
        actor,
        {
            "initiated_by": actor,
            "requested_operation": operation,
            "environment": environment,
            "risk_profile": risk_profile,
        },
        recorded_at="2026-07-18T12:00:00+00:00",
    )
    ledger.append(
        "EVIDENCE",
        "smerc-api",
        {
            "available_evidence": ["workflow_metadata", "actor_identity", "action_manifest"],
            "confidence_score": evidence_score,
            "missing_evidence": missing_evidence,
            "external_dependencies": ["github_actions", "sparta_router"],
            "model_version": "pilot-agent-declaration",
            "policy_version": "smerc.policy.v1:pilot",
        },
        recorded_at="2026-07-18T12:00:02+00:00",
    )
    ledger.append(
        "EVALUATION",
        "smerc-engine",
        {
            "structural_state": f"{environment} action evaluated for recoverability and blast radius",
            "entropy_indicators": reason_codes,
            "recoverability_score": max(0.05, min(0.95, evidence_score - 0.12)),
            "authorization_recommendation": posture,
            "reason_codes": reason_codes,
            "recommended_safeguards": safeguards,
        },
        recorded_at="2026-07-18T12:00:03+00:00",
    )
    ledger.append(
        "HUMAN_INTERACTION",
        "pilot-reviewer",
        {
            "interaction": interaction,
            "reviewer_id": "pilot-reviewer",
            "original_recommendation": posture,
            "final_recommendation": final_posture,
            "rationale": "Pilot reviewer disposition captured for DLL intelligence.",
        },
        recorded_at="2026-07-18T12:02:00+00:00",
    )
    ledger.append(
        "EXECUTION",
        "sparta-adapter",
        {
            "executed_operation": operation if final_posture not in {"DENY", "FREEZE"} else "No automated execution.",
            "execution_status": execution_status,
            "started_at": "2026-07-18T12:05:00+00:00",
            "duration_ms": 93000,
            "rollback_performed": rollback_performed,
            "rollback_success": rollback_success,
        },
        recorded_at="2026-07-18T12:07:00+00:00",
    )
    ledger.append(
        "OUTCOME",
        "pilot-review-lead",
        {
            "judged_correct": judged_correct,
            "unexpected_consequences": unexpected,
            "controls_sufficient": controls_sufficient,
            "cost_incurred": cost_incurred,
            "time_to_recover_minutes": time_to_recover_minutes,
            "customer_impact": "none observed" if not unexpected else "limited pilot impact",
            "security_impact": "none observed" if not unexpected else "review required",
            "financial_impact": "none observed" if cost_incurred == 0 else f"{cost_incurred} estimated",
        },
        recorded_at="2026-07-19T12:00:00+00:00",
    )
    ledger.append(
        "LEARNING_RECOMMENDATION",
        "smerc-dll",
        {
            "expected_outcome": "Action outcome remains bounded by selected posture and controls.",
            "actual_outcome": "Outcome label captured by pilot reviewer.",
            "prediction_error": "low" if judged_correct else "high",
            "human_override_effectiveness": "no override" if interaction != "overrode" else "captured for review",
            "recommended_policy_updates": [f"Review posture threshold for {risk_profile}."],
            "confidence_calibration_changes": ["Collect more customer-context outcomes before calibration."],
            "suggested_rule_modifications": [f"Map recurring controls for {risk_profile} actions."],
            "activation_status": "requires_review",
        },
        recorded_at="2026-07-19T12:05:00+00:00",
    )


def build_example_bundle() -> Dict[str, Any]:
    scenarios = [
        {
            "decision_id": "dll_pilot_001_safe_read_only_report",
            "actor": "ai-ops-agent",
            "operation": "Generate read-only deployment status report.",
            "environment": "staging",
            "risk_profile": "read_only_reporting",
            "evidence_score": 0.91,
            "missing_evidence": [],
            "posture": "ALLOW",
            "final_posture": "ALLOW",
            "interaction": "accepted",
            "execution_status": "succeeded",
            "rollback_performed": False,
            "rollback_success": None,
            "judged_correct": True,
            "unexpected": False,
            "controls_sufficient": True,
            "reason_codes": ["LOW_IMPACT", "RECOVERY_PATH_STRONG"],
            "safeguards": ["record_decision"],
        },
        {
            "decision_id": "dll_pilot_002_canary_deploy",
            "actor": "coding-agent",
            "operation": "Deploy generated API change to canary.",
            "environment": "production",
            "risk_profile": "github_actions_deployment",
            "evidence_score": 0.74,
            "missing_evidence": ["rollback_drill"],
            "posture": "THROTTLE",
            "final_posture": "THROTTLE",
            "interaction": "accepted",
            "execution_status": "succeeded",
            "rollback_performed": False,
            "rollback_success": None,
            "judged_correct": True,
            "unexpected": False,
            "controls_sufficient": True,
            "reason_codes": ["RECOVERY_PATH_PARTIAL", "IMPACT_SCOPE_ELEVATED"],
            "safeguards": ["canary_only", "retain_rollback_plan"],
        },
        {
            "decision_id": "dll_pilot_003_delete_customer_table",
            "actor": "support-agent",
            "operation": "Delete a customer table after ambiguous cleanup request.",
            "environment": "production",
            "risk_profile": "data_destruction",
            "evidence_score": 0.38,
            "missing_evidence": ["human_approval", "backup_verification"],
            "posture": "DENY",
            "final_posture": "DENY",
            "interaction": "accepted",
            "execution_status": "blocked",
            "rollback_performed": False,
            "rollback_success": None,
            "judged_correct": True,
            "unexpected": False,
            "controls_sufficient": True,
            "reason_codes": ["IRREVERSIBLE_EXPOSURE_HIGH", "EVIDENCE_INCOMPLETE"],
            "safeguards": ["block_execution", "require_data_owner_review"],
        },
        {
            "decision_id": "dll_pilot_004_override_refund",
            "actor": "finance-agent",
            "operation": "Issue high-value customer refund.",
            "environment": "production",
            "risk_profile": "finance_operations",
            "evidence_score": 0.57,
            "missing_evidence": ["dual_approval", "customer_entitlement_proof"],
            "posture": "ESCALATE",
            "final_posture": "THROTTLE",
            "interaction": "overrode",
            "execution_status": "succeeded",
            "rollback_performed": False,
            "rollback_success": None,
            "judged_correct": False,
            "unexpected": True,
            "controls_sufficient": False,
            "reason_codes": ["FINANCIAL_IMPACT_HIGH", "EVIDENCE_INCOMPLETE"],
            "safeguards": ["dual_approval", "transaction_limit"],
            "time_to_recover_minutes": 240,
            "cost_incurred": 1200,
        },
        {
            "decision_id": "dll_pilot_005_failed_deploy_rollback",
            "actor": "deployment-agent",
            "operation": "Apply infrastructure autoscaling change.",
            "environment": "production",
            "risk_profile": "cloud_administration",
            "evidence_score": 0.66,
            "missing_evidence": ["rollback_drill"],
            "posture": "THROTTLE",
            "final_posture": "THROTTLE",
            "interaction": "accepted",
            "execution_status": "failed",
            "rollback_performed": True,
            "rollback_success": True,
            "judged_correct": True,
            "unexpected": False,
            "controls_sufficient": True,
            "reason_codes": ["RECOVERY_PATH_PARTIAL", "ANOMALY_PRESSURE_ELEVATED"],
            "safeguards": ["canary_only", "automatic_rollback"],
        },
        {
            "decision_id": "dll_pilot_006_security_key_rotation",
            "actor": "security-agent",
            "operation": "Rotate production signing key without owner confirmation.",
            "environment": "production",
            "risk_profile": "security_operations",
            "evidence_score": 0.49,
            "missing_evidence": ["owner_confirmation", "rollback_drill"],
            "posture": "FREEZE",
            "final_posture": "FREEZE",
            "interaction": "accepted",
            "execution_status": "not_executed",
            "rollback_performed": False,
            "rollback_success": None,
            "judged_correct": True,
            "unexpected": False,
            "controls_sufficient": True,
            "reason_codes": ["AUTHORITY_CHANGE_HIGH", "EVIDENCE_INCOMPLETE"],
            "safeguards": ["pause_automation", "require_owner_confirmation"],
        },
    ]
    ledgers = []
    for scenario in scenarios:
        ledger = DecisionLifecycleLedger(scenario["decision_id"], tenant_id="example-design-partner")
        event_payload = {key: value for key, value in scenario.items() if key != "decision_id"}
        _append_common(ledger, **event_payload)
        ledgers.append(ledger.to_dict())
    return {
        "version": "smerc.dll-example-bundle.v1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "description": "Synthetic DLL portfolio for exercising DLL Intelligence. Not customer proof.",
        "ledgers": ledgers,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# SMERC DLL Intelligence Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        (
            f"DLL Intelligence analyzed `{summary['ledger_count']}` verified lifecycle ledger(s), "
            f"found `{summary['near_miss_count']}` near-miss decision(s), "
            f"`{summary['recovery_failure_count']}` recovery failure(s), and "
            f"`{len(report['policy_review_queue'])}` policy-review queue item(s)."
        ),
        "",
        "This is governance intelligence built from lifecycle evidence. It is not automatic policy activation.",
        "",
        "## Core Metrics",
        "",
        f"- Human reviewed: `{summary['human_reviewed_count']}`",
        f"- Override rate: `{summary['override_rate']}`",
        f"- Helpful overrides: `{summary['override_helpful_count']}`",
        f"- Harmful overrides: `{summary['override_harmful_count']}`",
        f"- Rollback success rate: `{summary['rollback_success_rate']}`",
        f"- Judged-correct rate: `{summary['judged_correct_rate']}`",
        f"- Unexpected consequence rate: `{summary['unexpected_consequence_rate']}`",
        f"- Controls sufficient rate: `{summary['controls_sufficient_rate']}`",
        f"- Initial postures: `{summary['initial_posture_counts']}`",
        f"- Final postures: `{summary['final_posture_counts']}`",
        "",
        "## Recurring Signals",
        "",
        f"- Top reason codes: `{report['top_reason_codes']}`",
        f"- Top missing evidence: `{report['top_missing_evidence']}`",
        f"- Top safeguards: `{report['top_safeguards']}`",
        "",
        "## Near-Miss Decisions",
        "",
    ]
    if report["near_miss_decisions"]:
        for item in report["near_miss_decisions"]:
            lines.append(f"- `{item['decision_id']}`: {item['operation']} -> `{item['final_posture']}`")
    else:
        lines.append("- None identified.")
    lines.extend(["", "## Policy Review Queue", ""])
    if report["policy_review_queue"]:
        for item in report["policy_review_queue"][:15]:
            lines.append(
                f"- `{item['recommendation_type']}`: {item['recommendation']} "
                f"(`{item['activation_status']}`)"
            )
    else:
        lines.append("- No review items generated.")
    lines.extend(["", "## Governance Drift Signals", ""])
    if report["governance_drift_signals"]:
        for signal in report["governance_drift_signals"]:
            lines.append(f"- `{signal}`")
    else:
        lines.append("- No drift signal crossed the configured threshold.")
    lines.extend(["", "## Evidence Boundary", ""])
    lines.extend(f"- {item}" for item in report["evidence_boundary"])
    lines.extend(["", "## Recommended Next Action", "", report["recommended_next_action"], ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze SMERC Decision Lifecycle Ledger records.")
    parser.add_argument("inputs", nargs="*", help="DLL JSON, DLL bundle, or pilot intake result files.")
    parser.add_argument("--example-bundle-output", type=Path)
    parser.add_argument("--json-output", type=Path, default=Path("reports/dll_intelligence_report.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("reports/DLL_Intelligence_Report.md"))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if args.example_bundle_output:
        bundle = build_example_bundle()
        args.example_bundle_output.parent.mkdir(parents=True, exist_ok=True)
        args.example_bundle_output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        ledgers = bundle["ledgers"]
    elif args.inputs:
        ledgers = load_ledgers(args.inputs)
    else:
        parser.error("provide input files or --example-bundle-output")

    report = analyze_ledgers(ledgers)
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.recoverability_engine import RecoverabilityEngine
from reference_engine.sparta_router import SPARTaRouter, ToolPlan


FAKE_CUSTOMER_PILOT_VERSION = "smerc.fake-customer-pilot.v1"
FIXED_BASE_TIME = "2026-07-17T15:00:00+00:00"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 0.0


def _scenario_plan(scenario: Mapping[str, Any]) -> ToolPlan:
    action = scenario["action"]
    path = scenario["path"]
    destructive = path == "destructive_request"
    escalated = path == "escalated_request"
    return ToolPlan(
        plan_id=f"{scenario['scenario_id']}-plan",
        tool=str(action["tool"]).replace(".", "_"),
        action=str(action["action_type"]),
        requested_capability="deployment" if "deploy" in str(action["tool"]) else str(action["action_type"]),
        supports_dry_run=not destructive,
        supports_scope_limit=not destructive,
        supports_checkpoint=not destructive,
        supports_rollback=not destructive,
        supports_human_approval=True if escalated or action.get("external_side_effect") else False,
        max_scope_units=100,
        requested_scope_units=25 if scenario["path"] in {"safe_deployment", "failure_rollback"} else 80,
        side_effect_level="destructive" if destructive else ("external" if action.get("external_side_effect") else "internal"),
        metadata={
            "customer": scenario["customer"],
            "repository": scenario["repository"],
            "environment": action.get("context", {}).get("environment", "unknown"),
            "simulation_path": scenario["path"],
        },
    )


def _execution_status(posture: str, route_state: str, scenario: Mapping[str, Any]) -> str:
    expected = str(scenario["expected_execution_status"])
    if posture in {"DENY", "FREEZE"}:
        return "blocked" if posture == "DENY" else "not_executed"
    if route_state in {"BLOCK", "PAUSE", "REVIEW_REQUIRED", "BLOCKED_ESCALATION_UNAVAILABLE"}:
        return "not_executed" if route_state == "REVIEW_REQUIRED" else "blocked"
    return expected


def _route_decision(decision: Mapping[str, Any], scenario: Mapping[str, Any]) -> Dict[str, Any]:
    return SPARTaRouter().route(
        {
            "posture": decision["posture"],
            "replay_id": decision["replay_id"],
            "reason_codes": decision["reason_codes"],
            "controls": decision["controls"],
            "policy": decision["policy"],
        },
        _scenario_plan(scenario),
    )


def _build_ledger(
    scenario: Mapping[str, Any],
    decision: Mapping[str, Any],
    route: Mapping[str, Any],
    execution_status: str,
    sequence_index: int,
) -> Dict[str, Any]:
    action = scenario["action"]
    scores = decision["scores"]
    ledger = DecisionLifecycleLedger(f"dll_{scenario['scenario_id']}", tenant_id="acmecloud")
    minute = sequence_index * 10
    stamp = f"2026-07-17T15:{minute:02d}:00+00:00"
    ledger.append(
        "REQUEST",
        str(action["actor"]),
        {
            "initiated_by": str(action["actor"]),
            "requested_operation": str(action["description"]),
            "environment": str(action.get("context", {}).get("environment", "unknown")),
            "risk_profile": str(action["action_type"]),
        },
        recorded_at=stamp,
    )
    ledger.append(
        "EVIDENCE",
        "smerc-fake-customer-runner",
        {
            "available_evidence": ["action_request", "domain_profile", "simulated_workflow_metadata"],
            "confidence_score": scores["confidence_score"],
            "missing_evidence": ["real_customer_logs", "real_reviewer_labels", "target_platform_audit"],
            "external_dependencies": ["github_actions_simulation", "sparta_router", "decision_lifecycle_ledger"],
            "model_version": "fake-customer-simulation",
            "policy_version": decision["policy"]["policy_id"],
        },
        recorded_at=stamp.replace(":00+00:00", ":01+00:00"),
    )
    ledger.append(
        "EVALUATION",
        "smerc-runtime",
        {
            "structural_state": decision["posture"],
            "entropy_indicators": decision["reason_codes"],
            "recoverability_score": scores["reversible_capacity_score"],
            "authorization_recommendation": decision["posture"],
            "reason_codes": decision["reason_codes"],
            "recommended_safeguards": decision["controls"] or ["record_execution_report"],
        },
        recorded_at=stamp.replace(":00+00:00", ":02+00:00"),
    )
    ledger.append(
        "HUMAN_INTERACTION",
        "acme-security-reviewer",
        {
            "interaction": scenario["human_interaction"],
            "reviewer_id": "acme-security-reviewer",
            "original_recommendation": decision["posture"],
            "final_recommendation": decision["posture"],
            "rationale": "Simulated reviewer accepts the fake-customer posture for production-like validation.",
        },
        recorded_at=stamp.replace(":00+00:00", ":03+00:00"),
    )
    rollback_performed = bool(scenario["expected_rollback"] and execution_status in {"failed", "timed_out", "cancelled"})
    ledger.append(
        "EXECUTION",
        "sparta-github-simulator",
        {
            "executed_operation": route["route_state"],
            "execution_status": execution_status,
            "started_at": stamp.replace(":00+00:00", ":04+00:00"),
            "duration_ms": 42000 if execution_status in {"succeeded", "failed"} else 0,
            "rollback_performed": rollback_performed,
            "rollback_success": True if rollback_performed else None,
        },
        recorded_at=stamp.replace(":00+00:00", ":05+00:00"),
    )
    ledger.append(
        "OUTCOME",
        "fake-customer-assessor",
        {
            "judged_correct": bool(scenario["judged_correct"]),
            "unexpected_consequences": False,
            "controls_sufficient": execution_status != "failed" or rollback_performed,
            "cost_incurred": 0 if execution_status != "failed" else 150.0,
            "time_to_recover_minutes": 0 if not rollback_performed else 4,
            "customer_impact": "none in simulated environment",
            "security_impact": "none in simulated environment",
            "financial_impact": "none in simulated environment",
        },
        recorded_at=stamp.replace(":00+00:00", ":06+00:00"),
    )
    ledger.append(
        "LEARNING_RECOMMENDATION",
        "smerc-fake-customer-runner",
        {
            "expected_outcome": str(scenario["expected_execution_status"]),
            "actual_outcome": execution_status,
            "prediction_error": "none" if execution_status == scenario["expected_execution_status"] else "simulated_route_changed_execution_status",
            "human_override_effectiveness": "not measured in fake customer environment",
            "recommended_policy_updates": ["review with real customer labels before changing policy"],
            "confidence_calibration_changes": ["do not calibrate from fake customer data"],
            "suggested_rule_modifications": ["none"],
            "activation_status": "requires_review",
        },
        recorded_at=stamp.replace(":00+00:00", ":07+00:00"),
    )
    return ledger.to_dict()


def run_fake_customer_pilot(scenarios: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    engine = RecoverabilityEngine(domain_profile="github_actions")
    records = []
    ledgers = []
    for index, scenario in enumerate(scenarios):
        decision = engine.evaluate(dict(scenario["action"]))
        route = _route_decision(decision, scenario)
        execution_status = _execution_status(decision["posture"], route["route_state"], scenario)
        ledger = _build_ledger(scenario, decision, route, execution_status, index)
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "path": scenario["path"],
                "customer": scenario["customer"],
                "repository": scenario["repository"],
                "traditional_policy_outcome": scenario["traditional_policy_outcome"],
                "smerc_posture": decision["posture"],
                "sparta_route_state": route["route_state"],
                "execution_status": execution_status,
                "rollback_performed": ledger["summary"]["rollback_performed"],
                "ledger_valid": ledger["verification"]["valid"],
                "irreversible_exposure_score": decision["scores"]["irreversible_exposure_score"],
                "reversible_capacity_score": decision["scores"]["reversible_capacity_score"],
                "risk_adjusted_authorization_score": decision["scores"]["risk_adjusted_authorization_score"],
                "reason_codes": decision["reason_codes"],
                "controls": decision["controls"],
                "plain_english_summary": decision["plain_english_summary"],
                "route_summary": route["plain_english_summary"],
                "ledger_head_hash": ledger["head_record_hash"],
            }
        )
        ledgers.append(ledger)
    return _package(records, ledgers)


def _package(records: list[Dict[str, Any]], ledgers: list[Dict[str, Any]]) -> Dict[str, Any]:
    posture_counts = Counter(record["smerc_posture"] for record in records)
    route_counts = Counter(record["sparta_route_state"] for record in records)
    execution_counts = Counter(record["execution_status"] for record in records)
    difference_count = sum(
        1
        for record in records
        if not (
            (record["traditional_policy_outcome"] == "ALLOW" and record["smerc_posture"] == "ALLOW")
            or (record["traditional_policy_outcome"] == "DENY" and record["smerc_posture"] == "DENY")
        )
    )
    package = {
        "version": FAKE_CUSTOMER_PILOT_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "customer_simulation": {
            "customer": "AcmeCloud",
            "purpose": "production-like fake customer validation",
            "environment": "simulated GitHub Actions and SPARTa execution path",
            "not_customer_evidence": True,
        },
        "summary": {
            "scenario_count": len(records),
            "decision_difference_count": difference_count,
            "decision_difference_rate": _pct(difference_count, len(records)),
            "posture_counts": {key: posture_counts.get(key, 0) for key in ["ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"]},
            "route_state_counts": dict(sorted(route_counts.items())),
            "execution_status_counts": dict(sorted(execution_counts.items())),
            "rollback_scenarios": sum(1 for record in records if record["rollback_performed"]),
            "valid_ledger_count": sum(1 for ledger in ledgers if ledger["verification"]["valid"]),
        },
        "records": records,
        "ledgers": ledgers,
        "boundary": {
            "proves": [
                "the reference engine can run a production-like multi-path pilot simulation",
                "SMERC decisions can be routed through SPARTa and recorded in valid DLL chains",
                "safe, constrained, blocked, review, and rollback paths can be represented as replayable evidence",
            ],
            "does_not_prove": [
                "real customer demand",
                "live production safety",
                "native GitHub runner isolation",
                "truth of external platform controls",
                "incident reduction in customer environments",
            ],
        },
    }
    package["markdown_report"] = render_markdown(package)
    return package


def render_markdown(package: Mapping[str, Any]) -> str:
    summary = package["summary"]
    lines = [
        "# SMERC Fake Customer Production-Like Pilot Report",
        "",
        "This report simulates AcmeCloud, a fake customer environment. It is useful for end-to-end program testing, not customer proof or production certification.",
        "",
        "## Summary",
        "",
        f"- Scenario count: `{summary['scenario_count']}`",
        f"- Decision differences from traditional allow/deny: `{summary['decision_difference_count']}`",
        f"- Decision difference rate: `{summary['decision_difference_rate']}`",
        f"- Valid DLL chains: `{summary['valid_ledger_count']}`",
        f"- Rollback scenarios: `{summary['rollback_scenarios']}`",
        "",
        "## Scenario Results",
        "",
        "| Scenario | Traditional | SMERC | SPARTa | Execution | Exposure | Capacity |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for record in package["records"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{record['scenario_id']}`",
                    f"`{record['traditional_policy_outcome']}`",
                    f"`{record['smerc_posture']}`",
                    f"`{record['sparta_route_state']}`",
                    f"`{record['execution_status']}`",
                    f"`{record['irreversible_exposure_score']}`",
                    f"`{record['reversible_capacity_score']}`",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Boundary", ""])
    lines.extend(f"- Does not prove: {item}" for item in package["boundary"]["does_not_prove"])
    return "\n".join(lines) + "\n"


def write_package(package: Mapping[str, Any], *, json_output: Path, markdown_output: Path) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(str(package["markdown_report"]), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a fake-customer production-like SMERC pilot simulation.")
    parser.add_argument("scenarios", type=Path)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    payload = _load_json(args.scenarios)
    if not isinstance(payload, list):
        raise TypeError("scenarios must be a JSON array")
    package = run_fake_customer_pilot(payload)
    if args.json_output or args.markdown_output:
        write_package(
            package,
            json_output=args.json_output or Path("fake_customer_pilot_report.json"),
            markdown_output=args.markdown_output or Path("Fake_Customer_Pilot_Report.md"),
        )
    print(json.dumps(package, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

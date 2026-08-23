from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


AUTONOMY_CONTINUANCE_VERSION = "smerc.autonomy-continuance.v1"
RIGHT_TO_CONTINUE_STATES = {"CONTINUE", "CONTINUE_CONSTRAINED", "PAUSE", "REQUALIFY"}


def load_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate_continuance(case: Mapping[str, Any]) -> Dict[str, Any]:
    if case.get("version") != AUTONOMY_CONTINUANCE_VERSION:
        raise ValueError(f"case must have version {AUTONOMY_CONTINUANCE_VERSION}")
    authority = evaluate_authority_provenance(case["authority"])
    intent = evaluate_intent_integrity(case["intent"])
    horizon = evaluate_consequence_horizon(case["consequence_horizon"])
    collective = evaluate_collective_autonomy(case["collective_autonomy"])
    right = evaluate_right_to_continue(
        authority=authority,
        intent=intent,
        horizon=horizon,
        collective=collective,
        earned_autonomy=case.get("earned_autonomy", {}),
        autonomy_budget=case.get("autonomy_budget", {}),
    )
    return {
        "version": AUTONOMY_CONTINUANCE_VERSION,
        "generated_at": _now(),
        "case_id": str(case.get("case_id", "autonomy_continuance_case")),
        "subject_id": str(case.get("subject_id", "unknown_subject")),
        "authority_provenance": authority,
        "intent_integrity": intent,
        "consequence_horizon": horizon,
        "collective_autonomy": collective,
        "earned_autonomy": dict(case.get("earned_autonomy", {})),
        "autonomy_budget": dict(case.get("autonomy_budget", {})),
        "right_to_continue": right,
        "plain_english_summary": _summary(right, authority, intent, horizon, collective),
    }


def evaluate_authority_provenance(authority: Mapping[str, Any]) -> Dict[str, Any]:
    drivers = []
    if not authority.get("identity_verified"):
        drivers.append("identity_not_verified")
    if not authority.get("delegation_valid"):
        drivers.append("delegation_invalid")
    if not authority.get("policy_binding_valid"):
        drivers.append("policy_binding_invalid")
    if not authority.get("tool_grant_valid"):
        drivers.append("tool_grant_invalid")
    if authority.get("approval_required") and not authority.get("approval_present"):
        drivers.append("required_approval_missing")
    if authority.get("credential_age_minutes", 0) > authority.get("max_credential_age_minutes", 60):
        drivers.append("credential_too_old")
    return {
        "status": "VERIFIED" if not drivers else "REJECTED",
        "score": 1.0 if not drivers else 0.0,
        "drivers": drivers,
    }


def evaluate_intent_integrity(intent: Mapping[str, Any]) -> Dict[str, Any]:
    drivers = []
    declared = str(intent.get("declared_intent", "")).lower()
    operation = str(intent.get("operation_class", "")).lower()
    if not intent.get("declared_intent"):
        drivers.append("missing_declared_intent")
    if intent.get("declared_scope_units", 0) < intent.get("requested_scope_units", 0):
        drivers.append("scope_exceeds_declared_intent")
    if intent.get("declared_data_boundary") != intent.get("requested_data_boundary"):
        drivers.append("data_boundary_mismatch")
    if "read" in declared and operation in {"delete", "payment", "deploy", "write"}:
        drivers.append("operation_conflicts_with_declared_intent")
    if intent.get("tool_name") not in intent.get("declared_allowed_tools", []):
        drivers.append("tool_not_in_declared_intent")
    status = "ALIGNED" if not drivers else "DIVERGED"
    return {"status": status, "score": 1.0 if status == "ALIGNED" else 0.15, "drivers": drivers}


def evaluate_consequence_horizon(horizon: Mapping[str, Any]) -> Dict[str, Any]:
    drivers = []
    score = 0.0
    if horizon.get("external_side_effect"):
        score += 0.25
        drivers.append("external_side_effect")
    if horizon.get("customer_impact_possible"):
        score += 0.2
        drivers.append("customer_impact_possible")
    if horizon.get("financial_settlement_possible"):
        score += 0.25
        drivers.append("financial_settlement_possible")
    if horizon.get("rollback_window_minutes", 9999) > 60:
        score += 0.15
        drivers.append("long_rollback_window")
    if horizon.get("downstream_system_count", 0) >= 3:
        score += 0.15
        drivers.append("multi_system_downstream_effect")
    score = round(min(1.0, score), 3)
    if score >= 0.75:
        band = "LONG"
    elif score >= 0.35:
        band = "MEDIUM"
    else:
        band = "SHORT"
    return {"horizon": band, "score": score, "drivers": drivers}


def evaluate_collective_autonomy(collective: Mapping[str, Any]) -> Dict[str, Any]:
    drivers = []
    actor_count = int(collective.get("active_actor_count", 1))
    shared_tool_count = int(collective.get("shared_tool_actor_count", 1))
    correlated = bool(collective.get("correlated_objective"))
    if actor_count >= 5:
        drivers.append("many_active_actors")
    if shared_tool_count >= 3:
        drivers.append("shared_tool_concentration")
    if correlated:
        drivers.append("correlated_objective")
    if collective.get("aggregate_scope_units", 0) > collective.get("aggregate_scope_limit", 1_000_000):
        drivers.append("aggregate_scope_limit_exceeded")
    if len(drivers) >= 3:
        state = "COLLECTIVE_RISK_HIGH"
    elif drivers:
        state = "COLLECTIVE_RISK_ELEVATED"
    else:
        state = "COLLECTIVE_RISK_LOW"
    return {"state": state, "drivers": drivers}


def evaluate_right_to_continue(
    *,
    authority: Mapping[str, Any],
    intent: Mapping[str, Any],
    horizon: Mapping[str, Any],
    collective: Mapping[str, Any],
    earned_autonomy: Mapping[str, Any],
    autonomy_budget: Mapping[str, Any],
) -> Dict[str, Any]:
    drivers = []
    if authority["status"] != "VERIFIED":
        drivers.append("authority_not_proven")
    if intent["status"] != "ALIGNED":
        drivers.append("intent_integrity_failed")
    if horizon["horizon"] == "LONG":
        drivers.append("long_consequence_horizon")
    if collective["state"] == "COLLECTIVE_RISK_HIGH":
        drivers.append("collective_autonomy_risk")
    if earned_autonomy.get("earned_tier") in {"TIER_0_OBSERVE", "TIER_5_REQUALIFY_REQUIRED"}:
        drivers.append("earned_autonomy_not_sufficient")
    if autonomy_budget.get("autonomy_state") in {"SUSPEND_AUTONOMY", "REQUALIFY"}:
        drivers.append("autonomy_budget_not_sufficient")

    if any(driver in drivers for driver in ["authority_not_proven", "intent_integrity_failed", "earned_autonomy_not_sufficient"]):
        state = "REQUALIFY"
    elif any(driver in drivers for driver in ["autonomy_budget_not_sufficient", "long_consequence_horizon", "collective_autonomy_risk"]):
        state = "PAUSE"
    elif drivers:
        state = "CONTINUE_CONSTRAINED"
    else:
        state = "CONTINUE"
    return {
        "state": state,
        "drivers": drivers,
        "recommended_next_action": _recommended_action(state),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Autonomy Continuance Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Case: `{report['case_id']}`",
        f"- Subject: `{report['subject_id']}`",
        f"- Right to continue: `{report['right_to_continue']['state']}`",
        f"- Authority provenance: `{report['authority_provenance']['status']}`",
        f"- Intent integrity: `{report['intent_integrity']['status']}`",
        f"- Consequence horizon: `{report['consequence_horizon']['horizon']}`",
        f"- Collective autonomy: `{report['collective_autonomy']['state']}`",
        f"- Earned tier: `{report.get('earned_autonomy', {}).get('earned_tier', 'not_supplied')}`",
        f"- Autonomy budget state: `{report.get('autonomy_budget', {}).get('autonomy_state', 'not_supplied')}`",
        "",
        "## Right To Continue Drivers",
        "",
    ]
    lines.extend(f"- `{driver}`" for driver in report["right_to_continue"]["drivers"] or ["none"])
    lines.extend(
        [
            "",
            "## Recommended Next Action",
            "",
            str(report["right_to_continue"]["recommended_next_action"]),
            "",
            "## Plain English Summary",
            "",
            str(report["plain_english_summary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _recommended_action(state: str) -> str:
    if state == "REQUALIFY":
        return "Stop autonomous continuation and require owner review before any further action."
    if state == "PAUSE":
        return "Pause the workflow, preserve evidence, and require review before continuation."
    if state == "CONTINUE_CONSTRAINED":
        return "Continue only with reduced scope, safer tools, and tighter review triggers."
    return "Continue within current authority, budget, and evidence boundaries."


def _summary(
    right: Mapping[str, Any],
    authority: Mapping[str, Any],
    intent: Mapping[str, Any],
    horizon: Mapping[str, Any],
    collective: Mapping[str, Any],
) -> str:
    return (
        f"The current right-to-continue state is {right['state']}. Authority is {authority['status']}, "
        f"intent is {intent['status']}, consequence horizon is {horizon['horizon']}, and collective autonomy is "
        f"{collective['state']}."
    )


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate authority, intent, horizon, collective autonomy, and right to continue.")
    parser.add_argument("--case", default="examples/autonomy/continuance_case.json")
    parser.add_argument("--json-output", default="reports/autonomy_continuance_report.json")
    parser.add_argument("--markdown-output", default="reports/Autonomy_Continuance_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = evaluate_continuance(load_json(args.case))
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

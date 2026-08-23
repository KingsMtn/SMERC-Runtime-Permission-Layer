from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


AUTONOMY_BUDGET_VERSION = "smerc.autonomy-budget.v1"
AUTONOMY_STATES = {"HEALTHY", "WATCH", "DEGRADE", "SUSPEND_AUTONOMY", "REQUALIFY"}
POSTURE_SPEND_MULTIPLIER = {
    "ALLOW": 0.25,
    "THROTTLE": 0.55,
    "FREEZE": 0.85,
    "DENY": 1.0,
    "ESCALATE": 0.9,
}
STATE_RANK = {
    "HEALTHY": 0,
    "WATCH": 1,
    "DEGRADE": 2,
    "SUSPEND_AUTONOMY": 3,
    "REQUALIFY": 4,
}
DEFAULT_BUDGETS = {
    "HEALTHY": {
        "max_actions": 10,
        "max_scope_units": 1000,
        "max_risk_spend": 3.0,
        "valid_for_minutes": 60,
        "allowed_tool_risk_tiers": ["low", "medium", "high", "financial", "destructive"],
    },
    "WATCH": {
        "max_actions": 7,
        "max_scope_units": 250,
        "max_risk_spend": 1.8,
        "valid_for_minutes": 30,
        "allowed_tool_risk_tiers": ["low", "medium", "high", "financial"],
    },
    "DEGRADE": {
        "max_actions": 3,
        "max_scope_units": 25,
        "max_risk_spend": 0.9,
        "valid_for_minutes": 15,
        "allowed_tool_risk_tiers": ["low", "medium"],
    },
    "SUSPEND_AUTONOMY": {
        "max_actions": 0,
        "max_scope_units": 0,
        "max_risk_spend": 0.0,
        "valid_for_minutes": 0,
        "allowed_tool_risk_tiers": [],
    },
    "REQUALIFY": {
        "max_actions": 0,
        "max_scope_units": 0,
        "max_risk_spend": 0.0,
        "valid_for_minutes": 0,
        "allowed_tool_risk_tiers": [],
    },
}


def evaluate_autonomy_budget(
    *,
    decisions: Iterable[Mapping[str, Any]],
    initial_state: str = "HEALTHY",
    budget_overrides: Mapping[str, Any] | None = None,
    earned_autonomy: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    if initial_state not in AUTONOMY_STATES:
        raise ValueError(f"initial_state must be one of: {', '.join(sorted(AUTONOMY_STATES))}")
    budget = _budget_for_state(initial_state, budget_overrides)
    state = initial_state
    spent_actions = 0
    spent_scope_units = 0.0
    spent_risk = 0.0
    ref_gate_failures = 0
    blocked_or_held_attempts = 0
    ledger = []

    for sequence, decision in enumerate(decisions, start=1):
        spent_actions += 1
        scope_units = float(decision.get("requested_scope_units", 1))
        spent_scope_units += scope_units
        risk_spend = _risk_spend(decision)
        spent_risk += risk_spend
        if decision.get("ref_gate", {}).get("status") == "fail":
            ref_gate_failures += 1
        if str(decision.get("posture", "")).upper() in {"FREEZE", "DENY", "ESCALATE"}:
            blocked_or_held_attempts += 1

        state = _max_state(
            state,
            _state_from_decision(
                decision=decision,
                budget=budget,
                spent_actions=spent_actions,
                spent_scope_units=spent_scope_units,
                spent_risk=spent_risk,
                ref_gate_failures=ref_gate_failures,
                blocked_or_held_attempts=blocked_or_held_attempts,
            ),
        )
        ledger.append(
            {
                "sequence": int(decision.get("sequence", sequence)),
                "request_id": str(decision.get("mcp_request_id", decision.get("request_id", f"request_{sequence}"))),
                "tool_name": str(decision.get("tool_name", "unknown_tool")),
                "posture": str(decision.get("posture", "UNKNOWN")),
                "ref_gate_status": str(decision.get("ref_gate", {}).get("status", "unknown")),
                "risk_spend": round(risk_spend, 3),
                "remaining_actions": max(0, int(budget["max_actions"]) - spent_actions),
                "remaining_scope_units": round(max(0.0, float(budget["max_scope_units"]) - spent_scope_units), 3),
                "remaining_risk_spend": round(max(0.0, float(budget["max_risk_spend"]) - spent_risk), 3),
                "autonomy_state_after": state,
            }
        )

    allowed_risk_tiers = _allowed_risk_tiers(state, budget)
    return {
        "version": AUTONOMY_BUDGET_VERSION,
        "generated_at": _now(),
        "initial_state": initial_state,
        "autonomy_state": state,
        "earned_autonomy": dict(earned_autonomy or {}),
        "budget": budget,
        "spent": {
            "actions": spent_actions,
            "scope_units": round(spent_scope_units, 3),
            "risk_spend": round(spent_risk, 3),
            "ref_gate_failures": ref_gate_failures,
            "blocked_or_held_attempts": blocked_or_held_attempts,
        },
        "remaining": {
            "actions": max(0, int(budget["max_actions"]) - spent_actions),
            "scope_units": round(max(0.0, float(budget["max_scope_units"]) - spent_scope_units), 3),
            "risk_spend": round(max(0.0, float(budget["max_risk_spend"]) - spent_risk), 3),
            "valid_for_minutes": int(budget["valid_for_minutes"]) if state in {"HEALTHY", "WATCH"} else 0,
        },
        "allowed_tool_risk_tiers": allowed_risk_tiers,
        "blocked_tool_risk_tiers": [
            tier for tier in ["low", "medium", "high", "financial", "destructive"] if tier not in allowed_risk_tiers
        ],
        "review_triggers": _review_triggers(
            state=state,
            spent_actions=spent_actions,
            spent_scope_units=spent_scope_units,
            spent_risk=spent_risk,
            budget=budget,
            ref_gate_failures=ref_gate_failures,
            blocked_or_held_attempts=blocked_or_held_attempts,
        ),
        "decision_ledger": ledger,
        "plain_english_summary": _summary(state, ref_gate_failures, blocked_or_held_attempts, spent_risk, budget),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Autonomy Budget Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Initial state: `{report['initial_state']}`",
        f"- Current autonomy state: `{report['autonomy_state']}`",
        f"- Earned tier: `{report.get('earned_autonomy', {}).get('earned_tier', 'not_supplied')}`",
        f"- Actions spent: `{report['spent']['actions']}` of `{report['budget']['max_actions']}`",
        f"- Scope units spent: `{report['spent']['scope_units']}` of `{report['budget']['max_scope_units']}`",
        f"- Risk spend: `{report['spent']['risk_spend']}` of `{report['budget']['max_risk_spend']}`",
        f"- Ref-gate failures: `{report['spent']['ref_gate_failures']}`",
        f"- Blocked or held attempts: `{report['spent']['blocked_or_held_attempts']}`",
        "",
        "## Review Triggers",
        "",
    ]
    lines.extend(f"- `{trigger}`" for trigger in report["review_triggers"] or ["none"])
    lines.extend(
        [
            "",
            "## Budget Ledger",
            "",
            "| # | Request | Tool | Posture | Ref Gate | Risk Spend | Remaining Actions | Remaining Scope | Remaining Risk | State After |",
            "| ---: | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for item in report["decision_ledger"]:
        lines.append(
            f"| {item['sequence']} | `{item['request_id']}` | `{item['tool_name']}` | `{item['posture']}` | "
            f"`{item['ref_gate_status']}` | {item['risk_spend']} | {item['remaining_actions']} | "
            f"{item['remaining_scope_units']} | {item['remaining_risk_spend']} | `{item['autonomy_state_after']}` |"
        )
    lines.extend(["", "## Plain English Summary", "", str(report["plain_english_summary"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _risk_spend(decision: Mapping[str, Any]) -> float:
    posture = str(decision.get("posture", "")).upper()
    pressure = float(decision.get("gateway_pressure", {}).get("score", decision.get("risk_score", 0.0)))
    ref_penalty = 0.5 if decision.get("ref_gate", {}).get("status") == "fail" else 0.0
    multiplier = POSTURE_SPEND_MULTIPLIER.get(posture, 0.75)
    return round(min(2.0, pressure * multiplier + ref_penalty), 3)


def _state_from_decision(
    *,
    decision: Mapping[str, Any],
    budget: Mapping[str, Any],
    spent_actions: int,
    spent_scope_units: float,
    spent_risk: float,
    ref_gate_failures: int,
    blocked_or_held_attempts: int,
) -> str:
    posture = str(decision.get("posture", "")).upper()
    pressure = float(decision.get("gateway_pressure", {}).get("score", 0.0))
    if ref_gate_failures > 0 or spent_risk > float(budget["max_risk_spend"]) or spent_actions > int(budget["max_actions"]):
        return "SUSPEND_AUTONOMY"
    if spent_scope_units > float(budget["max_scope_units"]) or blocked_or_held_attempts >= 2:
        return "SUSPEND_AUTONOMY"
    if posture in {"DENY", "FREEZE"} or pressure >= 0.7:
        return "DEGRADE"
    if posture == "THROTTLE" or pressure >= 0.45:
        return "WATCH"
    return "HEALTHY"


def _budget_for_state(initial_state: str, overrides: Mapping[str, Any] | None) -> Dict[str, Any]:
    budget = dict(DEFAULT_BUDGETS[initial_state])
    if overrides:
        budget.update(dict(overrides))
    return budget


def _allowed_risk_tiers(state: str, budget: Mapping[str, Any]) -> list[str]:
    if state in {"SUSPEND_AUTONOMY", "REQUALIFY"}:
        return []
    if state == "DEGRADE":
        return [tier for tier in budget["allowed_tool_risk_tiers"] if tier in {"low", "medium"}]
    if state == "WATCH":
        return [tier for tier in budget["allowed_tool_risk_tiers"] if tier != "destructive"]
    return list(budget["allowed_tool_risk_tiers"])


def _review_triggers(
    *,
    state: str,
    spent_actions: int,
    spent_scope_units: float,
    spent_risk: float,
    budget: Mapping[str, Any],
    ref_gate_failures: int,
    blocked_or_held_attempts: int,
) -> list[str]:
    triggers = []
    if ref_gate_failures:
        triggers.append("ref_gate_failure")
    if spent_actions >= int(budget["max_actions"]):
        triggers.append("action_budget_exhausted")
    if spent_scope_units >= float(budget["max_scope_units"]):
        triggers.append("scope_budget_exhausted")
    if spent_risk >= float(budget["max_risk_spend"]):
        triggers.append("risk_budget_exhausted")
    if blocked_or_held_attempts >= 2:
        triggers.append("repeated_blocked_or_held_attempts")
    if state in {"SUSPEND_AUTONOMY", "REQUALIFY"}:
        triggers.append("autonomy_removed_until_review")
    return triggers


def _summary(
    state: str,
    ref_gate_failures: int,
    blocked_or_held_attempts: int,
    spent_risk: float,
    budget: Mapping[str, Any],
) -> str:
    if state == "SUSPEND_AUTONOMY":
        return (
            "Autonomy should be suspended for this session because the action stream exhausted or violated the "
            "current autonomy budget. Human review should requalify the agent or tool family before more autonomous "
            "execution is allowed."
        )
    if state == "DEGRADE":
        return (
            "Autonomy should be degraded. The system may continue only with reduced scope, safer tools, and stronger "
            "review controls."
        )
    if state == "WATCH":
        return "Autonomy can continue, but the system is using enough budget to justify closer monitoring."
    return (
        f"Autonomy remains healthy. Risk spend is {round(spent_risk, 3)} of {budget['max_risk_spend']}, "
        f"with {ref_gate_failures} ref-gate failures and {blocked_or_held_attempts} blocked or held attempts."
    )


def _max_state(left: str, right: str) -> str:
    return left if STATE_RANK[left] >= STATE_RANK[right] else right


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an autonomy budget from a SMERC gateway report.")
    parser.add_argument("--gateway-report", default="reports/mcp_governance_gateway_report.json")
    parser.add_argument("--initial-state", default="HEALTHY", choices=sorted(AUTONOMY_STATES))
    parser.add_argument("--json-output", default="reports/autonomy_budget_report.json")
    parser.add_argument("--markdown-output", default="reports/Autonomy_Budget_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    gateway_report = json.loads(Path(args.gateway_report).read_text(encoding="utf-8"))
    earned_autonomy = gateway_report.get("earned_autonomy") or {}
    budget_context = earned_autonomy.get("budget_context", {}) if isinstance(earned_autonomy, Mapping) else {}
    report = evaluate_autonomy_budget(
        decisions=gateway_report["decisions"],
        initial_state=str(budget_context.get("initial_state", args.initial_state)),
        budget_overrides=budget_context.get("budget_overrides"),
        earned_autonomy=earned_autonomy,
    )
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

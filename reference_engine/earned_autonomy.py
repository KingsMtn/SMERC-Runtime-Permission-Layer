from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


EARNED_AUTONOMY_VERSION = "smerc.earned-autonomy.v1"
EARNED_AUTONOMY_TIERS = {
    "TIER_0_OBSERVE",
    "TIER_1_ASSIST",
    "TIER_2_CONSTRAINED",
    "TIER_3_BOUNDED",
    "TIER_4_TRUSTED",
    "TIER_5_REQUALIFY_REQUIRED",
}
TIER_ORDER = {
    "TIER_0_OBSERVE": 0,
    "TIER_1_ASSIST": 1,
    "TIER_2_CONSTRAINED": 2,
    "TIER_3_BOUNDED": 3,
    "TIER_4_TRUSTED": 4,
    "TIER_5_REQUALIFY_REQUIRED": -1,
}
TIER_BUDGET_CONTEXT = {
    "TIER_0_OBSERVE": {
        "initial_state": "SUSPEND_AUTONOMY",
        "budget_overrides": {"max_actions": 0, "max_scope_units": 0, "max_risk_spend": 0.0, "valid_for_minutes": 0},
    },
    "TIER_1_ASSIST": {
        "initial_state": "DEGRADE",
        "budget_overrides": {
            "max_actions": 1,
            "max_scope_units": 5,
            "max_risk_spend": 0.25,
            "valid_for_minutes": 10,
            "allowed_tool_risk_tiers": ["low"],
        },
    },
    "TIER_2_CONSTRAINED": {
        "initial_state": "WATCH",
        "budget_overrides": {
            "max_actions": 3,
            "max_scope_units": 25,
            "max_risk_spend": 0.9,
            "valid_for_minutes": 15,
            "allowed_tool_risk_tiers": ["low", "medium"],
        },
    },
    "TIER_3_BOUNDED": {
        "initial_state": "HEALTHY",
        "budget_overrides": {
            "max_actions": 7,
            "max_scope_units": 250,
            "max_risk_spend": 1.8,
            "valid_for_minutes": 30,
            "allowed_tool_risk_tiers": ["low", "medium", "high"],
        },
    },
    "TIER_4_TRUSTED": {
        "initial_state": "HEALTHY",
        "budget_overrides": {
            "max_actions": 12,
            "max_scope_units": 1000,
            "max_risk_spend": 3.2,
            "valid_for_minutes": 60,
            "allowed_tool_risk_tiers": ["low", "medium", "high", "financial"],
        },
    },
    "TIER_5_REQUALIFY_REQUIRED": {
        "initial_state": "REQUALIFY",
        "budget_overrides": {"max_actions": 0, "max_scope_units": 0, "max_risk_spend": 0.0, "valid_for_minutes": 0},
    },
}


def evaluate_earned_autonomy(*, subject_id: str, history: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    records = list(history)
    metrics = _metrics(records)
    tier, drivers = _tier(metrics)
    budget_context = budget_context_for_tier(tier)
    return {
        "version": EARNED_AUTONOMY_VERSION,
        "generated_at": _now(),
        "subject_id": subject_id,
        "earned_tier": tier,
        "metrics": metrics,
        "drivers": drivers,
        "budget_context": budget_context,
        "review_required": tier in {"TIER_0_OBSERVE", "TIER_5_REQUALIFY_REQUIRED"},
        "plain_english_summary": _summary(subject_id, tier, metrics, drivers),
    }


def budget_context_for_tier(tier: str) -> Dict[str, Any]:
    if tier not in EARNED_AUTONOMY_TIERS:
        raise ValueError(f"tier must be one of: {', '.join(sorted(EARNED_AUTONOMY_TIERS))}")
    context = TIER_BUDGET_CONTEXT[tier]
    return {
        "earned_tier": tier,
        "initial_state": context["initial_state"],
        "budget_overrides": dict(context["budget_overrides"]),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Earned Autonomy Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Subject: `{report['subject_id']}`",
        f"- Earned tier: `{report['earned_tier']}`",
        f"- Review required: `{str(report['review_required']).lower()}`",
        f"- Total decisions: `{report['metrics']['total_decisions']}`",
        f"- Reviewer agreement rate: `{report['metrics']['reviewer_agreement_rate']}`",
        f"- Ref-gate failure rate: `{report['metrics']['ref_gate_failure_rate']}`",
        f"- False release rate: `{report['metrics']['false_release_rate']}`",
        f"- Incident count: `{report['metrics']['incident_count']}`",
        "",
        "## Drivers",
        "",
    ]
    lines.extend(f"- `{driver}`" for driver in report["drivers"] or ["none"])
    lines.extend(
        [
            "",
            "## Budget Context",
            "",
            f"- Initial budget state: `{report['budget_context']['initial_state']}`",
            f"- Max actions: `{report['budget_context']['budget_overrides']['max_actions']}`",
            f"- Max scope units: `{report['budget_context']['budget_overrides']['max_scope_units']}`",
            f"- Max risk spend: `{report['budget_context']['budget_overrides']['max_risk_spend']}`",
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


def load_history(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("version") != EARNED_AUTONOMY_VERSION:
        raise ValueError(f"history must have version {EARNED_AUTONOMY_VERSION}")
    return payload


def _metrics(records: list[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    if total == 0:
        return {
            "total_decisions": 0,
            "allow_count": 0,
            "successful_execution_count": 0,
            "reviewer_agreement_rate": 0.0,
            "override_rate": 0.0,
            "ref_gate_failure_rate": 0.0,
            "rollback_success_rate": 0.0,
            "false_release_rate": 0.0,
            "incident_count": 0,
            "near_miss_count": 0,
            "scope_violation_count": 0,
            "evidence_gap_rate": 0.0,
        }
    reviewer_labeled = [item for item in records if item.get("reviewer_agreed") is not None]
    rollback_attempted = [item for item in records if item.get("rollback_attempted")]
    evidence_gap_count = sum(1 for item in records if item.get("evidence_quality") in {"missing", "stale", "self_attested"})
    return {
        "total_decisions": total,
        "allow_count": sum(1 for item in records if str(item.get("posture", "")).upper() == "ALLOW"),
        "successful_execution_count": sum(1 for item in records if item.get("execution_outcome") == "success"),
        "reviewer_agreement_rate": _rate(sum(1 for item in reviewer_labeled if item.get("reviewer_agreed")), len(reviewer_labeled)),
        "override_rate": _rate(sum(1 for item in records if item.get("human_override")), total),
        "ref_gate_failure_rate": _rate(sum(1 for item in records if item.get("ref_gate_status") == "fail"), total),
        "rollback_success_rate": _rate(sum(1 for item in rollback_attempted if item.get("rollback_outcome") == "success"), len(rollback_attempted)),
        "false_release_rate": _rate(sum(1 for item in records if item.get("false_release")), total),
        "incident_count": sum(1 for item in records if item.get("incident")),
        "near_miss_count": sum(1 for item in records if item.get("near_miss")),
        "scope_violation_count": sum(1 for item in records if item.get("scope_violation")),
        "evidence_gap_rate": _rate(evidence_gap_count, total),
    }


def _tier(metrics: Mapping[str, Any]) -> tuple[str, list[str]]:
    drivers = []
    total = int(metrics["total_decisions"])
    if total < 3:
        return "TIER_0_OBSERVE", ["insufficient_history"]
    if metrics["incident_count"] > 0 or metrics["false_release_rate"] > 0:
        drivers.append("incident_or_false_release")
    if metrics["ref_gate_failure_rate"] >= 0.1:
        drivers.append("ref_gate_failure_history")
    if metrics["scope_violation_count"] > 0:
        drivers.append("scope_violation_history")
    if metrics["evidence_gap_rate"] >= 0.2:
        drivers.append("evidence_gap_history")
    if drivers:
        return "TIER_5_REQUALIFY_REQUIRED", drivers
    if total < 8:
        return "TIER_1_ASSIST", ["limited_clean_history"]
    if metrics["reviewer_agreement_rate"] < 0.75 or metrics["override_rate"] > 0.25:
        return "TIER_1_ASSIST", ["weak_reviewer_alignment"]
    if total >= 50 and metrics["reviewer_agreement_rate"] >= 0.95 and metrics["override_rate"] <= 0.05:
        return "TIER_4_TRUSTED", ["large_clean_history", "high_reviewer_alignment"]
    if total >= 20 and metrics["reviewer_agreement_rate"] >= 0.88 and metrics["override_rate"] <= 0.12:
        return "TIER_3_BOUNDED", ["clean_operating_history", "stable_reviewer_alignment"]
    return "TIER_2_CONSTRAINED", ["adequate_but_not_deep_history"]


def _summary(subject_id: str, tier: str, metrics: Mapping[str, Any], drivers: list[str]) -> str:
    if tier == "TIER_5_REQUALIFY_REQUIRED":
        return (
            f"{subject_id} has not earned continued autonomy. The history contains disqualifying evidence: "
            f"{', '.join(drivers)}. Require review and requalification before granting autonomous execution."
        )
    if tier == "TIER_0_OBSERVE":
        return f"{subject_id} has insufficient history. Keep it in observe mode until it produces reviewable evidence."
    return (
        f"{subject_id} earned {tier} based on {metrics['total_decisions']} prior decisions, "
        f"reviewer agreement {metrics['reviewer_agreement_rate']}, and override rate {metrics['override_rate']}."
    )


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate earned autonomy from historical SMERC decision outcomes.")
    parser.add_argument("--history", default="examples/autonomy/agent_history.json")
    parser.add_argument("--subject-id", default=None)
    parser.add_argument("--json-output", default="reports/earned_autonomy_report.json")
    parser.add_argument("--markdown-output", default="reports/Earned_Autonomy_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = load_history(args.history)
    subject_id = args.subject_id or payload["subject_id"]
    report = evaluate_earned_autonomy(subject_id=subject_id, history=payload["history"])
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

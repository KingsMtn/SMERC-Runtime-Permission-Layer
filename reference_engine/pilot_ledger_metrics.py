from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.decision_lifecycle_ledger import LEDGER_VERSION, DecisionLifecycleLedger
from reference_engine.pilot_ledger_intake import PILOT_LEDGER_RESULT_VERSION


PILOT_LEDGER_METRICS_VERSION = "smerc.pilot-ledger-metrics.v1"


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 3)


def _load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def load_ledgers(paths: Iterable[str | Path]) -> list[Dict[str, Any]]:
    ledgers: list[Dict[str, Any]] = []
    for path in paths:
        payload = _load_json(path)
        if payload.get("version") == PILOT_LEDGER_RESULT_VERSION:
            ledger = payload.get("ledger")
            if not isinstance(ledger, dict):
                raise ValueError(f"{path} is missing a ledger object")
            ledgers.append(ledger)
        elif payload.get("version") == LEDGER_VERSION:
            ledgers.append(payload)
        else:
            raise ValueError(f"{path} must be a pilot intake result or DLL ledger")
    if not ledgers:
        raise ValueError("at least one ledger or pilot intake result is required")
    return ledgers


def _records_by_type(ledger: Mapping[str, Any], event_type: str) -> list[Mapping[str, Any]]:
    return [record for record in ledger.get("records", []) if record.get("event_type") == event_type]


def _first_payload(ledger: Mapping[str, Any], event_type: str) -> Mapping[str, Any] | None:
    records = _records_by_type(ledger, event_type)
    if not records:
        return None
    payload = records[0].get("payload")
    return payload if isinstance(payload, dict) else None


def summarize_ledgers(ledgers: list[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(ledgers)
    invalid = []
    complete = []
    decision_time_only = []
    reviewer_agreements = 0
    reviewer_overrides = 0
    human_reviewed = 0
    executed = 0
    execution_success = 0
    rollback_performed = 0
    rollback_success = 0
    outcome_reviewed = 0
    judged_correct = 0
    unexpected_consequence = 0
    controls_sufficient = 0
    learning_recommendations = 0
    posture_counts: Counter[str] = Counter()
    final_posture_counts: Counter[str] = Counter()
    event_completion_counts: Counter[str] = Counter()
    for ledger_payload in ledgers:
        ledger = DecisionLifecycleLedger.from_dict(ledger_payload)
        data = ledger.to_dict()
        decision_id = data["decision_id"]
        if not data["verification"]["valid"]:
            invalid.append(decision_id)
            continue
        summary = data["summary"]
        event_counts = summary["event_counts"]
        for event_type, count in event_counts.items():
            if count:
                event_completion_counts[event_type] += 1
        evaluation = _first_payload(data, "EVALUATION")
        if evaluation:
            posture_counts[str(evaluation.get("authorization_recommendation"))] += 1
        human = _first_payload(data, "HUMAN_INTERACTION")
        if human:
            human_reviewed += 1
            final_posture_counts[str(human.get("final_recommendation"))] += 1
            if human.get("interaction") == "accepted":
                reviewer_agreements += 1
            if human.get("interaction") == "overrode":
                reviewer_overrides += 1
        execution = _first_payload(data, "EXECUTION")
        if execution:
            executed += 1
            if execution.get("execution_status") == "succeeded":
                execution_success += 1
            if execution.get("rollback_performed"):
                rollback_performed += 1
                if execution.get("rollback_success"):
                    rollback_success += 1
        outcome = _first_payload(data, "OUTCOME")
        if outcome:
            outcome_reviewed += 1
            if outcome.get("judged_correct"):
                judged_correct += 1
            if outcome.get("unexpected_consequences"):
                unexpected_consequence += 1
            if outcome.get("controls_sufficient"):
                controls_sufficient += 1
        learning = _first_payload(data, "LEARNING_RECOMMENDATION")
        if learning:
            learning_recommendations += 1
        if event_counts.get("EXECUTION", 0) and event_counts.get("OUTCOME", 0):
            complete.append(decision_id)
        else:
            decision_time_only.append(decision_id)
    return {
        "ledger_count": total,
        "valid_ledger_count": total - len(invalid),
        "invalid_ledger_count": len(invalid),
        "invalid_ledger_ids": invalid,
        "complete_lifecycle_count": len(complete),
        "decision_time_only_count": len(decision_time_only),
        "human_reviewed_count": human_reviewed,
        "reviewer_agreement_count": reviewer_agreements,
        "reviewer_override_count": reviewer_overrides,
        "reviewer_agreement_rate": _rate(reviewer_agreements, human_reviewed),
        "reviewer_override_rate": _rate(reviewer_overrides, human_reviewed),
        "executed_count": executed,
        "execution_success_count": execution_success,
        "execution_success_rate": _rate(execution_success, executed),
        "rollback_performed_count": rollback_performed,
        "rollback_success_count": rollback_success,
        "rollback_success_rate": _rate(rollback_success, rollback_performed),
        "outcome_reviewed_count": outcome_reviewed,
        "judged_correct_count": judged_correct,
        "judged_correct_rate": _rate(judged_correct, outcome_reviewed),
        "unexpected_consequence_count": unexpected_consequence,
        "unexpected_consequence_rate": _rate(unexpected_consequence, outcome_reviewed),
        "controls_sufficient_count": controls_sufficient,
        "controls_sufficient_rate": _rate(controls_sufficient, outcome_reviewed),
        "learning_recommendation_count": learning_recommendations,
        "initial_posture_counts": dict(sorted(posture_counts.items())),
        "final_review_posture_counts": dict(sorted(final_posture_counts.items())),
        "event_completion_counts": dict(sorted(event_completion_counts.items())),
        "complete_lifecycle_ids": complete,
        "decision_time_only_ids": decision_time_only,
    }


def build_metrics(paths: Iterable[str | Path]) -> Dict[str, Any]:
    summary = summarize_ledgers(load_ledgers(paths))
    caveats = [
        "Metrics disclose denominators and must not be generalized beyond the supplied ledger set.",
        "Synthetic examples are useful for workflow testing, not customer validation.",
        "Production claims require customer pilot ledgers, reviewer labels, execution evidence, and outcome review.",
    ]
    if summary["ledger_count"] < 30:
        caveats.append("Sample size is below 30 ledgers; treat rates as directional workflow checks only.")
    if summary["complete_lifecycle_count"] == 0:
        caveats.append("No complete lifecycles are present; outcome and execution rates are unavailable.")
    return {
        "version": PILOT_LEDGER_METRICS_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "summary": summary,
        "caveats": caveats,
        "recommended_next_action": recommended_next_action(summary),
    }


def recommended_next_action(summary: Mapping[str, Any]) -> str:
    if summary["invalid_ledger_count"]:
        return "Resolve invalid DLL hash chains before using these metrics in a pilot review."
    if summary["complete_lifecycle_count"] < 30:
        return "Collect more design-partner ledgers before treating these rates as operational evidence."
    if summary["reviewer_agreement_rate"] is not None and summary["reviewer_agreement_rate"] < 0.6:
        return "Review threshold calibration with security reviewers before enforcement."
    return "Use the metrics as pilot review evidence while continuing to collect production-context outcomes."


def render_markdown(metrics: Mapping[str, Any]) -> str:
    summary = metrics["summary"]
    lines = [
        "# SMERC Pilot Ledger Metrics Report",
        "",
        f"Generated: `{metrics['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        (
            f"This report summarizes `{summary['ledger_count']}` Decision Lifecycle Ledger record(s), "
            f"including `{summary['complete_lifecycle_count']}` complete lifecycle(s)."
        ),
        "",
        "Metrics are evidence accounting, not proof of production risk reduction.",
        "",
        "## Core Metrics",
        "",
        f"- Valid ledgers: `{summary['valid_ledger_count']}` / `{summary['ledger_count']}`",
        f"- Human reviewed: `{summary['human_reviewed_count']}` / `{summary['ledger_count']}`",
        f"- Reviewer agreement rate: `{summary['reviewer_agreement_rate']}`",
        f"- Reviewer override rate: `{summary['reviewer_override_rate']}`",
        f"- Executed: `{summary['executed_count']}` / `{summary['ledger_count']}`",
        f"- Execution success rate: `{summary['execution_success_rate']}`",
        f"- Outcome reviewed: `{summary['outcome_reviewed_count']}` / `{summary['ledger_count']}`",
        f"- Judged correct rate: `{summary['judged_correct_rate']}`",
        f"- Unexpected consequence rate: `{summary['unexpected_consequence_rate']}`",
        f"- Controls sufficient rate: `{summary['controls_sufficient_rate']}`",
        f"- Learning recommendations: `{summary['learning_recommendation_count']}`",
        "",
        "## Posture Counts",
        "",
        f"- Initial SMERC postures: `{summary['initial_posture_counts']}`",
        f"- Final reviewed postures: `{summary['final_review_posture_counts']}`",
        "",
        "## Caveats",
        "",
    ]
    lines.extend(f"- {item}" for item in metrics["caveats"])
    lines.extend(["", "## Recommended Next Action", "", metrics["recommended_next_action"], ""])
    return "\n".join(lines)


def write_outputs(metrics: Mapping[str, Any], json_path: str | Path, markdown_path: str | Path) -> None:
    json_file = Path(json_path)
    markdown_file = Path(markdown_path)
    json_file.parent.mkdir(parents=True, exist_ok=True)
    markdown_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_file.write_text(render_markdown(metrics), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize pilot evidence from SMERC Decision Lifecycle Ledgers.")
    parser.add_argument("inputs", nargs="+", help="Pilot intake result JSON or DLL JSON files.")
    parser.add_argument("--json-output", default="reports/pilot_ledger_metrics.json")
    parser.add_argument("--markdown-output", default="reports/Pilot_Ledger_Metrics_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    metrics = build_metrics(args.inputs)
    write_outputs(metrics, args.json_output, args.markdown_output)
    print(json.dumps(metrics, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

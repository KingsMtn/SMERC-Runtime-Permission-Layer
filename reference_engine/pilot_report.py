from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from reference_engine.agent_permission_layer import RuntimePermissionEngine


POSTURE_ORDER = ["ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"]


def load_actions(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise TypeError("Pilot report expects a JSON list of action requests.")
    if not payload:
        raise ValueError("Pilot report requires at least one action request.")
    return payload


def evaluate_actions(actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    engine = RuntimePermissionEngine()
    records: List[Dict[str, Any]] = []
    for action in actions:
        decision = engine.evaluate(action)
        records.append({"action": action, "decision": decision})
    return records


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    posture_counts = Counter(record["decision"]["posture"] for record in records)
    total = len(records)
    non_allow = total - posture_counts.get("ALLOW", 0)
    constrained = posture_counts.get("THROTTLE", 0) + posture_counts.get("FREEZE", 0) + posture_counts.get("ESCALATE", 0)
    average_risk = sum(record["decision"]["risk_score"] for record in records) / total
    average_confidence = sum(record["decision"]["confidence_score"] for record in records) / total
    return {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "total_actions": total,
        "posture_counts": {posture: posture_counts.get(posture, 0) for posture in POSTURE_ORDER},
        "non_allow_rate": round(non_allow / total, 3),
        "constraint_rate": round(constrained / total, 3),
        "average_risk_score": round(average_risk, 3),
        "average_confidence_score": round(average_confidence, 3),
    }


def markdown_report(records: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    lines: List[str] = [
        "# SMERC GitHub Actions Shadow-Mode Pilot Report",
        "",
        f"Generated: `{summary['evaluated_at']}`",
        "",
        "## Executive Summary",
        "",
        (
            f"SMERC evaluated `{summary['total_actions']}` AI-assisted GitHub Actions scenarios. "
            f"The average risk score was `{summary['average_risk_score']}` and the average confidence score was "
            f"`{summary['average_confidence_score']}`."
        ),
        "",
        "This report is synthetic pilot evidence. It is intended to show the shape of a shadow-mode evaluation before a design partner supplies live workflow data.",
        "",
        "## Posture Distribution",
        "",
        "| Posture | Count |",
        "| --- | ---: |",
    ]
    for posture in POSTURE_ORDER:
        lines.append(f"| `{posture}` | {summary['posture_counts'][posture]} |")
    lines.extend(
        [
            "",
            "## Pilot Signals",
            "",
            f"- Non-allow rate: `{summary['non_allow_rate']}`",
            f"- Constraint-or-review rate: `{summary['constraint_rate']}`",
            "",
            "Non-allow decisions are not automatically evidence of value. In a live pilot, these decisions must be compared against reviewer agreement, overrides, false constraints, and false releases.",
            "",
            "## Scenario Decisions",
            "",
            "| Action | Existing Control Context | SMERC Posture | Risk | Confidence | Primary Reasons |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for record in records:
        action = record["action"]
        decision = record["decision"]
        context = action.get("context", {})
        controls = ", ".join(context.get("existing_controls", [])) or "none provided"
        reasons = ", ".join(decision["reason_codes"])
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_table(action["action_id"]),
                    escape_table(controls),
                    f"`{decision['posture']}`",
                    str(decision["risk_score"]),
                    str(decision["confidence_score"]),
                    escape_table(reasons),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## What This Would Prove In A Live Pilot",
            "",
            "- Whether recoverability-aware scoring changes reviewer judgment.",
            "- Whether SMERC catches risky actions that existing allow/deny controls permit.",
            "- Whether `THROTTLE`, `FREEZE`, and `ESCALATE` reduce unnecessary blocking while preserving safety.",
            "- Whether the extra review burden is acceptable.",
            "",
            "## What This Does Not Prove Yet",
            "",
            "- It does not prove production safety.",
            "- It does not prove calibrated thresholds for a specific enterprise.",
            "- It does not replace branch protection, code review, IAM, OPA, SIEM, EDR, or deployment approvals.",
            "- It does not establish regulatory compliance.",
        ]
    )
    return "\n".join(lines) + "\n"


def escape_table(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_json(path: Path, records: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"summary": summary, "records": records}, indent=2), encoding="utf-8")


def write_markdown(path: Path, records: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_report(records, summary), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a SMERC shadow-mode pilot report from action scenarios.")
    parser.add_argument("path", help="Path to a JSON list of action requests.")
    parser.add_argument("--json-output", default="reports/github_actions_shadow_mode_results.json")
    parser.add_argument("--markdown-output", default="reports/GitHub_Actions_Shadow_Mode_Pilot_Report.md")
    args = parser.parse_args()

    records = evaluate_actions(load_actions(Path(args.path)))
    summary = summarize(records)
    write_json(Path(args.json_output), records, summary)
    write_markdown(Path(args.markdown_output), records, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

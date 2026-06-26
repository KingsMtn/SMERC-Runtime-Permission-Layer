from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from reference_engine.recoverability_engine import evaluate_batch


POSTURES = ["ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"]


def load_actions(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise TypeError("Recoverability report expects a JSON list.")
    return payload


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = Counter(record["posture"] for record in records)
    total = len(records)
    if total == 0:
        raise ValueError("At least one record is required.")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_actions": total,
        "posture_counts": {posture: counts.get(posture, 0) for posture in POSTURES},
        "average_irreversible_exposure": avg(records, "irreversible_exposure_score"),
        "average_reversible_capacity": avg(records, "reversible_capacity_score"),
        "average_authorization_score": avg(records, "risk_adjusted_authorization_score"),
        "non_release_rate": round((total - counts.get("ALLOW", 0)) / total, 3),
    }


def avg(records: List[Dict[str, Any]], score_key: str) -> float:
    return round(sum(record["scores"][score_key] for record in records) / len(records), 3)


def markdown(records: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    lines = [
        "# SMERC Recoverability Engine Report",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Actions evaluated: `{summary['total_actions']}`",
        f"- Non-release rate: `{summary['non_release_rate']}`",
        f"- Average irreversible exposure: `{summary['average_irreversible_exposure']}`",
        f"- Average reversible capacity: `{summary['average_reversible_capacity']}`",
        f"- Average authorization score: `{summary['average_authorization_score']}`",
        "",
        "## Posture Distribution",
        "",
        "| Posture | Count |",
        "| --- | ---: |",
    ]
    for posture in POSTURES:
        lines.append(f"| `{posture}` | {summary['posture_counts'][posture]} |")
    lines.extend(
        [
            "",
            "## Action Decisions",
            "",
            "| Action | Posture | Enforcement | Exposure | Capacity | Authorization | Reason Codes |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for record in records:
        scores = record["scores"]
        lines.append(
            "| "
            + " | ".join(
                [
                    safe(record["action_id"]),
                    f"`{record['posture']}`",
                    f"`{record['enforcement_state']}`",
                    str(scores["irreversible_exposure_score"]),
                    str(scores["reversible_capacity_score"]),
                    str(scores["risk_adjusted_authorization_score"]),
                    safe(", ".join(record["reason_codes"])),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Product Interpretation",
            "",
            "This report demonstrates SMERC as a recoverability-aware pre-execution decision layer. In a real pilot, each non-release decision should be compared against human reviewer judgment, existing policy outcomes, overrides, and operational latency.",
        ]
    )
    return "\n".join(lines) + "\n"


def safe(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_bundle(actions_path: Path, json_output: Path, markdown_output: Path) -> Dict[str, Any]:
    records = evaluate_batch(load_actions(actions_path))
    summary = summarize(records)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps({"summary": summary, "records": records}, indent=2), encoding="utf-8")
    markdown_output.write_text(markdown(records, summary), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a recoverability-engine evidence bundle.")
    parser.add_argument("path", help="JSON list of recoverability action requests.")
    parser.add_argument("--json-output", default="reports/recoverability_engine_results.json")
    parser.add_argument("--markdown-output", default="reports/Recoverability_Engine_Report.md")
    args = parser.parse_args()
    summary = write_bundle(Path(args.path), Path(args.json_output), Path(args.markdown_output))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

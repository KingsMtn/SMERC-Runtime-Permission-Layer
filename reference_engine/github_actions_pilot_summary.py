from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


POSTURES = ["ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE", "UNAVAILABLE"]


def expand_paths(paths: Iterable[Path]) -> List[Path]:
    expanded: List[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(item for item in path.glob("*.json") if item.is_file()))
        elif path.is_file():
            expanded.append(path)
        else:
            raise FileNotFoundError(f"Pilot report path not found: {path}")
    if not expanded:
        raise ValueError("At least one SMERC decision report is required.")
    return expanded


def load_reports(paths: Iterable[Path]) -> List[Dict[str, Any]]:
    reports: List[Dict[str, Any]] = []
    for path in expand_paths(paths):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TypeError(f"SMERC decision report must be a JSON object: {path}")
        report = normalize_report(payload, source_path=path)
        reports.append(report)
    return reports


def normalize_report(payload: Dict[str, Any], *, source_path: Path) -> Dict[str, Any]:
    status = payload.get("integration_status")
    if status not in {"evaluated", "unavailable"}:
        raise ValueError(f"Invalid integration_status in {source_path}")
    decision = payload.get("decision")
    if status == "evaluated":
        if not isinstance(decision, dict):
            raise ValueError(f"Evaluated report is missing a decision object: {source_path}")
        posture = decision.get("posture")
        if posture not in POSTURES[:-1]:
            raise ValueError(f"Invalid decision posture in {source_path}")
    else:
        posture = "UNAVAILABLE"
    enforcement = payload.get("enforcement", {})
    if enforcement is not None and not isinstance(enforcement, dict):
        raise ValueError(f"Invalid enforcement object in {source_path}")

    return {
        "source_path": str(source_path),
        "mode": payload.get("mode", ""),
        "source": payload.get("source", ""),
        "integration_status": status,
        "posture": posture,
        "would_fail": bool(enforcement.get("would_fail")) if isinstance(enforcement, dict) else False,
        "risk_score": score_value(decision, "risk_score", "irreversible_exposure_score"),
        "confidence_score": score_value(decision, "confidence_score", "confidence_score"),
        "reason_codes": string_list(decision, "reason_codes"),
        "controls": controls(decision),
        "replay_id": decision.get("replay_id") if isinstance(decision, dict) else "",
        "summary": decision.get("plain_english_summary", "") if isinstance(decision, dict) else "",
        "error": payload.get("error") if status == "unavailable" else None,
    }


def score_value(decision: Any, direct_key: str, nested_key: str) -> Optional[float]:
    if not isinstance(decision, dict):
        return None
    value = decision.get(direct_key)
    if value is None and isinstance(decision.get("scores"), dict):
        value = decision["scores"].get(nested_key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return round(float(value), 3)


def string_list(decision: Any, key: str) -> List[str]:
    if not isinstance(decision, dict):
        return []
    values = decision.get(key, [])
    if not isinstance(values, list):
        return []
    return [item for item in values if isinstance(item, str)]


def controls(decision: Any) -> List[str]:
    if not isinstance(decision, dict):
        return []
    return string_list(decision, "controls") or string_list(decision, "constraints")


def summarize(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not reports:
        raise ValueError("At least one normalized report is required.")
    posture_counts = Counter(report["posture"] for report in reports)
    reason_counts = Counter(reason for report in reports for reason in report["reason_codes"])
    control_counts = Counter(control for report in reports for control in report["controls"])
    risk_scores = [report["risk_score"] for report in reports if report["risk_score"] is not None]
    confidence_scores = [report["confidence_score"] for report in reports if report["confidence_score"] is not None]
    total = len(reports)
    unavailable = posture_counts.get("UNAVAILABLE", 0)
    evaluated = total - unavailable
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_reports": total,
        "evaluated_reports": evaluated,
        "unavailable_reports": unavailable,
        "posture_counts": {posture: posture_counts.get(posture, 0) for posture in POSTURES},
        "non_allow_rate": round((total - posture_counts.get("ALLOW", 0)) / total, 3),
        "unavailable_rate": round(unavailable / total, 3),
        "would_fail_count": sum(1 for report in reports if report["would_fail"]),
        "average_risk_score": average(risk_scores),
        "average_confidence_score": average(confidence_scores),
        "top_reason_codes": reason_counts.most_common(10),
        "top_controls": control_counts.most_common(10),
        "evidence_boundary": "GitHub Actions decision artifacts only; reviewer labels and outcome evidence must be collected separately.",
    }


def average(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def markdown_report(reports: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    lines = [
        "# SMERC GitHub Actions Pilot Artifact Summary",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        (
            f"SMERC summarized `{summary['total_reports']}` GitHub Actions decision artifacts. "
            f"`{summary['evaluated_reports']}` were evaluated and `{summary['unavailable_reports']}` were unavailable."
        ),
        "",
        "This is pilot artifact evidence, not production validation. It does not measure false release, false constraint, incident reduction, or reviewer agreement unless customer review labels are supplied through a separate pilot review process.",
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
            "## Operating Signals",
            "",
            f"- Non-allow-or-unavailable rate: `{summary['non_allow_rate']}`",
            f"- Unavailable rate: `{summary['unavailable_rate']}`",
            f"- Would-fail count under current enforcement settings: `{summary['would_fail_count']}`",
            f"- Average risk score: `{summary['average_risk_score']}`",
            f"- Average confidence score: `{summary['average_confidence_score']}`",
            "",
            "## Top Reason Codes",
            "",
            "| Reason Code | Count |",
            "| --- | ---: |",
        ]
    )
    for reason, count in summary["top_reason_codes"]:
        lines.append(f"| `{escape_table(reason)}` | {count} |")
    if not summary["top_reason_codes"]:
        lines.append("| none | 0 |")
    lines.extend(["", "## Top Controls", "", "| Control | Count |", "| --- | ---: |"])
    for control, count in summary["top_controls"]:
        lines.append(f"| `{escape_table(control)}` | {count} |")
    if not summary["top_controls"]:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Decision Artifacts",
            "",
            "| Source | Mode | Integration | Posture | Risk | Confidence | Replay ID |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for report in reports:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_table(report["source_path"]),
                    escape_table(report["mode"]),
                    escape_table(report["integration_status"]),
                    f"`{report['posture']}`",
                    str(report["risk_score"]),
                    str(report["confidence_score"]),
                    escape_table(report["replay_id"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Required Human Review",
            "",
            "A commercially meaningful pilot still needs reviewer labels, override reasons, delayed outcomes, rollback observations, latency measurements, and a go/no-go decision. Use `pilot_package/Weekly_Review_Template.md` and `pilot_package/Go_No_Go_Criteria.md` to complete that review.",
        ]
    )
    return "\n".join(lines) + "\n"


def escape_table(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_json(path: Path, reports: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"summary": summary, "reports": reports}, indent=2), encoding="utf-8")


def write_markdown(path: Path, reports: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_report(reports, summary), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize SMERC GitHub Actions decision artifacts.")
    parser.add_argument("paths", nargs="+", help="Decision report JSON files or directories containing JSON reports.")
    parser.add_argument("--json-output", default="reports/github_actions_pilot_artifact_summary.json")
    parser.add_argument("--markdown-output", default="reports/GitHub_Actions_Pilot_Artifact_Summary.md")
    args = parser.parse_args()

    reports = load_reports(Path(path) for path in args.paths)
    summary = summarize(reports)
    write_json(Path(args.json_output), reports, summary)
    write_markdown(Path(args.markdown_output), reports, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()


from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


REAL_INCIDENT_REPLAY_VERSION = "smerc.real-public-incident-replay.v1"
POSTURES = ["ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"]


def load_scenarios(path: Path) -> list[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("real incident replay requires a non-empty JSON array")
    seen = set()
    for index, scenario in enumerate(payload):
        if not isinstance(scenario, dict):
            raise TypeError(f"scenario {index} must be an object")
        for field in [
            "scenario_id",
            "source",
            "category",
            "replay_question",
            "traditional_policy_outcome",
            "traditional_policy_rationale",
            "action",
        ]:
            if field not in scenario:
                raise ValueError(f"scenario {index} is missing {field}")
        if scenario["scenario_id"] in seen:
            raise ValueError(f"duplicate scenario_id: {scenario['scenario_id']}")
        seen.add(scenario["scenario_id"])
        if scenario["traditional_policy_outcome"] not in {"ALLOW", "DENY"}:
            raise ValueError("traditional_policy_outcome must be ALLOW or DENY")
        _validate_source(scenario["source"], index)
        context = scenario["action"].get("context", {})
        if context.get("analyst_assigned_signals") is not True:
            raise ValueError(f"scenario {index} must mark analyst_assigned_signals true")
    return payload


def _validate_source(source: Any, index: int) -> None:
    if not isinstance(source, dict):
        raise TypeError(f"scenario {index}.source must be an object")
    for field in ["title", "publisher", "url", "incident_date", "source_facts"]:
        if field not in source:
            raise ValueError(f"scenario {index}.source is missing {field}")
    if not isinstance(source["source_facts"], list) or not source["source_facts"]:
        raise ValueError(f"scenario {index}.source.source_facts must be a non-empty list")


def evaluate_scenarios(scenarios: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    engine = RecoverabilityEngine()
    records = []
    for scenario in scenarios:
        decision = engine.evaluate(dict(scenario["action"]))
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "source": scenario["source"],
                "replay_question": scenario["replay_question"],
                "traditional_policy_outcome": scenario["traditional_policy_outcome"],
                "traditional_policy_rationale": scenario["traditional_policy_rationale"],
                "smerc_posture": decision["posture"],
                "smerc_enforcement_state": decision["enforcement_state"],
                "irreversible_exposure_score": decision["scores"]["irreversible_exposure_score"],
                "reversible_capacity_score": decision["scores"]["reversible_capacity_score"],
                "risk_adjusted_authorization_score": decision["scores"]["risk_adjusted_authorization_score"],
                "operational_stress_score": decision["scores"]["operational_stress_score"],
                "confidence_score": decision["scores"]["confidence_score"],
                "reason_codes": decision["reason_codes"],
                "controls": decision["controls"],
                "plain_english_summary": decision["plain_english_summary"],
                "source_to_signal_boundary": (
                    "Source facts identify a public incident pattern; SMERC numeric inputs are analyst-assigned "
                    "replay assumptions and are not reconstructed telemetry from the source organization."
                ),
                "action": scenario["action"],
            }
        )
    return records


def summarize(records: list[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    if total == 0:
        raise ValueError("real incident replay requires at least one record")
    posture_counts = Counter(str(record["smerc_posture"]) for record in records)
    category_scores: dict[str, list[float]] = defaultdict(list)
    differences = 0
    for record in records:
        category_scores[str(record["category"])].append(float(record["irreversible_exposure_score"]))
        if not (
            record["traditional_policy_outcome"] == "ALLOW"
            and record["smerc_posture"] == "ALLOW"
        ) and not (
            record["traditional_policy_outcome"] == "DENY"
            and record["smerc_posture"] == "DENY"
        ):
            differences += 1
    highest_exposure = sorted(
        (
            {
                "category": category,
                "average_irreversible_exposure": round(sum(values) / len(values), 3),
                "scenario_count": len(values),
            }
            for category, values in category_scores.items()
        ),
        key=lambda item: item["average_irreversible_exposure"],
        reverse=True,
    )
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "evidence_type": "real_public_incident_replay",
        "evidence_limit": (
            "Public incident facts with analyst-assigned SMERC replay inputs; not customer telemetry, "
            "not reconstructed source-system state, and not proof of prevention."
        ),
        "total_scenarios": total,
        "source_count": len({record["source"]["url"] for record in records}),
        "decision_difference_count": differences,
        "decision_difference_rate": round(differences / total, 3),
        "smerc_posture_counts": {posture: posture_counts.get(posture, 0) for posture in POSTURES},
        "highest_irreversible_exposure_categories": highest_exposure,
        "average_irreversible_exposure_score": round(
            sum(float(record["irreversible_exposure_score"]) for record in records) / total,
            3,
        ),
        "average_reversible_capacity_score": round(
            sum(float(record["reversible_capacity_score"]) for record in records) / total,
            3,
        ),
    }


def build_report(records: list[Dict[str, Any]]) -> Dict[str, Any]:
    summary = summarize(records)
    report = {
        "version": REAL_INCIDENT_REPLAY_VERSION,
        "summary": summary,
        "records": records,
        "boundary": {
            "claims": [
                "replays real public incident patterns through the SMERC reference engine",
                "preserves source URLs, source facts, and analyst-assigned signal boundaries",
                "shows whether SMERC would add restraint compared with simple allow/deny assumptions",
            ],
            "limits": [
                "does not prove SMERC would have prevented the public incident",
                "does not use private telemetry from the source organization",
                "does not calibrate thresholds from ground-truth customer labels",
                "does not replace a design-partner pilot",
            ],
        },
    }
    report["markdown_report"] = render_markdown(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# SMERC Real Public Incident Replay Report",
        "",
        "This report replays public incident patterns through SMERC. Public source facts are real; SMERC numeric signals are analyst-assigned replay inputs.",
        "",
        "## Summary",
        "",
        f"- Scenario count: `{summary['total_scenarios']}`",
        f"- Public source count: `{summary['source_count']}`",
        f"- Decision difference rate: `{summary['decision_difference_rate']}`",
        f"- Average irreversible exposure: `{summary['average_irreversible_exposure_score']}`",
        f"- Average reversible capacity: `{summary['average_reversible_capacity_score']}`",
        "",
        "## Replay Results",
        "",
        "| Scenario | Source | Traditional | SMERC | Exposure | Capacity | Question |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for record in report["records"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape(record["scenario_id"]),
                    f"[{escape(record['source']['publisher'])}]({record['source']['url']})",
                    f"`{record['traditional_policy_outcome']}`",
                    f"`{record['smerc_posture']}`",
                    f"`{record['irreversible_exposure_score']}`",
                    f"`{record['reversible_capacity_score']}`",
                    escape(record["replay_question"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Boundary", ""])
    lines.extend(f"- {item}" for item in report["boundary"]["limits"])
    return "\n".join(lines) + "\n"


def escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_outputs(report: Mapping[str, Any], json_output: Path, markdown_output: Path) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(str(report["markdown_report"]), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay public incident patterns through SMERC.")
    parser.add_argument("scenarios", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    records = evaluate_scenarios(load_scenarios(args.scenarios))
    report = build_report(records)
    if args.json_output or args.markdown_output:
        write_outputs(
            report,
            args.json_output or Path("real-public-incident-replay.json"),
            args.markdown_output or Path("Real_Public_Incident_Replay_Report.md"),
        )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

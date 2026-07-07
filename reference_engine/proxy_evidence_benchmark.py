from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from reference_engine.recoverability_engine import RecoverabilityEngine


POSTURES = ["ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"]
RESTRAINT_POSTURES = {"THROTTLE", "FREEZE", "ESCALATE"}
BLOCKING_POSTURES = {"DENY"}


def load_scenarios(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise TypeError("Proxy evidence benchmark expects a JSON list of scenarios.")
    if not payload:
        raise ValueError("Proxy evidence benchmark requires at least one scenario.")
    scenario_ids = set()
    for index, scenario in enumerate(payload):
        if not isinstance(scenario, dict):
            raise TypeError(f"Scenario {index} must be an object.")
        for field in [
            "scenario_id",
            "category",
            "incident_pattern",
            "traditional_policy_outcome",
            "traditional_policy_rationale",
            "action",
        ]:
            if field not in scenario:
                raise ValueError(f"Scenario {index} is missing {field}.")
        if scenario["scenario_id"] in scenario_ids:
            raise ValueError(f"Duplicate scenario_id: {scenario['scenario_id']}")
        scenario_ids.add(scenario["scenario_id"])
        if scenario["traditional_policy_outcome"] not in {"ALLOW", "DENY"}:
            raise ValueError("traditional_policy_outcome must be ALLOW or DENY.")
    return payload


def evaluate_scenarios(scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    engine = RecoverabilityEngine()
    records = []
    for scenario in scenarios:
        decision = engine.evaluate(scenario["action"])
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "incident_pattern": scenario["incident_pattern"],
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
                "recoverability_analysis": recoverability_analysis(scenario, decision),
                "action": scenario["action"],
            }
        )
    return records


def recoverability_analysis(scenario: Dict[str, Any], decision: Dict[str, Any]) -> str:
    action = scenario["action"]
    exposure = decision["scores"]["irreversible_exposure_score"]
    capacity = decision["scores"]["reversible_capacity_score"]
    if exposure >= 0.72 and capacity < 0.45:
        return "High irreversible exposure and weak reversible capacity make automated execution difficult to defend."
    if exposure >= 0.58 and decision["posture"] in RESTRAINT_POSTURES:
        return "Recoverability is incomplete, so SMERC preserves options with constraints, pause, or escalation rather than a simple allow."
    if decision["posture"] == "ALLOW":
        return "Reversibility, containment, evidence, and impact profile are strong enough for automated release under the reference policy."
    return "SMERC applies additional restraint because the action has limited recovery margin under the reference policy."


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    posture_counts = Counter(record["smerc_posture"] for record in records)
    traditional_counts = Counter(record["traditional_policy_outcome"] for record in records)
    differences = [
        record
        for record in records
        if not (
            record["traditional_policy_outcome"] == "ALLOW"
            and record["smerc_posture"] == "ALLOW"
        )
        and not (
            record["traditional_policy_outcome"] == "DENY"
            and record["smerc_posture"] == "DENY"
        )
    ]
    constrained_not_blocked = [
        record
        for record in differences
        if record["traditional_policy_outcome"] == "ALLOW"
        and record["smerc_posture"] in RESTRAINT_POSTURES
    ]
    exposure_by_category: Dict[str, List[float]] = defaultdict(list)
    for record in records:
        exposure_by_category[record["category"]].append(record["irreversible_exposure_score"])
    highest_exposure = sorted(
        (
            {
                "category": category,
                "average_irreversible_exposure": round(sum(values) / len(values), 3),
                "scenario_count": len(values),
            }
            for category, values in exposure_by_category.items()
        ),
        key=lambda item: item["average_irreversible_exposure"],
        reverse=True,
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_type": "proxy_replay_benchmark",
        "evidence_limit": "Scenario-based proxy evidence generated from incident patterns; not production validation.",
        "total_scenarios": total,
        "traditional_policy_counts": {
            "ALLOW": traditional_counts.get("ALLOW", 0),
            "DENY": traditional_counts.get("DENY", 0),
        },
        "smerc_posture_counts": {posture: posture_counts.get(posture, 0) for posture in POSTURES},
        "decision_difference_count": len(differences),
        "decision_difference_rate": round(len(differences) / total, 3),
        "constrained_rather_than_blocked_count": len(constrained_not_blocked),
        "constrained_rather_than_blocked_rate_of_differences": (
            None if not differences else round(len(constrained_not_blocked) / len(differences), 3)
        ),
        "average_irreversible_exposure_score": round(
            sum(record["irreversible_exposure_score"] for record in records) / total, 3
        ),
        "average_reversible_capacity_score": round(
            sum(record["reversible_capacity_score"] for record in records) / total, 3
        ),
        "highest_irreversible_exposure_categories": highest_exposure,
    }


def markdown_report(records: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    lines = [
        "# SMERC Proxy Incident Replay Benchmark",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        (
            f"SMERC evaluated `{summary['total_scenarios']}` proxy incident-replay scenarios across software "
            "deployment, cloud administration, security operations, finance operations, customer support, and IT operations."
        ),
        "",
        (
            f"The benchmark found a decision difference rate of `{summary['decision_difference_rate']}` against a "
            "simple traditional allow/deny policy baseline. This is proxy evidence only; it is useful for review and "
            "hypothesis testing, not proof of production incident reduction."
        ),
        "",
        "## Key Metrics",
        "",
        f"- Decision difference count: `{summary['decision_difference_count']}`",
        f"- Decision difference rate: `{summary['decision_difference_rate']}`",
        f"- Constrained rather than blocked count: `{summary['constrained_rather_than_blocked_count']}`",
        (
            "- Constrained rather than blocked rate among differences: "
            f"`{summary['constrained_rather_than_blocked_rate_of_differences']}`"
        ),
        f"- Average irreversible exposure score: `{summary['average_irreversible_exposure_score']}`",
        f"- Average reversible capacity score: `{summary['average_reversible_capacity_score']}`",
        "",
        "## Why This Matters",
        "",
        "Traditional authorization usually asks whether the actor or workflow is allowed to perform an action. SMERC asks an additional runtime question: if the action is wrong, how recoverable is it?",
        "",
        "That distinction matters when actions are technically authorized but operationally hard to undo, such as deleting data, broadening firewall access, transferring funds, deprovisioning accounts, or sending large customer communications.",
        "",
        "## Highest Irreversible Exposure Categories",
        "",
        "| Rank | Category | Average Irreversible Exposure | Scenarios |",
        "| ---: | --- | ---: | ---: |",
    ]
    for index, item in enumerate(summary["highest_irreversible_exposure_categories"], start=1):
        lines.append(
            f"| {index} | {escape_table(item['category'])} | {item['average_irreversible_exposure']} | {item['scenario_count']} |"
        )
    lines.extend(
        [
            "",
            "## Scenario Replay Table",
            "",
            "| Scenario | Action | Category | Traditional Policy | SMERC Posture | Exposure | Capacity | Analysis |",
            "| --- | --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_table(record["scenario_id"]),
                    escape_table(record["action"]["action_id"]),
                    escape_table(record["category"]),
                    f"`{record['traditional_policy_outcome']}`",
                    f"`{record['smerc_posture']}`",
                    str(record["irreversible_exposure_score"]),
                    str(record["reversible_capacity_score"]),
                    escape_table(record["recoverability_analysis"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Demo-Ready Examples",
            "",
        ]
    )
    for record in sorted(records, key=lambda item: item["irreversible_exposure_score"], reverse=True)[:5]:
        lines.extend(
            [
                f"### {record['scenario_id']}",
                "",
                f"- Incident pattern: {record['incident_pattern']}",
                f"- Traditional policy outcome: `{record['traditional_policy_outcome']}`",
                f"- SMERC posture: `{record['smerc_posture']}`",
                f"- Irreversible exposure: `{record['irreversible_exposure_score']}`",
                f"- Reversible capacity: `{record['reversible_capacity_score']}`",
                f"- Reason codes: `{', '.join(record['reason_codes'])}`",
                f"- Explanation: {record['recoverability_analysis']}",
                "",
            ]
        )
    lines.extend(
        [
            "## What This Evidence Supports",
            "",
            "- SMERC can produce materially different runtime postures than a simple allow/deny baseline.",
            "- Recoverability scoring creates a practical language for actions that are authorized but difficult to undo.",
            "- `THROTTLE`, `FREEZE`, and `ESCALATE` create middle states that may preserve recovery options without treating every risky action as a permanent denial.",
            "",
            "## What This Evidence Does Not Prove",
            "",
            "- It does not prove customer demand or willingness to pay.",
            "- It does not prove production incident reduction.",
            "- It does not prove calibrated thresholds for a specific enterprise.",
            "- It does not replace live design-partner review, reviewer agreement measurement, or production security validation.",
        ]
    )
    return "\n".join(lines) + "\n"


def escape_table(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_outputs(records: List[Dict[str, Any]], summary: Dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps({"summary": summary, "records": records}, indent=2), encoding="utf-8")
    markdown_path.write_text(markdown_report(records, summary), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the SMERC proxy incident replay benchmark.")
    parser.add_argument("path", help="Path to proxy incident replay scenarios.")
    parser.add_argument("--json-output", default="reports/proxy_incident_replay_benchmark.json")
    parser.add_argument("--markdown-output", default="reports/Proxy_Incident_Replay_Benchmark.md")
    args = parser.parse_args()

    records = evaluate_scenarios(load_scenarios(Path(args.path)))
    summary = summarize(records)
    write_outputs(records, summary, Path(args.json_output), Path(args.markdown_output))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


VERSION = "smerc.change-management-governance-benchmark.v1"
RESTRAINT_STATES = {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}
TRADITIONAL_APPROVAL_STATES = {"APPROVE", "APPROVE_WITH_CAB", "EMERGENCY_APPROVE"}


def load_scenarios(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("change-management benchmark scenarios must be a non-empty JSON array")
    seen: set[str] = set()
    scenarios: list[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"scenario {index} must be an object")
        required = {
            "scenario_id",
            "category",
            "traditional_change_outcome",
            "traditional_change_rationale",
            "action",
        }
        missing = sorted(required - set(item))
        unknown = sorted(set(item) - required)
        if missing:
            raise ValueError(f"scenario {index} missing field(s): {', '.join(missing)}")
        if unknown:
            raise ValueError(f"scenario {index} contains unknown field(s): {', '.join(unknown)}")
        scenario_id = _text(item["scenario_id"], f"scenario {index} scenario_id")
        if scenario_id in seen:
            raise ValueError(f"duplicate scenario_id: {scenario_id}")
        seen.add(scenario_id)
        outcome = item["traditional_change_outcome"]
        if outcome not in {"APPROVE", "APPROVE_WITH_CAB", "EMERGENCY_APPROVE", "REJECT"}:
            raise ValueError(
                "traditional_change_outcome must be APPROVE, APPROVE_WITH_CAB, EMERGENCY_APPROVE, or REJECT"
            )
        if not isinstance(item["action"], dict):
            raise TypeError("scenario action must be an object")
        scenarios.append(dict(item))
    return scenarios


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def classify_delta(traditional_outcome: str, smerc_posture: str) -> str:
    if traditional_outcome in TRADITIONAL_APPROVAL_STATES and smerc_posture in RESTRAINT_STATES:
        return "CHANGE_APPROVED_SMERC_RESTRAINT"
    if traditional_outcome == "REJECT" and smerc_posture in {"ALLOW", "THROTTLE", "ESCALATE"}:
        return "CHANGE_REJECTED_SMERC_NON_DENY"
    if traditional_outcome in TRADITIONAL_APPROVAL_STATES and smerc_posture == "ALLOW":
        return "BOTH_APPROVE"
    return "BOTH_RESTRAIN"


def build_benchmark(scenarios: list[Mapping[str, Any]]) -> Dict[str, Any]:
    engine = RecoverabilityEngine(domain_profile="github_actions")
    records: list[Dict[str, Any]] = []
    traditional_counts: Counter[str] = Counter()
    smerc_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()
    for scenario in scenarios:
        decision = engine.evaluate(dict(scenario["action"]))
        posture = decision["posture"]
        scores = decision["scores"]
        traditional = str(scenario["traditional_change_outcome"])
        delta = classify_delta(traditional, posture)
        traditional_counts[traditional] += 1
        smerc_counts[posture] += 1
        delta_counts[delta] += 1
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "traditional_change_outcome": traditional,
                "traditional_change_rationale": scenario["traditional_change_rationale"],
                "smerc_posture": posture,
                "enforcement_state": decision["enforcement_state"],
                "irreversible_exposure_score": scores["irreversible_exposure_score"],
                "reversible_capacity_score": scores["reversible_capacity_score"],
                "risk_adjusted_authorization_score": scores["risk_adjusted_authorization_score"],
                "confidence_score": scores["confidence_score"],
                "reason_codes": decision["reason_codes"],
                "controls": decision["controls"],
                "plain_english_summary": decision["plain_english_summary"],
                "delta_type": delta,
                "interpretation": interpretation(delta),
                "replay_id": decision["replay_id"],
            }
        )
    total = len(records)
    recoverability_delta_count = (
        delta_counts["CHANGE_APPROVED_SMERC_RESTRAINT"] + delta_counts["CHANGE_REJECTED_SMERC_NON_DENY"]
    )
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scenario_count": total,
        "traditional_change_counts": {
            state: traditional_counts.get(state, 0)
            for state in ("APPROVE", "APPROVE_WITH_CAB", "EMERGENCY_APPROVE", "REJECT")
        },
        "smerc_posture_counts": {
            state: smerc_counts.get(state, 0)
            for state in ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")
        },
        "delta_counts": dict(sorted(delta_counts.items())),
        "recoverability_delta_count": recoverability_delta_count,
        "recoverability_delta_rate": round(recoverability_delta_count / total, 3),
        "evidence_boundary": (
            "Change-management-inspired benchmark only. It is not ITIL certification, change-management software, "
            "ServiceNow/Jira replacement, CAB replacement, production approval, compliance attestation, "
            "customer validation, production certification, or incident-reduction proof."
        ),
        "records": records,
    }


def interpretation(delta: str) -> str:
    if delta == "CHANGE_APPROVED_SMERC_RESTRAINT":
        return (
            "Traditional change review approves or emergency-approves the change, but SMERC restrains runtime "
            "execution because current recoverability, containment, rollback, evidence, or scope is weak."
        )
    if delta == "CHANGE_REJECTED_SMERC_NON_DENY":
        return (
            "Traditional change review rejects the change, while SMERC identifies a bounded runtime path such as "
            "constraint, escalation, or narrow release under the reference engine."
        )
    if delta == "BOTH_APPROVE":
        return "Both traditional change review and SMERC allow the action under the reference scenario."
    return "Both lenses require restraint, but SMERC preserves the runtime reason codes and controls."


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Change-Management-Inspired Governance Benchmark",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Purpose",
        "",
        "This benchmark compares traditional change-management outcomes with SMERC recoverability-aware runtime postures for software delivery, infrastructure, and operations changes.",
        "",
        "It does not test whether SMERC replaces change management. It tests whether recoverability scoring produces different runtime governance postures after a change has a familiar approval, CAB, emergency, or rejection label.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Scenarios: `{report['scenario_count']}`",
        f"- Traditional change counts: `{report['traditional_change_counts']}`",
        f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
        f"- Recoverability delta count: `{report['recoverability_delta_count']}`",
        f"- Recoverability delta rate: `{report['recoverability_delta_rate']}`",
        "",
        "## Delta Types",
        "",
        "| Delta | Count | Meaning |",
        "| --- | ---: | --- |",
    ]
    for delta, count in report["delta_counts"].items():
        lines.append(f"| `{delta}` | {count} | {interpretation(delta)} |")
    lines.extend(
        [
            "",
            "## Scenario Results",
            "",
            "| Scenario | Traditional Change | SMERC | Exposure | Capacity | Auth Score | Delta |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| `{record['scenario_id']}` | `{record['traditional_change_outcome']}` | `{record['smerc_posture']}` | "
            f"{record['irreversible_exposure_score']} | {record['reversible_capacity_score']} | "
            f"{record['risk_adjusted_authorization_score']} | `{record['delta_type']}` |"
        )
    lines.extend(["", "## Demo-Ready Examples", ""])
    sorted_records = sorted(
        report["records"],
        key=lambda item: (item["delta_type"] != "CHANGE_APPROVED_SMERC_RESTRAINT", -item["irreversible_exposure_score"]),
    )
    for record in sorted_records[:5]:
        lines.extend(
            [
                f"### {record['scenario_id']}",
                "",
                f"- Category: `{record['category']}`",
                f"- Traditional outcome: `{record['traditional_change_outcome']}` because {record['traditional_change_rationale']}",
                f"- SMERC posture: `{record['smerc_posture']}`",
                f"- Irreversible exposure score: `{record['irreversible_exposure_score']}`",
                f"- Reversible capacity score: `{record['reversible_capacity_score']}`",
                f"- Reason codes: `{record['reason_codes']}`",
                f"- Controls: `{record['controls']}`",
                f"- Interpretation: {record['interpretation']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Commercial Interpretation",
            "",
            "Change management is the familiar enterprise pattern for planning, approving, scheduling, reviewing, and documenting production changes. SMERC does not replace that discipline. It adds a pre-execution runtime question that change tickets often do not answer with enough precision: if this automated action is wrong, how fast and how completely can the organization recover?",
            "",
            "For the GitHub Actions pilot, this gives a CISO or platform team a concrete way to inspect where an approved change still deserves constraints, where a rejected change may have a safe bounded path, and where evidence should be preserved for later replay.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SMERC change-management-inspired governance benchmark.")
    parser.add_argument("path", help="Path to change-management governance scenario JSON.")
    parser.add_argument("--json-output", default="reports/change_management_governance_benchmark.json")
    parser.add_argument("--markdown-output", default="reports/Change_Management_Governance_Benchmark.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_benchmark(load_scenarios(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

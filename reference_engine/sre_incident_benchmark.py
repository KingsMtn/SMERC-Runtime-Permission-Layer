from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


VERSION = "smerc.sre-incident-governance-benchmark.v1"
RESTRAINT_STATES = {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}
SRE_ACTION_STATES = {"AUTO_MITIGATE", "MANUAL_APPROVAL", "INCIDENT_COMMAND", "HOLD"}


def load_scenarios(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("SRE incident benchmark scenarios must be a non-empty JSON array")
    seen: set[str] = set()
    scenarios: list[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"scenario {index} must be an object")
        required = {"scenario_id", "category", "sre_playbook_outcome", "sre_playbook_rationale", "action"}
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
        outcome = item["sre_playbook_outcome"]
        if outcome not in SRE_ACTION_STATES:
            raise ValueError("sre_playbook_outcome must be AUTO_MITIGATE, MANUAL_APPROVAL, INCIDENT_COMMAND, or HOLD")
        if not isinstance(item["action"], dict):
            raise TypeError("scenario action must be an object")
        scenarios.append(dict(item))
    return scenarios


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def classify_delta(sre_outcome: str, smerc_posture: str) -> str:
    if sre_outcome == "AUTO_MITIGATE" and smerc_posture in RESTRAINT_STATES:
        return "SRE_AUTO_SMERC_RESTRAINT"
    if sre_outcome in {"MANUAL_APPROVAL", "INCIDENT_COMMAND"} and smerc_posture == "ALLOW":
        return "SRE_REVIEW_SMERC_ALLOW"
    if sre_outcome == "HOLD" and smerc_posture in {"ALLOW", "THROTTLE", "ESCALATE"}:
        return "SRE_HOLD_SMERC_BOUNDED_PATH"
    if sre_outcome == "AUTO_MITIGATE" and smerc_posture == "ALLOW":
        return "BOTH_AUTO_ALLOW"
    return "BOTH_RESTRAIN"


def build_benchmark(scenarios: list[Mapping[str, Any]]) -> Dict[str, Any]:
    engine = RecoverabilityEngine(domain_profile="cloud_admin")
    records: list[Dict[str, Any]] = []
    sre_counts: Counter[str] = Counter()
    smerc_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()
    for scenario in scenarios:
        decision = engine.evaluate(dict(scenario["action"]))
        posture = decision["posture"]
        scores = decision["scores"]
        sre_outcome = str(scenario["sre_playbook_outcome"])
        delta = classify_delta(sre_outcome, posture)
        sre_counts[sre_outcome] += 1
        smerc_counts[posture] += 1
        delta_counts[delta] += 1
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "sre_playbook_outcome": sre_outcome,
                "sre_playbook_rationale": scenario["sre_playbook_rationale"],
                "smerc_posture": posture,
                "enforcement_state": decision["enforcement_state"],
                "irreversible_exposure_score": scores["irreversible_exposure_score"],
                "reversible_capacity_score": scores["reversible_capacity_score"],
                "risk_adjusted_authorization_score": scores["risk_adjusted_authorization_score"],
                "confidence_score": scores["confidence_score"],
                "operational_stress_score": scores["operational_stress_score"],
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
        delta_counts["SRE_AUTO_SMERC_RESTRAINT"]
        + delta_counts["SRE_REVIEW_SMERC_ALLOW"]
        + delta_counts["SRE_HOLD_SMERC_BOUNDED_PATH"]
    )
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scenario_count": total,
        "sre_playbook_counts": {
            state: sre_counts.get(state, 0) for state in ("AUTO_MITIGATE", "MANUAL_APPROVAL", "INCIDENT_COMMAND", "HOLD")
        },
        "smerc_posture_counts": {
            state: smerc_counts.get(state, 0)
            for state in ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")
        },
        "delta_counts": dict(sorted(delta_counts.items())),
        "recoverability_delta_count": recoverability_delta_count,
        "recoverability_delta_rate": round(recoverability_delta_count / total, 3),
        "evidence_boundary": (
            "SRE/incident-management-inspired benchmark only. It is not an observability platform, incident-management "
            "system, SLO calculator, pager routing service, production approval, customer validation, production "
            "certification, or incident-reduction proof."
        ),
        "records": records,
    }


def interpretation(delta: str) -> str:
    if delta == "SRE_AUTO_SMERC_RESTRAINT":
        return (
            "The SRE playbook would auto-mitigate, but SMERC restrains the action because rollback, containment, "
            "evidence, impact scope, or recovery capacity is not strong enough."
        )
    if delta == "SRE_REVIEW_SMERC_ALLOW":
        return (
            "The SRE playbook routes the action to approval or incident command, while SMERC sees the specific action "
            "as narrow and recoverable enough under the reference scenario."
        )
    if delta == "SRE_HOLD_SMERC_BOUNDED_PATH":
        return (
            "The SRE playbook holds execution, while SMERC identifies a bounded path such as constrained mitigation "
            "or escalation with replay evidence."
        )
    if delta == "BOTH_AUTO_ALLOW":
        return "Both the SRE playbook and SMERC allow automated execution under the reference scenario."
    return "Both lenses require restraint, but SMERC records recoverability scores, reason codes, and controls."


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC SRE Incident Governance Benchmark",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Purpose",
        "",
        "This benchmark compares SRE incident playbook outcomes with SMERC recoverability-aware runtime postures for reliability automation.",
        "",
        "It does not test whether SMERC replaces observability, incident management, SLOs, or pager workflows. It tests whether recoverability scoring changes how automated mitigations should proceed before they scale systems, roll back services, disable features, purge caches, alter traffic, or trigger failover.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Scenarios: `{report['scenario_count']}`",
        f"- SRE playbook counts: `{report['sre_playbook_counts']}`",
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
            "| Scenario | SRE Playbook | SMERC | Exposure | Capacity | Stress | Delta |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| `{record['scenario_id']}` | `{record['sre_playbook_outcome']}` | `{record['smerc_posture']}` | "
            f"{record['irreversible_exposure_score']} | {record['reversible_capacity_score']} | "
            f"{record['operational_stress_score']} | `{record['delta_type']}` |"
        )
    lines.extend(["", "## Demo-Ready Examples", ""])
    sorted_records = sorted(
        report["records"],
        key=lambda item: (item["delta_type"] != "SRE_AUTO_SMERC_RESTRAINT", -item["irreversible_exposure_score"]),
    )
    for record in sorted_records[:5]:
        lines.extend(
            [
                f"### {record['scenario_id']}",
                "",
                f"- Category: `{record['category']}`",
                f"- SRE playbook outcome: `{record['sre_playbook_outcome']}` because {record['sre_playbook_rationale']}",
                f"- SMERC posture: `{record['smerc_posture']}`",
                f"- Irreversible exposure score: `{record['irreversible_exposure_score']}`",
                f"- Reversible capacity score: `{record['reversible_capacity_score']}`",
                f"- Operational stress score: `{record['operational_stress_score']}`",
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
            "SRE and incident-management systems are strongest at detection, alerting, ownership, mitigation playbooks, SLOs, incident command, and post-incident review. SMERC does not replace those systems. It adds an execution-time recoverability checkpoint before an automated mitigation changes production state.",
            "",
            "For platform teams, this is useful when automation is asked to act during stress. The question is not only whether mitigation is urgent. The question is whether the mitigation itself is recoverable, bounded, and supported by enough evidence.",
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
    parser = argparse.ArgumentParser(description="Run the SMERC SRE incident-management-inspired governance benchmark.")
    parser.add_argument("path", help="Path to SRE incident governance scenario JSON.")
    parser.add_argument("--json-output", default="reports/sre_incident_governance_benchmark.json")
    parser.add_argument("--markdown-output", default="reports/SRE_Incident_Governance_Benchmark.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_benchmark(load_scenarios(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

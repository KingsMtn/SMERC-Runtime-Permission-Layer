from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.financial_permission_profile import FinancialPermissionProfile


VERSION = "smerc.aml-inspired-financial-governance-benchmark.v1"
RESTRAINT_STATES = {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}


def load_scenarios(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("AML-inspired benchmark scenarios must be a non-empty JSON array")
    seen: set[str] = set()
    scenarios: list[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"scenario {index} must be an object")
        required = {"scenario_id", "category", "aml_baseline_outcome", "aml_baseline_rationale", "action"}
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
        if item["aml_baseline_outcome"] not in {"CLEAR", "ALERT"}:
            raise ValueError("aml_baseline_outcome must be CLEAR or ALERT")
        if not isinstance(item["action"], dict):
            raise TypeError("scenario action must be an object")
        scenarios.append(dict(item))
    return scenarios


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def classify_delta(aml_outcome: str, smerc_state: str) -> str:
    if aml_outcome == "CLEAR" and smerc_state in RESTRAINT_STATES:
        return "AML_CLEAR_SMERC_RESTRAINT"
    if aml_outcome == "ALERT" and smerc_state == "ALLOW":
        return "AML_ALERT_SMERC_ALLOW"
    if aml_outcome == "ALERT" and smerc_state in RESTRAINT_STATES:
        return "AML_ALERT_SMERC_RESTRAINT"
    return "AML_CLEAR_SMERC_ALLOW"


def build_benchmark(scenarios: list[Mapping[str, Any]], *, policy: str = "balanced") -> Dict[str, Any]:
    engine = FinancialPermissionProfile(policy)
    records: list[Dict[str, Any]] = []
    aml_counts: Counter[str] = Counter()
    smerc_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()
    for scenario in scenarios:
        decision = engine.evaluate(dict(scenario["action"]))
        delta = classify_delta(str(scenario["aml_baseline_outcome"]), decision["state"])
        aml_counts[str(scenario["aml_baseline_outcome"])] += 1
        smerc_counts[decision["state"]] += 1
        delta_counts[delta] += 1
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "aml_baseline_outcome": scenario["aml_baseline_outcome"],
                "aml_baseline_rationale": scenario["aml_baseline_rationale"],
                "smerc_f_state": decision["state"],
                "smerc_f_confidence": decision["confidence"],
                "irreversible_exposure": decision["irreversible_exposure"],
                "reversible_capacity": decision["reversible_capacity"],
                "drivers": decision["drivers"],
                "controls": decision["controls"],
                "delta_type": delta,
                "interpretation": interpretation(delta),
                "decision_hash": decision["decision_hash"],
            }
        )
    total = len(records)
    recoverability_deltas = delta_counts["AML_CLEAR_SMERC_RESTRAINT"] + delta_counts["AML_ALERT_SMERC_ALLOW"]
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "policy": policy,
        "scenario_count": total,
        "aml_baseline_counts": {"CLEAR": aml_counts.get("CLEAR", 0), "ALERT": aml_counts.get("ALERT", 0)},
        "smerc_f_state_counts": {state: smerc_counts.get(state, 0) for state in ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")},
        "delta_counts": dict(sorted(delta_counts.items())),
        "recoverability_delta_count": recoverability_deltas,
        "recoverability_delta_rate": round(recoverability_deltas / total, 3),
        "evidence_boundary": (
            "AML-inspired benchmark only. It is not AML software, sanctions screening, suspicious-activity reporting, "
            "regulatory compliance, customer validation, production certification, or incident-reduction proof."
        ),
        "records": records,
    }


def interpretation(delta: str) -> str:
    if delta == "AML_CLEAR_SMERC_RESTRAINT":
        return "AML-style suspiciousness is clear, but SMERC-F restrains the action because recoverability or financial-operational exposure is weak."
    if delta == "AML_ALERT_SMERC_ALLOW":
        return "AML-style suspiciousness alerts, but SMERC-F sees the specific proposed action as recoverable enough to release under the reference profile."
    if delta == "AML_ALERT_SMERC_RESTRAINT":
        return "Both lenses indicate review or restraint, but for different reasons: suspiciousness versus recoverability and execution risk."
    return "Both lenses allow the action under the reference scenario."


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC-F AML-Inspired Financial Governance Benchmark",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Policy: `{report['policy']}`",
        "",
        "## Purpose",
        "",
        "This benchmark compares an AML-style `CLEAR` / `ALERT` lens with SMERC-F recoverability-aware financial action governance.",
        "",
        "It does not test whether SMERC-F can detect money laundering. It tests whether recoverability scoring produces different governance postures for financial actions that may be authorized, suspicious, reversible, irreversible, constrained, or review-worthy.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Scenarios: `{report['scenario_count']}`",
        f"- AML baseline counts: `{report['aml_baseline_counts']}`",
        f"- SMERC-F state counts: `{report['smerc_f_state_counts']}`",
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
            "| Scenario | AML | SMERC-F | Exposure | Capacity | Delta |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| `{record['scenario_id']}` | `{record['aml_baseline_outcome']}` | `{record['smerc_f_state']}` | "
            f"{record['irreversible_exposure']} | {record['reversible_capacity']} | `{record['delta_type']}` |"
        )
    lines.extend(["", "## Demo-Ready Examples", ""])
    for record in sorted(report["records"], key=lambda item: item["irreversible_exposure"], reverse=True)[:5]:
        lines.extend(
            [
                f"### {record['scenario_id']}",
                "",
                f"- Category: `{record['category']}`",
                f"- AML baseline: `{record['aml_baseline_outcome']}` because {record['aml_baseline_rationale']}",
                f"- SMERC-F state: `{record['smerc_f_state']}`",
                f"- Irreversible exposure: `{record['irreversible_exposure']}`",
                f"- Reversible capacity: `{record['reversible_capacity']}`",
                f"- Drivers: `{record['drivers']}`",
                f"- Controls: `{record['controls']}`",
                f"- Interpretation: {record['interpretation']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Commercial Interpretation",
            "",
            "AML is the familiar enterprise pattern: risk scoring, alert queues, analyst review, evidence, and auditability. SMERC-F borrows that operating pattern but applies it to pre-execution financial actions. The core question is not whether an action is suspicious; it is whether automated execution is recoverable, reviewable, and structurally defensible now.",
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
    parser = argparse.ArgumentParser(description="Run the SMERC-F AML-inspired financial governance benchmark.")
    parser.add_argument("path", help="Path to AML-inspired financial governance scenario JSON.")
    parser.add_argument("--policy", default="balanced")
    parser.add_argument("--json-output", default="reports/aml_inspired_financial_governance_benchmark.json")
    parser.add_argument("--markdown-output", default="reports/AML_Inspired_Financial_Governance_Benchmark.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_benchmark(load_scenarios(args.path), policy=args.policy)
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

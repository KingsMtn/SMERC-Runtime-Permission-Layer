from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


VERSION = "smerc.model-risk-governance-benchmark.v1"
RESTRAINT_STATES = {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}
MODEL_APPROVAL_STATES = {"APPROVE_FOR_USE", "APPROVE_WITH_MONITORING"}
MODEL_RESTRAINT_STATES = {"REQUIRE_VALIDATION", "PROHIBIT_USE"}


def load_scenarios(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("model-risk benchmark scenarios must be a non-empty JSON array")
    seen: set[str] = set()
    scenarios: list[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"scenario {index} must be an object")
        required = {
            "scenario_id",
            "category",
            "model_governance_outcome",
            "model_governance_rationale",
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
        outcome = item["model_governance_outcome"]
        if outcome not in {"APPROVE_FOR_USE", "APPROVE_WITH_MONITORING", "REQUIRE_VALIDATION", "PROHIBIT_USE"}:
            raise ValueError(
                "model_governance_outcome must be APPROVE_FOR_USE, APPROVE_WITH_MONITORING, REQUIRE_VALIDATION, or PROHIBIT_USE"
            )
        if not isinstance(item["action"], dict):
            raise TypeError("scenario action must be an object")
        scenarios.append(dict(item))
    return scenarios


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def classify_delta(model_outcome: str, smerc_posture: str) -> str:
    if model_outcome in MODEL_APPROVAL_STATES and smerc_posture in RESTRAINT_STATES:
        return "MODEL_APPROVED_SMERC_RESTRAINT"
    if model_outcome == "REQUIRE_VALIDATION" and smerc_posture == "ALLOW":
        return "MODEL_VALIDATION_SMERC_ALLOW"
    if model_outcome == "PROHIBIT_USE" and smerc_posture in {"ALLOW", "THROTTLE", "ESCALATE"}:
        return "MODEL_PROHIBITED_SMERC_BOUNDED_PATH"
    if model_outcome in MODEL_APPROVAL_STATES and smerc_posture == "ALLOW":
        return "BOTH_ALLOW"
    return "BOTH_RESTRAIN"


def build_benchmark(scenarios: list[Mapping[str, Any]]) -> Dict[str, Any]:
    engine = RecoverabilityEngine()
    records: list[Dict[str, Any]] = []
    model_counts: Counter[str] = Counter()
    smerc_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()
    for scenario in scenarios:
        decision = engine.evaluate(dict(scenario["action"]))
        posture = decision["posture"]
        scores = decision["scores"]
        model_outcome = str(scenario["model_governance_outcome"])
        delta = classify_delta(model_outcome, posture)
        model_counts[model_outcome] += 1
        smerc_counts[posture] += 1
        delta_counts[delta] += 1
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "model_governance_outcome": model_outcome,
                "model_governance_rationale": scenario["model_governance_rationale"],
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
    runtime_delta_count = (
        delta_counts["MODEL_APPROVED_SMERC_RESTRAINT"]
        + delta_counts["MODEL_VALIDATION_SMERC_ALLOW"]
        + delta_counts["MODEL_PROHIBITED_SMERC_BOUNDED_PATH"]
    )
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scenario_count": total,
        "model_governance_counts": {
            state: model_counts.get(state, 0)
            for state in ("APPROVE_FOR_USE", "APPROVE_WITH_MONITORING", "REQUIRE_VALIDATION", "PROHIBIT_USE")
        },
        "smerc_posture_counts": {
            state: smerc_counts.get(state, 0)
            for state in ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")
        },
        "delta_counts": dict(sorted(delta_counts.items())),
        "runtime_delta_count": runtime_delta_count,
        "runtime_delta_rate": round(runtime_delta_count / total, 3),
        "evidence_boundary": (
            "Model-risk-inspired benchmark only. It is not regulatory model-risk management, SR 11-7 compliance, "
            "model validation, model monitoring, bias testing, model approval, customer validation, production "
            "certification, or incident-reduction proof."
        ),
        "records": records,
    }


def interpretation(delta: str) -> str:
    if delta == "MODEL_APPROVED_SMERC_RESTRAINT":
        return (
            "The model is approved or monitored for use, but SMERC restrains this specific runtime action because "
            "recoverability, evidence, containment, rollback, confidence, or impact scope is not strong enough."
        )
    if delta == "MODEL_VALIDATION_SMERC_ALLOW":
        return (
            "Model governance requires more validation, while SMERC sees the proposed action as narrow and "
            "recoverable enough under the reference runtime scenario."
        )
    if delta == "MODEL_PROHIBITED_SMERC_BOUNDED_PATH":
        return (
            "Model governance prohibits model use, while SMERC identifies only a bounded runtime path; this remains "
            "a policy conflict that should be human-reviewed before any live deployment."
        )
    if delta == "BOTH_ALLOW":
        return "Both model governance and SMERC allow the action under the reference scenario."
    return "Both lenses require restraint, but SMERC preserves runtime recoverability evidence and controls."


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Model-Risk-Inspired Governance Benchmark",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Purpose",
        "",
        "This benchmark compares model-governance outcomes with SMERC recoverability-aware runtime postures for AI-agent and automated decision actions.",
        "",
        "It does not test whether SMERC validates models or replaces model-risk management. It tests whether model approval status and runtime action permission can diverge when the specific proposed action is high-impact, hard to reverse, weakly evidenced, or poorly contained.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Scenarios: `{report['scenario_count']}`",
        f"- Model governance counts: `{report['model_governance_counts']}`",
        f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
        f"- Runtime delta count: `{report['runtime_delta_count']}`",
        f"- Runtime delta rate: `{report['runtime_delta_rate']}`",
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
            "| Scenario | Model Governance | SMERC | Exposure | Capacity | Confidence | Delta |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| `{record['scenario_id']}` | `{record['model_governance_outcome']}` | `{record['smerc_posture']}` | "
            f"{record['irreversible_exposure_score']} | {record['reversible_capacity_score']} | "
            f"{record['confidence_score']} | `{record['delta_type']}` |"
        )
    lines.extend(["", "## Demo-Ready Examples", ""])
    sorted_records = sorted(
        report["records"],
        key=lambda item: (item["delta_type"] != "MODEL_APPROVED_SMERC_RESTRAINT", -item["irreversible_exposure_score"]),
    )
    for record in sorted_records[:5]:
        lines.extend(
            [
                f"### {record['scenario_id']}",
                "",
                f"- Category: `{record['category']}`",
                f"- Model governance outcome: `{record['model_governance_outcome']}` because {record['model_governance_rationale']}",
                f"- SMERC posture: `{record['smerc_posture']}`",
                f"- Irreversible exposure score: `{record['irreversible_exposure_score']}`",
                f"- Reversible capacity score: `{record['reversible_capacity_score']}`",
                f"- Confidence score: `{record['confidence_score']}`",
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
            "Model-risk management is strongest at inventory, validation, intended-use approval, monitoring, and governance oversight. SMERC does not replace those functions. It adds an execution-time permission layer for the specific action a model or agent is about to take.",
            "",
            "For AI governance leaders, this distinction is important: an approved model can still propose an action that is not recoverable enough to execute, and an unapproved model should not be treated as safe merely because an individual action looks low risk. SMERC preserves that decision boundary as replayable evidence.",
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
    parser = argparse.ArgumentParser(description="Run the SMERC model-risk-inspired governance benchmark.")
    parser.add_argument("path", help="Path to model-risk governance scenario JSON.")
    parser.add_argument("--json-output", default="reports/model_risk_governance_benchmark.json")
    parser.add_argument("--markdown-output", default="reports/Model_Risk_Governance_Benchmark.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_benchmark(load_scenarios(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


VERSION = "smerc.gitlab-agent-action-recoverability-benchmark.v1"
GITLAB_STATES = ("ALLOW", "ASK", "DENY")
SMERC_STATES = ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")
SMERC_RESTRAINT_STATES = {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}


def load_scenarios(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("GitLab agent-action benchmark scenarios must be a non-empty JSON array")
    seen: set[str] = set()
    scenarios: list[Dict[str, Any]] = []
    required = {
        "scenario_id",
        "category",
        "gitlab_tool_governance_outcome",
        "gitlab_rationale",
        "action",
    }
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"scenario {index} must be an object")
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
        outcome = _text(item["gitlab_tool_governance_outcome"], f"scenario {index} gitlab_tool_governance_outcome")
        if outcome not in GITLAB_STATES:
            raise ValueError("gitlab_tool_governance_outcome must be ALLOW, ASK, or DENY")
        if not isinstance(item["action"], dict):
            raise TypeError("scenario action must be an object")
        scenarios.append(dict(item))
    return scenarios


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def classify_delta(gitlab_outcome: str, smerc_posture: str) -> str:
    if gitlab_outcome == "ALLOW" and smerc_posture in SMERC_RESTRAINT_STATES:
        return "GITLAB_ALLOW_SMERC_RESTRAINT"
    if gitlab_outcome == "ASK" and smerc_posture == "ALLOW":
        return "GITLAB_ASK_SMERC_ALLOW"
    if gitlab_outcome == "ASK" and smerc_posture in {"THROTTLE", "FREEZE", "ESCALATE"}:
        return "GITLAB_ASK_SMERC_STRUCTURED_ROUTE"
    if gitlab_outcome == "DENY" and smerc_posture != "DENY":
        return "GITLAB_DENY_SMERC_NON_DENY"
    if gitlab_outcome == "ALLOW" and smerc_posture == "ALLOW":
        return "BOTH_ALLOW"
    if gitlab_outcome == "DENY" and smerc_posture == "DENY":
        return "BOTH_DENY"
    return "BOTH_RESTRAIN"


def interpretation(delta: str) -> str:
    if delta == "GITLAB_ALLOW_SMERC_RESTRAINT":
        return (
            "The platform-style permission outcome allows the action, but SMERC restrains execution because current "
            "rollback, evidence, containment, anomaly, or blast-radius conditions make the action hard to recover."
        )
    if delta == "GITLAB_ASK_SMERC_STRUCTURED_ROUTE":
        return (
            "The platform-style outcome asks for confirmation, while SMERC turns the same concern into a specific "
            "runtime posture with controls, reason codes, and replay evidence."
        )
    if delta == "GITLAB_ASK_SMERC_ALLOW":
        return (
            "The platform-style outcome asks for confirmation, while SMERC finds sufficient recovery margin under "
            "the reference signals. In a real pilot, reviewer agreement would decide whether that is acceptable."
        )
    if delta == "GITLAB_DENY_SMERC_NON_DENY":
        return (
            "The platform-style outcome blocks the action, while SMERC identifies a possible constrained or reviewable "
            "path. This is a calibration prompt, not an instruction to override platform policy."
        )
    if delta == "BOTH_ALLOW":
        return "Both lenses allow the action under the reference metadata."
    if delta == "BOTH_DENY":
        return "Both lenses block the action under the reference metadata."
    return "Both lenses require restraint, but SMERC preserves more runtime-specific controls."


def build_benchmark(scenarios: list[Mapping[str, Any]]) -> Dict[str, Any]:
    engine = RecoverabilityEngine(domain_profile="github_actions")
    records: list[Dict[str, Any]] = []
    gitlab_counts: Counter[str] = Counter()
    smerc_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()
    for scenario in scenarios:
        decision = engine.evaluate(dict(scenario["action"]))
        gitlab_outcome = str(scenario["gitlab_tool_governance_outcome"])
        posture = decision["posture"]
        delta = classify_delta(gitlab_outcome, posture)
        scores = decision["scores"]
        gitlab_counts[gitlab_outcome] += 1
        smerc_counts[posture] += 1
        delta_counts[delta] += 1
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "gitlab_tool_governance_outcome": gitlab_outcome,
                "gitlab_rationale": scenario["gitlab_rationale"],
                "smerc_posture": posture,
                "enforcement_state": decision["enforcement_state"],
                "irreversible_exposure_score": scores["irreversible_exposure_score"],
                "reversible_capacity_score": scores["reversible_capacity_score"],
                "risk_adjusted_authorization_score": scores["risk_adjusted_authorization_score"],
                "confidence_score": scores["confidence_score"],
                "reason_codes": decision["reason_codes"],
                "controls": decision["controls"],
                "delta_type": delta,
                "interpretation": interpretation(delta),
                "plain_english_summary": decision["plain_english_summary"],
                "replay_id": decision["replay_id"],
                "action_context": scenario["action"].get("context", {}),
            }
        )
    total = len(records)
    difference_count = sum(
        count for delta, count in delta_counts.items() if delta not in {"BOTH_ALLOW", "BOTH_DENY", "BOTH_RESTRAIN"}
    )
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scenario_count": total,
        "gitlab_tool_governance_counts": {state: gitlab_counts.get(state, 0) for state in GITLAB_STATES},
        "smerc_posture_counts": {state: smerc_counts.get(state, 0) for state in SMERC_STATES},
        "delta_counts": dict(sorted(delta_counts.items())),
        "decision_difference_count": difference_count,
        "decision_difference_rate": round(difference_count / total, 3),
        "average_irreversible_exposure_score": round(
            sum(record["irreversible_exposure_score"] for record in records) / total, 3
        ),
        "average_reversible_capacity_score": round(
            sum(record["reversible_capacity_score"] for record in records) / total, 3
        ),
        "evidence_boundary": (
            "GitLab-shaped public-pattern benchmark only. It is not a GitLab integration, GitLab endorsement, "
            "GitLab telemetry, production deployment, customer validation, or proof of incident reduction."
        ),
        "records": records,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# GitLab Agent Action Recoverability Benchmark",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Purpose",
        "",
        "This benchmark packages SMERC for a GitLab-style reviewer. It compares a familiar agent tool-governance lens, `ALLOW` / `ASK` / `DENY`, with SMERC recoverability postures before CI/CD, merge request, MCP-style tool, identity, and deployment actions execute.",
        "",
        "The point is not to claim SMERC replaces GitLab permissions. The point is to show where recoverability, rollback latency, blast radius, evidence quality, and approval reuse can change the execution route after ordinary authorization says an action may proceed.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Scenarios: `{report['scenario_count']}`",
        f"- GitLab-style counts: `{report['gitlab_tool_governance_counts']}`",
        f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
        f"- Decision difference count: `{report['decision_difference_count']}`",
        f"- Decision difference rate: `{report['decision_difference_rate']}`",
        f"- Average irreversible exposure: `{report['average_irreversible_exposure_score']}`",
        f"- Average reversible capacity: `{report['average_reversible_capacity_score']}`",
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
            "| Scenario | Category | GitLab-Style Outcome | SMERC | Exposure | Capacity | Delta |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| `{record['scenario_id']}` | `{record['category']}` | `{record['gitlab_tool_governance_outcome']}` | "
            f"`{record['smerc_posture']}` | {record['irreversible_exposure_score']} | "
            f"{record['reversible_capacity_score']} | `{record['delta_type']}` |"
        )
    lines.extend(["", "## Demo-Ready Examples", ""])
    demo_records = sorted(
        report["records"],
        key=lambda item: (item["delta_type"] != "GITLAB_ALLOW_SMERC_RESTRAINT", -item["irreversible_exposure_score"]),
    )
    for record in demo_records[:5]:
        lines.extend(
            [
                f"### {record['scenario_id']}",
                "",
                f"- GitLab-style outcome: `{record['gitlab_tool_governance_outcome']}` because {record['gitlab_rationale']}",
                f"- SMERC posture: `{record['smerc_posture']}`",
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
            "For GitLab, CI/CD, and DevSecOps buyers, the useful SMERC claim is narrow: existing permission systems can decide whether an agent has access to a tool, while SMERC can decide whether this specific action is recoverable enough to execute now. The practical impact is that an authorized action can still be unrecoverable, so the execution route should preserve rollback, evidence, containment, or human review before side effects occur.",
            "",
            "That makes this a positive addition to the core project, not a distraction. It creates a concrete external-review lane for teams already thinking about agentic coding, MCP tool calls, merge requests, CI/CD automation, protected environments, and project tokens.",
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
    parser = argparse.ArgumentParser(description="Run the SMERC GitLab agent-action recoverability benchmark.")
    parser.add_argument("path", help="Path to GitLab-shaped scenario JSON.")
    parser.add_argument("--json-output", default="reports/gitlab_agent_action_recoverability_benchmark.json")
    parser.add_argument("--markdown-output", default="reports/GitLab_Agent_Action_Recoverability_Benchmark.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_benchmark(load_scenarios(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


VERSION = "smerc.security-response-governance-benchmark.v1"
RESTRAINT_STATES = {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}
SECURITY_ACTION_STATES = {"AUTO_EXECUTE", "ANALYST_REVIEW", "ESCALATE_INCIDENT", "DO_NOT_EXECUTE"}


def load_scenarios(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("security-response benchmark scenarios must be a non-empty JSON array")
    seen: set[str] = set()
    scenarios: list[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"scenario {index} must be an object")
        required = {
            "scenario_id",
            "category",
            "security_playbook_outcome",
            "security_playbook_rationale",
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
        outcome = item["security_playbook_outcome"]
        if outcome not in SECURITY_ACTION_STATES:
            raise ValueError(
                "security_playbook_outcome must be AUTO_EXECUTE, ANALYST_REVIEW, ESCALATE_INCIDENT, or DO_NOT_EXECUTE"
            )
        if not isinstance(item["action"], dict):
            raise TypeError("scenario action must be an object")
        scenarios.append(dict(item))
    return scenarios


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def classify_delta(playbook_outcome: str, smerc_posture: str) -> str:
    if playbook_outcome == "AUTO_EXECUTE" and smerc_posture in RESTRAINT_STATES:
        return "PLAYBOOK_AUTO_SMERC_RESTRAINT"
    if playbook_outcome in {"ANALYST_REVIEW", "ESCALATE_INCIDENT"} and smerc_posture == "ALLOW":
        return "PLAYBOOK_REVIEW_SMERC_ALLOW"
    if playbook_outcome == "DO_NOT_EXECUTE" and smerc_posture in {"ALLOW", "THROTTLE", "ESCALATE"}:
        return "PLAYBOOK_BLOCK_SMERC_BOUNDED_PATH"
    if playbook_outcome == "AUTO_EXECUTE" and smerc_posture == "ALLOW":
        return "BOTH_AUTO_ALLOW"
    return "BOTH_RESTRAIN"


def build_benchmark(scenarios: list[Mapping[str, Any]]) -> Dict[str, Any]:
    engine = RecoverabilityEngine(domain_profile="security_ops")
    records: list[Dict[str, Any]] = []
    playbook_counts: Counter[str] = Counter()
    smerc_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()
    for scenario in scenarios:
        decision = engine.evaluate(dict(scenario["action"]))
        posture = decision["posture"]
        scores = decision["scores"]
        playbook = str(scenario["security_playbook_outcome"])
        delta = classify_delta(playbook, posture)
        playbook_counts[playbook] += 1
        smerc_counts[posture] += 1
        delta_counts[delta] += 1
        records.append(
            {
                "scenario_id": scenario["scenario_id"],
                "category": scenario["category"],
                "security_playbook_outcome": playbook,
                "security_playbook_rationale": scenario["security_playbook_rationale"],
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
        delta_counts["PLAYBOOK_AUTO_SMERC_RESTRAINT"]
        + delta_counts["PLAYBOOK_REVIEW_SMERC_ALLOW"]
        + delta_counts["PLAYBOOK_BLOCK_SMERC_BOUNDED_PATH"]
    )
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scenario_count": total,
        "security_playbook_counts": {
            state: playbook_counts.get(state, 0)
            for state in ("AUTO_EXECUTE", "ANALYST_REVIEW", "ESCALATE_INCIDENT", "DO_NOT_EXECUTE")
        },
        "smerc_posture_counts": {
            state: smerc_counts.get(state, 0)
            for state in ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")
        },
        "delta_counts": dict(sorted(delta_counts.items())),
        "recoverability_delta_count": recoverability_delta_count,
        "recoverability_delta_rate": round(recoverability_delta_count / total, 3),
        "evidence_boundary": (
            "Security-response-inspired benchmark only. It is not a SOAR platform, SIEM, EDR, incident-response "
            "service, malware classifier, threat-intelligence feed, compliance attestation, customer validation, "
            "production certification, or incident-reduction proof."
        ),
        "records": records,
    }


def interpretation(delta: str) -> str:
    if delta == "PLAYBOOK_AUTO_SMERC_RESTRAINT":
        return (
            "The security playbook would auto-execute, but SMERC restrains the action because the proposed "
            "response could be hard to reverse, too broad, weakly evidenced, or poorly contained."
        )
    if delta == "PLAYBOOK_REVIEW_SMERC_ALLOW":
        return (
            "The security playbook sends the action to review or incident escalation, while SMERC sees the narrow "
            "runtime action as recoverable enough under the reference scenario."
        )
    if delta == "PLAYBOOK_BLOCK_SMERC_BOUNDED_PATH":
        return (
            "The security playbook blocks execution, while SMERC identifies a bounded path such as throttled scope "
            "or escalation with replay evidence."
        )
    if delta == "BOTH_AUTO_ALLOW":
        return "Both the security playbook and SMERC allow automated execution under the reference scenario."
    return "Both lenses require restraint, but SMERC records recoverability scores, reason codes, and controls."


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Security-Response-Inspired Governance Benchmark",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Purpose",
        "",
        "This benchmark compares security playbook outcomes with SMERC recoverability-aware runtime postures for AI-assisted security operations.",
        "",
        "It does not test whether SMERC detects threats or replaces SOAR/SIEM/EDR tools. It tests whether recoverability scoring changes how automated response actions should proceed before they isolate systems, disable accounts, delete artifacts, notify customers, or alter controls.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Scenarios: `{report['scenario_count']}`",
        f"- Security playbook counts: `{report['security_playbook_counts']}`",
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
            "| Scenario | Playbook | SMERC | Exposure | Capacity | Auth Score | Delta |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| `{record['scenario_id']}` | `{record['security_playbook_outcome']}` | `{record['smerc_posture']}` | "
            f"{record['irreversible_exposure_score']} | {record['reversible_capacity_score']} | "
            f"{record['risk_adjusted_authorization_score']} | `{record['delta_type']}` |"
        )
    lines.extend(["", "## Demo-Ready Examples", ""])
    sorted_records = sorted(
        report["records"],
        key=lambda item: (item["delta_type"] != "PLAYBOOK_AUTO_SMERC_RESTRAINT", -item["irreversible_exposure_score"]),
    )
    for record in sorted_records[:5]:
        lines.extend(
            [
                f"### {record['scenario_id']}",
                "",
                f"- Category: `{record['category']}`",
                f"- Playbook outcome: `{record['security_playbook_outcome']}` because {record['security_playbook_rationale']}",
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
            "SOAR and incident-response programs are strongest at detection intake, enrichment, playbooks, analyst queues, and response execution. SMERC does not replace those systems. It adds a pre-execution recoverability checkpoint so automated security actions can be released, constrained, frozen, denied, or escalated based on blast radius and recovery capacity.",
            "",
            "For a CISO, this is useful when security automation is moving from recommendation to action. The question is not only whether the alert is real. The question is whether the response action can be safely undone if the system is wrong.",
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
    parser = argparse.ArgumentParser(description="Run the SMERC security-response-inspired governance benchmark.")
    parser.add_argument("path", help="Path to security-response governance scenario JSON.")
    parser.add_argument("--json-output", default="reports/security_response_governance_benchmark.json")
    parser.add_argument("--markdown-output", default="reports/Security_Response_Governance_Benchmark.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_benchmark(load_scenarios(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

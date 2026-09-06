from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.customer_evaluation import build_customer_evaluation, load_payload, write_outputs as write_customer_outputs


VERSION = "smerc.balanced-runtime-judgment-replay.v1"
EXPECTED_POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}


def build_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    evaluation = build_customer_evaluation(payload)
    expected = _expected_postures(payload)
    observed = {
        record["action_id"]: str(record["decision"]["posture"])
        for record in evaluation["records"]
    }
    deltas = [_delta(action_id, expected[action_id], observed[action_id]) for action_id in expected]
    delta_counts = Counter(item["delta"] for item in deltas)
    summary = evaluation["summary"]
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_name": "Balanced Runtime Judgment Replay",
        "record_count": len(expected),
        "expected_posture_counts": dict(sorted(Counter(expected.values()).items())),
        "smerc_posture_counts": summary["posture_counts"],
        "governance_route_counts": summary["route_state_counts"],
        "valid_dll_ledgers": summary["valid_ledgers"],
        "deltas": deltas,
        "delta_counts": dict(sorted(delta_counts.items())),
        "customer_evaluation": evaluation,
        "work_result_impact": {
            "work": "Run safe, borderline, uncertain, harmful, and escalation-worthy actions through the same SMERC evaluation path.",
            "result": (
                f"Evaluated {len(expected)} metadata-only records and compared expected postures with SMERC posture output."
            ),
            "impact": (
                "Reviewers can see whether SMERC demonstrates judgment across the whole posture ladder instead of acting "
                "like a simple blocker."
            ),
        },
        "evidence_boundary": (
            "This replay proves local posture discrimination on curated metadata-only examples. It is not customer "
            "validation, production certification, a formal false-positive rate, or proof that thresholds are calibrated "
            "for a specific organization."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Balanced Runtime Judgment Replay Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Posture Distribution",
        "",
        f"- Expected posture counts: `{report['expected_posture_counts']}`",
        f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
        f"- Governance Routing Workbench route counts: `{report['governance_route_counts']}`",
        f"- Valid DLL ledgers: `{report['valid_dll_ledgers']}`",
        f"- Delta counts: `{report['delta_counts']}`",
        "",
        "## Decision Deltas",
        "",
        "| Action | Expected posture | SMERC posture | Delta |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["deltas"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['expected_posture']}` | `{item['smerc_posture']}` | `{item['delta']}` |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Question",
            "",
            "Which posture is most useful to tune first for your workflow: ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE?",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    report: Mapping[str, Any],
    *,
    json_output: str | Path,
    markdown_output: str | Path,
    customer_json_output: str | Path,
    customer_markdown_output: str | Path,
) -> None:
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")
    write_customer_outputs(report["customer_evaluation"], customer_json_output, customer_markdown_output)


def _expected_postures(payload: Mapping[str, Any]) -> Dict[str, str]:
    actions = payload.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")
    expected: Dict[str, str] = {}
    for index, action in enumerate(actions):
        if not isinstance(action, Mapping):
            raise TypeError(f"actions[{index}] must be an object")
        action_id = str(action.get("action_id", "")).strip()
        posture = str(action.get("context", {}).get("expected_posture", "")).strip().upper()
        if not action_id:
            raise ValueError(f"actions[{index}].action_id is required")
        if posture not in EXPECTED_POSTURES:
            raise ValueError(f"{action_id}.context.expected_posture must be one of {sorted(EXPECTED_POSTURES)}")
        expected[action_id] = posture
    return expected


def _delta(action_id: str, expected: str, observed: str) -> Dict[str, str]:
    if observed == expected:
        delta = "MATCH"
    elif expected == "FREEZE" and observed in {"DENY", "ESCALATE"}:
        delta = "MORE_RESTRICTIVE_THAN_EXPECTED"
    elif expected == "THROTTLE" and observed in {"FREEZE", "DENY", "ESCALATE"}:
        delta = "MORE_RESTRICTIVE_THAN_EXPECTED"
    elif expected == "ESCALATE" and observed == "DENY":
        delta = "MORE_RESTRICTIVE_THAN_EXPECTED"
    else:
        delta = "NEEDS_THRESHOLD_REVIEW"
    return {
        "action_id": action_id,
        "expected_posture": expected,
        "smerc_posture": observed,
        "delta": delta,
    }


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a balanced SMERC posture judgment replay.")
    parser.add_argument("path", help="Path to smerc.customer-evaluation.v1 payload with context.expected_posture.")
    parser.add_argument("--json-output", default="reports/balanced_runtime_judgment_replay_report.json")
    parser.add_argument("--markdown-output", default="reports/Balanced_Runtime_Judgment_Replay_Report.md")
    parser.add_argument("--customer-json-output", default="reports/balanced_runtime_judgment_customer_evaluation/customer_evaluation_report.json")
    parser.add_argument("--customer-markdown-output", default="reports/balanced_runtime_judgment_customer_evaluation/Customer_Evaluation_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(load_payload(args.path))
    write_outputs(
        report,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
        customer_json_output=args.customer_json_output,
        customer_markdown_output=args.customer_markdown_output,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

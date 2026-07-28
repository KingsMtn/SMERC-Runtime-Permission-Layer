from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


VERSION = "smerc.customer-action-intake.v1"
REQUIRED_INTAKE_FIELDS = {
    "schema",
    "organization",
    "contact_role",
    "intake_date",
    "data_boundary",
    "workflow_context",
    "actions",
}
REQUIRED_ACTION_FIELDS = {
    "action_id",
    "description",
    "actor",
    "tool",
    "action_type",
    "base_action_risk",
    "reversibility",
    "containment_strength",
    "rollback_latency",
    "evidence_validity",
    "anomaly_pressure",
    "impact_scope",
    "cancel_reliability",
    "authorization_confidence",
    "external_side_effect",
    "sensitive_data",
}
POSTURES = ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")


def _text(value: Any, field: str, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{field} must be a non-empty string")
    result = value.strip()
    if len(result) > maximum:
        raise ValueError(f"{field} must be at most {maximum} characters")
    return result


def _action_missing_fields(action: Mapping[str, Any]) -> list[str]:
    return sorted(REQUIRED_ACTION_FIELDS - set(action))


def validate_intake(payload: Mapping[str, Any]) -> Dict[str, Any]:
    unknown = sorted(set(payload) - REQUIRED_INTAKE_FIELDS)
    missing = sorted(REQUIRED_INTAKE_FIELDS - set(payload))
    if unknown:
        raise ValueError(f"customer action intake contains unknown field(s): {', '.join(unknown)}")
    if missing:
        raise ValueError(f"customer action intake is missing field(s): {', '.join(missing)}")
    if payload["schema"] != VERSION:
        raise ValueError(f"schema must be {VERSION}")
    actions = payload["actions"]
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")
    seen: set[str] = set()
    parsed_actions: list[Dict[str, Any]] = []
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise TypeError(f"actions[{index}] must be an object")
        missing_action_fields = _action_missing_fields(action)
        if missing_action_fields:
            raise ValueError(f"actions[{index}] is missing field(s): {', '.join(missing_action_fields)}")
        action_id = _text(action["action_id"], f"actions[{index}].action_id", 128)
        if action_id in seen:
            raise ValueError(f"duplicate action_id: {action_id}")
        seen.add(action_id)
        parsed_actions.append(dict(action))
    return {
        "schema": VERSION,
        "organization": _text(payload["organization"], "organization", 160),
        "contact_role": _text(payload["contact_role"], "contact_role", 120),
        "intake_date": _text(payload["intake_date"], "intake_date", 40),
        "data_boundary": _text(payload["data_boundary"], "data_boundary", 1000),
        "workflow_context": _text(payload["workflow_context"], "workflow_context", 1000),
        "actions": parsed_actions,
    }


def _score_band(score: float) -> str:
    if score >= 0.70:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _metadata_notes(action: Mapping[str, Any]) -> list[str]:
    notes: list[str] = []
    context = action.get("context", {})
    if not isinstance(context, dict):
        notes.append("context must be an object for pilot metadata")
        return notes
    if "domain_profile" not in context:
        notes.append("context.domain_profile missing; pilot should declare a domain profile")
    if "workflow" not in context:
        notes.append("context.workflow missing; pilot should declare the workflow family")
    if action.get("external_side_effect") and action.get("rollback_latency", 1) > 0.50:
        notes.append("external side effect has slow rollback; reviewer should confirm rollback path")
    if action.get("sensitive_data") and action.get("evidence_validity", 0) < 0.70:
        notes.append("sensitive-data action has incomplete evidence; reviewer should confirm evidence source")
    return notes


def _pilot_fit(records: list[Mapping[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"fit": "weak", "reason": "No actions were provided."}
    side_effecting = sum(1 for record in records if record["input"]["external_side_effect"])
    restraint = sum(1 for record in records if record["decision"]["posture"] in {"THROTTLE", "FREEZE", "DENY", "ESCALATE"})
    metadata_gaps = sum(1 for record in records if record["metadata_notes"])
    if side_effecting >= 2 and restraint >= 2 and metadata_gaps <= len(records):
        return {
            "fit": "strong",
            "reason": "The intake includes multiple side-effecting actions where SMERC creates reviewable restraint or escalation decisions.",
        }
    if side_effecting >= 1 and restraint >= 1:
        return {
            "fit": "moderate",
            "reason": "The intake has at least one meaningful side-effecting action worth testing in observe mode.",
        }
    return {
        "fit": "weak",
        "reason": "The intake does not yet show enough side-effecting workflow risk to justify a pilot.",
    }


def evaluate_customer_intake(payload: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = validate_intake(payload)
    engine = RecoverabilityEngine()
    records: list[Dict[str, Any]] = []
    posture_counts: Counter[str] = Counter()
    profile_counts: Counter[str] = Counter()
    exposure_by_profile: dict[str, list[float]] = defaultdict(list)
    for action in parsed["actions"]:
        decision = engine.evaluate(action)
        scores = decision["scores"]
        posture_counts[decision["posture"]] += 1
        profile = decision["domain_profile"]["profile_id"]
        profile_counts[profile] += 1
        exposure_by_profile[profile].append(scores["irreversible_exposure_score"])
        records.append(
            {
                "action_id": action["action_id"],
                "description": action["description"],
                "input": {
                    "actor": action["actor"],
                    "tool": action["tool"],
                    "action_type": action["action_type"],
                    "external_side_effect": action["external_side_effect"],
                    "sensitive_data": action["sensitive_data"],
                    "context": action.get("context", {}),
                },
                "decision": {
                    "posture": decision["posture"],
                    "enforcement_state": decision["enforcement_state"],
                    "scores": scores,
                    "reason_codes": decision["reason_codes"],
                    "controls": decision["controls"],
                    "plain_english_summary": decision["plain_english_summary"],
                    "domain_profile": decision["domain_profile"],
                    "replay_id": decision["replay_id"],
                },
                "analysis": {
                    "irreversible_exposure_band": _score_band(scores["irreversible_exposure_score"]),
                    "reversible_capacity_band": _score_band(scores["reversible_capacity_score"]),
                    "confidence_band": _score_band(scores["confidence_score"]),
                },
                "metadata_notes": _metadata_notes(action),
            }
        )
    records_by_exposure = sorted(
        records,
        key=lambda item: item["decision"]["scores"]["irreversible_exposure_score"],
        reverse=True,
    )
    summary = {
        "total_actions": len(records),
        "posture_counts": {posture: posture_counts.get(posture, 0) for posture in POSTURES},
        "domain_profile_counts": dict(sorted(profile_counts.items())),
        "highest_exposure_actions": [
            {
                "action_id": record["action_id"],
                "posture": record["decision"]["posture"],
                "irreversible_exposure_score": record["decision"]["scores"]["irreversible_exposure_score"],
                "reversible_capacity_score": record["decision"]["scores"]["reversible_capacity_score"],
            }
            for record in records_by_exposure[:5]
        ],
        "average_exposure_by_domain_profile": {
            profile: round(sum(values) / len(values), 3)
            for profile, values in sorted(exposure_by_profile.items())
        },
        "actions_with_metadata_notes": sum(1 for record in records if record["metadata_notes"]),
    }
    return {
        "schema": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "organization": parsed["organization"],
        "contact_role": parsed["contact_role"],
        "intake_date": parsed["intake_date"],
        "workflow_context": parsed["workflow_context"],
        "data_boundary": parsed["data_boundary"],
        "evidence_boundary": "Customer action intake is metadata-only pilot preparation. It is not proof of production safety, customer demand, or incident reduction.",
        "summary": summary,
        "pilot_fit": _pilot_fit(records),
        "records": records,
        "recommended_next_action": (
            "Use the highest-exposure actions in a review call, ask human reviewers to label the preferred posture, "
            "and proceed to observe-mode pilot only if reviewer labels and workflow ownership are available."
        ),
    }


def load_payload(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("customer action intake must be a JSON object")
    return payload


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# {report['organization']} Customer Action Intake Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Contact role: `{report['contact_role']}`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Workflow Context",
        "",
        str(report["workflow_context"]),
        "",
        "## Summary",
        "",
        f"- Total actions: `{summary['total_actions']}`",
        f"- Posture counts: `{summary['posture_counts']}`",
        f"- Domain profiles: `{summary['domain_profile_counts']}`",
        f"- Actions with metadata notes: `{summary['actions_with_metadata_notes']}`",
        f"- Pilot fit: `{report['pilot_fit']['fit']}`",
        f"- Fit reason: {report['pilot_fit']['reason']}",
        "",
        "## Highest Exposure Actions",
        "",
        "| Action | Posture | Irreversible Exposure | Reversible Capacity |",
        "| --- | --- | ---: | ---: |",
    ]
    for item in summary["highest_exposure_actions"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['posture']}` | {item['irreversible_exposure_score']} | {item['reversible_capacity_score']} |"
        )
    lines.extend(["", "## Action Decisions", ""])
    for record in report["records"]:
        decision = record["decision"]
        lines.extend(
            [
                f"### {record['action_id']}",
                "",
                f"- Description: {record['description']}",
                f"- Tool: `{record['input']['tool']}`",
                f"- Posture: `{decision['posture']}`",
                f"- Enforcement state: `{decision['enforcement_state']}`",
                f"- Scores: `{decision['scores']}`",
                f"- Reason codes: `{decision['reason_codes']}`",
                f"- Controls: `{decision['controls']}`",
                f"- Summary: {decision['plain_english_summary']}",
            ]
        )
        if record["metadata_notes"]:
            lines.append(f"- Metadata notes: `{record['metadata_notes']}`")
        lines.append("")
    lines.extend(
        [
            "## Recommended Next Action",
            "",
            str(report["recommended_next_action"]),
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
    parser = argparse.ArgumentParser(description="Evaluate a metadata-only customer action intake for SMERC pilot fit.")
    parser.add_argument("path", help="Path to smerc.customer-action-intake.v1 JSON.")
    parser.add_argument("--json-output", default="reports/customer_action_intake_report.json")
    parser.add_argument("--markdown-output", default="reports/Customer_Action_Intake_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = evaluate_customer_intake(load_payload(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

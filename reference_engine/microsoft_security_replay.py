from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.recoverability_engine import RecoverabilityEngine


DATASET_VERSION = "smerc.microsoft-security-replay.dataset.v1"
REPORT_VERSION = "smerc.microsoft-security-replay.report.v1"
EVENT_SOURCES = {
    "microsoft_defender_alert",
    "microsoft_sentinel_incident",
    "azure_activity_log",
    "advanced_hunting_event",
}
SEVERITIES = {"informational", "low", "medium", "high"}
WORKFLOW_OUTCOMES = {"ALERT_ONLY", "AUTO_RESPONSE", "ANALYST_REVIEW", "ESCALATE_INCIDENT", "DO_NOT_EXECUTE"}
SMERC_RESTRAINT_POSTURES = {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}


def load_dataset(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Microsoft security replay dataset must be an object")
    return parse_dataset(payload)


def parse_dataset(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {"schema", "source_boundary", "events"}
    _exact_fields(payload, required, "dataset")
    if payload["schema"] != DATASET_VERSION:
        raise ValueError(f"dataset.schema must be {DATASET_VERSION}")
    source_boundary = _text(payload["source_boundary"], "dataset.source_boundary", 512)
    events = payload["events"]
    if not isinstance(events, list) or not events:
        raise ValueError("dataset.events must be a non-empty array")
    parsed_events = [_parse_event(event, index) for index, event in enumerate(events)]
    seen = set()
    for event in parsed_events:
        if event["event_id"] in seen:
            raise ValueError(f"duplicate event_id: {event['event_id']}")
        seen.add(event["event_id"])
    return {"schema": DATASET_VERSION, "source_boundary": source_boundary, "events": parsed_events}


def build_replay_report(dataset: Mapping[str, Any], *, engine: RecoverabilityEngine | None = None) -> Dict[str, Any]:
    parsed = parse_dataset(dataset)
    runtime = engine or RecoverabilityEngine()
    records: list[Dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    workflow_counts: Counter[str] = Counter()
    posture_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()
    exposure_by_source: dict[str, list[float]] = {}

    for event in parsed["events"]:
        action = action_from_event(event)
        decision = runtime.evaluate(action)
        posture = str(decision["posture"])
        workflow_outcome = str(event["microsoft_workflow_outcome"])
        delta = classify_delta(workflow_outcome, posture)
        scores = decision["scores"]
        source = str(event["event_source"])
        source_counts[source] += 1
        workflow_counts[workflow_outcome] += 1
        posture_counts[posture] += 1
        delta_counts[delta] += 1
        exposure_by_source.setdefault(source, []).append(float(scores["irreversible_exposure_score"]))
        records.append(
            {
                "event_id": event["event_id"],
                "event_source": source,
                "title": event["title"],
                "severity": event["severity"],
                "category": event["category"],
                "detection_source": event["detection_source"],
                "microsoft_workflow_outcome": workflow_outcome,
                "workflow_rationale": event["workflow_rationale"],
                "proposed_response": event["proposed_response"]["description"],
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

    event_count = len(records)
    restraint_after_auto = delta_counts["MICROSOFT_AUTO_SMERC_RESTRAINT"]
    bounded_after_review = delta_counts["MICROSOFT_REVIEW_SMERC_BOUNDED"]
    return {
        "version": REPORT_VERSION,
        "generated_at": _now(),
        "dataset_schema": parsed["schema"],
        "source_boundary": parsed["source_boundary"],
        "event_count": event_count,
        "event_source_counts": dict(sorted(source_counts.items())),
        "microsoft_workflow_counts": {outcome: workflow_counts.get(outcome, 0) for outcome in sorted(WORKFLOW_OUTCOMES)},
        "smerc_posture_counts": {
            posture: posture_counts.get(posture, 0) for posture in ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")
        },
        "delta_counts": dict(sorted(delta_counts.items())),
        "decision_difference_count": sum(
            count for delta, count in delta_counts.items() if delta not in {"BOTH_ALLOW", "BOTH_RESTRAIN"}
        ),
        "decision_difference_rate": round(
            sum(count for delta, count in delta_counts.items() if delta not in {"BOTH_ALLOW", "BOTH_RESTRAIN"})
            / event_count,
            3,
        ),
        "auto_response_restrained_count": restraint_after_auto,
        "review_queue_bounded_count": bounded_after_review,
        "average_exposure_by_source": {
            source: round(sum(values) / len(values), 3) for source, values in sorted(exposure_by_source.items())
        },
        "evidence_boundary": (
            "Microsoft-style replay based on public schema concepts and synthetic sample events only. This is not "
            "Microsoft telemetry, Microsoft certification, Sentinel validation, Defender validation, customer "
            "validation, threat detection, incident reduction proof, or a replacement for Microsoft security tools."
        ),
        "records": records,
    }


def action_from_event(event: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = _parse_event(event, 0)
    response = parsed["proposed_response"]
    return {
        "action_id": f"MSFT_REPLAY_{response['action_id']}",
        "description": response["description"],
        "actor": response["actor"],
        "tool": response["tool"],
        "action_type": response["action_type"],
        "base_action_risk": response["base_action_risk"],
        "reversibility": response["reversibility"],
        "containment_strength": response["containment_strength"],
        "rollback_latency": response["rollback_latency"],
        "evidence_validity": response["evidence_validity"],
        "anomaly_pressure": response["anomaly_pressure"],
        "impact_scope": response["impact_scope"],
        "cancel_reliability": response["cancel_reliability"],
        "authorization_confidence": response["authorization_confidence"],
        "external_side_effect": response["external_side_effect"],
        "sensitive_data": response["sensitive_data"],
        "context": {
            "domain_profile": response["domain_profile"],
            "microsoft_style_event_source": parsed["event_source"],
            "severity": parsed["severity"],
            "category": parsed["category"],
            "entity_counts": parsed["entities"],
            "source_boundary": "synthetic_microsoft_style_replay",
        },
    }


def classify_delta(microsoft_workflow_outcome: str, smerc_posture: str) -> str:
    if microsoft_workflow_outcome == "AUTO_RESPONSE" and smerc_posture in SMERC_RESTRAINT_POSTURES:
        return "MICROSOFT_AUTO_SMERC_RESTRAINT"
    if microsoft_workflow_outcome in {"ANALYST_REVIEW", "ESCALATE_INCIDENT"} and smerc_posture in {"ALLOW", "THROTTLE"}:
        return "MICROSOFT_REVIEW_SMERC_BOUNDED"
    if microsoft_workflow_outcome in {"ALERT_ONLY", "DO_NOT_EXECUTE"} and smerc_posture in {"ALLOW", "THROTTLE"}:
        return "MICROSOFT_HOLD_SMERC_BOUNDED"
    if microsoft_workflow_outcome == "AUTO_RESPONSE" and smerc_posture == "ALLOW":
        return "BOTH_ALLOW"
    return "BOTH_RESTRAIN"


def interpretation(delta: str) -> str:
    if delta == "MICROSOFT_AUTO_SMERC_RESTRAINT":
        return (
            "A Microsoft-style workflow would auto-respond, while SMERC restrains the action because runtime "
            "recoverability, containment, rollback latency, evidence, or impact scope warrants additional controls."
        )
    if delta == "MICROSOFT_REVIEW_SMERC_BOUNDED":
        return (
            "A Microsoft-style workflow would queue or escalate the event, while SMERC identifies a bounded runtime "
            "path that may be allowed or throttled with evidence and controls."
        )
    if delta == "MICROSOFT_HOLD_SMERC_BOUNDED":
        return (
            "A Microsoft-style workflow would hold or block the response, while SMERC identifies a recoverable, "
            "bounded action path under the sample metadata."
        )
    if delta == "BOTH_ALLOW":
        return "Both the Microsoft-style workflow and SMERC allow automated execution under the sample metadata."
    return "Both lenses require restraint, but SMERC adds recoverability scores, reason codes, controls, and replay IDs."


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Microsoft-Style Security Replay Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Purpose",
        "",
        "This replay shows how SMERC can evaluate proposed automated responses derived from Microsoft Sentinel, Defender, Azure Activity, and advanced-hunting style events before execution.",
        "",
        "It does not test Microsoft detection quality. It tests whether recoverability scoring changes the runtime posture of the next automated response action.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Events: `{report['event_count']}`",
        f"- Event sources: `{report['event_source_counts']}`",
        f"- Microsoft-style workflow counts: `{report['microsoft_workflow_counts']}`",
        f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
        f"- Decision difference count: `{report['decision_difference_count']}`",
        f"- Decision difference rate: `{report['decision_difference_rate']}`",
        f"- Auto responses restrained by SMERC: `{report['auto_response_restrained_count']}`",
        f"- Review/escalation events with bounded SMERC path: `{report['review_queue_bounded_count']}`",
        f"- Average exposure by source: `{report['average_exposure_by_source']}`",
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
            "## Replay Results",
            "",
            "| Event | Source | Microsoft-Style Workflow | SMERC | Exposure | Capacity | Delta |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| `{record['event_id']}` | `{record['event_source']}` | `{record['microsoft_workflow_outcome']}` | "
            f"`{record['smerc_posture']}` | {record['irreversible_exposure_score']} | "
            f"{record['reversible_capacity_score']} | `{record['delta_type']}` |"
        )
    lines.extend(["", "## Demo-Ready Examples", ""])
    for record in sorted(report["records"], key=lambda item: -float(item["irreversible_exposure_score"]))[:4]:
        lines.extend(
            [
                f"### {record['event_id']}: {record['title']}",
                "",
                f"- Source: `{record['event_source']}`",
                f"- Severity: `{record['severity']}`",
                f"- Proposed response: {record['proposed_response']}",
                f"- Microsoft-style workflow: `{record['microsoft_workflow_outcome']}` because {record['workflow_rationale']}",
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
            "Microsoft Sentinel, Defender, Entra, and Azure controls are strong at detection, identity, telemetry, workflow, and response execution. SMERC does not replace them. The commercial question is whether security and platform teams want a recoverability-aware checkpoint before an automated response creates business side effects.",
            "",
            "The practical first pilot would run in shadow mode: export Microsoft-style alert or incident metadata, map the proposed response action, let SMERC score the action, and compare SMERC posture with the existing workflow outcome. No production blocking or private telemetry is required for the first review.",
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


def _parse_event(payload: Any, index: int) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError(f"event {index} must be an object")
    required = {
        "event_id",
        "event_source",
        "event_time",
        "title",
        "severity",
        "category",
        "detection_source",
        "microsoft_workflow_outcome",
        "workflow_rationale",
        "entities",
        "proposed_response",
    }
    _exact_fields(payload, required, f"event {index}")
    event = dict(payload)
    event["event_id"] = _safe_identifier(event["event_id"], f"event {index}.event_id")
    event["event_source"] = _choice(event["event_source"], EVENT_SOURCES, f"event {index}.event_source")
    event["event_time"] = _text(event["event_time"], f"event {index}.event_time", 64)
    event["title"] = _text(event["title"], f"event {index}.title", 192)
    event["severity"] = _choice(str(event["severity"]).lower(), SEVERITIES, f"event {index}.severity")
    event["category"] = _safe_identifier(event["category"], f"event {index}.category")
    event["detection_source"] = _text(event["detection_source"], f"event {index}.detection_source", 160)
    event["microsoft_workflow_outcome"] = _choice(
        event["microsoft_workflow_outcome"], WORKFLOW_OUTCOMES, f"event {index}.microsoft_workflow_outcome"
    )
    event["workflow_rationale"] = _text(event["workflow_rationale"], f"event {index}.workflow_rationale", 384)
    event["entities"] = _parse_entities(event["entities"], index)
    event["proposed_response"] = _parse_response(event["proposed_response"], index)
    return event


def _parse_entities(payload: Any, index: int) -> Dict[str, int]:
    if not isinstance(payload, Mapping):
        raise TypeError(f"event {index}.entities must be an object")
    required = {"device_count", "user_count", "ip_count", "subscription_count"}
    _exact_fields(payload, required, f"event {index}.entities")
    return {key: _bounded_int(payload[key], f"event {index}.entities.{key}") for key in sorted(required)}


def _parse_response(payload: Any, index: int) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError(f"event {index}.proposed_response must be an object")
    required = {
        "action_id",
        "description",
        "actor",
        "tool",
        "action_type",
        "domain_profile",
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
    _exact_fields(payload, required, f"event {index}.proposed_response")
    response = dict(payload)
    for key in ("action_id", "actor", "action_type", "domain_profile"):
        response[key] = _safe_identifier(response[key], f"event {index}.proposed_response.{key}")
    response["description"] = _text(response["description"], f"event {index}.proposed_response.description", 256)
    response["tool"] = _text(response["tool"], f"event {index}.proposed_response.tool", 128)
    for key in (
        "base_action_risk",
        "reversibility",
        "containment_strength",
        "rollback_latency",
        "evidence_validity",
        "anomaly_pressure",
        "impact_scope",
        "cancel_reliability",
        "authorization_confidence",
    ):
        response[key] = _score(response[key], f"event {index}.proposed_response.{key}")
    for key in ("external_side_effect", "sensitive_data"):
        if not isinstance(response[key], bool):
            raise TypeError(f"event {index}.proposed_response.{key} must be a boolean")
    return response


def _exact_fields(payload: Mapping[str, Any], required: set[str], path: str) -> None:
    missing = sorted(required - set(payload))
    unknown = sorted(set(payload) - required)
    if missing:
        raise ValueError(f"{path} missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _choice(value: Any, allowed: set[str], path: str) -> str:
    text = _text(value, path, 96)
    if text not in allowed:
        raise ValueError(f"{path} must be one of: {', '.join(sorted(allowed))}")
    return text


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number from 0.0 through 1.0")
    if value < 0 or value > 1:
        raise ValueError(f"{path} must be from 0.0 through 1.0")
    return float(value)


def _bounded_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if value < 0 or value > 1_000_000:
        raise ValueError(f"{path} must be from 0 through 1000000")
    return value


def _safe_identifier(value: Any, path: str) -> str:
    text = _text(value, path, 128)
    if not text.replace("_", "-").replace(".", "-").replace(":", "-").replace("-", "").isalnum():
        raise ValueError(f"{path} must be a safe identifier")
    return text


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value.strip()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay Microsoft-style security events through SMERC.")
    parser.add_argument("path", nargs="?", default="examples/microsoft_security_replay_events.json")
    parser.add_argument("--json-output", default="reports/microsoft_security_replay_report.json")
    parser.add_argument("--markdown-output", default="reports/Microsoft_Security_Replay_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_replay_report(load_dataset(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.action_language import ACTION_VERSION, evaluate_language_action
from reference_engine.mcp_transport_proxy import MCP_TRANSPORT_ENVELOPE_VERSION, run_mcp_transport_proxy


SELF_SERVICE_CONNECTOR_VERSION = "smerc.self-service-pilot-connector.v1"
BUNDLE_VERSION = "smerc.self-service-pilot-bundle.v1"
SUPPORTED_EVENT_TYPES = {"action_language", "mcp_transport"}


def build_self_service_pilot_package(payload: Mapping[str, Any]) -> Dict[str, Any]:
    bundle = _parse_bundle(payload)
    records = [_evaluate_event(event) for event in bundle["events"]]
    posture_counts: Counter[str] = Counter(record["posture"] for record in records)
    source_counts: Counter[str] = Counter(record["source_type"] for record in records)
    highest_exposure = sorted(records, key=lambda item: item["scores"]["irreversible_exposure_score"], reverse=True)
    return {
        "schema": SELF_SERVICE_CONNECTOR_VERSION,
        "generated_at": _now(),
        "organization": bundle["organization"],
        "contact_role": bundle["contact_role"],
        "workflow_context": bundle["workflow_context"],
        "data_boundary": bundle["data_boundary"],
        "summary": {
            "total_events": len(records),
            "source_counts": dict(sorted(source_counts.items())),
            "posture_counts": dict(sorted(posture_counts.items())),
            "forwarded_mcp_calls": sum(1 for record in records if record.get("mcp_forwarded") is True),
            "blocked_mcp_calls": sum(1 for record in records if record.get("mcp_forwarded") is False),
            "highest_exposure_events": [
                {
                    "event_id": record["event_id"],
                    "source_type": record["source_type"],
                    "posture": record["posture"],
                    "irreversible_exposure_score": record["scores"]["irreversible_exposure_score"],
                    "reversible_capacity_score": record["scores"]["reversible_capacity_score"],
                }
                for record in highest_exposure[:5]
            ],
            "pilot_fit": _pilot_fit(records),
        },
        "records": records,
        "recommended_next_action": _recommended_next_action(records),
        "evidence_boundary": (
            "Self-service pilot connector output is metadata-only pilot preparation. It is not production certification, "
            "security attestation, customer demand proof, incident-reduction proof, MCP compliance, or approval to enforce."
        ),
    }


def render_markdown(package: Mapping[str, Any]) -> str:
    summary = package["summary"]
    lines = [
        "# SMERC Self-Service Pilot Connector Report",
        "",
        f"Generated: `{package['generated_at']}`",
        f"Organization: `{package['organization']}`",
        f"Contact role: `{package['contact_role']}`",
        "",
        "## What Was Evaluated",
        "",
        str(package["workflow_context"]),
        "",
        "## Summary",
        "",
        f"- Total events: `{summary['total_events']}`",
        f"- Source counts: `{summary['source_counts']}`",
        f"- Posture counts: `{summary['posture_counts']}`",
        f"- Forwarded MCP calls: `{summary['forwarded_mcp_calls']}`",
        f"- Blocked MCP calls: `{summary['blocked_mcp_calls']}`",
        f"- Pilot fit: `{summary['pilot_fit']['fit']}`",
        f"- Fit reason: {summary['pilot_fit']['reason']}",
        "",
        "## Highest Exposure Events",
        "",
    ]
    for item in summary["highest_exposure_events"]:
        lines.append(
            f"- `{item['event_id']}` ({item['source_type']}): {item['posture']} "
            f"exposure `{item['irreversible_exposure_score']}`, capacity `{item['reversible_capacity_score']}`"
        )
    lines.extend(
        [
            "",
            "## Records",
            "",
        ]
    )
    for record in package["records"]:
        lines.extend(
            [
                f"### {record['event_id']}",
                "",
                f"- Source: `{record['source_type']}`",
                f"- Description: {record['description']}",
                f"- Posture: `{record['posture']}`",
                f"- Enforcement state: `{record['enforcement_state']}`",
                f"- Irreversible exposure: `{record['scores']['irreversible_exposure_score']}`",
                f"- Reversible capacity: `{record['scores']['reversible_capacity_score']}`",
                f"- Confidence: `{record['scores']['confidence_score']}`",
                f"- Reason codes: `{record['reason_codes']}`",
                f"- Controls: `{record['controls']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Recommended Next Action",
            "",
            str(package["recommended_next_action"]),
            "",
            "## Evidence Boundary",
            "",
            str(package["evidence_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(package: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(package), encoding="utf-8")


def _evaluate_event(event: Mapping[str, Any]) -> Dict[str, Any]:
    source_type = event["source_type"]
    if source_type == "action_language":
        decision = evaluate_language_action(event["payload"])
        return {
            "event_id": event["event_id"],
            "source_type": source_type,
            "description": event["payload"]["action"]["description"],
            "posture": decision["posture"],
            "enforcement_state": decision["enforcement_state"],
            "scores": dict(decision["scores"]),
            "reason_codes": list(decision.get("reason_codes", [])),
            "controls": list(decision.get("controls", [])),
            "replay_id": decision["replay_id"],
            "plain_english_summary": decision["plain_english_summary"],
        }
    transport = run_mcp_transport_proxy(event["payload"])
    proxy_report = transport["proxy_report"]
    decision = proxy_report["governance_report"]["decision"]
    response = transport["mcp_jsonrpc_response"]
    return {
        "event_id": event["event_id"],
        "source_type": source_type,
        "description": event["payload"]["governance_request"]["tool_call"]["description"],
        "posture": decision["posture"],
        "enforcement_state": decision["enforcement_state"],
        "scores": dict(decision["scores"]),
        "reason_codes": list(decision.get("reason_codes", [])),
        "controls": list(decision.get("controls", [])),
        "replay_id": decision["replay_id"],
        "plain_english_summary": transport["transport_summary"],
        "mcp_forwarded": "result" in response,
        "mcp_proxy_action": proxy_report["proxy_response"]["proxy_action"],
        "mcp_response_shape": "result" if "result" in response else "error",
    }


def _parse_bundle(payload: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("self-service pilot bundle must be an object")
    required = {"schema", "organization", "contact_role", "workflow_context", "data_boundary", "events"}
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"self-service pilot bundle missing field(s): {', '.join(missing)}")
    unknown = sorted(set(payload) - required)
    if unknown:
        raise ValueError(f"self-service pilot bundle contains unknown field(s): {', '.join(unknown)}")
    if payload["schema"] != BUNDLE_VERSION:
        raise ValueError(f"schema must be {BUNDLE_VERSION}")
    events = payload["events"]
    if not isinstance(events, list) or not events:
        raise ValueError("events must be a non-empty list")
    seen: set[str] = set()
    parsed_events: list[Dict[str, Any]] = []
    for index, event in enumerate(events):
        parsed = _parse_event(event, index)
        if parsed["event_id"] in seen:
            raise ValueError(f"duplicate event_id: {parsed['event_id']}")
        seen.add(parsed["event_id"])
        parsed_events.append(parsed)
    return {
        "schema": BUNDLE_VERSION,
        "organization": _text(payload["organization"], "organization", 160),
        "contact_role": _text(payload["contact_role"], "contact_role", 120),
        "workflow_context": _text(payload["workflow_context"], "workflow_context", 1200),
        "data_boundary": _text(payload["data_boundary"], "data_boundary", 1200),
        "events": parsed_events,
    }


def _parse_event(event: Any, index: int) -> Dict[str, Any]:
    if not isinstance(event, Mapping):
        raise TypeError(f"events[{index}] must be an object")
    required = {"event_id", "source_type", "payload"}
    missing = sorted(required - set(event))
    if missing:
        raise ValueError(f"events[{index}] missing field(s): {', '.join(missing)}")
    unknown = sorted(set(event) - required)
    if unknown:
        raise ValueError(f"events[{index}] contains unknown field(s): {', '.join(unknown)}")
    source_type = _text(event["source_type"], f"events[{index}].source_type", 40)
    if source_type not in SUPPORTED_EVENT_TYPES:
        raise ValueError(f"events[{index}].source_type must be one of: {', '.join(sorted(SUPPORTED_EVENT_TYPES))}")
    if not isinstance(event["payload"], Mapping):
        raise TypeError(f"events[{index}].payload must be an object")
    payload = dict(event["payload"])
    if source_type == "action_language" and payload.get("language_version") != ACTION_VERSION:
        raise ValueError(f"events[{index}].payload.language_version must be {ACTION_VERSION}")
    if source_type == "mcp_transport" and payload.get("schema") != MCP_TRANSPORT_ENVELOPE_VERSION:
        raise ValueError(f"events[{index}].payload.schema must be {MCP_TRANSPORT_ENVELOPE_VERSION}")
    return {
        "event_id": _text(event["event_id"], f"events[{index}].event_id", 128),
        "source_type": source_type,
        "payload": payload,
    }


def _pilot_fit(records: list[Mapping[str, Any]]) -> Dict[str, str]:
    restraint = sum(1 for record in records if record["posture"] != "ALLOW")
    high_exposure = sum(1 for record in records if record["scores"]["irreversible_exposure_score"] >= 0.70)
    mcp = sum(1 for record in records if record["source_type"] == "mcp_transport")
    if len(records) >= 3 and high_exposure >= 1 and restraint >= 2 and mcp >= 1:
        return {
            "fit": "strong",
            "reason": "The bundle includes mixed workflow and MCP tool-call examples where SMERC creates concrete restraint decisions.",
        }
    if high_exposure >= 1 and restraint >= 1:
        return {
            "fit": "moderate",
            "reason": "The bundle includes at least one high-exposure action worth reviewing in observe mode.",
        }
    return {
        "fit": "weak",
        "reason": "The bundle does not yet show enough irreversible exposure or workflow variety to justify a pilot.",
    }


def _recommended_next_action(records: list[Mapping[str, Any]]) -> str:
    if _pilot_fit(records)["fit"] == "strong":
        return (
            "Ask reviewers to label whether each posture is acceptable, compare SMERC output with existing approvals, "
            "and replace examples with 10 to 25 customer-approved non-secret events."
        )
    return (
        "Collect more side-effecting workflow examples before proposing a pilot; include at least one MCP/tool-call event "
        "and one GitHub Actions or deployment event."
    )


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    text = value.strip()
    if len(text) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return text


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a self-service SMERC pilot decision package from sample events.")
    parser.add_argument("--bundle", default="examples/self_service_pilot_bundle.json")
    parser.add_argument("--json-output", default="reports/self_service_pilot_connector_report.json")
    parser.add_argument("--markdown-output", default="reports/Self_Service_Pilot_Connector_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    package = build_self_service_pilot_package(load_json(args.bundle))
    write_outputs(package, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(package, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

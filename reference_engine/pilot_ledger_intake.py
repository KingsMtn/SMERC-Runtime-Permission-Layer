from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.benchmark_ledger_builder import BENCHMARK_LEDGER_BUNDLE_VERSION
from reference_engine.decision_lifecycle_ledger import LEDGER_VERSION, DecisionLifecycleLedger, render_markdown


PILOT_LEDGER_INTAKE_VERSION = "smerc.pilot-ledger-intake.v1"
PILOT_LEDGER_RESULT_VERSION = "smerc.pilot-ledger-intake-result.v1"

EVENT_ORDER = {
    "REQUEST": 1,
    "EVIDENCE": 2,
    "EVALUATION": 3,
    "HUMAN_INTERACTION": 4,
    "EXECUTION": 5,
    "OUTCOME": 6,
    "LEARNING_RECOMMENDATION": 7,
}
APPENDABLE_EVENTS = {"HUMAN_INTERACTION", "EXECUTION", "OUTCOME", "LEARNING_RECOMMENDATION"}
SINGLETON_APPEND_EVENTS = {"EXECUTION", "OUTCOME", "LEARNING_RECOMMENDATION"}


def _text(value: Any, path: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    return dict(value)


def _event_counts(ledger: DecisionLifecycleLedger) -> Dict[str, int]:
    return ledger.summary()["event_counts"]


def _last_event_rank(ledger: DecisionLifecycleLedger) -> int:
    if not ledger.records:
        return 0
    return max(EVENT_ORDER[record["event_type"]] for record in ledger.records)


def _validate_recorded_at(value: Any, path: str) -> str:
    text = _text(value, path, 64)
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"{path} must include a timezone")
    return text


def load_intake(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("pilot intake file must contain a JSON object")
    if payload.get("version") != PILOT_LEDGER_INTAKE_VERSION:
        raise ValueError(f"pilot intake version must be {PILOT_LEDGER_INTAKE_VERSION}")
    events = payload.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("pilot intake must contain a non-empty events list")
    if len(events) > 32:
        raise ValueError("pilot intake may append at most 32 events at once")
    parsed_events = []
    for index, event in enumerate(events):
        item = _object(event, f"events[{index}]")
        event_type = _text(item.get("event_type"), f"events[{index}].event_type", 64)
        if event_type not in APPENDABLE_EVENTS:
            raise ValueError(f"events[{index}].event_type must be appendable pilot evidence")
        parsed_events.append(
            {
                "event_type": event_type,
                "actor": _text(item.get("actor"), f"events[{index}].actor", 128),
                "recorded_at": _validate_recorded_at(item.get("recorded_at"), f"events[{index}].recorded_at"),
                "payload": _object(item.get("payload"), f"events[{index}].payload"),
            }
        )
    return {
        "version": PILOT_LEDGER_INTAKE_VERSION,
        "intake_id": _text(payload.get("intake_id"), "intake_id", 128),
        "decision_id": _text(payload.get("decision_id"), "decision_id", 192),
        "tenant_id": _text(payload.get("tenant_id"), "tenant_id", 128),
        "events": parsed_events,
        "operator_notes": _text(payload.get("operator_notes", "No operator notes supplied."), "operator_notes", 1024),
    }


def load_ledger_source(path: str | Path, *, decision_id: str | None = None) -> DecisionLifecycleLedger:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("ledger source must contain a JSON object")
    if payload.get("version") == LEDGER_VERSION:
        ledger = DecisionLifecycleLedger.from_dict(payload)
        if decision_id is not None and ledger.decision_id != decision_id:
            raise ValueError("decision_id does not match source ledger")
        return ledger
    if payload.get("version") == BENCHMARK_LEDGER_BUNDLE_VERSION:
        if not decision_id:
            raise ValueError("decision_id is required when loading from a benchmark ledger bundle")
        for ledger_payload in payload.get("ledgers", []):
            if isinstance(ledger_payload, dict) and ledger_payload.get("decision_id") == decision_id:
                return DecisionLifecycleLedger.from_dict(ledger_payload)
        raise ValueError(f"decision_id not found in benchmark ledger bundle: {decision_id}")
    raise ValueError("ledger source must be a DLL JSON file or benchmark DLL bundle")


def apply_pilot_intake(ledger: DecisionLifecycleLedger, intake: Mapping[str, Any]) -> Dict[str, Any]:
    before = ledger.to_dict()
    if not before["verification"]["valid"]:
        raise ValueError("source ledger must verify before pilot evidence can be appended")
    if intake["decision_id"] != ledger.decision_id:
        raise ValueError("pilot intake decision_id must match ledger decision_id")
    if intake["tenant_id"] != ledger.tenant_id:
        raise ValueError("pilot intake tenant_id must match ledger tenant_id")
    counts = _event_counts(ledger)
    current_rank = _last_event_rank(ledger)
    appended = []
    for event in intake["events"]:
        event_type = event["event_type"]
        next_rank = EVENT_ORDER[event_type]
        if next_rank < current_rank:
            raise ValueError(f"{event_type} cannot be appended after later lifecycle evidence")
        if event_type == "EXECUTION" and counts.get("EVALUATION", 0) == 0:
            raise ValueError("EXECUTION requires a prior EVALUATION record")
        if event_type == "OUTCOME" and counts.get("EXECUTION", 0) == 0:
            raise ValueError("OUTCOME requires a prior EXECUTION record")
        if event_type == "LEARNING_RECOMMENDATION" and counts.get("OUTCOME", 0) == 0:
            raise ValueError("LEARNING_RECOMMENDATION requires a prior OUTCOME record")
        if event_type in SINGLETON_APPEND_EVENTS and counts.get(event_type, 0) > 0:
            raise ValueError(f"{event_type} may only be appended once by this pilot intake path")
        appended.append(
            ledger.append(
                event_type,
                event["actor"],
                event["payload"],
                recorded_at=event["recorded_at"],
            )
        )
        counts[event_type] = counts.get(event_type, 0) + 1
        current_rank = max(current_rank, next_rank)
    after = ledger.to_dict()
    return {
        "version": PILOT_LEDGER_RESULT_VERSION,
        "applied_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "intake_id": intake["intake_id"],
        "decision_id": ledger.decision_id,
        "tenant_id": ledger.tenant_id,
        "records_before": before["record_count"],
        "records_appended": len(appended),
        "records_after": after["record_count"],
        "head_record_hash_before": before["head_record_hash"],
        "head_record_hash_after": after["head_record_hash"],
        "verification": after["verification"],
        "summary": after["summary"],
        "operator_notes": intake["operator_notes"],
        "ledger": after,
    }


def render_result_markdown(result: Mapping[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# SMERC Pilot Ledger Intake Result",
        "",
        f"Intake ID: `{result['intake_id']}`",
        f"Decision ID: `{result['decision_id']}`",
        f"Tenant: `{result['tenant_id']}`",
        f"Records before: `{result['records_before']}`",
        f"Records appended: `{result['records_appended']}`",
        f"Records after: `{result['records_after']}`",
        f"Head hash before: `{result['head_record_hash_before']}`",
        f"Head hash after: `{result['head_record_hash_after']}`",
        f"Valid chain: `{'yes' if result['verification']['valid'] else 'no'}`",
        "",
        "## Lifecycle Summary",
        "",
        f"- Final event type: `{summary['final_event_type']}`",
        f"- Override count: `{summary['override_count']}`",
        f"- Rollback performed: `{summary['rollback_performed']}`",
        f"- Rollback success: `{summary['rollback_success']}`",
        f"- Judged correct: `{summary['judged_correct']}`",
        f"- Pending learning recommendations: `{summary['pending_learning_recommendations']}`",
        "",
        "## Operator Notes",
        "",
        result["operator_notes"],
        "",
        "## Boundary",
        "",
        "This report records pilot-supplied evidence appended to an existing DLL. It does not certify that the evidence is complete, independently verified, compliant with retention law, or sufficient for production enforcement.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(result: Mapping[str, Any], json_path: str | Path, markdown_path: str | Path, ledger_markdown_path: str | Path | None = None) -> None:
    json_file = Path(json_path)
    markdown_file = Path(markdown_path)
    json_file.parent.mkdir(parents=True, exist_ok=True)
    markdown_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_file.write_text(render_result_markdown(result), encoding="utf-8")
    if ledger_markdown_path is not None:
        ledger_file = Path(ledger_markdown_path)
        ledger_file.parent.mkdir(parents=True, exist_ok=True)
        ledger = DecisionLifecycleLedger.from_dict(result["ledger"])
        ledger_file.write_text(render_markdown(ledger), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Append pilot evidence to a SMERC Decision Lifecycle Ledger.")
    parser.add_argument("ledger", type=Path, help="Existing DLL JSON file or benchmark DLL bundle.")
    parser.add_argument("intake", type=Path, help="Pilot evidence intake JSON file.")
    parser.add_argument("--decision-id", help="Required when the ledger source is a benchmark DLL bundle.")
    parser.add_argument("--json-output", default="reports/pilot_ledger_intake_result.json")
    parser.add_argument("--markdown-output", default="reports/Pilot_Ledger_Intake_Result.md")
    parser.add_argument("--ledger-markdown-output")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    intake = load_intake(args.intake)
    ledger = load_ledger_source(args.ledger, decision_id=args.decision_id or intake["decision_id"])
    result = apply_pilot_intake(ledger, intake)
    write_outputs(result, args.json_output, args.markdown_output, args.ledger_markdown_output)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


TIMING_EVIDENCE_VERSION = "smerc.timing-evidence.v1"
TIMING_REPORT_VERSION = "smerc.timing-evidence-report.v1"
ROOT_FIELDS = {"version", "tenant_id", "workflow_id", "records", "evidence_boundary"}
RECORD_FIELDS = {
    "replay_id",
    "posture",
    "decision_latency_ms",
    "route_latency_ms",
    "workflow_overhead_ms",
    "cancellation_window_ms",
    "cancel_attempted",
    "cancel_success",
    "rollback_attempted",
    "rollback_latency_observed_ms",
    "rollback_success",
    "review_latency_ms",
    "unavailable_evaluation",
}
POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE", "UNAVAILABLE"}


def validate_timing_evidence(payload: Mapping[str, Any]) -> Dict[str, Any]:
    root = dict(_object(payload, "timing_evidence"))
    _required(root, ROOT_FIELDS, "timing_evidence")
    _strict(root, ROOT_FIELDS, "timing_evidence")
    if root["version"] != TIMING_EVIDENCE_VERSION:
        raise ValueError(f"version must be {TIMING_EVIDENCE_VERSION}")
    root["tenant_id"] = _text(root["tenant_id"], "tenant_id", 128)
    root["workflow_id"] = _text(root["workflow_id"], "workflow_id", 128)
    root["evidence_boundary"] = _text(root["evidence_boundary"], "evidence_boundary", 512)
    records = root["records"]
    if not isinstance(records, list) or not records:
        raise TypeError("records must be a non-empty list")
    root["records"] = [_record(item, index) for index, item in enumerate(records)]
    return root


def build_timing_report(payload: Mapping[str, Any], *, latency_slo_ms: int = 250) -> Dict[str, Any]:
    evidence = validate_timing_evidence(payload)
    records = evidence["records"]
    decision_latencies = [record["decision_latency_ms"] for record in records]
    route_latencies = [record["route_latency_ms"] for record in records if record["route_latency_ms"] is not None]
    overheads = [record["workflow_overhead_ms"] for record in records if record["workflow_overhead_ms"] is not None]
    rollbacks = [record for record in records if record["rollback_attempted"]]
    cancels = [record for record in records if record["cancel_attempted"]]
    unavailable_count = sum(1 for record in records if record["unavailable_evaluation"])
    posture_counts = Counter(record["posture"] for record in records)
    p95 = _percentile(decision_latencies, 95)
    return {
        "version": TIMING_REPORT_VERSION,
        "generated_at": _now(),
        "tenant_id": evidence["tenant_id"],
        "workflow_id": evidence["workflow_id"],
        "record_count": len(records),
        "posture_counts": {posture: posture_counts.get(posture, 0) for posture in sorted(POSTURES)},
        "decision_latency": _latency_summary(decision_latencies, latency_slo_ms),
        "route_latency": _latency_summary(route_latencies, latency_slo_ms) if route_latencies else _empty_latency(latency_slo_ms),
        "workflow_overhead": _latency_summary(overheads, latency_slo_ms) if overheads else _empty_latency(latency_slo_ms),
        "resilience": {
            "unavailable_evaluation_count": unavailable_count,
            "unavailable_evaluation_rate": round(unavailable_count / len(records), 4),
            "cancel_attempt_count": len(cancels),
            "cancel_success_count": sum(1 for record in cancels if record["cancel_success"] is True),
            "cancel_success_rate": None if not cancels else round(
                sum(1 for record in cancels if record["cancel_success"] is True) / len(cancels), 4
            ),
            "rollback_attempt_count": len(rollbacks),
            "rollback_success_count": sum(1 for record in rollbacks if record["rollback_success"] is True),
            "rollback_success_rate": None if not rollbacks else round(
                sum(1 for record in rollbacks if record["rollback_success"] is True) / len(rollbacks), 4
            ),
        },
        "operational_status": _operational_status(
            p95=p95,
            latency_slo_ms=latency_slo_ms,
            unavailable_count=unavailable_count,
            record_count=len(records),
        ),
        "records": records,
        "evidence_boundary": (
            "Timing evidence summarizes supplied pilot timing records. It does not prove production latency, "
            "rollback reliability across environments, incident reduction, or SLA compliance."
        ),
        "source_evidence_boundary": evidence["evidence_boundary"],
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Timing Evidence Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Tenant: `{report['tenant_id']}`",
        f"- Workflow: `{report['workflow_id']}`",
        f"- Records: `{report['record_count']}`",
        f"- Operational status: `{report['operational_status']}`",
        f"- Posture counts: `{report['posture_counts']}`",
        "",
        "## Latency",
        "",
        f"- Decision latency: `{report['decision_latency']}`",
        f"- Route latency: `{report['route_latency']}`",
        f"- Workflow overhead: `{report['workflow_overhead']}`",
        "",
        "## Resilience",
        "",
        f"- Unavailable evaluations: `{report['resilience']['unavailable_evaluation_count']}`",
        f"- Cancel success rate: `{report['resilience']['cancel_success_rate']}`",
        f"- Rollback success rate: `{report['resilience']['rollback_success_rate']}`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
    ]
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _record(value: Any, index: int) -> Dict[str, Any]:
    record = dict(_object(value, f"records[{index}]"))
    _required(record, RECORD_FIELDS, f"records[{index}]")
    _strict(record, RECORD_FIELDS, f"records[{index}]")
    record["replay_id"] = _text(record["replay_id"], f"records[{index}].replay_id", 128)
    record["posture"] = _enum(record["posture"], POSTURES, f"records[{index}].posture")
    for field in ("decision_latency_ms",):
        record[field] = _non_negative_number(record[field], f"records[{index}].{field}")
    for field in (
        "route_latency_ms",
        "workflow_overhead_ms",
        "cancellation_window_ms",
        "rollback_latency_observed_ms",
        "review_latency_ms",
    ):
        record[field] = _optional_non_negative_number(record[field], f"records[{index}].{field}")
    for field in ("cancel_attempted", "rollback_attempted", "unavailable_evaluation"):
        record[field] = _boolean(record[field], f"records[{index}].{field}")
    record["cancel_success"] = _optional_boolean(record["cancel_success"], f"records[{index}].cancel_success")
    record["rollback_success"] = _optional_boolean(record["rollback_success"], f"records[{index}].rollback_success")
    if not record["cancel_attempted"] and record["cancel_success"] is not None:
        raise ValueError(f"records[{index}].cancel_success must be null when cancel_attempted is false")
    if not record["rollback_attempted"] and record["rollback_success"] is not None:
        raise ValueError(f"records[{index}].rollback_success must be null when rollback_attempted is false")
    return record


def _latency_summary(values: list[float], slo_ms: int) -> Dict[str, Any]:
    return {
        "slo_ms": slo_ms,
        "sample_count": len(values),
        "minimum_ms": min(values),
        "average_ms": round(sum(values) / len(values), 2),
        "p50_ms": _percentile(values, 50),
        "p95_ms": _percentile(values, 95),
        "maximum_ms": max(values),
        "slo_met": _percentile(values, 95) <= slo_ms,
    }


def _empty_latency(slo_ms: int) -> Dict[str, Any]:
    return {
        "slo_ms": slo_ms,
        "sample_count": 0,
        "minimum_ms": None,
        "average_ms": None,
        "p50_ms": None,
        "p95_ms": None,
        "maximum_ms": None,
        "slo_met": None,
    }


def _operational_status(*, p95: Optional[float], latency_slo_ms: int, unavailable_count: int, record_count: int) -> str:
    if unavailable_count / record_count >= 0.05:
        return "blocker"
    if p95 is not None and p95 > latency_slo_ms:
        return "watch"
    if unavailable_count:
        return "watch"
    return "ready"


def _percentile(values: list[float], percentile: int) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percentile / 100
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return round(ordered[lower] * (1 - weight) + ordered[upper] * weight, 2)


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    return value


def _required(value: Mapping[str, Any], fields: Iterable[str], path: str) -> None:
    missing = sorted(set(fields) - set(value))
    if missing:
        raise ValueError(f"{path} is missing required field(s): {', '.join(missing)}")


def _strict(value: Mapping[str, Any], fields: Iterable[str], path: str) -> None:
    unknown = sorted(set(value) - set(fields))
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _enum(value: Any, allowed: set[str], path: str) -> str:
    if value not in allowed:
        raise ValueError(f"{path} must be one of: {', '.join(sorted(allowed))}")
    return str(value)


def _non_negative_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a non-negative number")
    if value < 0:
        raise ValueError(f"{path} must be non-negative")
    return float(value)


def _optional_non_negative_number(value: Any, path: str) -> Optional[float]:
    if value is None:
        return None
    return _non_negative_number(value, path)


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _optional_boolean(value: Any, path: str) -> Optional[bool]:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean or null")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize SMERC timing evidence records.")
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--latency-slo-ms", type=int, default=250)
    parser.add_argument("--json-output", default="reports/timing_evidence_report.json")
    parser.add_argument("--markdown-output", default="reports/Timing_Evidence_Report.md")
    args = parser.parse_args()
    payload = json.loads(args.evidence.read_text(encoding="utf-8"))
    report = build_timing_report(payload, latency_slo_ms=args.latency_slo_ms)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

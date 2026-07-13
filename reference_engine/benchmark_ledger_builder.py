from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger


BENCHMARK_LEDGER_BUNDLE_VERSION = "smerc.benchmark-ledger-bundle.v1"
DEFAULT_BASE_TIME = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)


def _text(value: Any, path: str, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _records(payload: Mapping[str, Any]) -> list[Dict[str, Any]]:
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("benchmark payload must contain a non-empty records list")
    parsed: list[Dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise TypeError(f"records[{index}] must be an object")
        parsed.append(dict(record))
    return parsed


def _score(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return default
    return round(max(0.0, min(1.0, float(value))), 3)


def _list(value: Any, fallback: Iterable[str] = ()) -> list[str]:
    if not isinstance(value, list):
        return list(fallback)
    return [str(item)[:128] for item in value if str(item).strip()]


def build_decision_time_ledger(
    benchmark_record: Mapping[str, Any],
    *,
    tenant_id: str = "benchmark-suite",
    base_time: datetime = DEFAULT_BASE_TIME,
    sequence_offset: int = 0,
) -> DecisionLifecycleLedger:
    scenario_id = _text(benchmark_record.get("scenario_id"), "benchmark_record.scenario_id", 160)
    action = benchmark_record.get("action")
    if not isinstance(action, dict):
        raise TypeError("benchmark_record.action must be an object")
    action_id = _text(action.get("action_id"), "benchmark_record.action.action_id", 160)
    recorded = base_time + timedelta(seconds=sequence_offset * 10)
    ledger = DecisionLifecycleLedger(f"dll:{scenario_id}", tenant_id=tenant_id)
    ledger.append(
        "REQUEST",
        _text(action.get("actor", "unknown_actor"), "benchmark_record.action.actor", 128),
        {
            "initiated_by": _text(action.get("actor", "unknown_actor"), "REQUEST.initiated_by", 128),
            "requested_operation": _text(action.get("description", action_id), "REQUEST.requested_operation", 512),
            "environment": _text(str(action.get("context", {}).get("environment", "benchmark_proxy")), "REQUEST.environment", 128),
            "risk_profile": _text(str(benchmark_record.get("category", "unknown_category")), "REQUEST.risk_profile", 128),
        },
        recorded_at=recorded.isoformat(),
    )
    ledger.append(
        "EVIDENCE",
        "runtime-benchmark-suite",
        {
            "available_evidence": [
                "benchmark_action_signals",
                "traditional_policy_outcome",
                "recoverability_scores",
            ],
            "confidence_score": _score(benchmark_record.get("confidence_score")),
            "missing_evidence": [
                "live_execution_result",
                "human_reviewer_label",
                "customer_incident_outcome",
                "production_latency_impact",
            ],
            "external_dependencies": [
                _text(str(action.get("tool", "unknown_tool")), "EVIDENCE.external_dependencies[]", 128)
            ],
            "model_version": "reference-runtime-benchmark",
            "policy_version": "smerc.proxy-evidence-policy.v1",
        },
        recorded_at=(recorded + timedelta(seconds=1)).isoformat(),
    )
    ledger.append(
        "EVALUATION",
        "smerc-runtime-benchmark",
        {
            "structural_state": (
                f"Traditional policy returned {benchmark_record.get('traditional_policy_outcome')}; "
                f"SMERC returned {benchmark_record.get('smerc_posture')} for {action_id}."
            ),
            "entropy_indicators": _list(
                benchmark_record.get("reason_codes"),
                fallback=["NO_REASON_CODES_REPORTED"],
            ),
            "recoverability_score": _score(benchmark_record.get("reversible_capacity_score")),
            "authorization_recommendation": _text(benchmark_record.get("smerc_posture"), "EVALUATION.authorization_recommendation", 32),
            "reason_codes": _list(benchmark_record.get("reason_codes"), fallback=["NO_REASON_CODES_REPORTED"]),
            "recommended_safeguards": _list(benchmark_record.get("controls"), fallback=["preserve_replay"]),
        },
        recorded_at=(recorded + timedelta(seconds=2)).isoformat(),
    )
    return ledger


def build_benchmark_ledger_bundle(
    benchmark_payload: Mapping[str, Any],
    *,
    tenant_id: str = "benchmark-suite",
) -> Dict[str, Any]:
    records = _records(benchmark_payload)
    ledgers = [
        build_decision_time_ledger(record, tenant_id=tenant_id, sequence_offset=index).to_dict()
        for index, record in enumerate(records)
    ]
    posture_counts = Counter(
        ledger["records"][2]["payload"]["authorization_recommendation"]
        for ledger in ledgers
        if len(ledger["records"]) >= 3
    )
    invalid = [ledger["decision_id"] for ledger in ledgers if not ledger["verification"]["valid"]]
    incomplete = [
        ledger["decision_id"]
        for ledger in ledgers
        if ledger["summary"]["event_counts"].get("EXECUTION", 0) == 0
        or ledger["summary"]["event_counts"].get("OUTCOME", 0) == 0
    ]
    return {
        "version": BENCHMARK_LEDGER_BUNDLE_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_benchmark_version": benchmark_payload.get("summary", {}).get("version", "unknown"),
        "tenant_id": tenant_id,
        "summary": {
            "ledger_count": len(ledgers),
            "valid_ledger_count": len(ledgers) - len(invalid),
            "invalid_ledger_count": len(invalid),
            "decision_time_only_count": len(incomplete),
            "posture_counts": dict(sorted(posture_counts.items())),
            "evidence_boundary": (
                "Decision-time ledgers built from expanded proxy benchmark records; execution, outcome, "
                "human review, and customer incident evidence are intentionally absent until pilot collection."
            ),
        },
        "invalid_ledger_ids": invalid,
        "decision_time_only_ledger_ids": incomplete,
        "ledgers": ledgers,
    }


def render_markdown(bundle: Mapping[str, Any]) -> str:
    summary = bundle["summary"]
    lines = [
        "# SMERC Benchmark Decision-Time Ledger Bundle",
        "",
        f"Generated: `{bundle['generated_at']}`",
        f"Source benchmark: `{bundle['source_benchmark_version']}`",
        f"Tenant: `{bundle['tenant_id']}`",
        "",
        "## Executive Summary",
        "",
        (
            f"This bundle creates `{summary['ledger_count']}` hash-chained Decision Lifecycle Ledger records "
            "from the runtime governance benchmark suite."
        ),
        "",
        "The ledgers intentionally stop at request, evidence, and evaluation. They do not claim live execution, customer outcome, human review, or incident-reduction evidence.",
        "",
        "## Metrics",
        "",
        f"- Valid ledgers: `{summary['valid_ledger_count']}`",
        f"- Invalid ledgers: `{summary['invalid_ledger_count']}`",
        f"- Decision-time only ledgers: `{summary['decision_time_only_count']}`",
        f"- Posture counts: `{summary['posture_counts']}`",
        "",
        "## Evidence Boundary",
        "",
        summary["evidence_boundary"],
        "",
        "## Example Ledger Heads",
        "",
        "| Decision ID | Records | Head Hash | Posture |",
        "| --- | ---: | --- | --- |",
    ]
    for ledger in list(bundle["ledgers"])[:12]:
        posture = ledger["records"][2]["payload"]["authorization_recommendation"]
        lines.append(
            f"| `{ledger['decision_id']}` | {ledger['record_count']} | `{ledger['head_record_hash']}` | `{posture}` |"
        )
    lines.extend(
        [
            "",
            "## What This Adds",
            "",
            "- Each benchmark decision becomes replayable evidence with a hash-chain integrity check.",
            "- Missing outcome and execution evidence is explicit instead of hidden.",
            "- The same ledger format can be reused when design partners provide real reviewer labels and execution outcomes.",
            "",
            "## What This Does Not Prove",
            "",
            "- It does not prove the benchmark reflects a customer's production environment.",
            "- It does not prove SMERC reduced incidents.",
            "- It does not replace customer security review, SIEM retention, GRC workflows, or legal recordkeeping.",
            "",
        ]
    )
    return "\n".join(lines)


def load_benchmark(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("benchmark file must contain a JSON object")
    return payload


def write_outputs(bundle: Mapping[str, Any], json_path: str | Path, markdown_path: str | Path) -> None:
    json_file = Path(json_path)
    markdown_file = Path(markdown_path)
    json_file.parent.mkdir(parents=True, exist_ok=True)
    markdown_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_file.write_text(render_markdown(bundle), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build decision-time DLL records from a SMERC runtime benchmark.")
    parser.add_argument("benchmark", help="Path to runtime governance benchmark JSON.")
    parser.add_argument("--tenant-id", default="benchmark-suite")
    parser.add_argument("--json-output", default="reports/runtime_benchmark_dll_bundle.json")
    parser.add_argument("--markdown-output", default="reports/Runtime_Benchmark_DLL_Bundle.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    bundle = build_benchmark_ledger_bundle(load_benchmark(args.benchmark), tenant_id=args.tenant_id)
    write_outputs(bundle, args.json_output, args.markdown_output)
    print(json.dumps(bundle, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

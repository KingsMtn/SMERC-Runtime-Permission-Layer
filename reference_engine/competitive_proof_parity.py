from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.fake_customer_pilot import run_fake_customer_pilot
from reference_engine.mcp_proxy_runner import run_mcp_proxy
from reference_engine.mcp_tool_governance import evaluate_mcp_tool_call
from reference_engine.mcp_tool_risk_scanner import scan_mcp_tool_definition
from reference_engine.mcp_transport_proxy import run_mcp_transport_proxy
from reference_engine.real_incident_replay import build_report as build_real_incident_report
from reference_engine.real_incident_replay import evaluate_scenarios as evaluate_real_incidents
from reference_engine.real_incident_replay import load_scenarios as load_real_incidents
from reference_engine.runtime_benchmark_suite import build_runtime_benchmark
from reference_engine.timing_evidence import build_timing_report


COMPETITIVE_PROOF_PARITY_VERSION = "smerc.competitive-proof-parity.v1"
DEFAULT_PATHS = {
    "mcp_tool_definitions": "examples/mcp/tool_definition_risk_examples.json",
    "mcp_delete_call": "examples/mcp/tool_call_delete_customer_records.json",
    "mcp_search_call": "examples/mcp/tool_call_search_docs.json",
    "mcp_transport_delete": "examples/mcp/transport_proxy_delete_customer_records.json",
    "runtime_benchmark_seeds": "examples/proxy_incident_replay_scenarios.json",
    "real_incidents": "examples/real_public_incident_replay_scenarios.json",
    "fake_customer": "examples/fake_customer_acme/production_like_scenarios.json",
    "timing": "examples/timing/github_actions_timing_evidence.json",
}


def build_competitive_proof_parity_report(*, root: str | Path = ".") -> Dict[str, Any]:
    root_path = Path(root)
    tool_catalog = _tool_catalog_section(_load_json(root_path / DEFAULT_PATHS["mcp_tool_definitions"]))
    runtime_decisions = _runtime_decision_section(
        _load_json(root_path / DEFAULT_PATHS["mcp_delete_call"]),
        _load_json(root_path / DEFAULT_PATHS["mcp_search_call"]),
    )
    proxy = _proxy_section(
        _load_json(root_path / DEFAULT_PATHS["mcp_delete_call"]),
        _load_json(root_path / DEFAULT_PATHS["mcp_search_call"]),
        _load_json(root_path / DEFAULT_PATHS["mcp_transport_delete"]),
    )
    benchmark = build_runtime_benchmark(root_path / DEFAULT_PATHS["runtime_benchmark_seeds"])
    real_incident_report = build_real_incident_report(
        evaluate_real_incidents(load_real_incidents(root_path / DEFAULT_PATHS["real_incidents"]))
    )
    fake_customer = run_fake_customer_pilot(_load_json(root_path / DEFAULT_PATHS["fake_customer"]))
    timing = build_timing_report(_load_json(root_path / DEFAULT_PATHS["timing"]))
    sections = {
        "catalog_evidence": tool_catalog,
        "runtime_decision_evidence": runtime_decisions,
        "proxy_enforcement_evidence": proxy,
        "benchmark_evidence": _benchmark_section(benchmark),
        "public_incident_replay_evidence": _real_incident_section(real_incident_report),
        "production_like_simulation_evidence": _fake_customer_section(fake_customer),
        "operational_evidence": _timing_section(timing),
    }
    summary = _summary(sections)
    report = {
        "version": COMPETITIVE_PROOF_PARITY_VERSION,
        "generated_at": _now(),
        "purpose": (
            "Aggregate SMERC evidence across the same public proof categories commonly used by adjacent MCP gateway, "
            "AI gateway, policy-as-code, runtime governance, and agent security products."
        ),
        "summary": summary,
        "sections": sections,
        "proof_boundaries": {
            "supports": [
                "SMERC can generate evidence in the same categories adjacent products commonly use for review.",
                "SMERC can add recoverability-specific scores and controls to catalog, runtime, proxy, benchmark, incident-replay, simulation, and timing evidence.",
                "SMERC can preserve middle-state posture evidence instead of collapsing every decision into allow or deny.",
            ],
            "does_not_support": [
                "customer-validated incident reduction",
                "production certification",
                "superiority over a named competitor in that competitor's own environment",
                "customer willingness to pay",
                "threshold calibration for a specific enterprise",
                "use of competitor private telemetry or proprietary benchmark data",
            ],
        },
    }
    report["markdown_report"] = render_markdown(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    sections = report["sections"]
    lines = [
        "# SMERC Competitive Proof Parity Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        (
            "This report runs SMERC across the same proof categories commonly used by adjacent MCP gateway, AI gateway, "
            "policy-as-code, runtime governance, and agent security products."
        ),
        "",
        (
            "It shows proof-category parity and recoverability-specific decision evidence. It does not claim that SMERC "
            "is better than named competitors, production-certified, or customer-validated."
        ),
        "",
        "## Top Metrics",
        "",
        f"- Proof categories covered: `{summary['proof_categories_covered']}`",
        f"- Total records evaluated across sections: `{summary['total_records_evaluated']}`",
        f"- Aggregated posture counts: `{summary['aggregated_posture_counts']}`",
        f"- Average irreversible exposure across scored sections: `{summary['average_irreversible_exposure_score']}`",
        f"- Average reversible capacity across scored sections: `{summary['average_reversible_capacity_score']}`",
        f"- Runtime benchmark decision difference rate: `{sections['benchmark_evidence']['key_metrics']['decision_difference_rate']}`",
        f"- Real public incident replay difference rate: `{sections['public_incident_replay_evidence']['key_metrics']['decision_difference_rate']}`",
        f"- Fake-customer valid DLL chains: `{sections['production_like_simulation_evidence']['key_metrics']['valid_ledger_count']}`",
        f"- Timing operational status: `{sections['operational_evidence']['key_metrics']['operational_status']}`",
        "",
        "## Proof Category Table",
        "",
        "| Proof Category | Adjacent Products Usually Show | SMERC Evidence Produced | Source Boundary |",
        "|---|---|---|---|",
    ]
    for key, section in sections.items():
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(section["label"]),
                    _escape(section["competitor_pattern"]),
                    _escape(section["smerc_result"]),
                    _escape(section["source_boundary"]),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Section Summaries", ""])
    for section in sections.values():
        lines.extend(
            [
                f"### {section['label']}",
                "",
                f"- Records: `{section['record_count']}`",
                f"- Result: {section['smerc_result']}",
                f"- Boundary: {section['source_boundary']}",
                "",
            ]
        )
        for metric, value in section.get("key_metrics", {}).items():
            lines.append(f"- {metric}: `{value}`")
        lines.append("")
    lines.extend(
        [
            "## What This Supports",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["proof_boundaries"]["supports"])
    lines.extend(["", "## What This Does Not Support", ""])
    lines.extend(f"- {item}" for item in report["proof_boundaries"]["does_not_support"])
    lines.extend(
        [
            "",
            "## Recommended Next Step",
            "",
            (
                "Use this parity harness as the reusable evidence package for public review, then replace synthetic "
                "and analyst-assigned records with customer-approved metadata during a shadow-mode pilot."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).write_text(str(report["markdown_report"]) + "\n", encoding="utf-8")


def _tool_catalog_section(payload: Mapping[str, Any]) -> Dict[str, Any]:
    tools = payload.get("tools")
    if not isinstance(tools, Mapping) or not tools:
        raise ValueError("tool definition examples must contain a non-empty tools object")
    scans = [scan_mcp_tool_definition(tool) for tool in tools.values()]
    posture_counts = Counter(scan["likely_smerc_posture"] for scan in scans)
    missing_metadata = sum(len(scan["missing_metadata"]) for scan in scans)
    return {
        "label": "Catalog evidence",
        "competitor_pattern": "Tool inventory, risk annotations, missing metadata, and dangerous-tool review.",
        "smerc_result": (
            f"Scanned {len(scans)} MCP-style tool definitions and identified "
            f"{posture_counts.get('DENY', 0)} deny-class and {posture_counts.get('THROTTLE', 0)} throttle-class tools."
        ),
        "source_boundary": "Synthetic MCP-style tool definitions; no private MCP registry or customer tool catalog.",
        "record_count": len(scans),
        "posture_counts": dict(sorted(posture_counts.items())),
        "key_metrics": {
            "missing_metadata_items": missing_metadata,
            "high_impact_tool_count": sum("HIGH_IMPACT_TOOL_CLASS" in scan["reason_codes"] for scan in scans),
            "average_irreversible_exposure_score": _average(scan["irreversible_exposure_score"] for scan in scans),
            "average_reversible_capacity_score": _average(scan["reversible_capacity_score"] for scan in scans),
        },
        "records": scans,
    }


def _runtime_decision_section(delete_call: Mapping[str, Any], search_call: Mapping[str, Any]) -> Dict[str, Any]:
    records = [evaluate_mcp_tool_call(delete_call), evaluate_mcp_tool_call(search_call)]
    posture_counts = Counter(record["decision"]["posture"] for record in records)
    return {
        "label": "Runtime decision evidence",
        "competitor_pattern": "Pre-execution policy or governance decisions before a tool call runs.",
        "smerc_result": f"Evaluated {len(records)} MCP-style tool calls before execution with replayable posture and route evidence.",
        "source_boundary": "Metadata-only MCP tool-call examples; no live MCP server or production agent runtime.",
        "record_count": len(records),
        "posture_counts": dict(sorted(posture_counts.items())),
        "key_metrics": {
            "allow_count": posture_counts.get("ALLOW", 0),
            "deny_count": posture_counts.get("DENY", 0),
            "average_irreversible_exposure_score": _average(record["decision"]["scores"]["irreversible_exposure_score"] for record in records),
            "average_reversible_capacity_score": _average(record["decision"]["scores"]["reversible_capacity_score"] for record in records),
        },
        "records": records,
    }


def _proxy_section(delete_call: Mapping[str, Any], search_call: Mapping[str, Any], transport_delete: Mapping[str, Any]) -> Dict[str, Any]:
    records = [
        run_mcp_proxy(delete_call, mode="shadow"),
        run_mcp_proxy(delete_call, mode="enforce"),
        run_mcp_proxy(search_call, mode="enforce"),
        run_mcp_transport_proxy(transport_delete),
    ]
    proxy_actions = Counter(_proxy_action(record) for record in records)
    forwarded = sum(_forwarded(record) for record in records)
    valid_ledgers = sum(_valid_ledger(record) for record in records)
    return {
        "label": "Proxy/enforcement evidence",
        "competitor_pattern": "Gateway/proxy monitor mode, enforce mode, forwarding decisions, and audit trail.",
        "smerc_result": f"Ran {len(records)} proxy samples across shadow, enforce, and JSON-RPC-shaped transport behavior.",
        "source_boundary": "Local reference proxy samples; no network proxy, OAuth broker, sandbox, or native tool execution.",
        "record_count": len(records),
        "key_metrics": {
            "forwarded_count": forwarded,
            "blocked_or_held_count": len(records) - forwarded,
            "valid_ledger_count": valid_ledgers,
            "proxy_actions": dict(sorted(proxy_actions.items())),
        },
        "records": records,
    }


def _benchmark_section(payload: Mapping[str, Any]) -> Dict[str, Any]:
    summary = payload["summary"]
    return {
        "label": "Benchmark evidence",
        "competitor_pattern": "Scenario benchmark showing decision distribution and comparison to baseline policy.",
        "smerc_result": (
            f"Evaluated {summary['total_scenarios']} expanded proxy scenarios with a "
            f"{summary['decision_difference_rate']} difference rate from simple allow/deny."
        ),
        "source_boundary": summary["evidence_limit"],
        "record_count": summary["total_scenarios"],
        "posture_counts": summary["smerc_posture_counts"],
        "key_metrics": {
            "decision_difference_rate": summary["decision_difference_rate"],
            "constrained_instead_of_allowed_count": summary["constrained_instead_of_allowed_count"],
            "traditional_denies_with_non_deny_smerc_count": summary["traditional_denies_with_non_deny_smerc_count"],
            "average_irreversible_exposure_score": summary["average_irreversible_exposure_score"],
            "average_reversible_capacity_score": summary["average_reversible_capacity_score"],
        },
    }


def _real_incident_section(report: Mapping[str, Any]) -> Dict[str, Any]:
    summary = report["summary"]
    return {
        "label": "Public incident replay evidence",
        "competitor_pattern": "Incident-pattern replay or narrative evidence showing governance behavior on known failure modes.",
        "smerc_result": (
            f"Replayed {summary['total_scenarios']} public incident patterns from {summary['source_count']} sources "
            f"with a {summary['decision_difference_rate']} difference rate."
        ),
        "source_boundary": summary["evidence_limit"],
        "record_count": summary["total_scenarios"],
        "posture_counts": summary["smerc_posture_counts"],
        "key_metrics": {
            "source_count": summary["source_count"],
            "decision_difference_rate": summary["decision_difference_rate"],
            "average_irreversible_exposure_score": summary["average_irreversible_exposure_score"],
            "average_reversible_capacity_score": summary["average_reversible_capacity_score"],
        },
    }


def _fake_customer_section(package: Mapping[str, Any]) -> Dict[str, Any]:
    summary = package["summary"]
    return {
        "label": "Production-like simulation evidence",
        "competitor_pattern": "End-to-end demo path showing workflow decisions, routes, evidence records, and review artifacts.",
        "smerc_result": (
            f"Ran {summary['scenario_count']} fake-customer scenarios with {summary['valid_ledger_count']} valid DLL chains."
        ),
        "source_boundary": "Fake customer simulation; not customer proof or production certification.",
        "record_count": summary["scenario_count"],
        "posture_counts": summary["posture_counts"],
        "key_metrics": {
            "decision_difference_rate": summary["decision_difference_rate"],
            "valid_ledger_count": summary["valid_ledger_count"],
            "rollback_scenarios": summary["rollback_scenarios"],
            "route_state_counts": summary["route_state_counts"],
        },
    }


def _timing_section(report: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "label": "Operational evidence",
        "competitor_pattern": "Latency, overhead, unavailable-evaluation, cancellation, and rollback metrics.",
        "smerc_result": (
            f"Summarized {report['record_count']} timing records with operational status {report['operational_status']}."
        ),
        "source_boundary": report["source_evidence_boundary"],
        "record_count": report["record_count"],
        "posture_counts": report["posture_counts"],
        "key_metrics": {
            "operational_status": report["operational_status"],
            "decision_p95_ms": report["decision_latency"]["p95_ms"],
            "workflow_overhead_p95_ms": report["workflow_overhead"]["p95_ms"],
            "unavailable_evaluation_rate": report["resilience"]["unavailable_evaluation_rate"],
            "rollback_success_rate": report["resilience"]["rollback_success_rate"],
        },
    }


def _summary(sections: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    posture_counts: Counter[str] = Counter()
    exposure_values: list[float] = []
    capacity_values: list[float] = []
    for section in sections.values():
        posture_counts.update(section.get("posture_counts", {}))
        metrics = section.get("key_metrics", {})
        if "average_irreversible_exposure_score" in metrics:
            exposure_values.append(float(metrics["average_irreversible_exposure_score"]))
        if "average_reversible_capacity_score" in metrics:
            capacity_values.append(float(metrics["average_reversible_capacity_score"]))
    return {
        "proof_categories_covered": len(sections),
        "total_records_evaluated": sum(int(section["record_count"]) for section in sections.values()),
        "aggregated_posture_counts": dict(sorted(posture_counts.items())),
        "average_irreversible_exposure_score": _average(exposure_values),
        "average_reversible_capacity_score": _average(capacity_values),
        "source_boundary": (
            "Aggregates synthetic, public, analyst-assigned, and local reference evidence. It is not customer validation."
        ),
    }


def _proxy_action(record: Mapping[str, Any]) -> str:
    if "proxy_response" in record:
        return str(record["proxy_response"]["proxy_action"])
    return str(record["proxy_report"]["proxy_response"]["proxy_action"])


def _forwarded(record: Mapping[str, Any]) -> bool:
    if "proxy_response" in record:
        return bool(record["proxy_response"]["should_forward_tool_call"])
    return "result" in record["mcp_jsonrpc_response"]


def _valid_ledger(record: Mapping[str, Any]) -> bool:
    if "decision_lifecycle_ledger" in record:
        return bool(record["decision_lifecycle_ledger"]["verification"]["valid"])
    return bool(record["proxy_report"]["decision_lifecycle_ledger"]["verification"]["valid"])


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _average(values: Any) -> float | None:
    parsed = list(values)
    if not parsed:
        return None
    return round(sum(float(value) for value in parsed) / len(parsed), 3)


def _escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a competitive proof parity report for SMERC.")
    parser.add_argument("--json-output", default="reports/competitive_proof_parity_report.json")
    parser.add_argument("--markdown-output", default="reports/Competitive_Proof_Parity_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_competitive_proof_parity_report()
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

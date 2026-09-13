from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.public_benchmark_ingestion import (
    build_public_benchmark_ingestion_report,
    load_benchmark_examples,
    render_markdown as render_benchmark_markdown,
    write_outputs as write_benchmark_outputs,
)


VERSION = "smerc.public-fallback-adapter.v1"
SUPPORTED_SOURCE_PROFILES = {"agent_action_boundary_benchmark", "agentshield_bench"}


def load_fallback_examples(path: str | Path) -> list[Dict[str, Any]]:
    rows = load_benchmark_examples(path)
    for row in rows:
        profile = row.get("source_profile")
        if profile not in SUPPORTED_SOURCE_PROFILES:
            raise ValueError(f"{row['record_id']} source_profile must be one of {sorted(SUPPORTED_SOURCE_PROFILES)}")
        if not isinstance(row.get("metadata_origin"), str) or not row["metadata_origin"].strip():
            raise ValueError(f"{row['record_id']} metadata_origin must be a non-empty string")
    return rows


def build_fallback_adapter_report(rows: list[Mapping[str, Any]]) -> Dict[str, Any]:
    benchmark_report = build_public_benchmark_ingestion_report(rows)
    profiles = Counter(str(row["source_profile"]) for row in rows)
    origins = Counter(str(row["metadata_origin"]) for row in rows)
    return {
        "version": VERSION,
        "source_example_count": len(rows),
        "source_profile_counts": dict(sorted(profiles.items())),
        "metadata_origin_counts": dict(sorted(origins.items())),
        "benchmark_report": benchmark_report,
        "replacement_metadata_ask": (
            "Can you replace these six public-pattern rows with 5 to 25 metadata-only actions from one real workflow "
            "and label whether the SMERC posture is useful, too strict, too loose, irrelevant, or unclear?"
        ),
        "work_result_impact": {
            "work": "Adapt the two closest public-pattern source shapes into SMERC customer-evaluation metadata.",
            "result": (
                "Agent Action Boundary-style drift and AgentShield-style MCP/tool-call safety rows now produce "
                "SMERC postures, SPARTa routes, DLL evidence, and a replacement-metadata ask."
            ),
            "impact": (
                "SMERC can keep moving if outside reviewers stay quiet, while still making customer-owned metadata "
                "the next validation gate."
            ),
        },
        "evidence_boundary": (
            "This adapter uses public-pattern, benchmark-shaped metadata only. It is not an official benchmark score, "
            "customer validation, production evidence, endorsement, or permission to copy upstream raw prompts, secrets, "
            "canary values, traces, customer data, or proprietary rows."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    benchmark = report["benchmark_report"]
    lines = [
        "# Public Fallback Adapter Report",
        "",
        f"Version: `{report['version']}`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Source Profiles",
        "",
        f"- Source profile counts: `{report['source_profile_counts']}`",
        f"- Metadata origin counts: `{report['metadata_origin_counts']}`",
        "",
        "## SMERC Output",
        "",
        f"- Source examples: `{report['source_example_count']}`",
        f"- SMERC posture counts: `{benchmark['smerc_posture_counts']}`",
        f"- SPARTa route counts: `{benchmark['smerc_route_counts']}`",
        f"- Delta counts: `{benchmark['delta_counts']}`",
        f"- Valid DLL ledgers: `{benchmark['valid_dll_ledgers']}`",
        "",
        "## Replacement Metadata Ask",
        "",
        str(report["replacement_metadata_ask"]),
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Underlying Benchmark-Shaped Report",
        "",
        render_benchmark_markdown(benchmark),
    ]
    return "\n".join(lines)


def write_outputs(
    report: Mapping[str, Any],
    *,
    normalized_output: str | Path,
    json_output: str | Path,
    markdown_output: str | Path,
    customer_json_output: str | Path,
    customer_markdown_output: str | Path,
) -> None:
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")
    write_benchmark_outputs(
        report["benchmark_report"],
        normalized_output=normalized_output,
        json_output=Path(json_output).with_name("public_fallback_adapter_benchmark_report.json"),
        markdown_output=Path(markdown_output).with_name("Public_Fallback_Adapter_Benchmark_Report.md"),
        customer_json_output=customer_json_output,
        customer_markdown_output=customer_markdown_output,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SMERC's focused public fallback adapter.")
    parser.add_argument("path", nargs="?", default="examples/public_fallback_adapter_examples.json")
    parser.add_argument("--normalized-output", default="examples/public_fallback_adapter_normalized_customer_eval_actions.json")
    parser.add_argument("--json-output", default="reports/public_fallback_adapter_report.json")
    parser.add_argument("--markdown-output", default="reports/Public_Fallback_Adapter_Report.md")
    parser.add_argument("--customer-json-output", default="reports/public_fallback_adapter_customer_evaluation/customer_evaluation_report.json")
    parser.add_argument("--customer-markdown-output", default="reports/public_fallback_adapter_customer_evaluation/Customer_Evaluation_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_fallback_adapter_report(load_fallback_examples(args.path))
    write_outputs(
        report,
        normalized_output=args.normalized_output,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
        customer_json_output=args.customer_json_output,
        customer_markdown_output=args.customer_markdown_output,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

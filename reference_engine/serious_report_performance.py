from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping

from reference_engine.cloud_metadata_connector import build_connector_report, load_source_exports
from reference_engine.customer_evaluation import build_customer_evaluation, load_payload
from reference_engine.postcondition_evidence import (
    build_postcondition_report,
    load_json_object,
    load_observations,
)
from reference_engine.public_benchmark_ingestion import (
    build_public_benchmark_ingestion_report,
    load_benchmark_examples,
)


VERSION = "smerc.serious-report-performance.v1"


def build_performance_report(*, root: str | Path = ".", iterations: int = 5) -> Dict[str, Any]:
    if iterations < 1 or iterations > 50:
        raise ValueError("iterations must be between 1 and 50")
    base = Path(root)
    paths = {
        "customer_evaluation": base / "examples" / "customer_eval_actions.json",
        "cloud_metadata_connector": base / "examples" / "cloud_admin_source_exports.json",
        "public_benchmark_ingestion": base / "examples" / "public_benchmark_ingestion_examples.json",
        "postcondition_evidence_evaluation": base
        / "reports"
        / "public_benchmark_customer_evaluation"
        / "customer_evaluation_report.json",
        "postcondition_observations": base / "examples" / "postcondition_observations.json",
    }

    workloads = [
        {
            "workload_id": "customer_evaluation_general",
            "description": "General metadata-only customer evaluation.",
            "runner": lambda: build_customer_evaluation(load_payload(paths["customer_evaluation"])),
        },
        {
            "workload_id": "cloud_metadata_connector",
            "description": "Read-only cloud metadata connector plus customer evaluation.",
            "runner": lambda: build_connector_report(load_source_exports(paths["cloud_metadata_connector"])),
        },
        {
            "workload_id": "public_benchmark_ingestion",
            "description": "Public benchmark-shaped ingestion plus customer evaluation.",
            "runner": lambda: build_public_benchmark_ingestion_report(
                load_benchmark_examples(paths["public_benchmark_ingestion"])
            ),
        },
        {
            "workload_id": "postcondition_evidence",
            "description": "Postcondition comparison of SPARTa route controls and observation metadata.",
            "runner": lambda: build_postcondition_report(
                load_json_object(paths["postcondition_evidence_evaluation"]),
                load_observations(paths["postcondition_observations"]),
            ),
        },
    ]

    records = [_measure_workload(item["workload_id"], item["description"], item["runner"], iterations) for item in workloads]
    p95_values = [record["latency_ms"]["p95_ms"] for record in records]
    max_p95 = max(p95_values)
    status = "ready_for_local_review" if max_p95 < 250 else "measure_in_customer_environment"
    return {
        "version": VERSION,
        "generated_at": _now(),
        "iterations_per_workload": iterations,
        "workload_count": len(records),
        "status": status,
        "slowest_p95_ms": max_p95,
        "records": records,
        "work_result_impact": {
            "work": "Run serious SMERC proof paths repeatedly and summarize local execution latency.",
            "result": (
                f"Measured {len(records)} proof workloads across {iterations} iteration(s) each with "
                f"slowest p95 of {max_p95} ms."
            ),
            "impact": (
                "Reviewers can see whether proof generation is lightweight enough for local evaluation, while "
                "customer pilots still measure production p50, p95, workflow overhead, and reviewer impact."
            ),
        },
        "evidence_boundary": (
            "This is local reference performance evidence for report builders. It does not prove production "
            "latency, hosted API performance, customer workflow overhead, reviewer burden, throughput, SLA, "
            "or enforcement-path performance."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Serious Report Performance",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        f"Iterations per workload: `{report['iterations_per_workload']}`",
        f"Status: `{report['status']}`",
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
        "## Workloads",
        "",
        "| Workload | Runs | p50 ms | p95 ms | Max ms | Result facts |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in report["records"]:
        facts = ", ".join(f"{key}={value}" for key, value in item["result_facts"].items())
        lines.append(
            f"| `{item['workload_id']}` | {item['latency_ms']['sample_count']} | "
            f"{item['latency_ms']['p50_ms']} | {item['latency_ms']['p95_ms']} | "
            f"{item['latency_ms']['maximum_ms']} | {facts} |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Question",
            "",
            "Which proof path should be timed inside a customer workflow, and what p95 overhead would make the integration unacceptable?",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    json_output = Path(json_path)
    markdown_output = Path(markdown_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(report), encoding="utf-8")


def _measure_workload(
    workload_id: str,
    description: str,
    runner: Callable[[], Mapping[str, Any]],
    iterations: int,
) -> Dict[str, Any]:
    samples: list[float] = []
    last_result: Mapping[str, Any] | None = None
    for _ in range(iterations):
        started = time.perf_counter()
        last_result = runner()
        samples.append(round((time.perf_counter() - started) * 1000, 3))
    if last_result is None:
        raise RuntimeError("workload did not run")
    return {
        "workload_id": workload_id,
        "description": description,
        "latency_ms": _latency_summary(samples),
        "result_facts": _result_facts(last_result),
    }


def _result_facts(result: Mapping[str, Any]) -> Dict[str, Any]:
    if "customer_evaluation" in result:
        summary = result["customer_evaluation"]["summary"]
        return {
            "actions": summary["total_actions"],
            "valid_ledgers": summary["valid_ledgers"],
            "postures": summary["posture_counts"],
        }
    if "summary" in result:
        summary = result["summary"]
        return {
            "actions": summary["total_actions"],
            "valid_ledgers": summary["valid_ledgers"],
            "postures": summary["posture_counts"],
        }
    if "postcondition_status_counts" in result:
        return {
            "actions": result["evaluated_actions"],
            "observed": result["observed_actions"],
            "statuses": result["postcondition_status_counts"],
        }
    return {"version": result.get("version", "unknown")}


def _latency_summary(values: list[float]) -> Dict[str, Any]:
    return {
        "sample_count": len(values),
        "minimum_ms": min(values),
        "average_ms": round(statistics.fmean(values), 3),
        "p50_ms": _percentile(values, 50),
        "p95_ms": _percentile(values, 95),
        "maximum_ms": max(values),
    }


def _percentile(values: list[float], percentile: int) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percentile / 100
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return round(ordered[lower] * (1 - weight) + ordered[upper] * weight, 3)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure local latency for serious SMERC proof report builders.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--json-output", default="reports/serious_report_performance.json")
    parser.add_argument("--markdown-output", default="reports/Serious_Report_Performance.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_performance_report(root=args.root, iterations=args.iterations)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

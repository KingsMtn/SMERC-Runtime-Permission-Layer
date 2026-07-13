from __future__ import annotations

import argparse
import copy
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from reference_engine.proxy_evidence_benchmark import (
    POSTURES,
    RESTRAINT_POSTURES,
    evaluate_scenarios,
    load_scenarios,
)


RUNTIME_BENCHMARK_VERSION = "smerc.runtime-benchmark-suite.v1"

VARIANTS = [
    {
        "variant_id": "baseline",
        "description": "Original seed scenario.",
        "risk_delta": 0.0,
        "recovery_delta": 0.0,
        "evidence_delta": 0.0,
        "scope_delta": 0.0,
        "traditional_override": None,
    },
    {
        "variant_id": "better_evidence",
        "description": "Evidence quality and authorization support improve before execution.",
        "risk_delta": -0.04,
        "recovery_delta": 0.08,
        "evidence_delta": 0.12,
        "scope_delta": -0.03,
        "traditional_override": None,
    },
    {
        "variant_id": "wider_scope",
        "description": "The same action expands to a wider operational blast radius.",
        "risk_delta": 0.08,
        "recovery_delta": -0.04,
        "evidence_delta": -0.02,
        "scope_delta": 0.15,
        "traditional_override": None,
    },
    {
        "variant_id": "faster_rollback",
        "description": "Rollback latency improves and cancellation is more reliable.",
        "risk_delta": -0.02,
        "recovery_delta": 0.12,
        "evidence_delta": 0.02,
        "scope_delta": -0.02,
        "traditional_override": None,
    },
    {
        "variant_id": "weak_evidence",
        "description": "Evidence becomes incomplete or stale while the actor remains technically authorized.",
        "risk_delta": 0.07,
        "recovery_delta": -0.06,
        "evidence_delta": -0.18,
        "scope_delta": 0.05,
        "traditional_override": None,
    },
    {
        "variant_id": "traditional_deny",
        "description": "Traditional policy blocks the action based on static policy while SMERC still scores recoverability.",
        "risk_delta": 0.03,
        "recovery_delta": -0.02,
        "evidence_delta": -0.05,
        "scope_delta": 0.02,
        "traditional_override": "DENY",
    },
]


def clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def expand_scenarios(seed_scenarios: List[Dict[str, Any]], variants: Iterable[Mapping[str, Any]] = VARIANTS) -> List[Dict[str, Any]]:
    expanded: List[Dict[str, Any]] = []
    for seed in seed_scenarios:
        for variant in variants:
            scenario = copy.deepcopy(seed)
            action = scenario["action"]
            variant_id = str(variant["variant_id"])
            scenario["scenario_id"] = f"{seed['scenario_id']}::{variant_id}"
            scenario["incident_pattern"] = f"{seed['incident_pattern']} Variant: {variant['description']}"
            if variant.get("traditional_override") is not None:
                scenario["traditional_policy_outcome"] = str(variant["traditional_override"])
                scenario["traditional_policy_rationale"] = (
                    "Static policy blocks this variant before runtime recoverability is considered."
                )
            action["action_id"] = f"{action['action_id']}__{variant_id.upper()}"
            action["description"] = f"{action['description']} Variant: {variant['description']}"
            action["base_action_risk"] = clamp(action["base_action_risk"] + float(variant["risk_delta"]))
            action["reversibility"] = clamp(action["reversibility"] + float(variant["recovery_delta"]))
            action["containment_strength"] = clamp(action["containment_strength"] + float(variant["recovery_delta"]) / 2)
            action["rollback_latency"] = clamp(action["rollback_latency"] - float(variant["recovery_delta"]))
            action["evidence_validity"] = clamp(action["evidence_validity"] + float(variant["evidence_delta"]))
            action["authorization_confidence"] = clamp(action["authorization_confidence"] + float(variant["evidence_delta"]) / 2)
            action["impact_scope"] = clamp(action["impact_scope"] + float(variant["scope_delta"]))
            action["anomaly_pressure"] = clamp(action["anomaly_pressure"] + float(variant["risk_delta"]) / 2)
            action["cancel_reliability"] = clamp(action["cancel_reliability"] + float(variant["recovery_delta"]) / 2)
            action.setdefault("context", {})["benchmark_variant"] = variant_id
            expanded.append(scenario)
    return expanded


def decision_difference(record: Mapping[str, Any]) -> bool:
    traditional = record["traditional_policy_outcome"]
    posture = record["smerc_posture"]
    if traditional == "ALLOW" and posture == "ALLOW":
        return False
    if traditional == "DENY" and posture == "DENY":
        return False
    return True


def summarize_runtime_benchmark(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    if total == 0:
        raise ValueError("runtime benchmark requires at least one record")
    posture_counts = Counter(record["smerc_posture"] for record in records)
    traditional_counts = Counter(record["traditional_policy_outcome"] for record in records)
    differences = [record for record in records if decision_difference(record)]
    constrained_instead_of_allowed = [
        record
        for record in differences
        if record["traditional_policy_outcome"] == "ALLOW"
        and record["smerc_posture"] in RESTRAINT_POSTURES
    ]
    blocked_by_traditional_but_scored_by_smerc = [
        record
        for record in differences
        if record["traditional_policy_outcome"] == "DENY"
        and record["smerc_posture"] in {"ALLOW", *RESTRAINT_POSTURES}
    ]
    category_counts: Dict[str, Counter[str]] = defaultdict(Counter)
    exposure_by_category: Dict[str, list[float]] = defaultdict(list)
    for record in records:
        category_counts[record["category"]][record["smerc_posture"]] += 1
        exposure_by_category[record["category"]].append(record["irreversible_exposure_score"])
    return {
        "version": RUNTIME_BENCHMARK_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_type": "expanded_proxy_runtime_benchmark",
        "evidence_limit": "Deterministic scenario expansion from seed proxy scenarios; not production validation or customer incident evidence.",
        "total_scenarios": total,
        "traditional_policy_counts": {
            "ALLOW": traditional_counts.get("ALLOW", 0),
            "DENY": traditional_counts.get("DENY", 0),
        },
        "smerc_posture_counts": {posture: posture_counts.get(posture, 0) for posture in POSTURES},
        "decision_difference_count": len(differences),
        "decision_difference_rate": round(len(differences) / total, 3),
        "constrained_instead_of_allowed_count": len(constrained_instead_of_allowed),
        "constrained_instead_of_allowed_rate": round(len(constrained_instead_of_allowed) / total, 3),
        "traditional_denies_with_non_deny_smerc_count": len(blocked_by_traditional_but_scored_by_smerc),
        "average_irreversible_exposure_score": round(
            sum(record["irreversible_exposure_score"] for record in records) / total,
            3,
        ),
        "average_reversible_capacity_score": round(
            sum(record["reversible_capacity_score"] for record in records) / total,
            3,
        ),
        "category_posture_counts": {
            category: {posture: counts.get(posture, 0) for posture in POSTURES}
            for category, counts in sorted(category_counts.items())
        },
        "highest_irreversible_exposure_categories": sorted(
            [
                {
                    "category": category,
                    "average_irreversible_exposure": round(sum(values) / len(values), 3),
                    "scenario_count": len(values),
                }
                for category, values in exposure_by_category.items()
            ],
            key=lambda item: item["average_irreversible_exposure"],
            reverse=True,
        ),
    }


def build_runtime_benchmark(seed_path: str | Path) -> Dict[str, Any]:
    seed_scenarios = load_scenarios(Path(seed_path))
    scenarios = expand_scenarios(seed_scenarios)
    records = evaluate_scenarios(scenarios)
    summary = summarize_runtime_benchmark(records)
    return {
        "summary": summary,
        "variant_model": VARIANTS,
        "records": records,
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    records = payload["records"]
    lines = [
        "# SMERC Runtime Governance Benchmark Suite",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        (
            f"This benchmark evaluates `{summary['total_scenarios']}` deterministic proxy scenarios derived from "
            "seed AI-agent and automation action scenarios."
        ),
        "",
        (
            f"SMERC differs from a simple allow/deny baseline in `{summary['decision_difference_count']}` scenarios "
            f"for a difference rate of `{summary['decision_difference_rate']}`."
        ),
        "",
        "This is expanded proxy evidence. It is useful for product review, test coverage, and pilot design. It is not customer validation, production incident evidence, or proof of incident reduction.",
        "",
        "## Key Metrics",
        "",
        f"- Traditional `ALLOW`: `{summary['traditional_policy_counts']['ALLOW']}`",
        f"- Traditional `DENY`: `{summary['traditional_policy_counts']['DENY']}`",
        f"- SMERC posture counts: `{summary['smerc_posture_counts']}`",
        f"- Constrained instead of allowed: `{summary['constrained_instead_of_allowed_count']}`",
        f"- Traditional deny but SMERC non-deny: `{summary['traditional_denies_with_non_deny_smerc_count']}`",
        f"- Average irreversible exposure: `{summary['average_irreversible_exposure_score']}`",
        f"- Average reversible capacity: `{summary['average_reversible_capacity_score']}`",
        "",
        "## Highest Exposure Categories",
        "",
        "| Rank | Category | Average Exposure | Scenarios |",
        "| ---: | --- | ---: | ---: |",
    ]
    for index, item in enumerate(summary["highest_irreversible_exposure_categories"], start=1):
        lines.append(
            f"| {index} | {escape(item['category'])} | {item['average_irreversible_exposure']} | {item['scenario_count']} |"
        )
    lines.extend(["", "## Category Posture Counts", "", "| Category | ALLOW | THROTTLE | FREEZE | DENY | ESCALATE |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
    for category, counts in summary["category_posture_counts"].items():
        lines.append(
            f"| {escape(category)} | {counts['ALLOW']} | {counts['THROTTLE']} | {counts['FREEZE']} | {counts['DENY']} | {counts['ESCALATE']} |"
        )
    lines.extend(["", "## Demo-Ready Decision Differences", ""])
    examples = [record for record in records if decision_difference(record)]
    examples = sorted(examples, key=lambda item: item["irreversible_exposure_score"], reverse=True)[:10]
    for record in examples:
        lines.extend(
            [
                f"### {record['scenario_id']}",
                "",
                f"- Category: `{record['category']}`",
                f"- Traditional policy: `{record['traditional_policy_outcome']}`",
                f"- SMERC posture: `{record['smerc_posture']}`",
                f"- Irreversible exposure: `{record['irreversible_exposure_score']}`",
                f"- Reversible capacity: `{record['reversible_capacity_score']}`",
                f"- Controls: `{', '.join(record['controls'])}`",
                f"- Explanation: {record['recoverability_analysis']}",
                "",
            ]
        )
    lines.extend(
        [
            "## What This Supports",
            "",
            "- SMERC can be tested against broad action categories without relying on private customer data.",
            "- The product creates middle outcomes for actions that are authorized but operationally hard to recover.",
            "- The benchmark gives design partners concrete scenarios to accept, reject, or calibrate.",
            "",
            "## What This Does Not Prove",
            "",
            "- It does not prove customer demand.",
            "- It does not prove incident reduction.",
            "- It does not prove the thresholds are correct for a specific enterprise.",
            "- It does not replace shadow-mode pilots, reviewer labeling, or external security review.",
            "",
        ]
    )
    return "\n".join(lines)


def escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_outputs(payload: Mapping[str, Any], json_path: str | Path, markdown_path: str | Path) -> None:
    json_file = Path(json_path)
    markdown_file = Path(markdown_path)
    json_file.parent.mkdir(parents=True, exist_ok=True)
    markdown_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_file.write_text(render_markdown(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an expanded SMERC runtime governance benchmark suite.")
    parser.add_argument("seed_scenarios", help="Path to seed proxy scenario JSON.")
    parser.add_argument("--json-output", default="reports/runtime_governance_benchmark.json")
    parser.add_argument("--markdown-output", default="reports/Runtime_Governance_Benchmark.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = build_runtime_benchmark(args.seed_scenarios)
    write_outputs(payload, args.json_output, args.markdown_output)
    print(json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

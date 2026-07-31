from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


VERSION = "smerc.governance-pattern-atlas.v1"

DEFAULT_BENCHMARKS = [
    {
        "discipline": "AML-inspired financial governance",
        "report_path": "reports/aml_inspired_financial_governance_benchmark.json",
        "doc_path": "docs/SMERC_F_AML_Inspired_Spur.md",
        "benchmark_report_path": "reports/AML_Inspired_Financial_Governance_Benchmark.md",
        "scenario_count_key": "scenario_count",
        "delta_count_key": "recoverability_delta_count",
        "delta_rate_key": "recoverability_delta_rate",
        "posture_counts_key": "smerc_f_state_counts",
        "delta_focus": "Where suspiciousness and recoverability produce different financial-action guidance.",
        "smerc_adds": "Pre-execution recoverability scoring for financial actions without claiming AML compliance.",
        "does_not_replace": "AML, sanctions screening, KYC, suspicious-activity reporting, custody, settlement, or payment execution.",
    },
    {
        "discipline": "Change-management-inspired production governance",
        "report_path": "reports/change_management_governance_benchmark.json",
        "doc_path": "docs/Change_Management_Inspired_Governance.md",
        "benchmark_report_path": "reports/Change_Management_Governance_Benchmark.md",
        "scenario_count_key": "scenario_count",
        "delta_count_key": "recoverability_delta_count",
        "delta_rate_key": "recoverability_delta_rate",
        "posture_counts_key": "smerc_posture_counts",
        "delta_focus": "Where approved changes still deserve runtime restraint or rejected changes have bounded paths.",
        "smerc_adds": "Runtime recoverability scoring after ticket approval but before automation executes.",
        "does_not_replace": "ITIL, ServiceNow, Jira, CABs, production approval, compliance attestation, or change-management software.",
    },
    {
        "discipline": "Security-response-inspired automation governance",
        "report_path": "reports/security_response_governance_benchmark.json",
        "doc_path": "docs/Security_Response_Inspired_Governance.md",
        "benchmark_report_path": "reports/Security_Response_Governance_Benchmark.md",
        "scenario_count_key": "scenario_count",
        "delta_count_key": "recoverability_delta_count",
        "delta_rate_key": "recoverability_delta_rate",
        "posture_counts_key": "smerc_posture_counts",
        "delta_focus": "Where automated response playbooks should be constrained because the response itself may cause harm.",
        "smerc_adds": "Recoverability checkpoint before security automation isolates, disables, deletes, notifies, or alters controls.",
        "does_not_replace": "SOAR, SIEM, EDR, threat intelligence, malware classification, or incident-response services.",
    },
    {
        "discipline": "Model-risk-inspired AI governance",
        "report_path": "reports/model_risk_governance_benchmark.json",
        "doc_path": "docs/Model_Risk_Inspired_Governance.md",
        "benchmark_report_path": "reports/Model_Risk_Governance_Benchmark.md",
        "scenario_count_key": "scenario_count",
        "delta_count_key": "runtime_delta_count",
        "delta_rate_key": "runtime_delta_rate",
        "posture_counts_key": "smerc_posture_counts",
        "delta_focus": "Where model approval status and runtime action permission diverge.",
        "smerc_adds": "Execution-time permission boundary between approved models, agents, tools, data, and real-world actions.",
        "does_not_replace": "Model validation, model approval, SR 11-7 programs, model monitoring, bias testing, or AI governance systems of record.",
    },
    {
        "discipline": "SRE/incident-management-inspired reliability governance",
        "report_path": "reports/sre_incident_governance_benchmark.json",
        "doc_path": "docs/SRE_Incident_Inspired_Governance.md",
        "benchmark_report_path": "reports/SRE_Incident_Governance_Benchmark.md",
        "scenario_count_key": "scenario_count",
        "delta_count_key": "recoverability_delta_count",
        "delta_rate_key": "recoverability_delta_rate",
        "posture_counts_key": "smerc_posture_counts",
        "delta_focus": "Where urgent mitigation should still be constrained because recovery capacity is weak.",
        "smerc_adds": "Runtime recoverability checkpoint before reliability automation changes production state.",
        "does_not_replace": "Observability, incident management, SLO tooling, pager routing, incident command, or post-incident review.",
    },
]


def _load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def _number(payload: Mapping[str, Any], key: str) -> int | float:
    value = payload.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"benchmark report field {key} must be numeric")
    return value


def _mapping(payload: Mapping[str, Any], key: str) -> Dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise TypeError(f"benchmark report field {key} must be an object")
    return dict(value)


def _records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    value = payload.get("records")
    if not isinstance(value, list) or not value:
        raise TypeError("benchmark report records must be a non-empty list")
    if not all(isinstance(item, dict) for item in value):
        raise TypeError("benchmark report records must contain objects")
    return value


def _strongest_record(records: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    def exposure(record: Mapping[str, Any]) -> float:
        for key in ("irreversible_exposure_score", "irreversible_exposure"):
            value = record.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
        return 0.0

    record = max(records, key=exposure)
    return {
        "scenario_id": record.get("scenario_id"),
        "category": record.get("category"),
        "smerc_posture": record.get("smerc_posture", record.get("smerc_f_state")),
        "delta_type": record.get("delta_type"),
        "irreversible_exposure_score": round(exposure(record), 3),
        "reversible_capacity_score": record.get("reversible_capacity_score", record.get("reversible_capacity")),
        "interpretation": record.get("interpretation"),
    }


def build_atlas(benchmark_specs: list[Mapping[str, Any]] | None = None) -> Dict[str, Any]:
    specs = benchmark_specs or DEFAULT_BENCHMARKS
    patterns: list[Dict[str, Any]] = []
    total_scenarios = 0
    total_deltas = 0
    weighted_delta = 0.0
    for spec in specs:
        report = _load_json(str(spec["report_path"]))
        scenario_count = int(_number(report, str(spec["scenario_count_key"])))
        delta_count = int(_number(report, str(spec["delta_count_key"])))
        delta_rate = float(_number(report, str(spec["delta_rate_key"])))
        total_scenarios += scenario_count
        total_deltas += delta_count
        weighted_delta += delta_rate * scenario_count
        patterns.append(
            {
                "discipline": spec["discipline"],
                "scenario_count": scenario_count,
                "delta_count": delta_count,
                "delta_rate": round(delta_rate, 3),
                "posture_counts": _mapping(report, str(spec["posture_counts_key"])),
                "delta_focus": spec["delta_focus"],
                "smerc_adds": spec["smerc_adds"],
                "does_not_replace": spec["does_not_replace"],
                "doc_path": spec["doc_path"],
                "benchmark_report_path": spec["benchmark_report_path"],
                "strongest_example": _strongest_record(_records(report)),
                "evidence_boundary": report.get("evidence_boundary"),
            }
        )
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "pattern_count": len(patterns),
        "total_scenarios": total_scenarios,
        "total_delta_count": total_deltas,
        "weighted_delta_rate": round(weighted_delta / total_scenarios, 3),
        "primary_wedge": "GitHub Actions and AI-assisted software delivery shadow-mode pilot",
        "core_claim": (
            "SMERC is runtime permission infrastructure that scores whether automated actions are recoverable "
            "enough to execute before they create real side effects."
        ),
        "credibility_partner_goal": (
            "Find a security, platform, reliability, or AI-governance team willing to review the evidence package "
            "and test SMERC in shadow mode against their own metadata-only workflow examples."
        ),
        "evidence_boundary": (
            "Unified synthetic/proxy benchmark summary only. It is not customer validation, product-market fit, "
            "production certification, compliance attestation, incident-reduction proof, or proof that any buyer "
            "will purchase SMERC."
        ),
        "patterns": patterns,
    }


def render_markdown(atlas: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Governance Pattern Atlas",
        "",
        f"Generated at: `{atlas['generated_at']}`",
        "",
        "## Purpose",
        "",
        "This atlas consolidates the enterprise operating models SMERC has been tested against in the repository.",
        "",
        "The point is not to claim SMERC replaces those systems. The point is to show a coherent product pattern: established governance disciplines all leave a gap at the moment an automated action is about to execute.",
        "",
        "## Core Claim",
        "",
        str(atlas["core_claim"]),
        "",
        "## Evidence Boundary",
        "",
        str(atlas["evidence_boundary"]),
        "",
        "## Unified Benchmark Summary",
        "",
        f"- Pattern count: `{atlas['pattern_count']}`",
        f"- Total scenarios: `{atlas['total_scenarios']}`",
        f"- Total deltas: `{atlas['total_delta_count']}`",
        f"- Weighted delta rate: `{atlas['weighted_delta_rate']}`",
        f"- Primary wedge: `{atlas['primary_wedge']}`",
        "",
        "| Discipline | Scenarios | Deltas | Delta Rate | What SMERC Adds | Does Not Replace |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for pattern in atlas["patterns"]:
        lines.append(
            f"| {pattern['discipline']} | {pattern['scenario_count']} | {pattern['delta_count']} | "
            f"{pattern['delta_rate']} | {pattern['smerc_adds']} | {pattern['does_not_replace']} |"
        )
    lines.extend(["", "## Strongest Examples", ""])
    for pattern in atlas["patterns"]:
        example = pattern["strongest_example"]
        lines.extend(
            [
                f"### {pattern['discipline']}",
                "",
                f"- Benchmark: `{pattern['benchmark_report_path']}`",
                f"- Scenario: `{example['scenario_id']}`",
                f"- Category: `{example['category']}`",
                f"- SMERC posture: `{example['smerc_posture']}`",
                f"- Delta type: `{example['delta_type']}`",
                f"- Irreversible exposure: `{example['irreversible_exposure_score']}`",
                f"- Reversible capacity: `{example['reversible_capacity_score']}`",
                f"- Interpretation: {example['interpretation']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Why This Makes SMERC One System",
            "",
            "Across AML, change management, security response, model risk, and SRE, the recurring enterprise question is not whether a tool can detect risk or open a ticket. The recurring gap is whether a specific automated action should proceed at the moment of execution.",
            "",
            "SMERC's common mechanism is recoverability-weighted authorization: irreversible exposure, reversible capacity, confidence, operational stress, reason codes, controls, and replay evidence.",
            "",
            "## Credibility Partner Readiness",
            "",
            str(atlas["credibility_partner_goal"]),
            "",
            "A credibility partner should be asked to challenge three things:",
            "",
            "- whether the scenarios resemble real workflow actions",
            "- whether the SMERC deltas are useful or noisy",
            "- whether shadow-mode scoring would be worth testing against their own metadata-only examples",
            "",
            "## Next Action",
            "",
            "Use this atlas as the front-door evidence artifact before asking for a design-partner or credibility-partner review.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(atlas: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(atlas), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC governance pattern atlas from benchmark reports.")
    parser.add_argument("--json-output", default="reports/governance_pattern_atlas.json")
    parser.add_argument("--markdown-output", default="reports/Governance_Pattern_Atlas.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    atlas = build_atlas()
    write_outputs(atlas, args.json_output, args.markdown_output)
    print(json.dumps(atlas, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

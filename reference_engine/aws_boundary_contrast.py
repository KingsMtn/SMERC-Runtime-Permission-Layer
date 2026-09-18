from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.aws_metadata_adapter import build_adapter_report, load_source_exports, write_outputs as write_adapter_outputs


VERSION = "smerc.aws-boundary-contrast.v1"
SOURCE_RECORD_IDS = {
    "aws-open-agentcore-create-runtime-002",
    "aws-open-bedrock-invoke-004",
}
POSTURE_RANK = {"ALLOW": 0, "THROTTLE": 1, "FREEZE": 2, "ESCALATE": 3, "DENY": 4}


def build_boundary_pairs(rows: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    selected = [dict(row) for row in rows if row.get("record_id") in SOURCE_RECORD_IDS]
    if {row["record_id"] for row in selected} != SOURCE_RECORD_IDS:
        raise ValueError("external AWS corpus is missing a required boundary-contrast source record")

    pairs: list[Dict[str, Any]] = []
    for source in selected:
        for variant in ("bounded", "broad"):
            row = copy.deepcopy(source)
            row["record_id"] = f"{source['record_id']}-{variant}"
            row["workflow_family"] = f"{source['workflow_family']}_boundary_contrast"
            row["label_basis"] = (
                f"{source['label_basis']} Boundary fields are a SMERC test fixture, not an observed AWS deployment."
            )
            if variant == "bounded":
                row.update(
                    {
                        "tooling_isolation": "restricted_tools",
                        "host_isolation": "hardened_container",
                        "network_isolation": "scoped_private_network",
                        "sandbox_escape_surface": ["none_known"],
                        "execution_environment_boundary": "cloud_function",
                    }
                )
            else:
                row.update(
                    {
                        "tooling_isolation": "privileged_automation",
                        "host_isolation": "process",
                        "network_isolation": "production_network",
                        "sandbox_escape_surface": ["cloud_metadata_access", "production_credentials"],
                        "execution_environment_boundary": "production_host",
                    }
                )
            pairs.append(row)
    return pairs


def build_contrast_report(adapter_report: Mapping[str, Any]) -> Dict[str, Any]:
    evaluation = adapter_report["customer_evaluation"]
    records = evaluation["records"]
    by_source_id = {
        record["sparta_route"]["tool_plan"]["metadata"]["source_record_id"]: record for record in records
    }
    comparisons = []
    for source_id in sorted(SOURCE_RECORD_IDS):
        bounded = by_source_id[f"{source_id}-bounded"]
        broad = by_source_id[f"{source_id}-broad"]
        bounded_posture = bounded["decision"]["posture"]
        broad_posture = broad["decision"]["posture"]
        comparisons.append(
            {
                "source_record_id": source_id,
                "bounded_posture": bounded_posture,
                "broad_posture": broad_posture,
                "broad_is_stricter": POSTURE_RANK[broad_posture] > POSTURE_RANK[bounded_posture],
                "bounded_reason_codes": bounded["decision"]["reason_codes"],
                "broad_reason_codes": broad["decision"]["reason_codes"],
                "bounded_route": bounded["sparta_route"]["route_state"],
                "broad_route": broad["sparta_route"]["route_state"],
            }
        )
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_record_count": len(SOURCE_RECORD_IDS),
        "variant_count": len(records),
        "posture_counts": dict(sorted(Counter(record["decision"]["posture"] for record in records).items())),
        "all_broad_variants_stricter": all(item["broad_is_stricter"] for item in comparisons),
        "comparisons": comparisons,
        "evidence_boundary": (
            "Boundary variants are controlled SMERC fixtures derived from public AWS action descriptions. "
            "They are not observed AWS configurations, customer outcomes, or proof of deployed enforcement."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# AWS Execution-Boundary Contrast Report",
        "",
        f"- Source action families: **{report['source_record_count']}**",
        f"- Evaluated variants: **{report['variant_count']}**",
        f"- Postures: `{report['posture_counts']}`",
        f"- Every broad variant stricter: **{str(report['all_broad_variants_stricter']).lower()}**",
        "",
        "## Comparisons",
        "",
    ]
    for item in report["comparisons"]:
        lines.extend(
            [
                f"### {item['source_record_id']}",
                "",
                f"- Bounded: `{item['bounded_posture']}` / `{item['bounded_route']}`",
                f"- Broad: `{item['broad_posture']}` / `{item['broad_route']}`",
                f"- Broad is stricter: **{str(item['broad_is_stricter']).lower()}**",
                f"- Bounded reasons: `{item['bounded_reason_codes']}`",
                f"- Broad reasons: `{item['broad_reason_codes']}`",
                "",
            ]
        )
    lines.extend(["## Evidence Boundary", "", report["evidence_boundary"], ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare bounded and broad execution environments for AWS actions")
    parser.add_argument("source", nargs="?", default="examples/aws_open_source_validation_corpus.json")
    parser.add_argument("--output-dir", default="reports/aws_boundary_contrast")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = build_boundary_pairs(load_source_exports(args.source))
    source_path = output_dir / "boundary_contrast_source_rows.json"
    source_path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    adapter_report = build_adapter_report(rows)
    write_adapter_outputs(
        adapter_report,
        normalized_output=output_dir / "normalized_customer_actions.json",
        json_output=output_dir / "aws_metadata_adapter_report.json",
        markdown_output=output_dir / "AWS_Metadata_Adapter_Report.md",
        customer_json_output=output_dir / "customer_evaluation_report.json",
        customer_markdown_output=output_dir / "Customer_Evaluation_Report.md",
    )
    contrast = build_contrast_report(adapter_report)
    (output_dir / "aws_boundary_contrast_report.json").write_text(
        json.dumps(contrast, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "AWS_Boundary_Contrast_Report.md").write_text(render_markdown(contrast), encoding="utf-8")
    print(json.dumps(contrast, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

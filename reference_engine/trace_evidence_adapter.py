from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.postcondition_evidence import build_postcondition_report, load_json_object, render_markdown


VERSION = "smerc.trace-evidence-adapter.v0"
PROHIBITED_FIELDS = {
    "raw_attestation",
    "attestation_document",
    "quote",
    "private_key",
    "secret",
    "credential",
    "token",
    "raw_log",
    "payload",
}

EVIDENCE_BOUNDARY = (
    "This is a metadata-only TRACE-style adapter stub. It does not implement TRACE, verify hardware attestation, "
    "validate TPM/TEE quotes, inspect raw attestations, process secrets, connect to a runtime, prove Linux Foundation "
    "endorsement, prove TRACE compatibility, or establish production integrity."
)


def load_trace_evidence(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("TRACE-style evidence input must be a non-empty JSON array")
    return [dict(item) for item in payload]


def build_trace_adapter_report(
    evaluation: Mapping[str, Any],
    trace_rows: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    accepted = []
    skipped = []
    observation_rows = []
    attestation_classes: Counter[str] = Counter()
    evidence_depths: Counter[str] = Counter()

    for index, row in enumerate(trace_rows):
        row_id = str(row.get("evidence_id") or f"trace-row-{index + 1}")
        unsafe = _unsafe_fields(row)
        if unsafe:
            skipped.append({"evidence_id": row_id, "reason": f"prohibited field present: {unsafe[0]}"})
            continue

        normalized = _normalize_trace_row(row, index)
        accepted.append(normalized)
        observation_rows.append(_to_postcondition_observation(normalized))
        attestation_classes[str(normalized["attestation_class"])] += 1
        evidence_depths[str(normalized["evidence_depth"])] += 1

    postcondition = build_postcondition_report(evaluation, observation_rows) if observation_rows else None
    status = "ready_for_trace_style_review" if accepted else "no_accepted_trace_style_evidence"
    if skipped:
        status = "limited_trace_style_review"

    return {
        "version": VERSION,
        "generated_at": _now(),
        "status": status,
        "source_evaluation_version": str(evaluation.get("version", "unknown")),
        "source_organization": str(evaluation.get("organization", "unknown")),
        "source_row_count": len(list(accepted)) + len(list(skipped)),
        "accepted_rows": len(accepted),
        "skipped_rows": len(skipped),
        "attestation_class_counts": dict(sorted(attestation_classes.items())),
        "evidence_depth_counts": dict(sorted(evidence_depths.items())),
        "normalized_observations": observation_rows,
        "postcondition_report": postcondition,
        "skipped": skipped,
        "evidence_boundary": EVIDENCE_BOUNDARY,
        "work_result_impact": {
            "work": "Normalize TRACE-style runtime evidence metadata into SMERC postcondition observations.",
            "result": (
                f"Accepted {len(accepted)} metadata-only rows, skipped {len(skipped)} unsafe rows, and "
                f"produced {len(observation_rows)} postcondition observation rows."
            ),
            "impact": (
                "SMERC can show how attested-runtime-shaped evidence could strengthen postcondition checks "
                "without claiming live TRACE compatibility or hardware attestation verification."
            ),
        },
    }


def render_trace_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# TRACE-Style Evidence Adapter Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        f"Status: `{report['status']}`",
        "",
        "## Purpose",
        "",
        "This report shows how metadata-only runtime evidence shaped like future TRACE-style attestations can be normalized into SMERC postcondition evidence.",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Summary",
        "",
        f"- Accepted rows: `{report['accepted_rows']}`",
        f"- Skipped rows: `{report['skipped_rows']}`",
        f"- Attestation class counts: `{report['attestation_class_counts']}`",
        f"- Evidence depth counts: `{report['evidence_depth_counts']}`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
    ]
    if report.get("postcondition_report"):
        post = report["postcondition_report"]
        lines.extend(
            [
                "## Postcondition Summary",
                "",
                f"- Evaluated actions: `{post['evaluated_actions']}`",
                f"- Observed actions: `{post['observed_actions']}`",
                f"- Postcondition status counts: `{post['postcondition_status_counts']}`",
                f"- Route control evidence: `{post['route_control_evidence']}`",
                "",
            ]
        )
    if report.get("skipped"):
        lines.extend(["## Skipped Rows", "", "| Evidence ID | Reason |", "| --- | --- |"])
        for item in report["skipped"]:
            lines.append(f"| `{item['evidence_id']}` | `{item['reason']}` |")
        lines.append("")
    lines.extend(
        [
            "## Reviewer Question",
            "",
            "Could a real runtime or attestation service produce signed metadata for these controls without exposing raw attestations, secrets, raw logs, or customer data?",
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
    markdown_output.write_text(render_trace_markdown(report), encoding="utf-8")
    if report.get("postcondition_report"):
        (markdown_output.parent / "TRACE_Style_Postcondition_Evidence.md").write_text(
            render_markdown(report["postcondition_report"]),
            encoding="utf-8",
        )


def _normalize_trace_row(row: Mapping[str, Any], index: int) -> Dict[str, Any]:
    evidence = row.get("evidence")
    if not isinstance(evidence, dict):
        raise TypeError(f"trace_rows[{index}].evidence must be an object")
    controls = row.get("controls")
    if not isinstance(controls, list) or not controls:
        raise TypeError(f"trace_rows[{index}].controls must be a non-empty list")
    execution = row.get("execution")
    if not isinstance(execution, dict):
        raise TypeError(f"trace_rows[{index}].execution must be an object")
    return {
        "evidence_id": _text(row.get("evidence_id"), f"trace_rows[{index}].evidence_id"),
        "action_id": _text(row.get("action_id"), f"trace_rows[{index}].action_id"),
        "attestation_class": _text(evidence.get("attestation_class"), f"trace_rows[{index}].evidence.attestation_class"),
        "evidence_depth": _text(evidence.get("evidence_depth"), f"trace_rows[{index}].evidence.evidence_depth"),
        "runtime_context": {
            "runtime_class": _text(evidence.get("runtime_class"), f"trace_rows[{index}].evidence.runtime_class"),
            "workload_class": _text(evidence.get("workload_class"), f"trace_rows[{index}].evidence.workload_class"),
            "policy_context_ref": _text(evidence.get("policy_context_ref"), f"trace_rows[{index}].evidence.policy_context_ref"),
        },
        "controls": [_normalize_control(control, index, control_index) for control_index, control in enumerate(controls)],
        "execution": {
            "attempted": _boolean(execution.get("attempted"), f"trace_rows[{index}].execution.attempted"),
            "status": _text(execution.get("status"), f"trace_rows[{index}].execution.status"),
            "rollback_performed": _boolean(
                execution.get("rollback_performed"),
                f"trace_rows[{index}].execution.rollback_performed",
            ),
            "rollback_success": execution.get("rollback_success"),
            "notes": _text(execution.get("notes"), f"trace_rows[{index}].execution.notes", 320),
        },
    }


def _normalize_control(control: Mapping[str, Any], row_index: int, control_index: int) -> Dict[str, Any]:
    if not isinstance(control, dict):
        raise TypeError(f"trace_rows[{row_index}].controls[{control_index}] must be an object")
    return {
        "control_id": _text(control.get("control_id"), f"trace_rows[{row_index}].controls[{control_index}].control_id"),
        "outcome": _text(control.get("outcome"), f"trace_rows[{row_index}].controls[{control_index}].outcome"),
        "mechanism": _text(control.get("mechanism"), f"trace_rows[{row_index}].controls[{control_index}].mechanism"),
        "evidence_ref": _text(control.get("evidence_ref"), f"trace_rows[{row_index}].controls[{control_index}].evidence_ref", 256),
        "observed_at": _text(control.get("observed_at"), f"trace_rows[{row_index}].controls[{control_index}].observed_at", 64),
    }


def _to_postcondition_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "action_id": row["action_id"],
        "observed_controls": [
            {
                "control_id": control["control_id"],
                "outcome": control["outcome"],
                "mechanism": control["mechanism"],
                "evidence_ref": control["evidence_ref"],
                "observed_at": control["observed_at"],
            }
            for control in row["controls"]
        ],
        "execution": dict(row["execution"]),
    }


def _unsafe_fields(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, Mapping):
        found = []
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in PROHIBITED_FIELDS:
                found.append(path)
            found.extend(_unsafe_fields(nested, path))
        return found
    if isinstance(value, list):
        found = []
        for index, nested in enumerate(value):
            found.extend(_unsafe_fields(nested, f"{prefix}[{index}]"))
        return found
    return []


def _text(value: Any, path: str, maximum: int = 160) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    clean = value.strip()
    if len(clean) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return clean


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize TRACE-style evidence metadata into SMERC postconditions.")
    parser.add_argument("--evaluation", default="reports/public_benchmark_customer_evaluation/customer_evaluation_report.json")
    parser.add_argument("--trace-evidence", default="examples/trace_runtime_evidence_examples.json")
    parser.add_argument("--json-output", default="reports/trace_evidence_adapter/trace_evidence_adapter_report.json")
    parser.add_argument("--markdown-output", default="reports/trace_evidence_adapter/TRACE_Evidence_Adapter_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_trace_adapter_report(
        load_json_object(args.evaluation),
        load_trace_evidence(args.trace_evidence),
    )
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

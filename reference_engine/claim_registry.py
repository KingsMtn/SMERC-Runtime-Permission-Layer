from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.claim-registry.v1"
STATUSES = {"supported", "partial", "not_supported"}

CLAIMS = [
    {
        "claim_id": "local_end_to_end_reviewer_flow_runs",
        "claim": "SMERC has a local end-to-end reviewer flow connecting metadata intake, schema validation, policy identity, posture output, and evidence reporting.",
        "status": "supported",
        "evidence": [
            "docs/End_To_End_Reviewer_Flow.md",
            "reports/End_To_End_Reviewer_Flow.md",
            "reference_engine/end_to_end_reviewer_flow.py",
            "tests/test_end_to_end_reviewer_flow.py",
        ],
        "boundary": "Local proof only; no live AWS, MCP server, customer data, or production execution.",
    },
    {
        "claim_id": "reject_first_metadata_intake_exists",
        "claim": "SMERC has a reject-first local intake path for preparing metadata-only action summaries.",
        "status": "supported",
        "evidence": [
            "docs/Local_Shadow_Intake.md",
            "reports/Local_Shadow_Intake_Report.md",
            "reference_engine/local_shadow_intake.py",
            "tests/test_local_shadow_intake.py",
        ],
        "boundary": "Reject-first intake is not guaranteed anonymization and still requires human review before sharing.",
    },
    {
        "claim_id": "public_pattern_fallback_adapter_runs",
        "claim": "SMERC can map public-pattern action-boundary and MCP/tool-call safety rows into customer-evaluation posture, route, and ledger evidence.",
        "status": "supported",
        "evidence": [
            "docs/Public_Fallback_Adapter.md",
            "reports/Public_Fallback_Adapter_Report.md",
            "reference_engine/public_fallback_adapter.py",
            "tests/test_public_fallback_adapter.py",
        ],
        "boundary": "This is adapter readiness on benchmark-shaped metadata, not an official benchmark score or customer validation.",
    },
    {
        "claim_id": "public_evidence_fallback_plan_exists",
        "claim": "SMERC has a fallback evidence plan if outside reviewers do not provide metadata.",
        "status": "supported",
        "evidence": [
            "docs/Public_Evidence_Fallback_Plan.md",
            "reports/Public_Evidence_Fallback_Plan.md",
            "reference_engine/public_evidence_fallback.py",
            "tests/test_public_evidence_fallback.py",
        ],
        "boundary": "Public-pattern evidence improves technical proof but is not customer validation.",
    },
    {
        "claim_id": "small_generated_stress_corpus_exists",
        "claim": "SMERC has a small generated metadata-only stress corpus that runs through the customer-evaluation path.",
        "status": "supported",
        "evidence": [
            "docs/Small_Generated_Stress_Corpus.md",
            "examples/smerc_stress_corpus_small.json",
            "reports/Small_Generated_Stress_Corpus_Report.md",
            "reports/small_generated_stress_corpus_report.json",
            "reference_engine/small_stress_corpus.py",
        ],
        "boundary": "Generated stress data is fallback technical evidence, not customer validation or production proof.",
    },
    {
        "claim_id": "recoverability_metadata_contract_exists",
        "claim": "SMERC defines a small recoverability metadata contract for individual action and tool-call hints.",
        "status": "supported",
        "evidence": [
            "docs/Recoverability_Metadata_Contract.md",
            "schemas/smerc-recoverability-metadata-v0.schema.json",
            "examples/recoverability_metadata_examples.json",
            "reference_engine/recoverability_metadata_contract.py",
            "reports/Recoverability_Metadata_Contract_Report.md",
        ],
        "boundary": "The contract supplies recoverability hints only; it is not authorization, production certification, or a replacement for runtime scoring.",
    },
    {
        "claim_id": "customer_owned_metadata_received",
        "claim": "SMERC has received enough customer-owned metadata to validate usefulness against a real workflow.",
        "status": "not_supported",
        "evidence": [
            "docs/External_Metadata_Reviewer_Request.md",
            ".github/ISSUE_TEMPLATE/workflow-intake-template.md",
        ],
        "boundary": "The repo has the ask and templates, but no sufficient customer-owned response is recorded here.",
    },
    {
        "claim_id": "production_aws_connector_ready",
        "claim": "SMERC is ready as a production AWS connector or AWS-endorsed deployed control.",
        "status": "not_supported",
        "evidence": [
            "docs/AWS_Deployable_Bot_Readiness_Path.md",
            "docs/AWS_Metadata_Intake_Contract.md",
            "docs/AWS_Reviewer_Bundle.md",
        ],
        "boundary": "AWS proof is metadata-only and local; no AWS endorsement, production certification, or live-account control is claimed.",
    },
    {
        "claim_id": "incident_reduction_proven",
        "claim": "SMERC is proven to reduce production incidents.",
        "status": "not_supported",
        "evidence": [
            "docs/SMERC_Premortem.md",
            "docs/Public_Evidence_Fallback_Plan.md",
        ],
        "boundary": "No production deployment or incident-reduction study is present.",
    },
]


def build_claim_registry(*, root: str | Path = ".") -> Dict[str, Any]:
    base = Path(root)
    records = []
    for claim in CLAIMS:
        status = claim["status"]
        if status not in STATUSES:
            raise ValueError(f"{claim['claim_id']} has invalid status {status}")
        records.append(
            {
                **claim,
                "evidence_status": _evidence_status(base, claim["evidence"]),
            }
        )
    counts = Counter(record["status"] for record in records)
    return {
        "version": VERSION,
        "generated_at": _now(),
        "claim_count": len(records),
        "status_counts": dict(sorted(counts.items())),
        "claims": records,
        "work_result_impact": {
            "work": "Separate supported SMERC claims from partial or unsupported claims.",
            "result": "Reviewers can inspect the exact evidence and boundary for each major public claim.",
            "impact": "SMERC can keep moving aggressively without overstating customer validation, AWS readiness, or incident-reduction proof.",
        },
        "evidence_boundary": "The registry is a claims-control artifact. It does not create validation by itself; it records what the repository evidence currently supports.",
    }


def render_markdown(registry: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Claim Registry",
        "",
        f"Generated: `{registry['generated_at']}`",
        f"Version: `{registry['version']}`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {registry['work_result_impact']['work']}",
        f"- Result: {registry['work_result_impact']['result']}",
        f"- Impact: {registry['work_result_impact']['impact']}",
        "",
        "## Status Counts",
        "",
        f"`{registry['status_counts']}`",
        "",
        "## Claims",
        "",
        "| Claim ID | Status | Evidence | Boundary |",
        "| --- | --- | --- | --- |",
    ]
    for claim in registry["claims"]:
        evidence = "<br>".join(f"`{item}`" for item in claim["evidence"])
        lines.append(
            f"| `{claim['claim_id']}` | `{claim['status']}` | {evidence} | {claim['boundary']} |"
        )
    lines.extend(["", "## Evidence Boundary", "", str(registry["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(
    registry: Mapping[str, Any],
    *,
    json_output: str | Path = "reports/claim_registry.json",
    markdown_output: str | Path = "reports/Claim_Registry.md",
) -> None:
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(registry), encoding="utf-8")


def _evidence_status(root: Path, paths: list[str]) -> Dict[str, Any]:
    existing = [path for path in paths if (root / path).exists()]
    missing = [path for path in paths if not (root / path).exists()]
    return {
        "existing_count": len(existing),
        "missing_count": len(missing),
        "missing": missing,
    }


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC claim registry.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json-output", default="reports/claim_registry.json")
    parser.add_argument("--markdown-output", default="reports/Claim_Registry.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    registry = build_claim_registry(root=args.root)
    write_outputs(registry, json_output=args.json_output, markdown_output=args.markdown_output)
    print(json.dumps(registry, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

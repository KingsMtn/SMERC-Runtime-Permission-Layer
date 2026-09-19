from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.aws_agent_action_chain import (
    build_report as build_chain_report,
    render_markdown as render_chain_markdown,
)
from reference_engine.aws_agent_action_chain_postcondition import (
    build_report as build_chain_postcondition_report,
    render_markdown as render_chain_postcondition_markdown,
)
from reference_engine.aws_decision_api_surface import (
    build_decision_api_surface,
    render_markdown as render_decision_api_surface_markdown,
)
from reference_engine.aws_metadata_adapter import (
    build_adapter_report,
    load_source_exports,
    render_markdown as render_aws_metadata_adapter_markdown,
)
from reference_engine.aws_postcondition_evidence import (
    build_aws_postcondition_report,
    load_aws_observations,
    load_json_object,
    render_markdown as render_aws_postcondition_markdown,
    verify_aws_observation_provenance,
)
from reference_engine.evidence_provenance import hmac_key_from_env
from reference_engine.aws_shadow_mirror_adapter import (
    build_adapter_report as build_shadow_mirror_report,
    load_source_exports as load_shadow_mirror_exports,
    render_markdown as render_shadow_mirror_markdown,
)
from reference_engine.customer_evaluation import load_payload
from reference_engine.customer_owned_metadata_request import (
    build_request_report,
    render_markdown as render_metadata_request_markdown,
)
from reference_engine.serious_report_performance import (
    build_performance_report,
    render_markdown as render_performance_markdown,
)


VERSION = "smerc.aws-reviewer-bundle.v1"


def build_aws_reviewer_bundle(
    *,
    root: str | Path = ".",
    requested_actions: int = 12,
    iterations: int = 5,
    customer_aws_source_exports: str | Path | None = None,
    customer_aws_observations: str | Path | None = None,
    customer_aws_provenance_ledger: str | Path | None = None,
    customer_aws_hmac_key: bytes | None = None,
    customer_aws_shadow_mirror_exports: str | Path | None = None,
) -> Dict[str, Any]:
    base = Path(root)
    chain_report = build_chain_report(load_payload(base / "examples/aws_agent_action_chain.json"))
    decision_api_surface = build_decision_api_surface(root=base)
    chain_postcondition = build_chain_postcondition_report(
        load_payload(base / "examples/aws_agent_action_chain.json"),
        base / "examples/aws_agent_action_chain_observations.json",
    )
    aws_postcondition = build_aws_postcondition_report(
        load_json_object(base / "reports/aws_metadata_adapter/customer_evaluation_report.json"),
        load_aws_observations(base / "examples/aws_postcondition_observations.json"),
    )
    shadow_mirror = build_shadow_mirror_report(
        load_shadow_mirror_exports(base / "examples/aws_shadow_mirror_source_exports.json")
    )
    performance = build_performance_report(root=base, iterations=iterations)
    metadata_request = build_request_report(workflow_family="aws", requested_actions=requested_actions)
    customer_metadata_review = None
    customer_postcondition = None
    customer_shadow_mirror_review = None
    if customer_aws_source_exports:
        customer_metadata_review = build_adapter_report(load_source_exports(_resolve_path(base, customer_aws_source_exports)))
        if customer_aws_observations:
            customer_observations = load_aws_observations(_resolve_path(base, customer_aws_observations))
            customer_provenance = None
            if customer_aws_provenance_ledger:
                customer_provenance = verify_aws_observation_provenance(
                    customer_observations,
                    load_json_object(_resolve_path(base, customer_aws_provenance_ledger)),
                    hmac_key=customer_aws_hmac_key,
                )
            customer_postcondition = build_aws_postcondition_report(
                customer_metadata_review["customer_evaluation"],
                customer_observations,
                provenance_verification=customer_provenance,
            )
    elif customer_aws_observations or customer_aws_provenance_ledger:
        raise ValueError("customer AWS observations and provenance require customer AWS source exports")
    if customer_aws_provenance_ledger and not customer_aws_observations:
        raise ValueError("customer AWS provenance ledger requires customer AWS observations")
    if customer_aws_hmac_key is not None and not customer_aws_provenance_ledger:
        raise ValueError("customer AWS HMAC key requires customer AWS provenance ledger")
    if customer_aws_shadow_mirror_exports:
        customer_shadow_mirror_review = build_shadow_mirror_report(
            load_shadow_mirror_exports(_resolve_path(base, customer_aws_shadow_mirror_exports))
        )
    readiness = _readiness(
        chain_postcondition=chain_postcondition,
        aws_postcondition=aws_postcondition,
        shadow_mirror=shadow_mirror,
        performance=performance,
        customer_metadata_review=customer_metadata_review,
        customer_postcondition=customer_postcondition,
        customer_shadow_mirror_review=customer_shadow_mirror_review,
    )
    return {
        "version": VERSION,
        "generated_at": _now(),
        "requested_action_count": requested_actions,
        "bundle_status": readiness["status"],
        "aws_reviewer_path": [
            "Bedrock-style guardrails check content and model behavior.",
            "IAM and change systems check identity, authority, session, and allowed path.",
            "SMERC checks recoverability, blast radius, rollback, cost velocity, fallback, and evidence before execution.",
            "Shadow mirror metadata can test operational flow behavior without packet payloads or live AWS access.",
            "Postcondition evidence checks whether the required route controls actually happened after the decision.",
        ],
        "work_result_impact": {
            "work": (
                "Assemble the AWS-style reviewer path into one local package: action-chain proof, decision API "
                "surface, route-control postcondition evidence, AWS postcondition evidence, shadow mirror metadata "
                "evidence, performance metrics, and customer-owned AWS metadata request."
            ),
            "result": (
                f"Generated an AWS reviewer bundle with {chain_report['scenario_count']} action-chain examples, "
                f"decision API status {decision_api_surface['status']}, "
                f"chain postcondition statuses {chain_postcondition['aws_postcondition_status_counts']}, "
                f"AWS postcondition statuses {aws_postcondition['aws_postcondition_status_counts']}, and slowest "
                f"local p95 {performance['slowest_p95_ms']} ms. The shadow mirror path accepted "
                f"{shadow_mirror['accepted_rows']} safe rows and skipped {shadow_mirror['skipped_rows']} unsafe rows."
            ),
            "impact": (
                "An AWS-style platform reviewer can inspect where SMERC fits, what it decides, what evidence would "
                "prove the route, and what safe customer-owned metadata is needed next without granting live AWS access."
            ),
        },
        "readiness": readiness,
        "reports": {
            "aws_agent_action_chain": chain_report,
            "aws_decision_api_surface": decision_api_surface,
            "aws_agent_action_chain_postcondition": chain_postcondition,
            "aws_postcondition_evidence": aws_postcondition,
            "aws_shadow_mirror": shadow_mirror,
            "performance": performance,
            "aws_customer_owned_metadata_request": metadata_request,
            "customer_aws_metadata_review": customer_metadata_review,
            "customer_aws_postcondition_evidence": customer_postcondition,
            "customer_aws_shadow_mirror_review": customer_shadow_mirror_review,
        },
        "evidence_boundary": (
            "This is a local, metadata-only AWS-style review package. It does not connect to AWS, invoke Amazon "
            "Bedrock, call IAM, run Systems Manager, apply CloudFormation, read CloudTrail or CloudWatch, modify "
            "infrastructure, configure VPC Traffic Mirroring, inspect packet payloads, process secrets, prove AWS "
            "endorsement, prove AWS certification, or establish production safety."
        ),
    }


def render_markdown(bundle: Mapping[str, Any]) -> str:
    readiness = bundle["readiness"]
    reports = bundle["reports"]
    lines = [
        "# AWS-Style Reviewer Bundle",
        "",
        f"Generated: `{bundle['generated_at']}`",
        f"Version: `{bundle['version']}`",
        f"Bundle status: `{bundle['bundle_status']}`",
        "",
        "## One-Line Reviewer Frame",
        "",
        "Guardrails check content. IAM checks authority. SMERC checks recoverability. Shadow mirror metadata tests operational behavior. Postcondition evidence checks whether the route happened.",
        "",
        "## AWS Reviewer Path",
        "",
    ]
    lines.extend(f"{index}. {item}" for index, item in enumerate(bundle["aws_reviewer_path"], start=1))
    lines.extend(
        [
            "",
            "## Work / Result / Impact",
            "",
            f"- Work: {bundle['work_result_impact']['work']}",
            f"- Result: {bundle['work_result_impact']['result']}",
            f"- Impact: {bundle['work_result_impact']['impact']}",
            "",
            "## Readiness",
            "",
            f"- Status: `{readiness['status']}`",
            f"- Slowest local p95 ms: `{readiness['slowest_p95_ms']}`",
            f"- Chain postcondition gaps: `{readiness['chain_postcondition_gaps']}`",
            f"- Chain postcondition violations: `{readiness['chain_postcondition_violations']}`",
            f"- AWS postcondition gaps: `{readiness['aws_postcondition_gaps']}`",
            f"- AWS postcondition violations: `{readiness['aws_postcondition_violations']}`",
            f"- Chain proof-eligible observations: `{readiness['chain_proof_eligible_actions']}`",
            f"- AWS proof-eligible observations: `{readiness['aws_proof_eligible_actions']}`",
            f"- Customer proof-eligible observations: `{readiness['customer_proof_eligible_actions']}`",
            "",
            "## Reviewer Takeaways",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in readiness["takeaways"])
    lines.extend(
        [
            "",
            "## Included Reports",
            "",
            "| Report | Main Result |",
            "| --- | --- |",
            (
                f"| AWS agent action chain | scenarios=`{reports['aws_agent_action_chain']['scenario_count']}`, "
                f"postures=`{reports['aws_agent_action_chain']['summary']['posture_counts']}` |"
            ),
            (
                f"| AWS decision API surface | status=`{reports['aws_decision_api_surface']['status']}`, "
                f"operation_id=`{reports['aws_decision_api_surface']['operation_id']}`, "
                f"posture=`{reports['aws_decision_api_surface']['posture']}` |"
            ),
            (
                f"| AWS chain postcondition evidence | statuses="
                f"`{reports['aws_agent_action_chain_postcondition']['aws_postcondition_status_counts']}`, "
                f"proof_eligible=`{reports['aws_agent_action_chain_postcondition']['proof_eligible_actions']}` |"
            ),
            (
                f"| AWS postcondition evidence | statuses="
                f"`{reports['aws_postcondition_evidence']['aws_postcondition_status_counts']}`, "
                f"proof_eligible=`{reports['aws_postcondition_evidence']['proof_eligible_actions']}` |"
            ),
            (
                f"| AWS shadow mirror metadata | accepted_rows=`{reports['aws_shadow_mirror']['accepted_rows']}`, "
                f"skipped_rows=`{reports['aws_shadow_mirror']['skipped_rows']}`, "
                f"postures=`{reports['aws_shadow_mirror']['customer_evaluation']['summary']['posture_counts']}` |"
            ),
            (
                f"| Performance | status=`{reports['performance']['status']}`, "
                f"slowest_p95_ms=`{reports['performance']['slowest_p95_ms']}` |"
            ),
            (
                f"| AWS customer-owned metadata request | requested_actions="
                f"`{reports['aws_customer_owned_metadata_request']['requested_action_count']}` |"
            ),
        ]
    )
    if reports.get("customer_aws_metadata_review"):
        customer = reports["customer_aws_metadata_review"]
        lines.append(
            f"| Customer AWS metadata review | accepted_rows=`{customer['accepted_rows']}`, "
            f"skipped_rows=`{customer['skipped_rows']}` |"
        )
    if reports.get("customer_aws_postcondition_evidence"):
        customer_postcondition = reports["customer_aws_postcondition_evidence"]
        lines.append(
            f"| Customer AWS postcondition evidence | statuses="
            f"`{customer_postcondition['aws_postcondition_status_counts']}`, "
            f"proof_eligible=`{customer_postcondition['proof_eligible_actions']}` |"
        )
    if reports.get("customer_aws_shadow_mirror_review"):
        customer_shadow = reports["customer_aws_shadow_mirror_review"]
        lines.append(
            f"| Customer AWS shadow mirror review | accepted_rows=`{customer_shadow['accepted_rows']}`, "
            f"skipped_rows=`{customer_shadow['skipped_rows']}` |"
        )
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(bundle["evidence_boundary"]),
            "",
            "## Next Action",
            "",
            str(readiness["next_action"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(bundle: Mapping[str, Any], *, output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    _write_json(out / "aws_reviewer_bundle.json", bundle)
    (out / "AWS_Reviewer_Bundle.md").write_text(render_markdown(bundle), encoding="utf-8")

    reports = bundle["reports"]
    _write_json(out / "aws_agent_action_chain.json", reports["aws_agent_action_chain"])
    (out / "AWS_Agent_Action_Chain.md").write_text(
        render_chain_markdown(reports["aws_agent_action_chain"]),
        encoding="utf-8",
    )
    _write_json(out / "aws_decision_api_surface.json", reports["aws_decision_api_surface"])
    (out / "AWS_Decision_API_Surface.md").write_text(
        render_decision_api_surface_markdown(reports["aws_decision_api_surface"]),
        encoding="utf-8",
    )
    _write_json(out / "sample_decision_request.json", reports["aws_decision_api_surface"]["request"])
    _write_json(out / "sample_decision_response.json", reports["aws_decision_api_surface"]["response"])
    _write_json(out / "aws_agent_action_chain_postcondition.json", reports["aws_agent_action_chain_postcondition"])
    (out / "AWS_Agent_Action_Chain_Postcondition_Evidence.md").write_text(
        render_chain_postcondition_markdown(reports["aws_agent_action_chain_postcondition"]),
        encoding="utf-8",
    )
    _write_json(out / "aws_postcondition_evidence_report.json", reports["aws_postcondition_evidence"])
    (out / "AWS_Postcondition_Evidence_Report.md").write_text(
        render_aws_postcondition_markdown(reports["aws_postcondition_evidence"]),
        encoding="utf-8",
    )
    _write_json(out / "aws_shadow_mirror_adapter_report.json", reports["aws_shadow_mirror"])
    (out / "AWS_Shadow_Mirror_Adapter_Report.md").write_text(
        render_shadow_mirror_markdown(reports["aws_shadow_mirror"]),
        encoding="utf-8",
    )
    _write_json(out / "serious_report_performance.json", reports["performance"])
    (out / "Serious_Report_Performance.md").write_text(
        render_performance_markdown(reports["performance"]),
        encoding="utf-8",
    )
    _write_json(out / "aws_customer_owned_metadata_request.json", reports["aws_customer_owned_metadata_request"])
    (out / "AWS_Customer_Owned_Metadata_Request.md").write_text(
        render_metadata_request_markdown(reports["aws_customer_owned_metadata_request"]),
        encoding="utf-8",
    )
    if reports.get("customer_aws_metadata_review"):
        customer = reports["customer_aws_metadata_review"]
        _write_json(out / "customer_aws_metadata_adapter_report.json", customer)
        (out / "Customer_AWS_Metadata_Adapter_Report.md").write_text(
            render_aws_metadata_adapter_markdown(customer),
            encoding="utf-8",
        )
        _write_json(out / "customer_aws_normalized_customer_actions.json", customer["normalized_customer_evaluation"])
        if customer["customer_evaluation"]:
            _write_json(out / "customer_aws_customer_evaluation_report.json", customer["customer_evaluation"])
    if reports.get("customer_aws_postcondition_evidence"):
        customer_postcondition = reports["customer_aws_postcondition_evidence"]
        _write_json(out / "customer_aws_postcondition_evidence_report.json", customer_postcondition)
        (out / "Customer_AWS_Postcondition_Evidence_Report.md").write_text(
            render_aws_postcondition_markdown(customer_postcondition),
            encoding="utf-8",
        )
    if reports.get("customer_aws_shadow_mirror_review"):
        customer_shadow = reports["customer_aws_shadow_mirror_review"]
        _write_json(out / "customer_aws_shadow_mirror_adapter_report.json", customer_shadow)
        (out / "Customer_AWS_Shadow_Mirror_Adapter_Report.md").write_text(
            render_shadow_mirror_markdown(customer_shadow),
            encoding="utf-8",
        )
        _write_json(
            out / "customer_aws_shadow_mirror_normalized_customer_actions.json",
            customer_shadow["normalized_customer_evaluation"],
        )
        if customer_shadow["customer_evaluation"]:
            _write_json(
                out / "customer_aws_shadow_mirror_customer_evaluation_report.json",
                customer_shadow["customer_evaluation"],
            )


def _readiness(
    *,
    chain_postcondition: Mapping[str, Any],
    aws_postcondition: Mapping[str, Any],
    shadow_mirror: Mapping[str, Any],
    performance: Mapping[str, Any],
    customer_metadata_review: Mapping[str, Any] | None = None,
    customer_postcondition: Mapping[str, Any] | None = None,
    customer_shadow_mirror_review: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    chain_counts = chain_postcondition["aws_postcondition_status_counts"]
    aws_counts = aws_postcondition["aws_postcondition_status_counts"]
    chain_gaps = int(chain_counts.get("gap", 0))
    chain_violations = int(chain_counts.get("violation", 0))
    aws_gaps = int(aws_counts.get("gap", 0))
    aws_violations = int(aws_counts.get("violation", 0))
    slowest_p95 = float(performance["slowest_p95_ms"])
    chain_proof_eligible = int(chain_postcondition.get("proof_eligible_actions", 0))
    aws_proof_eligible = int(aws_postcondition.get("proof_eligible_actions", 0))
    customer_proof_eligible = int(customer_postcondition.get("proof_eligible_actions", 0)) if customer_postcondition else 0

    blockers = []
    if chain_violations or aws_violations:
        blockers.append("postcondition evidence includes a route violation")
    if slowest_p95 >= 1000:
        blockers.append("local proof-path p95 exceeds the AWS reviewer bundle hard threshold")

    warnings = []
    if chain_gaps:
        warnings.append("AWS chain postcondition evidence includes expected evidence gaps")
    if aws_gaps:
        warnings.append("AWS postcondition evidence includes expected evidence gaps")
    if chain_proof_eligible < int(chain_postcondition.get("observed_actions", 0)):
        warnings.append("AWS chain observations are modeled and not proof-eligible")
    if aws_proof_eligible < int(aws_postcondition.get("observed_actions", 0)):
        warnings.append("AWS observations are modeled and not proof-eligible")
    if slowest_p95 >= 250:
        warnings.append("local proof-path p95 should be remeasured in the reviewer environment")
    if customer_metadata_review is not None and int(customer_metadata_review["accepted_rows"]) < 5:
        warnings.append("customer AWS metadata review has fewer than 5 accepted rows")
    if customer_postcondition is not None and int(customer_postcondition["aws_postcondition_status_counts"].get("violation", 0)):
        blockers.append("customer AWS postcondition evidence includes a route violation")
    if customer_postcondition is not None and customer_proof_eligible < int(customer_postcondition.get("observed_actions", 0)):
        warnings.append("customer AWS observations are not fully authenticated or proof-eligible")
    if int(shadow_mirror["skipped_rows"]) > 0:
        warnings.append("AWS shadow mirror proof intentionally skipped unsafe or unsupported rows")
    if customer_shadow_mirror_review is not None and int(customer_shadow_mirror_review["accepted_rows"]) < 5:
        warnings.append("customer AWS shadow mirror review has fewer than 5 accepted rows")

    if blockers:
        status = "not_ready_for_aws_reviewer"
        next_action = "Repair blockers before asking an AWS-style reviewer for customer-owned metadata."
    elif warnings:
        status = "ready_for_limited_aws_review"
        next_action = "Use the gaps as reviewer questions and ask for 5 to 25 safe AWS-style action and observation summaries."
    else:
        status = "ready_for_aws_shadow_mode_discussion"
        next_action = "Ask for 10 to 25 customer-owned AWS-style metadata actions from one workflow and schedule bounded shadow-mode review."

    takeaways = [
        "The AWS path is now one command instead of separate documents.",
        "The bundle explains the difference between content guardrails, authority controls, recoverability control, and postcondition evidence.",
        "The shadow mirror path adds operational flow evidence without packet payloads or live AWS access.",
        "The proof remains metadata-only and does not need live AWS access.",
        "The next real proof is reviewer-owned AWS-style metadata from one workflow.",
    ]
    if customer_metadata_review is not None:
        takeaways.append(
            f"Customer AWS metadata supplied: {customer_metadata_review['accepted_rows']} accepted rows and "
            f"{customer_metadata_review['skipped_rows']} skipped rows."
        )
    if customer_postcondition is not None:
        takeaways.append(
            f"Customer AWS postcondition statuses: {customer_postcondition['aws_postcondition_status_counts']}."
        )
    if customer_shadow_mirror_review is not None:
        takeaways.append(
            f"Customer AWS shadow mirror metadata supplied: {customer_shadow_mirror_review['accepted_rows']} "
            f"accepted rows and {customer_shadow_mirror_review['skipped_rows']} skipped rows."
        )
    if warnings:
        takeaways.append(f"Warnings: {', '.join(warnings)}.")
    if blockers:
        takeaways.append(f"Blockers: {', '.join(blockers)}.")

    return {
        "status": status,
        "slowest_p95_ms": slowest_p95,
        "chain_postcondition_gaps": chain_gaps,
        "chain_postcondition_violations": chain_violations,
        "aws_postcondition_gaps": aws_gaps,
        "aws_postcondition_violations": aws_violations,
        "chain_proof_eligible_actions": chain_proof_eligible,
        "aws_proof_eligible_actions": aws_proof_eligible,
        "customer_proof_eligible_actions": customer_proof_eligible,
        "warnings": warnings,
        "blockers": blockers,
        "takeaways": takeaways,
        "next_action": next_action,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve_path(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble the SMERC AWS-style reviewer bundle.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--requested-actions", type=int, default=12)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--customer-aws-source-exports")
    parser.add_argument("--customer-aws-observations")
    parser.add_argument("--customer-aws-provenance-ledger")
    parser.add_argument("--customer-aws-hmac-key-env")
    parser.add_argument("--customer-aws-shadow-mirror-exports")
    parser.add_argument("--output-dir", default="reports/aws_reviewer_bundle")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    bundle = build_aws_reviewer_bundle(
        root=args.root,
        requested_actions=args.requested_actions,
        iterations=args.iterations,
        customer_aws_source_exports=args.customer_aws_source_exports,
        customer_aws_observations=args.customer_aws_observations,
        customer_aws_provenance_ledger=args.customer_aws_provenance_ledger,
        customer_aws_hmac_key=hmac_key_from_env(args.customer_aws_hmac_key_env),
        customer_aws_shadow_mirror_exports=args.customer_aws_shadow_mirror_exports,
    )
    write_outputs(bundle, output_dir=args.output_dir)
    print(json.dumps(bundle, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

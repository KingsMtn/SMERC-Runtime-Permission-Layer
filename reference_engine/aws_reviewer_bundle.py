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
from reference_engine.aws_postcondition_evidence import (
    build_aws_postcondition_report,
    load_aws_observations,
    load_json_object,
    render_markdown as render_aws_postcondition_markdown,
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


def build_aws_reviewer_bundle(*, root: str | Path = ".", requested_actions: int = 12, iterations: int = 5) -> Dict[str, Any]:
    base = Path(root)
    chain_report = build_chain_report(load_payload(base / "examples/aws_agent_action_chain.json"))
    chain_postcondition = build_chain_postcondition_report(
        load_payload(base / "examples/aws_agent_action_chain.json"),
        base / "examples/aws_agent_action_chain_observations.json",
    )
    aws_postcondition = build_aws_postcondition_report(
        load_json_object(base / "reports/aws_metadata_adapter/customer_evaluation_report.json"),
        load_aws_observations(base / "examples/aws_postcondition_observations.json"),
    )
    performance = build_performance_report(root=base, iterations=iterations)
    metadata_request = build_request_report(workflow_family="aws", requested_actions=requested_actions)
    readiness = _readiness(
        chain_postcondition=chain_postcondition,
        aws_postcondition=aws_postcondition,
        performance=performance,
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
            "Postcondition evidence checks whether the required route controls actually happened after the decision.",
        ],
        "work_result_impact": {
            "work": (
                "Assemble the AWS-style reviewer path into one local package: action-chain proof, route-control "
                "postcondition evidence, AWS postcondition evidence, performance metrics, and customer-owned "
                "AWS metadata request."
            ),
            "result": (
                f"Generated an AWS reviewer bundle with {chain_report['scenario_count']} action-chain examples, "
                f"chain postcondition statuses {chain_postcondition['aws_postcondition_status_counts']}, "
                f"AWS postcondition statuses {aws_postcondition['aws_postcondition_status_counts']}, and slowest "
                f"local p95 {performance['slowest_p95_ms']} ms."
            ),
            "impact": (
                "An AWS-style platform reviewer can inspect where SMERC fits, what it decides, what evidence would "
                "prove the route, and what safe customer-owned metadata is needed next without granting live AWS access."
            ),
        },
        "readiness": readiness,
        "reports": {
            "aws_agent_action_chain": chain_report,
            "aws_agent_action_chain_postcondition": chain_postcondition,
            "aws_postcondition_evidence": aws_postcondition,
            "performance": performance,
            "aws_customer_owned_metadata_request": metadata_request,
        },
        "evidence_boundary": (
            "This is a local, metadata-only AWS-style review package. It does not connect to AWS, invoke Amazon "
            "Bedrock, call IAM, run Systems Manager, apply CloudFormation, read CloudTrail or CloudWatch, modify "
            "infrastructure, prove AWS endorsement, prove AWS certification, or establish production safety."
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
        "Guardrails check content. IAM checks authority. SMERC checks recoverability. Postcondition evidence checks whether the route happened.",
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
                f"| AWS chain postcondition evidence | statuses="
                f"`{reports['aws_agent_action_chain_postcondition']['aws_postcondition_status_counts']}` |"
            ),
            (
                f"| AWS postcondition evidence | statuses="
                f"`{reports['aws_postcondition_evidence']['aws_postcondition_status_counts']}` |"
            ),
            (
                f"| Performance | status=`{reports['performance']['status']}`, "
                f"slowest_p95_ms=`{reports['performance']['slowest_p95_ms']}` |"
            ),
            (
                f"| AWS customer-owned metadata request | requested_actions="
                f"`{reports['aws_customer_owned_metadata_request']['requested_action_count']}` |"
            ),
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


def _readiness(
    *,
    chain_postcondition: Mapping[str, Any],
    aws_postcondition: Mapping[str, Any],
    performance: Mapping[str, Any],
) -> Dict[str, Any]:
    chain_counts = chain_postcondition["aws_postcondition_status_counts"]
    aws_counts = aws_postcondition["aws_postcondition_status_counts"]
    chain_gaps = int(chain_counts.get("gap", 0))
    chain_violations = int(chain_counts.get("violation", 0))
    aws_gaps = int(aws_counts.get("gap", 0))
    aws_violations = int(aws_counts.get("violation", 0))
    slowest_p95 = float(performance["slowest_p95_ms"])

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
    if slowest_p95 >= 250:
        warnings.append("local proof-path p95 should be remeasured in the reviewer environment")

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
        "The proof remains metadata-only and does not need live AWS access.",
        "The next real proof is reviewer-owned AWS-style metadata from one workflow.",
    ]
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
        "warnings": warnings,
        "blockers": blockers,
        "takeaways": takeaways,
        "next_action": next_action,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble the SMERC AWS-style reviewer bundle.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--requested-actions", type=int, default=12)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--output-dir", default="reports/aws_reviewer_bundle")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    bundle = build_aws_reviewer_bundle(
        root=args.root,
        requested_actions=args.requested_actions,
        iterations=args.iterations,
    )
    write_outputs(bundle, output_dir=args.output_dir)
    print(json.dumps(bundle, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

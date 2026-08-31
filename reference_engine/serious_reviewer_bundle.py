from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.customer_evaluation import (
    build_customer_evaluation,
    load_payload as load_customer_payload,
    render_markdown as render_customer_evaluation_markdown,
)
from reference_engine.customer_owned_metadata_request import (
    build_request_report,
    render_markdown as render_metadata_request_markdown,
)
from reference_engine.external_reviewer_metadata_response import (
    assess_response,
    load_payload as load_reviewer_response,
    render_markdown as render_response_assessment_markdown,
)
from reference_engine.postcondition_evidence import (
    build_postcondition_report,
    load_json_object,
    load_observations,
    render_markdown as render_postcondition_markdown,
)
from reference_engine.serious_report_performance import (
    build_performance_report,
    render_markdown as render_performance_markdown,
)


VERSION = "smerc.serious-reviewer-bundle.v1"

CUSTOMER_EVALUATION_INPUTS = {
    "general": Path("examples/customer_eval_actions.json"),
    "cloud": Path("examples/cloud_admin_customer_eval_actions.json"),
    "financial": Path("examples/smerc_f_customer_eval_actions.json"),
}


def build_serious_reviewer_bundle(
    *,
    root: str | Path = ".",
    workflow_family: str = "general",
    requested_actions: int = 10,
    response_path: str | Path = "examples/external_reviewer_metadata_response_example.json",
    performance_iterations: int = 5,
) -> Dict[str, Any]:
    if workflow_family not in CUSTOMER_EVALUATION_INPUTS:
        raise ValueError(f"workflow_family must be one of: {', '.join(sorted(CUSTOMER_EVALUATION_INPUTS))}")

    base = Path(root)
    customer_evaluation = build_customer_evaluation(
        load_customer_payload(base / CUSTOMER_EVALUATION_INPUTS[workflow_family])
    )
    postcondition_evidence = build_postcondition_report(
        load_json_object(base / "reports/public_benchmark_customer_evaluation/customer_evaluation_report.json"),
        load_observations(base / "examples/postcondition_observations.json"),
    )
    performance = build_performance_report(root=base, iterations=performance_iterations)
    metadata_request = build_request_report(
        workflow_family=workflow_family,
        requested_actions=requested_actions,
    )
    response_assessment = assess_response(load_reviewer_response(base / response_path))

    readiness = _readiness(
        customer_evaluation=customer_evaluation,
        postcondition_evidence=postcondition_evidence,
        performance=performance,
        response_assessment=response_assessment,
    )
    return {
        "version": VERSION,
        "generated_at": _now(),
        "workflow_family": workflow_family,
        "requested_action_count": requested_actions,
        "bundle_status": readiness["status"],
        "work_result_impact": {
            "work": (
                "Assemble the serious reviewer path into one local package: customer evaluation, postcondition "
                "evidence, performance metrics, customer-owned metadata request, and reviewer-response assessment."
            ),
            "result": (
                f"Generated a {workflow_family} reviewer bundle with customer evaluation fit "
                f"`{customer_evaluation['pilot_fit']['fit']}`, postcondition counts "
                f"`{postcondition_evidence['postcondition_status_counts']}`, slowest p95 "
                f"`{performance['slowest_p95_ms']}` ms, and response disposition "
                f"`{response_assessment['disposition']}`."
            ),
            "impact": (
                "A company reviewer can inspect the full proof-to-pilot handoff without production access, secrets, "
                "regulated payloads, or founder-led assembly of separate reports."
            ),
        },
        "readiness": readiness,
        "reports": {
            "customer_evaluation": customer_evaluation,
            "postcondition_evidence": postcondition_evidence,
            "performance": performance,
            "customer_owned_metadata_request": metadata_request,
            "external_reviewer_metadata_response_assessment": response_assessment,
        },
        "evidence_boundary": (
            "This bundle is a local, metadata-only technical review package. It does not require production access "
            "and does not prove customer demand, production safety, hosted API latency, compliance, incident "
            "reduction, or enforce-mode readiness."
        ),
    }


def render_markdown(bundle: Mapping[str, Any]) -> str:
    readiness = bundle["readiness"]
    reports = bundle["reports"]
    lines = [
        "# SMERC Serious Reviewer Bundle",
        "",
        f"Generated: `{bundle['generated_at']}`",
        f"Version: `{bundle['version']}`",
        f"Workflow family: `{bundle['workflow_family']}`",
        f"Bundle status: `{bundle['bundle_status']}`",
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
        f"- Customer evaluation fit: `{readiness['customer_evaluation_fit']}`",
        f"- Response disposition: `{readiness['response_disposition']}`",
        f"- Slowest local p95 ms: `{readiness['slowest_p95_ms']}`",
        f"- Postcondition gaps: `{readiness['postcondition_gaps']}`",
        f"- Postcondition violations: `{readiness['postcondition_violations']}`",
        "",
        "## Reviewer Takeaways",
        "",
    ]
    lines.extend(f"- {item}" for item in readiness["takeaways"])
    lines.extend(
        [
            "",
            "## Included Reports",
            "",
            "| Report | Main Result |",
            "| --- | --- |",
            (
                f"| Customer evaluation | pilot_fit="
                f"`{reports['customer_evaluation']['pilot_fit']['fit']}`, "
                f"actions=`{reports['customer_evaluation']['summary']['total_actions']}` |"
            ),
            (
                f"| Postcondition evidence | statuses="
                f"`{reports['postcondition_evidence']['postcondition_status_counts']}` |"
            ),
            (
                f"| Serious performance | status=`{reports['performance']['status']}`, "
                f"slowest_p95_ms=`{reports['performance']['slowest_p95_ms']}` |"
            ),
            (
                f"| Customer-owned metadata request | requested_actions="
                f"`{reports['customer_owned_metadata_request']['requested_action_count']}` |"
            ),
            (
                f"| Reviewer response assessment | disposition="
                f"`{reports['external_reviewer_metadata_response_assessment']['disposition']}` |"
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
    _write_json(out / "serious_reviewer_bundle.json", bundle)
    (out / "Serious_Reviewer_Bundle.md").write_text(render_markdown(bundle), encoding="utf-8")

    reports = bundle["reports"]
    _write_json(out / "customer_evaluation_report.json", reports["customer_evaluation"])
    (out / "Customer_Evaluation_Report.md").write_text(
        render_customer_evaluation_markdown(reports["customer_evaluation"]),
        encoding="utf-8",
    )
    _write_json(out / "postcondition_evidence_report.json", reports["postcondition_evidence"])
    (out / "Postcondition_Evidence_Report.md").write_text(
        render_postcondition_markdown(reports["postcondition_evidence"]),
        encoding="utf-8",
    )
    _write_json(out / "serious_report_performance.json", reports["performance"])
    (out / "Serious_Report_Performance.md").write_text(
        render_performance_markdown(reports["performance"]),
        encoding="utf-8",
    )
    _write_json(out / "customer_owned_metadata_request.json", reports["customer_owned_metadata_request"])
    (out / "Customer_Owned_Metadata_Request.md").write_text(
        render_metadata_request_markdown(reports["customer_owned_metadata_request"]),
        encoding="utf-8",
    )
    _write_json(
        out / "external_reviewer_metadata_response_assessment.json",
        reports["external_reviewer_metadata_response_assessment"],
    )
    (out / "External_Reviewer_Metadata_Response_Assessment.md").write_text(
        render_response_assessment_markdown(reports["external_reviewer_metadata_response_assessment"]),
        encoding="utf-8",
    )


def _readiness(
    *,
    customer_evaluation: Mapping[str, Any],
    postcondition_evidence: Mapping[str, Any],
    performance: Mapping[str, Any],
    response_assessment: Mapping[str, Any],
) -> Dict[str, Any]:
    customer_fit = str(customer_evaluation["pilot_fit"]["fit"])
    response_disposition = str(response_assessment["disposition"])
    postcondition_counts = postcondition_evidence["postcondition_status_counts"]
    gaps = int(postcondition_counts.get("gap", 0))
    violations = int(postcondition_counts.get("violation", 0))
    slowest_p95 = float(performance["slowest_p95_ms"])

    blockers = []
    if response_disposition == "not_ready":
        blockers.append("external reviewer response is not ready")
    if customer_fit == "weak":
        blockers.append("customer evaluation examples do not show enough side-effecting risk")
    if violations:
        blockers.append("postcondition evidence includes a route violation")
    if slowest_p95 >= 250:
        blockers.append("local proof-path p95 exceeds the default review threshold")

    warnings = []
    if response_disposition == "ready_with_review_limits":
        warnings.append("reviewer response is usable only with explicit review limits")
    if gaps:
        warnings.append("postcondition evidence includes control gaps that need adapter proof")

    if blockers:
        status = "not_ready_for_pilot"
        next_action = "Do not propose a pilot yet; repair blockers and rerun the serious reviewer bundle."
    elif warnings:
        status = "ready_for_limited_review"
        next_action = "Run a limited customer-metadata review and ask the reviewer to resolve warnings before pilot approval."
    else:
        status = "ready_for_shadow_mode_discussion"
        next_action = "Ask for 10 to 25 customer-owned metadata actions from one workflow and schedule a bounded shadow-mode review."

    takeaways = [
        "One command now assembles the core customer-review evidence path.",
        "Performance is included as local operational-overhead evidence, not a production SLA.",
        "Customer-owned metadata is requested without secrets, raw records, production logs, or live access.",
        "Postconditions show whether route controls were observed, missing, violated, or unobserved.",
    ]
    if blockers:
        takeaways.append(f"Blockers: {', '.join(blockers)}.")
    if warnings:
        takeaways.append(f"Warnings: {', '.join(warnings)}.")

    return {
        "status": status,
        "customer_evaluation_fit": customer_fit,
        "response_disposition": response_disposition,
        "slowest_p95_ms": slowest_p95,
        "postcondition_gaps": gaps,
        "postcondition_violations": violations,
        "blockers": blockers,
        "warnings": warnings,
        "takeaways": takeaways,
        "next_action": next_action,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble the SMERC serious reviewer bundle.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--workflow-family", choices=sorted(CUSTOMER_EVALUATION_INPUTS), default="general")
    parser.add_argument("--requested-actions", type=int, default=10)
    parser.add_argument("--response", default="examples/external_reviewer_metadata_response_example.json")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--output-dir", default="reports/serious_reviewer_bundle")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    bundle = build_serious_reviewer_bundle(
        root=args.root,
        workflow_family=args.workflow_family,
        requested_actions=args.requested_actions,
        response_path=args.response,
        performance_iterations=args.iterations,
    )
    write_outputs(bundle, output_dir=args.output_dir)
    print(json.dumps(bundle, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

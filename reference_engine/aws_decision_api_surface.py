from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.aws_lambda_decision_handler import EVIDENCE_BOUNDARY, VERSION as HANDLER_VERSION, lambda_handler


VERSION = "smerc.aws-decision-api-surface.v1"
OPENAPI_PATH = "schemas/smerc-aws-decision-api-openapi-v1.json"
SAMPLE_REQUEST_PATH = "examples/aws_lambda_decision_event.json"
OPERATION_ID = "evaluateAwsActionRecoverability"


def build_decision_api_surface(*, root: str | Path = ".") -> Dict[str, Any]:
    base = Path(root)
    request = _read_json(base / SAMPLE_REQUEST_PATH)
    openapi = _read_json(base / OPENAPI_PATH)
    response = lambda_handler(request)
    required_response_fields = [
        "version",
        "request_id",
        "posture",
        "route_state",
        "executable",
        "required_controls",
        "blocked_controls",
        "scores",
        "ledger_id",
        "ledger_head_hash",
        "ledger_valid",
        "evidence_boundary",
    ]
    missing_fields = [field for field in required_response_fields if field not in response]
    operation = openapi["paths"]["/smerc/decision"]["post"]
    readiness_blockers = []
    if operation.get("operationId") != OPERATION_ID:
        readiness_blockers.append("OpenAPI operationId does not match the AWS decision-surface operation.")
    if missing_fields:
        readiness_blockers.append(f"Handler response is missing required fields: {', '.join(missing_fields)}.")
    if not response.get("ledger_valid"):
        readiness_blockers.append("Decision lifecycle ledger did not validate.")
    if "does not call AWS" not in response.get("evidence_boundary", ""):
        readiness_blockers.append("Evidence boundary does not make the no-live-AWS limit explicit.")

    status = "reviewable_aws_decision_surface" if not readiness_blockers else "needs_repair"
    return {
        "version": VERSION,
        "generated_at": _now(),
        "status": status,
        "handler_version": HANDLER_VERSION,
        "operation_id": OPERATION_ID,
        "openapi_path": OPENAPI_PATH,
        "sample_request_path": SAMPLE_REQUEST_PATH,
        "request_id": response["request_id"],
        "posture": response["posture"],
        "route_state": response["route_state"],
        "executable": response["executable"],
        "ledger_valid": response["ledger_valid"],
        "required_controls_count": len(response.get("required_controls", [])),
        "blocked_controls_count": len(response.get("blocked_controls", [])),
        "decision_summary": {
            "reason": response["reason"],
            "scores": response["scores"],
            "recommended_next_action": response["recommended_next_action"],
        },
        "compatibility_targets": [
            "AWS Lambda-compatible handler",
            "API Gateway or Function URL JSON body",
            "Bedrock Agent Action Group pre-execution decision check",
            "AgentCore Gateway-style OpenAPI tool surface",
            "local reviewer CLI proof without live AWS access",
        ],
        "reviewer_runbook": [
            f"Inspect {OPENAPI_PATH}.",
            f"Inspect {SAMPLE_REQUEST_PATH}.",
            "Run python -m reference_engine.aws_decision_api_surface --pretty.",
            "Confirm the response returns posture, route controls, scores, and ledger evidence.",
            "Replace the sample with 5 to 25 metadata-only actions from one workflow when safe.",
        ],
        "readiness_blockers": readiness_blockers,
        "request": request,
        "response": response,
        "evidence_boundary": EVIDENCE_BOUNDARY,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# AWS Decision API Surface",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        f"Status: `{report['status']}`",
        f"Handler version: `{report['handler_version']}`",
        "",
        "## Purpose",
        "",
        "This report packages SMERC as a small AWS-style decision API surface: one metadata-only request, one compact decision response, and one OpenAPI operation a reviewer can inspect before any live AWS integration exists.",
        "",
        "## Contract",
        "",
        f"- OpenAPI: `{report['openapi_path']}`",
        f"- Operation ID: `{report['operation_id']}`",
        f"- Sample request: `{report['sample_request_path']}`",
        f"- Sample request ID: `{report['request_id']}`",
        "",
        "## Sample Decision",
        "",
        f"- Posture: `{report['posture']}`",
        f"- Route state: `{report['route_state']}`",
        f"- Executable: `{report['executable']}`",
        f"- Ledger valid: `{report['ledger_valid']}`",
        f"- Required controls: `{report['required_controls_count']}`",
        f"- Blocked controls: `{report['blocked_controls_count']}`",
        "",
        "## Compatibility Targets",
        "",
    ]
    lines.extend(f"- {item}" for item in report["compatibility_targets"])
    lines.extend(
        [
            "",
            "## Reviewer Runbook",
            "",
        ]
    )
    lines.extend(f"{index}. {item}" for index, item in enumerate(report["reviewer_runbook"], start=1))
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
            "## Work / Result / Impact",
            "",
            "- Work: Convert the AWS lane from a strategy document into a reviewable Lambda/OpenAPI decision surface.",
            "- Result: A reviewer can inspect one request, one response, one operation ID, route controls, scores, and ledger evidence without live AWS access.",
            "- Impact: SMERC becomes easier to evaluate as a future Bedrock Action Group, AgentCore Gateway, or AWS-adjacent decision tool while preserving honest boundaries.",
            "",
        ]
    )
    if report["readiness_blockers"]:
        lines.extend(["## Readiness Blockers", ""])
        lines.extend(f"- {item}" for item in report["readiness_blockers"])
        lines.append("")
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    _write_json(out / "aws_decision_api_surface.json", report)
    (out / "AWS_Decision_API_Surface.md").write_text(render_markdown(report), encoding="utf-8")
    _write_json(out / "sample_decision_request.json", report["request"])
    _write_json(out / "sample_decision_response.json", report["response"])


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC AWS decision API surface proof.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-dir", default="reports/aws_decision_api_surface")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_decision_api_surface(root=args.root)
    write_outputs(report, output_dir=args.output_dir)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

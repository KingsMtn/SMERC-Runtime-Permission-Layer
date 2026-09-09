from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, Mapping

from reference_engine.customer_evaluation import build_customer_evaluation


VERSION = "smerc.aws-lambda-decision-handler.v1"

EVIDENCE_BOUNDARY = (
    "This Lambda-shaped handler is a local, metadata-only adapter. It does not call AWS, invoke Amazon Bedrock, "
    "read CloudTrail or CloudWatch, assume roles, modify IAM, execute CloudFormation, access S3, change RDS, "
    "rotate secrets, deploy infrastructure, or prove AWS endorsement, AWS certification, production safety, "
    "or incident reduction."
)


def lambda_handler(event: Mapping[str, Any], context: Any = None) -> Dict[str, Any]:
    """AWS Lambda-compatible entry point for Bedrock-style action gating.

    The handler accepts either a complete `smerc.customer-evaluation.v1` payload
    or a single `action` object. It returns the first SMERC decision in a
    compact shape that a Bedrock Agent Action Group, gateway, or local reviewer
    can inspect without granting live AWS access.
    """

    payload = _payload_from_event(event)
    report = build_customer_evaluation(payload)
    record = report["records"][0]
    decision = record["decision"]
    route = record["sparta_route"]

    return {
        "version": VERSION,
        "request_id": record["action_id"],
        "posture": decision["posture"],
        "route_state": route["route_state"],
        "executable": route["executable"],
        "required_controls": route.get("applied_controls", []),
        "blocked_controls": route.get("blocked_controls", []),
        "reason": _decision_reason(record),
        "scores": decision["scores"],
        "ref_gate_status": record["ref_gate"]["status"],
        "identity_gate_status": record["identity_gate"]["status"],
        "ledger_id": record["decision_lifecycle_ledger"]["decision_id"],
        "ledger_head_hash": record["decision_lifecycle_ledger"]["head_record_hash"],
        "ledger_valid": record["decision_lifecycle_ledger"]["verification"]["valid"],
        "recommended_next_action": report["recommended_next_action"],
        "evidence_boundary": EVIDENCE_BOUNDARY,
    }


def _payload_from_event(event: Mapping[str, Any]) -> Dict[str, Any]:
    body = event.get("body") if isinstance(event, Mapping) else None
    if isinstance(body, str) and body.strip():
        event = json.loads(body)
    elif isinstance(body, Mapping):
        event = body

    if not isinstance(event, Mapping):
        raise TypeError("event must be a mapping or contain a JSON object body")

    if event.get("version") == "smerc.customer-evaluation.v1":
        return dict(event)

    action = event.get("action")
    if isinstance(action, Mapping):
        return {
            "version": "smerc.customer-evaluation.v1",
            "tenant_id": _text(event.get("tenant_id"), "aws-lambda-local-review"),
            "organization": _text(event.get("organization"), "AWS-Style Local Review"),
            "contact_role": _text(event.get("contact_role"), "aws_platform_reviewer"),
            "evaluation_date": _text(event.get("evaluation_date"), date.today().isoformat()),
            "data_boundary": _text(
                event.get("data_boundary"),
                "Metadata-only AWS-style action review. No account IDs, ARNs, raw logs, credentials, secrets, "
                "customer records, private topology, production commands, or live AWS access are included.",
            ),
            "workflow_context": _text(
                event.get("workflow_context"),
                "Lambda-shaped SMERC decision request for a proposed Bedrock Agent Action Group or cloud action.",
            ),
            "initial_autonomy_state": _text(event.get("initial_autonomy_state"), "HEALTHY"),
            "actions": [dict(action)],
        }

    raise ValueError("event must be a customer-evaluation payload or include an action object")


def _decision_reason(record: Mapping[str, Any]) -> str:
    decision = record["decision"]
    route = record["sparta_route"]
    posture = decision["posture"]
    exposure = decision["scores"]["irreversible_exposure_score"]
    route_state = route["route_state"]
    return (
        f"SMERC returned {posture} and route {route_state} because the proposed action's recoverability, "
        f"containment, evidence, rollback, and blast-radius signals produced irreversible exposure {exposure}."
    )


def _text(value: Any, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback

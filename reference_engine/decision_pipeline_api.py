from __future__ import annotations

import json
from typing import Any, Mapping

from reference_engine.decision_pipeline_contract import evaluate_pipeline


VERSION = "smerc.decision-pipeline-api.v1"
EVIDENCE_BOUNDARY = (
    "This dependency-free handler evaluates supplied metadata in the caller's environment. It does not call "
    "AWS, verify upstream evidence, prove adapter enforcement, establish customer production safety, or imply "
    "AWS endorsement or certification."
)


def lambda_handler(event: Mapping[str, Any], context: Any = None) -> dict[str, Any]:
    payload = _payload(event)
    result = evaluate_pipeline(payload)
    return {
        "version": VERSION,
        "pipeline_id": result["pipeline_id"],
        "final_decision": result["final_decision"],
        "should_execute": result["should_execute"],
        "should_commit": result["should_commit"],
        "controls": result["controls"],
        "stages": result["stages"],
        "pipeline_sha256": result["pipeline_sha256"],
        "contract_rule": result["contract_rule"],
        "evidence_boundary": EVIDENCE_BOUNDARY,
    }


def api_gateway_handler(event: Mapping[str, Any], context: Any = None) -> dict[str, Any]:
    try:
        result = lambda_handler(event, context)
        return {"statusCode": 200, "headers": {"content-type": "application/json"},
                "body": json.dumps(result, separators=(",", ":"))}
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        body = {"version": VERSION, "error": "invalid_request", "message": str(exc),
                "evidence_boundary": EVIDENCE_BOUNDARY}
        return {"statusCode": 400, "headers": {"content-type": "application/json"},
                "body": json.dumps(body, separators=(",", ":"))}


def _payload(event: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(event, Mapping):
        raise TypeError("event must be an object")
    body = event.get("body")
    if isinstance(body, str):
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise TypeError("event body must contain a JSON object")
        return parsed
    if isinstance(body, Mapping):
        return dict(body)
    return dict(event)

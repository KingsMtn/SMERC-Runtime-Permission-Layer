from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from reference_engine.aws_mcp_enforced_live_proof import build_request
from reference_engine.mcp_aws_enforcement_adapter import AWSMCPEnforcementAdapter


SCHEMA = "smerc.aws-mcp-denied-write-proof.v1"
PROOF_BUCKET = "smerc-proof-never-execute"


def build_denied_write_request() -> dict[str, Any]:
    request = build_request()
    request["id"] = "smerc-denied-write-proof"
    arguments = request["params"]["arguments"]
    governance = arguments["governance_request"]
    governance["mcp_request_id"] = "AWS_MCP_DELETE_BUCKET_DENIED_001"
    governance["canonical_action_id"] = "AWS_MCP_DELETE_BUCKET_DENIED_001"
    governance["tool_call"].update(
        {
            "tool_name": "delete_bucket",
            "description": "Delete an AWS S3 bucket.",
            "operation_class": "delete",
            "requested_capability": "delete_bucket",
            "external_side_effect": True,
            "supports_dry_run": False,
            "supports_checkpoint": False,
            "supports_rollback": False,
            "requested_scope_units": 100,
            "max_scope_units": 100,
        }
    )
    governance["risk_signals"].update(
        {
            "base_action_risk": 1.0,
            "reversibility": 0.0,
            "containment_strength": 0.0,
            "rollback_latency": 1.0,
            "evidence_validity": 0.4,
            "anomaly_pressure": 0.8,
            "impact_scope": 1.0,
            "cancel_reliability": 0.0,
            "authorization_confidence": 0.4,
        }
    )
    arguments["aws_call"].update(
        {
            "tool_name": "delete_bucket",
            "arguments": {"bucket": PROOF_BUCKET},
        }
    )
    return request


def run_denied_write_proof(*, observed_at: str | None = None) -> dict[str, Any]:
    executor_called = False

    def tripwire_executor(*_args: Any) -> Mapping[str, Any]:
        nonlocal executor_called
        executor_called = True
        raise RuntimeError("denied write reached the AWS executor")

    response = AWSMCPEnforcementAdapter(tripwire_executor, approved_cost_usd=0.0).handle(
        build_denied_write_request()
    )
    if not isinstance(response, Mapping) or "result" not in response:
        raise RuntimeError("SMERC returned no denied-write decision")
    result = response["result"]
    if not isinstance(result, Mapping) or result.get("isError") is not True:
        raise RuntimeError("destructive AWS request was not denied")
    structured = result.get("structuredContent")
    if not isinstance(structured, Mapping) or not isinstance(structured.get("smerc"), Mapping):
        raise RuntimeError("SMERC returned no structured denial evidence")
    evidence = dict(structured["smerc"])
    if executor_called:
        raise RuntimeError("destructive AWS request crossed the enforcement boundary")
    if evidence.get("posture") != "DENY" or evidence.get("route_state") != "BLOCK":
        raise RuntimeError("destructive AWS request did not reach the required DENY/BLOCK state")
    return {
        "schema": SCHEMA,
        "observed_at": observed_at or datetime.now(timezone.utc).isoformat(),
        "evidence_class": "pre_execution_denied_write",
        "production_evidence": False,
        "aws_executor_called": False,
        "aws_resource_changed": False,
        "estimated_incremental_cost_usd": 0.0,
        "action": {
            "server_name": "aws-mcp",
            "tool_name": "delete_bucket",
            "arguments": {"bucket": PROOF_BUCKET},
            "external_side_effect": True,
        },
        "smerc": evidence,
        "boundary": {
            "proves": "This destructive request passed runtime admission but was denied by SMERC recoverability policy before the configured AWS executor was called.",
            "does_not_prove": "AWS independently enforced the decision or that every alternate AWS access path is blocked.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a zero-cost SMERC denied AWS write proof.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    proof = run_denied_write_proof()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "denied_before_execution", "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

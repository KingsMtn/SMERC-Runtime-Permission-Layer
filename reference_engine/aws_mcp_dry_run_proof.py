from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from reference_engine.aws_mcp_enforced_live_proof import PINNED_PROXY_VERSION, build_request
from reference_engine.mcp_aws_enforcement_adapter import AWSMCPEnforcementAdapter, Executor, ManagedAWSMCPProxyExecutor


SCHEMA = "smerc.aws-mcp-dry-run-proof.v1"
TOOL_NAME = "aws___run_script"
SENTINEL_GROUP = "smerc-dry-run-never-create"
AWS_DRY_RUN_SCRIPT = '''vpcs = await call_boto3(service_name="ec2", operation_name="DescribeVpcs", region_name="us-east-1", params={"Filters": [{"Name": "is-default", "Values": ["true"]}]})
vpc_ids = [item["VpcId"] for item in vpcs.get("Vpcs", [])]
if not vpc_ids:
    result = {"status": "no_default_vpc", "authorized": False, "resource_created": False, "matching_group_count": 0}
else:
    error_code = None
    try:
        await call_boto3(service_name="ec2", operation_name="CreateSecurityGroup", region_name="us-east-1", params={"GroupName": "smerc-dry-run-never-create", "Description": "SMERC authorization dry-run only", "VpcId": vpc_ids[0], "DryRun": True})
    except Exception as exc:
        if "DryRunOperation" in str(exc):
            error_code = "DryRunOperation"
        else:
            error_code = "UnexpectedDryRunError"
    groups = await call_boto3(service_name="ec2", operation_name="DescribeSecurityGroups", region_name="us-east-1", params={"Filters": [{"Name": "group-name", "Values": ["smerc-dry-run-never-create"]}]})
    matching_count = len(groups.get("SecurityGroups", []))
    result = {"status": "dry_run_result", "error_code": error_code, "authorized": error_code == "DryRunOperation", "matching_group_count": matching_count, "resource_created": matching_count > 0}
result'''


def build_dry_run_request() -> dict[str, Any]:
    request = build_request()
    request["id"] = "smerc-aws-dry-run-proof"
    arguments = request["params"]["arguments"]
    governance = arguments["governance_request"]
    governance["mcp_request_id"] = "AWS_MCP_EC2_DRY_RUN_001"
    governance["canonical_action_id"] = "AWS_MCP_EC2_DRY_RUN_001"
    governance["agent_identity"]["credential_scope"] = "production_write"
    governance["agent_identity"]["context"] = {
        "proof": "enforced_aws_authorization_dry_run",
        "mutation_permitted": False,
        "dry_run_required": True,
    }
    governance["tool_call"].update(
        {
            "tool_name": TOOL_NAME,
            "description": "Validate EC2 create authorization with DryRun and verify no sentinel resource exists.",
            "operation_class": "dry_run",
            "requested_capability": "ec2_create_security_group_dry_run",
            "external_side_effect": False,
            "supports_dry_run": True,
            "supports_scope_limit": True,
            "supports_checkpoint": True,
            "supports_rollback": True,
            "requested_scope_units": 1,
            "max_scope_units": 1,
        }
    )
    governance["risk_signals"].update(
        {
            "base_action_risk": 0.12,
            "reversibility": 1.0,
            "containment_strength": 1.0,
            "rollback_latency": 0.0,
            "evidence_validity": 0.95,
            "anomaly_pressure": 0.0,
            "impact_scope": 0.01,
            "cancel_reliability": 1.0,
            "authorization_confidence": 0.95,
        }
    )
    arguments["aws_call"].update(
        {
            "tool_name": TOOL_NAME,
            "arguments": {"code": AWS_DRY_RUN_SCRIPT},
            "cost_control": {"estimated_incremental_cost_usd": 0.0},
        }
    )
    return request


def _find_dry_run_result(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        if {"error_code", "authorized", "matching_group_count", "resource_created"} <= set(value):
            return value
        for child in value.values():
            found = _find_dry_run_result(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_dry_run_result(child)
            if found is not None:
                return found
    elif isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return None
        return _find_dry_run_result(decoded)
    return None


def run_dry_run_proof(executor: Executor, *, observed_at: str | None = None) -> dict[str, Any]:
    response = AWSMCPEnforcementAdapter(executor, approved_cost_usd=0.0).handle(build_dry_run_request())
    if not isinstance(response, Mapping):
        raise RuntimeError("SMERC returned no dry-run response")
    result = response.get("result")
    if not isinstance(result, Mapping) or result.get("isError") is not False:
        raise RuntimeError("AWS dry-run execution did not succeed; no success proof was created")
    structured = result.get("structuredContent")
    if not isinstance(structured, Mapping) or not isinstance(structured.get("smerc"), Mapping):
        raise RuntimeError("SMERC returned no structured execution evidence")
    dry_run = _find_dry_run_result(structured.get("aws_result"))
    if (
        dry_run is None
        or dry_run.get("error_code") != "DryRunOperation"
        or dry_run.get("authorized") is not True
        or dry_run.get("matching_group_count") != 0
        or dry_run.get("resource_created") is not False
    ):
        raise RuntimeError("AWS did not prove authorized non-mutation; no success proof was created")
    return {
        "schema": SCHEMA,
        "observed_at": observed_at or datetime.now(timezone.utc).isoformat(),
        "evidence_class": "enforced_aws_authorization_dry_run",
        "production_evidence": False,
        "transport_enforced_for_observed_call": True,
        "estimated_incremental_cost_usd": 0.0,
        "action": {
            "server_name": "aws-mcp",
            "tool_name": TOOL_NAME,
            "operation": "EC2.CreateSecurityGroup",
            "dry_run": True,
            "sentinel_group": SENTINEL_GROUP,
        },
        "aws_observation": {
            "error_code": "DryRunOperation",
            "authorized": True,
            "matching_group_count": 0,
            "resource_created": False,
        },
        "smerc": dict(structured["smerc"]),
        "sanitation": {"credentials_stored": False, "raw_aws_response_stored": False},
        "boundary": {
            "proves": "This observed authorization dry-run crossed SMERC before AWS reported DryRunOperation, and read-back found no sentinel resource.",
            "does_not_prove": "A real mutation or rollback succeeded, that every AWS path is SMERC-enforced, or that this is production enforcement.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded SMERC-to-AWS authorization dry-run proof.")
    parser.add_argument("--confirm-dry-run", action="store_true")
    parser.add_argument("--aws-resource-region", default="us-east-1")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()
    if not args.confirm_dry_run:
        parser.error("--confirm-dry-run is required")
    executor = ManagedAWSMCPProxyExecutor(
        ["uvx", f"mcp-proxy-for-aws-cli@{PINNED_PROXY_VERSION}"],
        resource_region=args.aws_resource_region,
        timeout_seconds=args.timeout,
    )
    try:
        proof = run_dry_run_proof(executor)
    except RuntimeError as exc:
        print(json.dumps({"status": "failed_closed", "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "succeeded", "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

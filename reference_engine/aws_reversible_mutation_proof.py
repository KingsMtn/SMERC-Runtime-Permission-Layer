from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from reference_engine.aws_portable_evidence import build_aws_portable_evidence
from reference_engine.aws_mcp_dry_run_proof import PINNED_PROXY_VERSION
from reference_engine.aws_mcp_enforced_live_proof import build_request
from reference_engine.mcp_aws_enforcement_adapter import AWSMCPEnforcementAdapter, Executor, ManagedAWSMCPProxyExecutor


SCHEMA = "smerc.aws-reversible-mutation-proof.v1"
TOOL_NAME = "aws___run_script"
AWS_MUTATION_SCRIPT = '''vpcs = await call_boto3(service_name="ec2", operation_name="DescribeVpcs", region_name="us-east-1", params={"Filters": [{"Name": "is-default", "Values": ["true"]}]})
vpc_ids = [item["VpcId"] for item in vpcs.get("Vpcs", [])]
if not vpc_ids:
    result = {"status": "not_run", "resource_created": False, "resource_deleted": False, "residual_count": 0}
else:
    proof_id = uuid.uuid4().hex[:12]
    group_name = "smerc-reversible-proof-" + proof_id
    created_at = time.time()
    created = await call_boto3(service_name="ec2", operation_name="CreateSecurityGroup", region_name="us-east-1", params={"GroupName": group_name, "Description": "SMERC contained reversible mutation proof", "VpcId": vpc_ids[0], "TagSpecifications": [{"ResourceType": "security-group", "Tags": [{"Key": "Purpose", "Value": "SMERC-Reversible-Proof"}, {"Key": "AutoDelete", "Value": "true"}]}]})
    group_id = created.get("GroupId")
    delete_started_at = time.time()
    await call_boto3(service_name="ec2", operation_name="DeleteSecurityGroup", region_name="us-east-1", params={"GroupId": group_id})
    deleted_at = time.time()
    remaining = await call_boto3(service_name="ec2", operation_name="DescribeSecurityGroups", region_name="us-east-1", params={"Filters": [{"Name": "group-name", "Values": [group_name]}]})
    residual_count = len(remaining.get("SecurityGroups", []))
    result = {"status": "completed" if residual_count == 0 else "residual_detected", "proof_id": proof_id, "resource_created": True, "resource_deleted": residual_count == 0, "rollback_latency_seconds": round(deleted_at - delete_started_at, 3), "total_exposure_seconds": round(deleted_at - created_at, 3), "residual_count": residual_count, "estimated_incremental_cost_usd": 0.0}
result'''


def build_mutation_request() -> dict[str, Any]:
    request = build_request()
    request["id"] = "smerc-aws-reversible-mutation-proof"
    arguments = request["params"]["arguments"]
    governance = arguments["governance_request"]
    governance["mcp_request_id"] = "AWS_MCP_REVERSIBLE_MUTATION_001"
    governance["canonical_action_id"] = "AWS_MCP_REVERSIBLE_MUTATION_001"
    governance["agent_identity"]["credential_scope"] = "production_write"
    governance["agent_identity"]["context"] = {
        "proof": "enforced_reversible_mutation",
        "fixed_empty_security_group": True,
        "same_run_cleanup_required": True,
    }
    governance["tool_call"].update(
        {
            "tool_name": TOOL_NAME,
            "description": "Create and immediately delete one empty tagged security group, then verify zero residual state.",
            "operation_class": "reversible_write",
            "requested_capability": "ec2_security_group_create_delete_proof",
            "external_side_effect": True,
            "supports_dry_run": False,
            "supports_scope_limit": True,
            "supports_checkpoint": True,
            "supports_rollback": True,
            "supports_human_approval": True,
            "requested_scope_units": 1,
            "max_scope_units": 1,
        }
    )
    governance["risk_signals"].update(
        {
            "base_action_risk": 0.12,
            "reversibility": 1.0,
            "containment_strength": 1.0,
            "rollback_latency": 0.01,
            "evidence_validity": 0.98,
            "anomaly_pressure": 0.0,
            "impact_scope": 0.01,
            "cancel_reliability": 1.0,
            "authorization_confidence": 0.98,
        }
    )
    arguments["aws_call"].update(
        {
            "tool_name": TOOL_NAME,
            "arguments": {"code": AWS_MUTATION_SCRIPT},
            "cost_control": {"estimated_incremental_cost_usd": 0.0},
        }
    )
    return request


def build_mutation_approval() -> dict[str, str]:
    tool_arguments = {"code": AWS_MUTATION_SCRIPT}
    arguments_sha256 = hashlib.sha256(
        json.dumps(tool_arguments, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    target_sha256 = hashlib.sha256(
        json.dumps(
            {"server_name": "aws-mcp", "tool_name": TOOL_NAME, "arguments_sha256": arguments_sha256},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()
    return {
        "approver_id": "owner_confirmed_reversible_proof",
        "approved_target_sha256": target_sha256,
    }


def _find_result(value: Any) -> Mapping[str, Any] | None:
    required = {"resource_created", "resource_deleted", "rollback_latency_seconds", "residual_count"}
    if isinstance(value, Mapping):
        if required <= set(value):
            return value
        for child in value.values():
            found = _find_result(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_result(child)
            if found is not None:
                return found
    elif isinstance(value, str):
        try:
            return _find_result(json.loads(value))
        except json.JSONDecodeError:
            return None
    return None


def run_mutation_proof(
    executor: Executor,
    *,
    observed_at: str | None = None,
    repository: str = "KingsMtn/SMERC-Runtime-Permission-Layer",
    commit_sha: str = "0" * 40,
    ephemeral_ref: str = "not-observed",
) -> dict[str, Any]:
    approval = build_mutation_approval()
    response = AWSMCPEnforcementAdapter(
        executor,
        approved_cost_usd=0.0,
        approved_target_sha256=approval["approved_target_sha256"],
        approver_id=approval["approver_id"],
    ).handle(build_mutation_request())
    if not isinstance(response, Mapping) or not isinstance(response.get("result"), Mapping):
        raise RuntimeError("SMERC returned no mutation response")
    result = response["result"]
    if result.get("isError") is not False:
        raise RuntimeError("reversible mutation did not succeed; no proof was created")
    structured = result.get("structuredContent")
    if not isinstance(structured, Mapping) or not isinstance(structured.get("smerc"), Mapping):
        raise RuntimeError("SMERC returned no structured mutation evidence")
    observation = _find_result(structured.get("aws_result"))
    if (
        observation is None
        or observation.get("resource_created") is not True
        or observation.get("resource_deleted") is not True
        or observation.get("residual_count") != 0
        or not isinstance(observation.get("rollback_latency_seconds"), (int, float))
    ):
        raise RuntimeError("rollback or residual-state verification failed; no proof was created")
    proof = {
        "schema": SCHEMA,
        "observed_at": observed_at or datetime.now(timezone.utc).isoformat(),
        "evidence_class": "enforced_live_reversible_mutation",
        "production_evidence": False,
        "transport_enforced_for_observed_call": True,
        "estimated_incremental_cost_usd": 0.0,
        "aws_observation": {
            "resource_created": True,
            "resource_deleted": True,
            "rollback_latency_seconds": observation["rollback_latency_seconds"],
            "total_exposure_seconds": observation.get("total_exposure_seconds"),
            "residual_count": 0,
        },
        "smerc": dict(structured["smerc"]),
        "sanitation": {"credentials_stored": False, "raw_aws_response_stored": False, "resource_ids_stored": False},
        "boundary": {
            "proves": "This observed empty-security-group mutation crossed SMERC, completed cleanup, and returned zero residual state.",
            "does_not_prove": "Every AWS path is SMERC-enforced, unrelated resource types are recoverable, or this is production enforcement.",
        },
    }
    proof["portable_evidence"] = build_aws_portable_evidence(
        proof,
        repository=repository,
        commit_sha=commit_sha,
        ephemeral_ref=ephemeral_ref,
        workflow="aws-reversible-mutation-proof",
    )
    return proof


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded SMERC AWS reversible mutation proof.")
    parser.add_argument("--confirm-reversible-mutation", action="store_true")
    parser.add_argument("--aws-resource-region", default="us-east-1")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--repository", default="KingsMtn/SMERC-Runtime-Permission-Layer")
    parser.add_argument("--commit-sha", default="0" * 40)
    parser.add_argument("--ephemeral-ref", default="not-observed")
    args = parser.parse_args()
    if not args.confirm_reversible_mutation:
        parser.error("--confirm-reversible-mutation is required")
    executor = ManagedAWSMCPProxyExecutor(
        ["uvx", f"mcp-proxy-for-aws-cli@{PINNED_PROXY_VERSION}"],
        resource_region=args.aws_resource_region,
        timeout_seconds=args.timeout,
    )
    try:
        proof = run_mutation_proof(
            executor,
            repository=args.repository,
            commit_sha=args.commit_sha,
            ephemeral_ref=args.ephemeral_ref,
        )
    except RuntimeError as exc:
        print(json.dumps({"status": "failed_closed", "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "succeeded", "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

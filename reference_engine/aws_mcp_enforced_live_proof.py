from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from reference_engine.mcp_aws_enforcement_adapter import (
    AWSOAuthMCPExecutor,
    AWSMCPEnforcementAdapter,
    Executor,
    ManagedAWSMCPProxyExecutor,
    OAuthTokenHelperProvider,
    TOOL_NAME,
)


SCHEMA = "smerc.aws-mcp-enforced-live-proof.v1"
PINNED_PROXY_VERSION = "1.7.0"


def build_request() -> dict[str, Any]:
    governance = {
        "schema": "smerc.mcp-tool-governance.v1",
        "mcp_request_id": "AWS_MCP_LIST_REGIONS_ENFORCED_001",
        "canonical_action_id": "AWS_MCP_LIST_REGIONS_ENFORCED_001",
        "agent": {
            "agent_id": "smerc_aws_pilot",
            "display_name": "SMERC AWS Pilot",
            "provider": "smerc-runtime",
        },
        "agent_identity": {
            "version": "smerc.agent-identity.v1",
            "agent_id": "smerc_aws_pilot",
            "agent_name": "SMERC AWS Pilot",
            "agent_type": "automation_runner",
            "provider": "smerc-runtime",
            "owner_team": "smerc_labs",
            "trust_tier": "trusted",
            "authorized_tool_families": ["aws-mcp"],
            "max_autonomy_level": "execute",
            "credential_scope": "read_only",
            "recent_denials": 0,
            "recent_overrides": 0,
            "recent_success_rate": 1.0,
            "model": "deterministic-reference-runner",
            "last_reviewed_at": "2026-09-20",
            "context": {"proof": "enforced_live_read_only"},
        },
        "server": {
            "name": "aws-mcp",
            "transport": "stdio-proxy-to-streamable-http",
            "trust_boundary": "aws-managed-mcp",
        },
        "tool_call": {
            "tool_name": "list_regions",
            "description": "List AWS Regions without creating or modifying resources.",
            "operation_class": "read",
            "requested_capability": "read_region_catalog",
            "domain_profile": "general",
            "external_side_effect": False,
            "sensitive_data": False,
            "supports_dry_run": True,
            "supports_scope_limit": True,
            "supports_checkpoint": True,
            "supports_rollback": True,
            "supports_human_approval": True,
            "requested_scope_units": 1,
            "max_scope_units": 1,
            "typed_contract_valid": True,
            "attestation_valid": True,
            "least_privilege_confirmed": True,
            "object_shape_expected": True,
        },
        "risk_signals": {
            "base_action_risk": 0.02,
            "reversibility": 1.0,
            "containment_strength": 1.0,
            "rollback_latency": 0.0,
            "evidence_validity": 0.95,
            "anomaly_pressure": 0.0,
            "impact_scope": 0.01,
            "cancel_reliability": 1.0,
            "authorization_confidence": 0.95,
        },
    }
    return {
        "jsonrpc": "2.0",
        "id": "smerc-enforced-live-proof",
        "method": "tools/call",
        "params": {
            "name": TOOL_NAME,
            "arguments": {
                "runtime_admission": {
                    "version": "smerc.runtime-admission-input.v1",
                    "request_id": "aws-mcp-enforced-live-proof",
                    "checks": {
                        "identity_valid": True,
                        "session_scope_valid": True,
                        "permit_valid": True,
                        "typed_contract_valid": True,
                        "attestation_valid": True,
                        "least_privilege_confirmed": True,
                        "object_shape_expected": True,
                        "required_evidence_present": True,
                    },
                },
                "governance_request": governance,
                "aws_call": {
                    "server_name": "aws-mcp",
                    "tool_name": "list_regions",
                    "arguments": {},
                    "cost_control": {"estimated_incremental_cost_usd": 0.0},
                },
            },
        },
    }


def run_proof(executor: Executor, *, observed_at: str | None = None) -> dict[str, Any]:
    response = AWSMCPEnforcementAdapter(executor, approved_cost_usd=0.0).handle(build_request())
    if not isinstance(response, Mapping):
        raise RuntimeError("SMERC returned no proof response")
    result = response.get("result")
    if not isinstance(result, Mapping) or result.get("isError") is not False:
        raise RuntimeError("enforced AWS MCP execution did not succeed; no success proof was created")
    structured = result.get("structuredContent")
    if not isinstance(structured, Mapping) or not isinstance(structured.get("smerc"), Mapping):
        raise RuntimeError("SMERC returned no structured execution evidence")
    evidence = dict(structured["smerc"])
    return {
        "schema": SCHEMA,
        "observed_at": observed_at or datetime.now(timezone.utc).isoformat(),
        "evidence_class": "enforced_live_read_only",
        "production_evidence": False,
        "transport_enforced_for_observed_call": True,
        "action": {
            "server_name": "aws-mcp",
            "tool_name": "list_regions",
            "arguments": {},
            "external_side_effect": False,
            "estimated_incremental_cost_usd": 0.0,
        },
        "smerc": evidence,
        "sanitation": {
            "credentials_stored": False,
            "raw_aws_response_stored": False,
            "result_digest_only": True,
        },
        "boundary": {
            "proves": "This observed read-only call crossed SMERC admission and policy enforcement before the configured AWS MCP executor returned success.",
            "does_not_prove": "All alternate AWS access paths are impossible, that AWS independently attested the SMERC decision, or that this is production enforcement.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded SMERC-to-AWS MCP enforced live proof.")
    parser.add_argument("--confirm-read-only", action="store_true")
    parser.add_argument("--aws-resource-region", default="us-east-1")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--oauth-token-helper-command",
        nargs="+",
        help="Fixed argv for a host credential helper implementing smerc.oauth-token-helper.v1.",
    )
    args = parser.parse_args()
    if not args.confirm_read_only:
        parser.error("--confirm-read-only is required")
    if args.oauth_token_helper_command:
        provider = OAuthTokenHelperProvider(args.oauth_token_helper_command, timeout_seconds=args.timeout)
        executor = AWSOAuthMCPExecutor(provider, timeout_seconds=args.timeout)
    else:
        executor = ManagedAWSMCPProxyExecutor(
            ["uvx", f"mcp-proxy-for-aws-cli@{PINNED_PROXY_VERSION}"],
            resource_region=args.aws_resource_region,
            timeout_seconds=args.timeout,
        )
    try:
        proof = run_proof(executor)
    except RuntimeError as exc:
        print(json.dumps({"status": "failed_closed", "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "succeeded", "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

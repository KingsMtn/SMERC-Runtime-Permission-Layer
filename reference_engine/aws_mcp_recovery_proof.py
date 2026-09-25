from __future__ import annotations

import hashlib
import json
from typing import Any

from reference_engine.mcp_transport_proxy import run_mcp_transport_proxy

VERSION = "smerc.aws-mcp-recovery-proof.v1"


def build_capability(test_status: str = "VERIFIED") -> dict[str, Any]:
    capability = {
        "version": "smerc.recovery-capability.v1", "provider_id": "aws-mcp-cloudformation-adapter",
        "tool_family": "mcp.aws-mcp", "operation": "update_stack",
        "scope": {"resource_patterns": ["arn:aws:cloudformation:us-east-1:123456789012:stack/smerc-pilot/*"], "environment": "synthetic-pilot"},
        "mechanism": {"type": "RECREATE_FROM_DECLARATION", "isolation": "RESOURCE", "trigger": "EXTERNAL_AUTHORITY", "max_rollback_latency_seconds": 120, "validity_window_seconds": 3600},
        "evidence": {"plan_ref": "evidence://aws/cloudformation/synthetic-rollback-test", "test_status": test_status, "tested_at_ms": 1_000, "evidence_sha256": "a" * 64},
        "limits": {"max_scope_units": 1, "max_mutations": 1, "irreversible_side_effects": False},
        "authority_effect": "NONE", "advisory_only": True, "issued_at_ms": 1_000, "expires_at_ms": 2_000,
    }
    capability["capability_sha256"] = _sha(capability)
    capability["capability_id"] = f"recovery_{capability['capability_sha256'][:24]}"
    return capability


def build_envelope(test_status: str | None) -> dict[str, Any]:
    governance = {
        "schema": "smerc.mcp-tool-governance.v1", "mcp_request_id": "AWS_MCP_UPDATE_STACK_RECOVERY_001",
        "agent": {"agent_id": "smerc_aws_pilot", "display_name": "SMERC AWS Pilot", "provider": "smerc-runtime"},
        "server": {"name": "aws-mcp", "transport": "synthetic", "trust_boundary": "aws-managed-mcp"},
        "tool_call": {"tool_name": "update_stack", "description": "Synthetic CloudFormation stack update proof.", "operation_class": "write", "requested_capability": "update_cloudformation_stack", "domain_profile": "it_ops", "external_side_effect": True, "sensitive_data": False, "supports_dry_run": True, "supports_scope_limit": True, "supports_checkpoint": True, "supports_rollback": True, "supports_human_approval": True, "requested_scope_units": 1, "max_scope_units": 1},
        "risk_signals": {"base_action_risk": 0.42, "reversibility": 0.78, "containment_strength": 0.8, "rollback_latency": 0.35, "evidence_validity": 0.9, "anomaly_pressure": 0.05, "impact_scope": 0.25, "cancel_reliability": 0.82, "authorization_confidence": 0.9},
    }
    envelope = {
        "schema": "smerc.mcp-transport-proxy-envelope.v1", "proxy_request_id": "AWS_MCP_RECOVERY_TRANSPORT_001",
        "mode": "enforce", "require_recovery_boundary": True, "recovery_now_ms": 1_500,
        "mcp_jsonrpc_request": {"jsonrpc": "2.0", "id": "aws-recovery-proof", "method": "tools/call", "params": {"name": "update_stack", "arguments": {"stack": "smerc-pilot", "change_set": "synthetic"}}},
        "governance_request": governance,
        "simulated_tool_result": {"content": [{"type": "text", "text": "synthetic result"}], "isError": False},
    }
    if test_status is not None:
        envelope["recovery_boundary"] = {
            "version": "smerc.mcp-recovery-boundary.v1", "request_id": governance["mcp_request_id"],
            "server_name": "aws-mcp", "tool_name": "update_stack", "operation": "write",
            "environment": "synthetic-pilot", "requested_scope_units": 1, "requested_mutations": 1,
            "max_acceptable_rollback_latency_seconds": 180, "recovery_capability": build_capability(test_status),
        }
    return envelope


def run_proof() -> dict[str, Any]:
    cases = {}
    for name, status in (("missing", None), ("stale", "STALE"), ("verified", "VERIFIED")):
        report = run_mcp_transport_proxy(build_envelope(status))
        cases[name] = {"recovery_boundary": report["recovery_boundary"], "normal_governance_reached": report["proxy_report"] is not None, "transport_response": report["mcp_jsonrpc_response"]}
    return {
        "version": VERSION, "evidence_class": "synthetic_metadata_only",
        "aws_resources_created_or_modified": False, "incremental_aws_cost_usd": 0.0, "cases": cases,
        "result": {"missing_stopped_before_governance": not cases["missing"]["normal_governance_reached"], "stale_stopped_before_governance": not cases["stale"]["normal_governance_reached"], "verified_reached_normal_governance": cases["verified"]["normal_governance_reached"], "verified_did_not_gain_authority": cases["verified"]["recovery_boundary"]["authority_effect"] == "NONE"},
        "boundary": "This is deterministic local evidence for ordering and fail-closed behavior. It is not a live AWS call, production validation, AWS attestation, or proof that CloudFormation recovery succeeds externally.",
    }


def _sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()

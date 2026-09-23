from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from reference_engine.portable_evidence import build_portable_evidence


CLAIM_BOUNDARY = (
    "This record binds observed SMERC and AWS MCP evidence to one execution. "
    "It is not AWS attestation, proof that alternate access paths are blocked, "
    "or production certification."
)


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_aws_portable_evidence(
    proof: Mapping[str, Any],
    *,
    repository: str,
    commit_sha: str,
    ephemeral_ref: str,
    workflow: str,
    account: str = "redacted",
    region: str = "us-east-1",
) -> dict[str, Any]:
    if not isinstance(proof, Mapping) or not isinstance(proof.get("smerc"), Mapping):
        raise TypeError("proof must contain SMERC execution evidence")
    smerc = proof["smerc"]
    binding = smerc.get("execution_binding")
    result = smerc.get("execution_result")
    if not isinstance(binding, Mapping) or not isinstance(result, Mapping):
        raise ValueError("proof must contain execution binding and result evidence")
    if result.get("status") != "succeeded":
        raise ValueError("portable AWS evidence requires a succeeded execution")

    mutation = proof.get("aws_observation")
    is_mutation = isinstance(mutation, Mapping)
    if is_mutation:
        cleanup_verified = (
            mutation.get("resource_deleted") is True and mutation.get("residual_count") == 0
        )
        if not cleanup_verified:
            raise ValueError("reversible mutation evidence requires verified cleanup")
        cleanup_status = "SUCCEEDED"
        data_classes = ["cloud-control-metadata"]
    else:
        cleanup_verified = False
        cleanup_status = "NOT_REQUIRED"
        data_classes = ["cloud-metadata"]

    payload = {
        "record_id": str(binding.get("target_sha256", "")),
        "observed_at": proof.get("observed_at"),
        "workload": {
            "workload_id": "smerc-aws-mcp",
            "model_id": "deterministic-reference-runner",
            "model_digest": _digest("deterministic-reference-runner"),
        },
        "source_control": {
            "repository": repository,
            "commit_sha": commit_sha,
            "workflow": workflow,
            "ephemeral_ref": ephemeral_ref,
        },
        "runtime": {
            "platform": "aws",
            "account": account,
            "region": region,
            "principal": "SMERC-MCP-Pilot",
            "execution_boundary": "managed-aws-mcp",
        },
        "policy": {
            "policy_id": "smerc-aws-pilot",
            "policy_revision": str(smerc.get("adapter_version", "unknown")),
            "policy_bundle_sha256": _digest(
                {
                    "adapter_version": smerc.get("adapter_version"),
                    "reason_codes": smerc.get("reason_codes", []),
                    "required_controls": smerc.get("required_controls", []),
                }
            ),
            "enforcement_mode": "ENFORCE",
        },
        "decision": {
            "admission": smerc.get("admission_decision"),
            "posture": smerc.get("posture"),
            "explanation_code": (smerc.get("reason_codes") or ["NO_REASON_CODE"])[0],
            "decision_id": str(smerc.get("replay_id", "unknown")),
        },
        "tool_activity": {
            "transcript_sha256": str(result.get("result_sha256", "")),
            "call_count": 1,
            "tools": [f"{binding.get('server_name')}.{binding.get('tool_name')}"],
        },
        "containment": {
            "isolation": "bounded-single-call",
            "network_scope": "aws-mcp-only",
            "failure_contained": True,
            "cleanup_status": cleanup_status,
            "cleanup_verified": cleanup_verified,
        },
        "data_handling": {
            "data_classes": data_classes,
            "redacted_fields": ["account", "authorization", "resource_ids"],
            "secrets_persisted": False,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return build_portable_evidence(payload, issuer="smerc-reference-engine")

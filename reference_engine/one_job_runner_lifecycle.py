from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Mapping

from reference_engine.ephemeral_execution_envelope import verify_envelope
from reference_engine.portable_evidence import build_portable_evidence


VERSION = "smerc.one-job-runner-lifecycle.v1"
RESULT_FIELDS = {"status", "tool", "transcript_sha256", "failure_contained"}
CLEANUP_FIELDS = {"status", "runner_destroyed", "credentials_revoked", "ephemeral_ref_deleted"}


class OneJobLifecycleError(RuntimeError):
    def __init__(self, code: str, message: str, *, receipt: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.receipt = dict(receipt) if receipt is not None else None


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _exact(value: Any, fields: set[str], path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != fields:
        raise OneJobLifecycleError("invalid_receipt", f"{path} fields must match the contract exactly")
    return value


def _sha256(value: Any, path: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise OneJobLifecycleError("invalid_receipt", f"{path} must be a lowercase SHA-256 digest")
    return value


def run_one_job(
    envelope: Mapping[str, Any],
    *,
    now: int,
    job_id: str,
    tool: str,
    execute: Callable[[], Mapping[str, Any]],
    cleanup: Callable[[], Mapping[str, Any]],
) -> dict[str, Any]:
    """Execute one admitted operation and require independently reported cleanup.

    The caller owns runner provisioning and destruction. This function owns the
    fail-closed lifecycle contract and never retries the operation.
    """
    verified = verify_envelope(envelope, now=now)
    if verified["state"] != "ACTIVE":
        raise OneJobLifecycleError("envelope_not_active", "one-job execution requires an ACTIVE envelope")
    if not isinstance(job_id, str) or not job_id.strip():
        raise OneJobLifecycleError("invalid_job", "job_id must be non-empty")
    if not isinstance(tool, str) or not tool.strip():
        raise OneJobLifecycleError("invalid_job", "tool must be non-empty")

    execution: Mapping[str, Any] | None = None
    execution_error: Exception | None = None
    try:
        execution = execute()
    except Exception as exc:  # cleanup must still run after executor failure
        execution_error = exc

    try:
        cleanup_receipt = _validate_cleanup(cleanup())
    except Exception as exc:
        partial = _receipt(verified, job_id, tool, execution, None, execution_error)
        raise OneJobLifecycleError(
            "cleanup_unverified", "runner cleanup could not be verified", receipt=partial
        ) from exc

    receipt = _receipt(verified, job_id, tool, execution, cleanup_receipt, execution_error)
    if not receipt["cleanup_verified"]:
        raise OneJobLifecycleError("cleanup_unverified", "runner cleanup did not complete", receipt=receipt)
    if execution_error is not None:
        raise OneJobLifecycleError("execution_failed", "job execution failed after verified cleanup", receipt=receipt) from execution_error
    return receipt


def _validate_execution(value: Any, expected_tool: str) -> Mapping[str, Any]:
    result = _exact(value, RESULT_FIELDS, "execution")
    if result["status"] not in {"SUCCEEDED", "FAILED"}:
        raise OneJobLifecycleError("invalid_receipt", "execution.status must be SUCCEEDED or FAILED")
    if result["tool"] != expected_tool:
        raise OneJobLifecycleError("tool_mismatch", "executor returned a different tool")
    _sha256(result["transcript_sha256"], "execution.transcript_sha256")
    if not isinstance(result["failure_contained"], bool):
        raise OneJobLifecycleError("invalid_receipt", "execution.failure_contained must be boolean")
    return result


def _validate_cleanup(value: Any) -> Mapping[str, Any]:
    result = _exact(value, CLEANUP_FIELDS, "cleanup")
    if result["status"] not in {"SUCCEEDED", "FAILED"}:
        raise OneJobLifecycleError("invalid_receipt", "cleanup.status must be SUCCEEDED or FAILED")
    for field in CLEANUP_FIELDS - {"status"}:
        if not isinstance(result[field], bool):
            raise OneJobLifecycleError("invalid_receipt", f"cleanup.{field} must be boolean")
    return result


def _receipt(
    envelope: Mapping[str, Any], job_id: str, tool: str,
    execution: Mapping[str, Any] | None, cleanup: Mapping[str, Any] | None,
    execution_error: Exception | None,
) -> dict[str, Any]:
    valid_execution = None
    if execution is not None:
        valid_execution = dict(_validate_execution(execution, tool))
    cleanup_verified = bool(
        cleanup
        and cleanup["status"] == "SUCCEEDED"
        and cleanup["runner_destroyed"]
        and cleanup["credentials_revoked"]
        and cleanup["ephemeral_ref_deleted"]
    )
    material = {
        "version": VERSION,
        "job_id": job_id.strip(),
        "envelope_id": envelope["envelope_id"],
        "envelope_sha256": envelope["envelope_sha256"],
        "operation_count": 1,
        "tool": tool.strip(),
        "execution": valid_execution,
        "execution_error": type(execution_error).__name__ if execution_error else None,
        "cleanup": dict(cleanup) if cleanup else None,
        "cleanup_verified": cleanup_verified,
    }
    return {**material, "receipt_sha256": _digest(material)}


def build_one_job_portable_evidence(
    receipt: Mapping[str, Any], payload: Mapping[str, Any], *, issuer: str,
    key_id: str | None = None, signing_key: bytes | None = None,
) -> dict[str, Any]:
    if receipt.get("version") != VERSION or receipt.get("operation_count") != 1:
        raise OneJobLifecycleError("invalid_receipt", "receipt is not a one-job lifecycle receipt")
    if receipt.get("receipt_sha256") != _digest({k: v for k, v in receipt.items() if k != "receipt_sha256"}):
        raise OneJobLifecycleError("invalid_receipt", "receipt digest mismatch")
    evidence = {key: dict(value) if isinstance(value, Mapping) else value for key, value in payload.items()}
    execution = receipt.get("execution")
    evidence["tool_activity"] = {
        "transcript_sha256": execution["transcript_sha256"] if execution else _digest("execution-error"),
        "call_count": 1 if execution else 0,
        "tools": [receipt["tool"]] if execution else [],
    }
    evidence["containment"] = {
        "isolation": "one-job-ephemeral-runner",
        "network_scope": "brokered-only",
        "failure_contained": bool(execution and execution["failure_contained"]),
        "cleanup_status": "SUCCEEDED" if receipt.get("cleanup_verified") else "UNVERIFIED",
        "cleanup_verified": bool(receipt.get("cleanup_verified")),
    }
    return build_portable_evidence(
        evidence, issuer=issuer, key_id=key_id, signing_key=signing_key,
    )

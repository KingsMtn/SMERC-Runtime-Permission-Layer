from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any, Dict, Mapping, Optional


VERSION = "smerc.portable-evidence.v1"
AUTHENTICATION_METHODS = {"sha256", "hmac_sha256"}
TOP_LEVEL_FIELDS = {
    "version", "record_id", "observed_at", "workload", "source_control", "runtime",
    "policy", "decision", "tool_activity", "containment", "data_handling", "verification",
    "claim_boundary",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _unsigned(record: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in record.items() if key != "verification"}


def build_portable_evidence(
    payload: Mapping[str, Any],
    *,
    issuer: str,
    key_id: Optional[str] = None,
    signing_key: Optional[bytes] = None,
) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be an object")
    record = dict(payload)
    record["version"] = VERSION
    _validate_unsigned(record)
    issuer = _identifier(issuer, "issuer")
    if (key_id is None) != (signing_key is None):
        raise ValueError("key_id and signing_key must be supplied together")
    unsigned_sha256 = _digest(record)
    if signing_key is None:
        verification = {
            "method": "sha256",
            "issuer": issuer,
            "key_id": None,
            "payload_sha256": unsigned_sha256,
            "signature": None,
        }
    else:
        if len(signing_key) < 32:
            raise ValueError("signing_key must contain at least 32 bytes")
        verification = {
            "method": "hmac_sha256",
            "issuer": issuer,
            "key_id": _identifier(key_id, "key_id"),
            "payload_sha256": unsigned_sha256,
            "signature": hmac.new(signing_key, canonical_json(record).encode("utf-8"), hashlib.sha256).hexdigest(),
        }
    return {**record, "verification": verification}


def verify_portable_evidence(record: Mapping[str, Any], *, verification_key: Optional[bytes] = None) -> Dict[str, Any]:
    if not isinstance(record, Mapping):
        raise TypeError("record must be an object")
    if set(record) != TOP_LEVEL_FIELDS:
        missing = sorted(TOP_LEVEL_FIELDS - set(record))
        unknown = sorted(set(record) - TOP_LEVEL_FIELDS)
        raise ValueError(f"record fields are invalid; missing={missing}, unknown={unknown}")
    unsigned = _unsigned(record)
    _validate_unsigned(unsigned)
    verification = record["verification"]
    _exact(verification, {"method", "issuer", "key_id", "payload_sha256", "signature"}, "verification")
    method = verification["method"]
    if method not in AUTHENTICATION_METHODS:
        raise ValueError("verification.method is not supported")
    _identifier(verification["issuer"], "verification.issuer")
    _sha256(verification["payload_sha256"], "verification.payload_sha256")
    expected_digest = _digest(unsigned)
    if not hmac.compare_digest(verification["payload_sha256"], expected_digest):
        raise ValueError("verification.payload_sha256 does not match the record")
    if method == "hmac_sha256":
        _identifier(verification["key_id"], "verification.key_id")
        _sha256(verification["signature"], "verification.signature")
        if verification_key is None:
            raise ValueError("verification_key is required for authenticated evidence")
        expected = hmac.new(
            verification_key, canonical_json(unsigned).encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(verification["signature"], expected):
            raise ValueError("verification.signature is invalid")
        status = "AUTHENTICATED"
    else:
        if verification["key_id"] is not None or verification["signature"] is not None:
            raise ValueError("hash-only evidence cannot contain key_id or signature")
        status = "HASH_VERIFIED"
    return {
        "status": status,
        "version": VERSION,
        "record_id": record["record_id"],
        "payload_sha256": expected_digest,
        "issuer": verification["issuer"],
        "cleanup_verified": record["containment"]["cleanup_verified"],
    }


def _validate_unsigned(record: Mapping[str, Any]) -> None:
    required = TOP_LEVEL_FIELDS - {"verification"}
    _exact(record, required, "record")
    if record["version"] != VERSION:
        raise ValueError(f"version must be {VERSION}")
    _identifier(record["record_id"], "record_id")
    _text(record["observed_at"], "observed_at", 64)
    sections = {
        "workload": {"workload_id", "model_id", "model_digest"},
        "source_control": {"repository", "commit_sha", "workflow", "ephemeral_ref"},
        "runtime": {"platform", "account", "region", "principal", "execution_boundary"},
        "policy": {"policy_id", "policy_revision", "policy_bundle_sha256", "enforcement_mode"},
        "decision": {"admission", "posture", "explanation_code", "decision_id"},
        "tool_activity": {"transcript_sha256", "call_count", "tools"},
        "containment": {"isolation", "network_scope", "failure_contained", "cleanup_status", "cleanup_verified"},
        "data_handling": {"data_classes", "redacted_fields", "secrets_persisted"},
    }
    for name, fields in sections.items():
        value = record[name]
        if not isinstance(value, Mapping):
            raise TypeError(f"{name} must be an object")
        _exact(value, fields, name)
    for path, value in (
        ("workload.model_digest", record["workload"]["model_digest"]),
        ("policy.policy_bundle_sha256", record["policy"]["policy_bundle_sha256"]),
        ("tool_activity.transcript_sha256", record["tool_activity"]["transcript_sha256"]),
    ):
        _sha256(value, path)
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", str(record["source_control"]["commit_sha"])):
        raise ValueError("source_control.commit_sha must be a full Git commit digest")
    if record["decision"]["admission"] not in {"ADMIT", "REJECT"}:
        raise ValueError("decision.admission must be ADMIT or REJECT")
    if record["decision"]["posture"] not in {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}:
        raise ValueError("decision.posture is invalid")
    if record["policy"]["enforcement_mode"] not in {"OBSERVE", "ENFORCE"}:
        raise ValueError("policy.enforcement_mode must be OBSERVE or ENFORCE")
    if not isinstance(record["tool_activity"]["call_count"], int) or record["tool_activity"]["call_count"] < 0:
        raise ValueError("tool_activity.call_count must be a non-negative integer")
    for path, value in (
        ("containment.failure_contained", record["containment"]["failure_contained"]),
        ("containment.cleanup_verified", record["containment"]["cleanup_verified"]),
        ("data_handling.secrets_persisted", record["data_handling"]["secrets_persisted"]),
    ):
        if not isinstance(value, bool):
            raise TypeError(f"{path} must be a boolean")
    if record["containment"]["cleanup_status"] not in {"NOT_REQUIRED", "SUCCEEDED", "FAILED", "UNVERIFIED"}:
        raise ValueError("containment.cleanup_status is invalid")
    if record["containment"]["cleanup_verified"] and record["containment"]["cleanup_status"] != "SUCCEEDED":
        raise ValueError("verified cleanup requires cleanup_status SUCCEEDED")
    if record["data_handling"]["secrets_persisted"]:
        raise ValueError("portable evidence must never claim that secrets were persisted")
    _text(record["claim_boundary"], "claim_boundary", 1024)


def _exact(value: Mapping[str, Any], fields: set[str], path: str) -> None:
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields)
    if missing or unknown:
        raise ValueError(f"{path} fields are invalid; missing={missing}, unknown={unknown}")


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{path} must be non-empty and at most {maximum} characters")
    return value.strip()


def _identifier(value: Any, path: str) -> str:
    text = _text(value, path, 192)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{0,191}", text):
        raise ValueError(f"{path} must be a safe identifier")
    return text


def _sha256(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError(f"{path} must be a lowercase SHA-256 digest")
    return value

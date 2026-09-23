from __future__ import annotations

import hashlib
import hmac
import json
import re
from typing import Any, Mapping

from reference_engine.portable_evidence import verify_portable_evidence


VERSION = "smerc.aws-external-outcome-label.v1"
SOURCE_TYPES = {"HUMAN_REVIEW", "INCIDENT_OUTCOME", "CUSTOMER_POSTCONDITION"}
FIELDS = {
    "version", "label_id", "record_id", "record_payload_sha256", "source_type",
    "reviewer_id", "observed_at", "judged_correct", "unexpected_consequences",
    "controls_sufficient", "rationale", "verification",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _identifier(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{0,191}", value):
        raise ValueError(f"{path} must be a safe identifier")
    return value


def _validate_unsigned(label: Mapping[str, Any]) -> None:
    required = FIELDS - {"verification"}
    if set(label) != required:
        raise ValueError("external outcome label fields are invalid")
    if label["version"] != VERSION:
        raise ValueError(f"version must be {VERSION}")
    for field in ("label_id", "record_id", "reviewer_id"):
        _identifier(label[field], field)
    if label["source_type"] not in SOURCE_TYPES:
        raise ValueError("source_type is invalid")
    if not isinstance(label["observed_at"], str) or not label["observed_at"].strip():
        raise ValueError("observed_at must be non-empty")
    for field in ("judged_correct", "unexpected_consequences", "controls_sufficient"):
        if not isinstance(label[field], bool):
            raise TypeError(f"{field} must be a boolean")
    if not isinstance(label["rationale"], str) or not label["rationale"].strip() or len(label["rationale"]) > 1024:
        raise ValueError("rationale must be non-empty and at most 1024 characters")
    if not isinstance(label["record_payload_sha256"], str) or not re.fullmatch(
        r"[0-9a-f]{64}", label["record_payload_sha256"]
    ):
        raise ValueError("record_payload_sha256 must be a lowercase SHA-256 digest")


def build_external_outcome_label(
    record: Mapping[str, Any],
    *,
    label_id: str,
    source_type: str,
    reviewer_id: str,
    observed_at: str,
    judged_correct: bool,
    unexpected_consequences: bool,
    controls_sufficient: bool,
    rationale: str,
    key_id: str,
    signing_key: bytes,
) -> dict[str, Any]:
    record_verification = verify_portable_evidence(record)
    if len(signing_key) < 32:
        raise ValueError("signing_key must contain at least 32 bytes")
    label = {
        "version": VERSION,
        "label_id": label_id,
        "record_id": record["record_id"],
        "record_payload_sha256": record_verification["payload_sha256"],
        "source_type": source_type,
        "reviewer_id": reviewer_id,
        "observed_at": observed_at,
        "judged_correct": judged_correct,
        "unexpected_consequences": unexpected_consequences,
        "controls_sufficient": controls_sufficient,
        "rationale": rationale,
    }
    _validate_unsigned(label)
    verification = {
        "method": "hmac_sha256",
        "key_id": _identifier(key_id, "key_id"),
        "signature": hmac.new(signing_key, _canonical(label).encode("utf-8"), hashlib.sha256).hexdigest(),
    }
    return {**label, "verification": verification}


def verify_external_outcome_label(
    label: Mapping[str, Any], record: Mapping[str, Any], *, verification_key: bytes
) -> dict[str, Any]:
    if set(label) != FIELDS:
        raise ValueError("external outcome label fields are invalid")
    unsigned = {key: value for key, value in label.items() if key != "verification"}
    _validate_unsigned(unsigned)
    verification = label["verification"]
    if not isinstance(verification, Mapping) or set(verification) != {"method", "key_id", "signature"}:
        raise ValueError("label verification fields are invalid")
    if verification["method"] != "hmac_sha256":
        raise ValueError("label verification method is invalid")
    _identifier(verification["key_id"], "verification.key_id")
    expected = hmac.new(verification_key, _canonical(unsigned).encode("utf-8"), hashlib.sha256).hexdigest()
    if not isinstance(verification["signature"], str) or not hmac.compare_digest(verification["signature"], expected):
        raise ValueError("external outcome label signature is invalid")
    record_verification = verify_portable_evidence(record)
    if label["record_id"] != record["record_id"] or label["record_payload_sha256"] != record_verification["payload_sha256"]:
        raise ValueError("external outcome label is not bound to this evidence record")
    return {
        "status": "AUTHENTICATED",
        "label_id": label["label_id"],
        "source_type": label["source_type"],
        "record_id": label["record_id"],
    }

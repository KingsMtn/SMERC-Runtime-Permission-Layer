from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


VERSION = "smerc.runtime-assurance.recovery-capability-evaluation.v1"
CONTRACT_VERSION = "smerc.recovery-capability.v1"
MECHANISMS = {
    "TRANSACTION_ROLLBACK", "SNAPSHOT_RESTORE", "COMPENSATING_ACTION",
    "VERSION_RESTORE", "RECREATE_FROM_DECLARATION", "NONE",
}
ISOLATION = {"SESSION", "ACTION", "RESOURCE", "ENVIRONMENT", "NONE"}
TRIGGERS = {"AUTOMATED", "MANUAL", "EXTERNAL_AUTHORITY"}
TEST_STATES = {"VERIFIED", "STALE", "UNVERIFIED", "FAILED"}


def evaluate_recovery_capability(
    capability: Mapping[str, Any], *, now_ms: int, expected_tool_family: str,
    expected_operation: str, expected_environment: str,
    requested_scope_units: float, requested_mutations: int,
    max_acceptable_rollback_latency_seconds: int,
) -> dict[str, Any]:
    """Evaluate typed recovery evidence without converting it into authority."""
    try:
        _validate(
            capability, now_ms=now_ms, expected_tool_family=expected_tool_family,
            expected_operation=expected_operation, expected_environment=expected_environment,
        )
    except ValueError as exc:
        return _result("REJECT", "DENY", ["RECOVERY_CAPABILITY_INVALID"],
            ["replace_recovery_capability_before_execution"], str(exc), capability)

    mechanism = capability["mechanism"]
    evidence = capability["evidence"]
    limits = capability["limits"]
    if mechanism["type"] == "NONE" or mechanism["isolation"] == "NONE":
        return _result("REJECT", "DENY", ["RECOVERY_MECHANISM_ABSENT"],
            ["provide_bounded_recovery_mechanism"],
            "The declared recovery capability has no bounded recovery mechanism.", capability)
    if limits["irreversible_side_effects"]:
        return _result("REJECT", "DENY", ["IRREVERSIBLE_SIDE_EFFECT_DECLARED"],
            ["remove_irreversible_side_effect_or_require_separate_policy"],
            "The operation declares an irreversible side effect that this capability cannot recover.", capability)
    if evidence["test_status"] == "FAILED":
        return _result("REJECT", "DENY", ["RECOVERY_TEST_FAILED"],
            ["repair_and_retest_recovery_mechanism"],
            "The recovery mechanism failed its supplied verification test.", capability)
    if evidence["test_status"] in {"STALE", "UNVERIFIED"}:
        return _result("CONSTRAIN", "FREEZE", [f"RECOVERY_EVIDENCE_{evidence['test_status']}"],
            ["verify_recovery_mechanism_before_execution"],
            "The recovery mechanism is declared but lacks fresh verified evidence.", capability)
    if requested_scope_units > limits["max_scope_units"] or requested_mutations > limits["max_mutations"]:
        return _result("CONSTRAIN", "FREEZE", ["RECOVERY_CAPABILITY_LIMIT_EXCEEDED"],
            ["reduce_action_scope_or_supply_broader_verified_recovery"],
            "The requested action exceeds the verified recovery capability limits.", capability)
    if mechanism["max_rollback_latency_seconds"] > max_acceptable_rollback_latency_seconds:
        return _result("CONSTRAIN", "FREEZE", ["RECOVERY_LATENCY_TOO_HIGH"],
            ["provide_faster_recovery_or_obtain_review"],
            "The verified rollback latency exceeds the runtime action's acceptable recovery window.", capability)
    return _result("ACCEPT_EVIDENCE", None, ["RECOVERY_CAPABILITY_VERIFIED"], [],
        "The typed recovery capability passed scope, integrity, freshness, test, limit, and latency checks. "
        "It adds no permission; Runtime Assurance must still apply every other gate.", capability)


def _validate(capability: Mapping[str, Any], *, now_ms: int, expected_tool_family: str,
    expected_operation: str, expected_environment: str) -> None:
    if not isinstance(capability, Mapping):
        raise ValueError("recovery capability must be an object")
    required = {
        "version", "capability_id", "provider_id", "tool_family", "operation", "scope",
        "mechanism", "evidence", "limits", "authority_effect", "advisory_only",
        "issued_at_ms", "expires_at_ms", "capability_sha256",
    }
    if set(capability) != required or capability.get("version") != CONTRACT_VERSION:
        raise ValueError("recovery capability fields or version are invalid")
    if capability["authority_effect"] != "NONE" or capability["advisory_only"] is not True:
        raise ValueError("recovery capability cannot grant authority")
    for field in ("provider_id", "tool_family", "operation"):
        _text(capability[field], field)
    if capability["tool_family"] != expected_tool_family or capability["operation"] != expected_operation:
        raise ValueError("recovery capability does not match the runtime tool operation")
    scope = capability["scope"]
    if not isinstance(scope, Mapping) or set(scope) != {"resource_patterns", "environment"}:
        raise ValueError("recovery capability scope is invalid")
    patterns = scope["resource_patterns"]
    if not isinstance(patterns, list) or not patterns or patterns != sorted(set(patterns)):
        raise ValueError("resource_patterns must be non-empty, unique, and sorted")
    for pattern in patterns:
        _text(pattern, "resource_patterns")
    if scope["environment"] != expected_environment:
        raise ValueError("recovery capability environment does not match the runtime action")
    mechanism = capability["mechanism"]
    if not isinstance(mechanism, Mapping) or set(mechanism) != {
        "type", "isolation", "trigger", "max_rollback_latency_seconds", "validity_window_seconds"
    }:
        raise ValueError("recovery mechanism fields are invalid")
    if mechanism["type"] not in MECHANISMS or mechanism["isolation"] not in ISOLATION or mechanism["trigger"] not in TRIGGERS:
        raise ValueError("recovery mechanism vocabulary is invalid")
    latency = _integer(mechanism["max_rollback_latency_seconds"], "max_rollback_latency_seconds")
    window = _integer(mechanism["validity_window_seconds"], "validity_window_seconds")
    if window < 1:
        raise ValueError("validity_window_seconds must be positive")
    evidence = capability["evidence"]
    if not isinstance(evidence, Mapping) or set(evidence) != {"plan_ref", "test_status", "tested_at_ms", "evidence_sha256"}:
        raise ValueError("recovery evidence fields are invalid")
    _text(evidence["plan_ref"], "plan_ref")
    if evidence["test_status"] not in TEST_STATES:
        raise ValueError("recovery test status is invalid")
    _integer(evidence["tested_at_ms"], "tested_at_ms")
    _digest(evidence["evidence_sha256"], "evidence_sha256")
    limits = capability["limits"]
    if not isinstance(limits, Mapping) or set(limits) != {"max_scope_units", "max_mutations", "irreversible_side_effects"}:
        raise ValueError("recovery capability limits are invalid")
    _number(limits["max_scope_units"], "max_scope_units")
    _integer(limits["max_mutations"], "max_mutations")
    if not isinstance(limits["irreversible_side_effects"], bool):
        raise ValueError("irreversible_side_effects must be a boolean")
    issued = _integer(capability["issued_at_ms"], "issued_at_ms")
    expires = _integer(capability["expires_at_ms"], "expires_at_ms")
    if expires <= issued or expires - issued > window * 1000:
        raise ValueError("recovery capability validity window is invalid")
    if now_ms < issued or now_ms >= expires:
        raise ValueError("recovery capability is not currently valid")
    supplied = _digest(capability["capability_sha256"], "capability_sha256")
    unsigned = {key: value for key, value in capability.items() if key not in {"capability_id", "capability_sha256"}}
    if supplied != _sha(unsigned) or capability["capability_id"] != f"recovery_{supplied[:24]}":
        raise ValueError("recovery capability digest or identifier does not match its content")


def _result(decision: str, posture: str | None, reasons: list[str], controls: list[str],
    summary: str, capability: Mapping[str, Any]) -> dict[str, Any]:
    return {"version": VERSION, "decision": decision, "max_recommended_posture": posture,
        "reason_codes": reasons, "required_controls": controls, "authority_effect": "NONE",
        "capability_id": capability.get("capability_id") if isinstance(capability, Mapping) else None,
        "plain_english_summary": summary}


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(f"{path} must be non-empty text")
    return value


def _integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{path} must be a non-negative integer")
    return value


def _number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{path} must be a non-negative number")
    return float(value)


def _digest(value: Any, path: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(f"{path} must be a lowercase SHA-256 digest")
    return value


def _sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()

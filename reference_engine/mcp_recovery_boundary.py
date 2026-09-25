from __future__ import annotations

from typing import Any, Mapping

from reference_engine.recovery_capability_contract import evaluate_recovery_capability


VERSION = "smerc.mcp-recovery-boundary.v1"
MUTATING_OPERATIONS = {"write", "execute", "deploy", "delete", "payment"}


def evaluate_mcp_recovery_boundary(envelope: Mapping[str, Any], *, now_ms: int) -> dict[str, Any]:
    """Admit an MCP call to downstream governance; never authorize tool execution."""
    try:
        request = _validate_envelope(envelope)
    except (TypeError, ValueError) as exc:
        return _boundary_result("REJECT", "DENY", False, ["MCP_RECOVERY_BOUNDARY_INVALID"], str(exc), None)

    operation = request["operation"]
    capability = request.get("recovery_capability")
    if operation in MUTATING_OPERATIONS and capability is None:
        return _boundary_result(
            "REJECT", "DENY", False, ["MCP_RECOVERY_CAPABILITY_REQUIRED"],
            "A mutating MCP call must supply typed recovery capability evidence before downstream governance.", None,
        )
    if capability is None:
        return _boundary_result(
            "ADMIT_READ_ONLY", None, True, ["MCP_READ_ONLY_NO_RECOVERY_CAPABILITY_REQUIRED"],
            "The read-only call may continue to downstream Runtime Assurance checks. This boundary adds no authority.", None,
        )

    evaluation = evaluate_recovery_capability(
        capability,
        now_ms=now_ms,
        expected_tool_family=f"mcp.{request['server_name']}",
        expected_operation=request["tool_name"],
        expected_environment=request["environment"],
        requested_scope_units=request["requested_scope_units"],
        requested_mutations=request["requested_mutations"],
        max_acceptable_rollback_latency_seconds=request["max_acceptable_rollback_latency_seconds"],
    )
    if evaluation["decision"] == "ACCEPT_EVIDENCE":
        return _boundary_result(
            "ADMIT_TO_GOVERNANCE", None, True, evaluation["reason_codes"],
            "Typed recovery evidence passed the MCP boundary. The call is only eligible for downstream identity, "
            "policy, recoverability, routing, permit, and enforcement checks; it is not authorized to execute.", evaluation,
        )
    return _boundary_result(
        "HOLD" if evaluation["max_recommended_posture"] == "FREEZE" else "REJECT",
        evaluation["max_recommended_posture"], False, evaluation["reason_codes"],
        evaluation["plain_english_summary"], evaluation,
    )


def _validate_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, Mapping):
        raise TypeError("MCP recovery boundary envelope must be an object")
    required = {
        "version", "request_id", "server_name", "tool_name", "operation", "environment",
        "requested_scope_units", "requested_mutations", "max_acceptable_rollback_latency_seconds",
    }
    allowed = required | {"recovery_capability"}
    if set(envelope) - allowed or required - set(envelope):
        raise ValueError("MCP recovery boundary envelope fields are invalid")
    if envelope["version"] != VERSION:
        raise ValueError(f"version must be {VERSION}")
    result = dict(envelope)
    for field in ("request_id", "server_name", "tool_name", "environment"):
        result[field] = _text(result[field], field)
    operation = _text(result["operation"], "operation")
    if operation not in MUTATING_OPERATIONS | {"read"}:
        raise ValueError("operation is not supported by the MCP recovery boundary")
    result["operation"] = operation
    result["requested_scope_units"] = _number(result["requested_scope_units"], "requested_scope_units")
    result["requested_mutations"] = _integer(result["requested_mutations"], "requested_mutations")
    result["max_acceptable_rollback_latency_seconds"] = _integer(
        result["max_acceptable_rollback_latency_seconds"], "max_acceptable_rollback_latency_seconds"
    )
    capability = result.get("recovery_capability")
    if capability is not None and not isinstance(capability, Mapping):
        raise TypeError("recovery_capability must be an object")
    return result


def _boundary_result(state: str, posture: str | None, eligible: bool, reasons: list[str],
    summary: str, evaluation: Mapping[str, Any] | None) -> dict[str, Any]:
    return {
        "version": VERSION,
        "boundary_state": state,
        "eligible_for_downstream_governance": eligible,
        "should_execute_tool": False,
        "max_recommended_posture": posture,
        "reason_codes": reasons,
        "authority_effect": "NONE",
        "recovery_evaluation": dict(evaluation) if evaluation is not None else None,
        "plain_english_summary": summary,
    }


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(f"{field} must be non-empty text")
    return value.strip()


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{field} must be a non-negative number")
    return float(value)

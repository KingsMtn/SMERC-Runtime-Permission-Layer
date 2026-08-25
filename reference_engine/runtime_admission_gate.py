from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


RUNTIME_ADMISSION_GATE_VERSION = "smerc.runtime-admission-gate.v1"
ADMISSION_INPUT_VERSION = "smerc.runtime-admission-input.v1"

ADMISSION_CHECKS = {
    "identity_valid": "identity_invalid",
    "session_scope_valid": "session_scope_invalid",
    "permit_valid": "permit_invalid",
    "typed_contract_valid": "typed_contract_invalid",
    "attestation_valid": "attestation_invalid",
    "least_privilege_confirmed": "least_privilege_unconfirmed",
    "object_shape_expected": "object_shape_unexpected",
    "required_evidence_present": "required_evidence_missing",
}

DEFAULT_REQUIRED_CHECKS = (
    "identity_valid",
    "session_scope_valid",
    "typed_contract_valid",
    "attestation_valid",
    "least_privilege_confirmed",
    "object_shape_expected",
)


def evaluate_runtime_admission_gate(payload: Mapping[str, Any], *, required: bool = True) -> Dict[str, Any]:
    data = _object(payload, "admission")
    if data.get("version", ADMISSION_INPUT_VERSION) != ADMISSION_INPUT_VERSION:
        raise ValueError(f"admission.version must be {ADMISSION_INPUT_VERSION}")
    request_id = _text(data.get("request_id", "unknown-request"), "admission.request_id", 160)
    checks_payload = _object(data.get("checks", data), "admission.checks")
    required_checks = _required_checks(data.get("required_checks"), required=required)

    checks: dict[str, dict[str, Any]] = {}
    failed_required = []
    missing_required = []
    warning_drivers = []
    for field in ADMISSION_CHECKS:
        check_required = field in required_checks
        if field in checks_payload:
            value = _bool(checks_payload[field], f"admission.checks.{field}")
            source = "explicit"
        else:
            value = not check_required
            source = "missing"
        checks[field] = {"value": value, "required": check_required, "source": source}
        if check_required and source == "missing":
            missing_required.append(field)
        if check_required and not value:
            failed_required.append(field)
        elif not check_required and not value:
            warning_drivers.append(ADMISSION_CHECKS[field])

    if failed_required:
        decision = "REJECT"
        max_posture = "DENY"
    elif warning_drivers:
        decision = "ESCALATE"
        max_posture = "FREEZE"
    else:
        decision = "ADMIT"
        max_posture = "ALLOW"

    reason_codes = _reason_codes(decision, failed_required, missing_required, warning_drivers)
    return {
        "version": RUNTIME_ADMISSION_GATE_VERSION,
        "generated_at": _now(),
        "request_id": request_id,
        "decision": decision,
        "admissible_for_recoverability_scoring": decision == "ADMIT",
        "max_recommended_posture": max_posture,
        "drivers": [ADMISSION_CHECKS[field] for field in failed_required] + warning_drivers,
        "failed_required_checks": failed_required,
        "missing_required_checks": missing_required,
        "checks": checks,
        "reason_codes": reason_codes,
        "required_controls": _controls(decision, failed_required, warning_drivers),
        "plain_english_summary": _summary(decision, failed_required, warning_drivers),
        "claim_boundary": (
            "The runtime admission gate is a deterministic pre-scoring check. It does not authenticate a remote "
            "system by itself, prove compliance, or replace IAM, OPA, API validation, endpoint type checking, "
            "or customer-specific policy."
        ),
    }


def ref_gate_compat_report(payload: Mapping[str, Any], *, required: bool = True) -> Dict[str, Any]:
    report = evaluate_runtime_admission_gate(
        {
            "version": ADMISSION_INPUT_VERSION,
            "request_id": str(payload.get("request_id", payload.get("mcp_request_id", "unknown-request"))),
            "required_checks": [
                "typed_contract_valid",
                "attestation_valid",
                "least_privilege_confirmed",
                "object_shape_expected",
            ],
            "checks": {
                "typed_contract_valid": payload.get("typed_contract_valid"),
                "attestation_valid": payload.get("attestation_valid"),
                "least_privilege_confirmed": payload.get("least_privilege_confirmed"),
                "object_shape_expected": payload.get("object_shape_expected"),
            },
        },
        required=required,
    )
    return {
        "pattern": "deterministic_pre_execution_ref_gate",
        "status": "pass" if report["decision"] == "ADMIT" else "fail",
        "required": required,
        "drivers": report["drivers"],
        "checks": {
            key: {"value": value["value"], "source": value["source"]}
            for key, value in report["checks"].items()
            if key in {
                "typed_contract_valid",
                "attestation_valid",
                "least_privilege_confirmed",
                "object_shape_expected",
            }
        },
        "admission_gate": report,
    }


def _required_checks(value: Any, *, required: bool) -> tuple[str, ...]:
    if value is None:
        return DEFAULT_REQUIRED_CHECKS if required else ()
    if not isinstance(value, list):
        raise TypeError("admission.required_checks must be a list when provided")
    checks = tuple(_text(item, f"admission.required_checks[{index}]", 128) for index, item in enumerate(value))
    unknown = sorted(set(checks) - set(ADMISSION_CHECKS))
    if unknown:
        raise ValueError(f"admission.required_checks contains unknown check(s): {', '.join(unknown)}")
    if len(set(checks)) != len(checks):
        raise ValueError("admission.required_checks must not contain duplicates")
    return checks


def _reason_codes(
    decision: str,
    failed_required: list[str],
    missing_required: list[str],
    warning_drivers: list[str],
) -> list[str]:
    codes = [f"RUNTIME_ADMISSION_{decision}"]
    codes.extend(ADMISSION_CHECKS[field].upper() for field in failed_required)
    codes.extend(f"{field}_MISSING".upper() for field in missing_required)
    codes.extend(driver.upper() for driver in warning_drivers)
    return codes


def _controls(decision: str, failed_required: list[str], warning_drivers: list[str]) -> list[str]:
    if decision == "ADMIT":
        return ["continue_to_recoverability_scoring"]
    controls = ["do_not_use_recoverability_to_rescue_failed_admission"]
    if failed_required:
        controls.append("reject_before_scoring")
    if warning_drivers:
        controls.append("route_to_review_before_execution")
    controls.append("collect_valid_runtime_admission_evidence")
    return controls


def _summary(decision: str, failed_required: list[str], warning_drivers: list[str]) -> str:
    if decision == "ADMIT":
        return "The request passed deterministic runtime admission checks and may proceed to recoverability scoring."
    if failed_required:
        return (
            "The request failed required runtime admission checks. It must not be rescued by recoverability scoring; "
            "reject or hold it before execution."
        )
    return (
        "The request passed required checks but has non-required admission warnings. Escalate or hold before execution "
        "unless a reviewer accepts the remaining evidence gap."
    )


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    return dict(value)


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the SMERC runtime admission gate before recoverability scoring.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = evaluate_runtime_admission_gate(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

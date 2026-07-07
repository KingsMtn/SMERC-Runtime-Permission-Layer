from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.policy import RuntimePolicy, canonical_json


SPL_VERSION = "smerc.spl.v0"


def compile_spl(payload: Mapping[str, Any]) -> RuntimePolicy:
    """Compile the human-oriented SPL profile into the runtime policy contract."""
    _exact(
        payload,
        {
            "version",
            "tenant",
            "policy",
            "evidence",
            "thresholds",
        },
        "spl",
    )
    if payload["version"] != SPL_VERSION:
        raise ValueError(f"spl.version must be {SPL_VERSION}")

    tenant = _object(payload["tenant"], "spl.tenant")
    policy = _object(payload["policy"], "spl.policy")
    evidence = _object(payload["evidence"], "spl.evidence")
    thresholds = _object(payload["thresholds"], "spl.thresholds")

    _exact(tenant, {"id"}, "spl.tenant")
    _exact(
        policy,
        {"id", "revision", "mode", "fail_behavior", "approved_by_role", "effective_at"},
        "spl.policy",
    )
    _exact(evidence, {"program_id", "ceiling"}, "spl.evidence")
    _exact(thresholds, {"throttle", "freeze", "deny", "escalate"}, "spl.thresholds")

    throttle = _object(thresholds["throttle"], "spl.thresholds.throttle")
    freeze = _object(thresholds["freeze"], "spl.thresholds.freeze")
    deny = _object(thresholds["deny"], "spl.thresholds.deny")
    escalate = _object(thresholds["escalate"], "spl.thresholds.escalate")

    _exact(throttle, {"authorization_min", "exposure_min"}, "spl.thresholds.throttle")
    _exact(freeze, {"confidence_max", "capacity_max"}, "spl.thresholds.freeze")
    _exact(
        deny,
        {
            "exposure_min",
            "capacity_max",
            "confidence_max",
            "cancel_reliability_max",
            "cancel_exposure_min",
        },
        "spl.thresholds.deny",
    )
    _exact(escalate, {"stress_min"}, "spl.thresholds.escalate")

    runtime_payload = {
        "version": "smerc.policy.v1",
        "tenant_id": tenant["id"],
        "policy_id": policy["id"],
        "policy_revision": policy["revision"],
        "mode": policy["mode"],
        "evidence_program_id": evidence["program_id"],
        "evidence_ceiling": evidence["ceiling"],
        "fail_behavior": policy["fail_behavior"],
        "approved_by_role": policy["approved_by_role"],
        "effective_at": policy["effective_at"],
        "thresholds": {
            "deny_exposure_min": deny["exposure_min"],
            "deny_capacity_max": deny["capacity_max"],
            "deny_confidence_max": deny["confidence_max"],
            "deny_cancel_reliability_max": deny["cancel_reliability_max"],
            "deny_cancel_exposure_min": deny["cancel_exposure_min"],
            "escalate_stress_min": escalate["stress_min"],
            "freeze_confidence_max": freeze["confidence_max"],
            "freeze_capacity_max": freeze["capacity_max"],
            "throttle_authorization_min": throttle["authorization_min"],
            "throttle_exposure_min": throttle["exposure_min"],
        },
    }
    return RuntimePolicy.from_dict(runtime_payload)


def compile_spl_file(path: str | Path) -> RuntimePolicy:
    return compile_spl(json.loads(Path(path).read_text(encoding="utf-8")))


def compile_spl_to_dict(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return compile_spl(payload).to_dict()


def _object(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    return value


def _exact(value: Mapping[str, Any], required: set[str], path: str) -> None:
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - required)
    if missing:
        raise ValueError(f"{path} is missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile SMERC SPL v0 into smerc.policy.v1 JSON.")
    parser.add_argument("spl_file", help="Path to a smerc.spl.v0 JSON document")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print compiled policy JSON")
    parser.add_argument("--hash", action="store_true", help="Print only the compiled policy hash")
    args = parser.parse_args()

    compiled = compile_spl_file(args.spl_file)
    if args.hash:
        print(compiled.policy_hash)
        return
    if args.pretty:
        print(json.dumps(compiled.to_dict(), indent=2, sort_keys=True))
    else:
        print(canonical_json(compiled.to_dict()))


if __name__ == "__main__":
    main()


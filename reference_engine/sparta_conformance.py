from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.sparta_registry import SPARTaAdapter, load_sparta_adapter_registry
from reference_engine.sparta_router import route_decision


SPARTA_CONFORMANCE_REPORT_VERSION = "smerc.sparta-conformance-report.v1"
POSTURES = ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")
THROTTLE_CONTROLS = (
    "limit_scope",
    "preview_before_execution",
    "require_rollback_plan",
    "preserve_replay",
)
SIDE_EFFECT_RANK = {
    "none": 0,
    "internal": 1,
    "external": 2,
    "financial": 3,
    "destructive": 4,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _representative_request(adapter: SPARTaAdapter) -> Dict[str, Any]:
    side_effect_level = sorted(adapter.allowed_side_effect_levels, key=lambda item: SIDE_EFFECT_RANK[item])[-1]
    return {
        "adapter_id": adapter.adapter_id,
        "action": adapter.supported_actions[0],
        "requested_capability": adapter.supported_capabilities[0],
        "requested_scope_units": max(1, min(adapter.max_scope_units, 10)),
        "side_effect_level": side_effect_level,
        "metadata": {
            "conformance_probe": True,
            "evidence_boundary": "synthetic_adapter_conformance_probe",
        },
    }


def _decision(adapter_id: str, posture: str) -> Dict[str, Any]:
    controls: Iterable[str] = THROTTLE_CONTROLS if posture == "THROTTLE" else ()
    return {
        "posture": posture,
        "replay_id": f"conformance:{adapter_id}:{posture.lower()}",
        "reason_codes": [f"CONFORMANCE_{posture}"],
        "controls": list(controls),
        "policy": {
            "policy_id": "sparta-conformance",
            "policy_revision": "1.0.0",
            "mode": "SHADOW",
            "policy_hash": "conformance-only",
        },
    }


def _expected_route_state(adapter: SPARTaAdapter, posture: str) -> str:
    if posture == "ALLOW":
        return "EXECUTE"
    if posture == "DENY":
        return "BLOCK"
    if posture == "FREEZE":
        return "PAUSE"
    if posture == "ESCALATE":
        return "REVIEW_REQUIRED" if adapter.supports_human_approval else "BLOCKED_ESCALATION_UNAVAILABLE"
    if adapter.supports_scope_limit and adapter.supports_dry_run and (adapter.supports_checkpoint or adapter.supports_rollback):
        return "CONSTRAINED_EXECUTE"
    return "REVIEW_REQUIRED"


def _expected_executable(route_state: str) -> bool:
    return route_state in {"EXECUTE", "CONSTRAINED_EXECUTE"}


def _adapter_result(registry: Any, adapter: SPARTaAdapter) -> Dict[str, Any]:
    request = _representative_request(adapter)
    plan = registry.plan_from_request(request)
    posture_results = []
    for posture in POSTURES:
        route = route_decision(_decision(adapter.adapter_id, posture), plan)
        expected_state = _expected_route_state(adapter, posture)
        expected_executable = _expected_executable(expected_state)
        passed = route["route_state"] == expected_state and route["executable"] is expected_executable
        posture_results.append(
            {
                "posture": posture,
                "expected_route_state": expected_state,
                "actual_route_state": route["route_state"],
                "expected_executable": expected_executable,
                "actual_executable": route["executable"],
                "passed": passed,
                "applied_controls": route["applied_controls"],
                "blocked_controls": route["blocked_controls"],
                "reason_codes": route["reason_codes"],
            }
        )
    capability_gaps = []
    if not adapter.supports_scope_limit:
        capability_gaps.append("scope_limit")
    if not adapter.supports_dry_run:
        capability_gaps.append("dry_run")
    if not adapter.supports_checkpoint and not adapter.supports_rollback:
        capability_gaps.append("checkpoint_or_rollback")
    if not adapter.supports_human_approval:
        capability_gaps.append("human_approval")
    return {
        "adapter_id": adapter.adapter_id,
        "tool": adapter.tool,
        "representative_request": request,
        "production_boundary": adapter.metadata.get("production_boundary", "declared_adapter"),
        "capability_gaps": capability_gaps,
        "posture_results": posture_results,
        "passed": all(item["passed"] for item in posture_results),
    }


def build_conformance_report(registry_path: str | Path) -> Dict[str, Any]:
    registry = load_sparta_adapter_registry(Path(registry_path))
    adapters = [SPARTaAdapter.from_dict(item) for item in registry.to_dict()["adapters"]]
    adapter_results = [_adapter_result(registry, adapter) for adapter in adapters]
    failed = [
        f"{adapter['adapter_id']}:{result['posture']}"
        for adapter in adapter_results
        for result in adapter["posture_results"]
        if not result["passed"]
    ]
    live_like = [
        adapter["adapter_id"]
        for adapter in adapter_results
        if adapter["production_boundary"] != "example_adapter_only"
    ]
    return {
        "version": SPARTA_CONFORMANCE_REPORT_VERSION,
        "registry_path": str(registry_path).replace("\\", "/"),
        "summary": {
            "adapter_count": len(adapter_results),
            "posture_probe_count": len(adapter_results) * len(POSTURES),
            "failed_posture_probe_count": len(failed),
            "example_only_adapter_count": len(adapter_results) - len(live_like),
            "declared_adapter_count": len(live_like),
            "passed": not failed,
        },
        "adapter_results": adapter_results,
        "failed_probes": failed,
        "evidence_boundary": (
            "Static SPARTa adapter conformance report only. It verifies registry declarations "
            "against deterministic route behavior; it does not prove live vendor enforcement, "
            "production readiness, independent security review, or incident reduction."
        ),
        "recommended_next_action": _recommended_next_action(adapter_results, failed),
    }


def _recommended_next_action(adapter_results: list[Mapping[str, Any]], failed: list[str]) -> str:
    if failed:
        return "Fix failed conformance probes before using this registry in pilot routing: " + ", ".join(failed)
    example_only = [item["adapter_id"] for item in adapter_results if item["production_boundary"] == "example_adapter_only"]
    if example_only:
        return (
            "Use this registry for pilot discussion and mock review flows. Before enforcement, replace example-only "
            "adapters with live integrations or keep them explicitly marked as production_boundary=example_adapter_only: "
            + ", ".join(example_only)
        )
    return "Use this registry as a candidate for pilot validation, subject to live adapter evidence and customer review."


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# SPARTa Adapter Conformance Report",
        "",
        "This report checks whether declared SPARTa adapters route each SMERC posture into the expected execution state. It is not production certification or live vendor attestation.",
        "",
        "## Summary",
        "",
        f"- Adapter count: `{summary['adapter_count']}`",
        f"- Posture probes: `{summary['posture_probe_count']}`",
        f"- Failed posture probes: `{summary['failed_posture_probe_count']}`",
        f"- Example-only adapters: `{summary['example_only_adapter_count']}`",
        f"- Declared adapters: `{summary['declared_adapter_count']}`",
        f"- Passed: `{str(summary['passed']).lower()}`",
        "",
        "## Adapter Results",
        "",
        "| Adapter | Tool | Boundary | Gaps | Passed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for adapter in report["adapter_results"]:
        gaps = ", ".join(adapter["capability_gaps"]) or "none"
        lines.append(
            f"| `{adapter['adapter_id']}` | `{adapter['tool']}` | `{adapter['production_boundary']}` | {gaps} | `{str(adapter['passed']).lower()}` |"
        )
    lines.extend(["", "## Posture Probes", "", "| Adapter | Posture | Expected | Actual | Result |", "| --- | --- | --- | --- | --- |"])
    for adapter in report["adapter_results"]:
        for result in adapter["posture_results"]:
            outcome = "pass" if result["passed"] else "fail"
            lines.append(
                f"| `{adapter['adapter_id']}` | `{result['posture']}` | `{result['expected_route_state']}` | `{result['actual_route_state']}` | `{outcome}` |"
            )
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            report["evidence_boundary"],
            "",
            "## Recommended Next Action",
            "",
            report["recommended_next_action"],
            "",
        ]
    )
    return "\n".join(lines)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run static SPARTa adapter conformance probes.")
    parser.add_argument("registry", type=Path, help="Path to a SPARTa adapter registry JSON file.")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--json-output")
    parser.add_argument("--markdown-output")
    args = parser.parse_args()
    report = build_conformance_report(args.registry)
    if args.json_output:
        _write_json(Path(args.json_output), report)
    if args.markdown_output:
        _write_text(Path(args.markdown_output), render_markdown(report))
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

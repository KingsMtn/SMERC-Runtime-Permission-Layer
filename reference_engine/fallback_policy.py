from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


FALLBACK_POLICY_INPUT_VERSION = "smerc.fallback-policy-input.v1"
FALLBACK_POLICY_VERSION = "smerc.fallback-policy.v1"
FALLBACK_POLICY_REPORT_VERSION = "smerc.fallback-policy-report.v1"

POSTURE_RANK = {"ALLOW": 0, "THROTTLE": 1, "FREEZE": 2, "ESCALATE": 3, "DENY": 4}
RANK_POSTURE = {value: key for key, value in POSTURE_RANK.items()}
FAILURE_TYPES = {
    "none",
    "smerc_api_unavailable",
    "content_scanner_unavailable",
    "metadata_incomplete",
    "policy_bundle_stale",
    "evidence_stale",
    "evidence_conflict",
    "unknown_tool",
    "adapter_unavailable",
    "timeout",
    "review_queue_unavailable",
    "rollback_plan_missing",
}
HIGH_IMPACT_ACTION_CLASSES = {
    "delete_data",
    "modify_production",
    "move_money",
    "change_iam",
    "external_communication",
    "security_response",
    "stablecoin_transfer",
    "customer_state_change",
}


def evaluate_fallback_policy(payload: Mapping[str, Any]) -> Dict[str, Any]:
    data = _object(payload, "fallback_policy")
    if data.get("schema") != FALLBACK_POLICY_INPUT_VERSION:
        raise ValueError(f"schema must be {FALLBACK_POLICY_INPUT_VERSION}")
    action_id = _text(data.get("action_id"), "action_id", 128)
    action_class = _text(data.get("action_class"), "action_class", 128)
    proposed_posture = _posture(data.get("proposed_posture"), "proposed_posture")
    failure_type = _failure_type(data.get("failure_type"))
    metadata_complete = _bool(data.get("metadata_complete"), "metadata_complete")
    policy_fresh = _bool(data.get("policy_fresh"), "policy_fresh")
    evidence_fresh = _bool(data.get("evidence_fresh"), "evidence_fresh")
    scanner_available = _bool(data.get("scanner_available"), "scanner_available")
    adapter_available = _bool(data.get("adapter_available"), "adapter_available")
    review_queue_available = _bool(data.get("review_queue_available"), "review_queue_available")
    rollback_plan_available = _bool(data.get("rollback_plan_available"), "rollback_plan_available")
    timeout_ms = _non_negative_number(data.get("timeout_ms"), "timeout_ms")
    max_timeout_ms = _non_negative_number(data.get("max_timeout_ms"), "max_timeout_ms")
    content_risk_score = _score(data.get("content_risk_score"), "content_risk_score")
    irreversible_exposure_score = _score(data.get("irreversible_exposure_score"), "irreversible_exposure_score")
    reversible_capacity_score = _score(data.get("reversible_capacity_score"), "reversible_capacity_score")

    restrictive_rank = POSTURE_RANK[proposed_posture]
    reason_codes = []

    def restrict(posture: str, reason: str) -> None:
        nonlocal restrictive_rank
        restrictive_rank = max(restrictive_rank, POSTURE_RANK[posture])
        reason_codes.append(reason)

    high_impact = action_class in HIGH_IMPACT_ACTION_CLASSES or irreversible_exposure_score >= 0.70
    if failure_type != "none":
        restrict("THROTTLE", f"FALLBACK_FAILURE_{failure_type.upper()}")
    if not metadata_complete:
        restrict("FREEZE", "FALLBACK_METADATA_INCOMPLETE")
    if not policy_fresh:
        restrict("FREEZE", "FALLBACK_POLICY_STALE")
    if not evidence_fresh:
        restrict("FREEZE", "FALLBACK_EVIDENCE_STALE")
    if not scanner_available and (content_risk_score >= 0.42 or high_impact):
        restrict("FREEZE", "FALLBACK_CONTENT_SCANNER_UNAVAILABLE")
    if content_risk_score >= 0.86:
        restrict("DENY", "FALLBACK_CONTENT_RISK_CRITICAL")
    elif content_risk_score >= 0.70:
        restrict("ESCALATE", "FALLBACK_CONTENT_RISK_HIGH")
    if not adapter_available:
        restrict("FREEZE", "FALLBACK_ADAPTER_UNAVAILABLE")
    if timeout_ms > max_timeout_ms:
        restrict("FREEZE", "FALLBACK_TIMEOUT_EXCEEDED")
    if high_impact and not rollback_plan_available:
        restrict("DENY", "FALLBACK_ROLLBACK_PLAN_MISSING_FOR_HIGH_IMPACT")
    elif not rollback_plan_available:
        restrict("THROTTLE", "FALLBACK_ROLLBACK_PLAN_MISSING")
    if high_impact and not review_queue_available and restrictive_rank >= POSTURE_RANK["FREEZE"]:
        restrict("DENY", "FALLBACK_REVIEW_QUEUE_UNAVAILABLE_FOR_HELD_HIGH_IMPACT_ACTION")
    if reversible_capacity_score < 0.35 and irreversible_exposure_score >= 0.68:
        restrict("DENY", "FALLBACK_LOW_RECOVERY_HIGH_EXPOSURE")

    final_posture = RANK_POSTURE[restrictive_rank]
    controls = _controls(final_posture, reason_codes)
    return {
        "version": FALLBACK_POLICY_VERSION,
        "generated_at": _now(),
        "action_id": action_id,
        "action_class": action_class,
        "proposed_posture": proposed_posture,
        "fallback_posture": final_posture,
        "fallback_applied": final_posture != proposed_posture or bool(reason_codes),
        "failure_type": failure_type,
        "high_impact": high_impact,
        "reason_codes": sorted(set(reason_codes)) or ["FALLBACK_NOT_APPLIED"],
        "controls": controls,
        "plain_english_summary": _summary(action_id, proposed_posture, final_posture, reason_codes),
        "evidence_boundary": (
            "Fallback policy is deterministic fail-safe routing for unavailable, stale, incomplete, conflicting, "
            "or timeout-prone evidence. It is not proof of production safety or regulatory compliance."
        ),
    }


def build_fallback_policy_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("payload.scenarios must be a non-empty list")
    results = [evaluate_fallback_policy(item) for item in scenarios]
    counts: Dict[str, int] = {}
    for result in results:
        counts[result["fallback_posture"]] = counts.get(result["fallback_posture"], 0) + 1
    report = {
        "version": FALLBACK_POLICY_REPORT_VERSION,
        "generated_at": _now(),
        "scenario_count": len(results),
        "fallback_applied_count": sum(1 for item in results if item["fallback_applied"]),
        "fallback_posture_counts": dict(sorted(counts.items())),
        "results": results,
        "evidence_boundary": "Synthetic fallback examples demonstrate deterministic failure handling, not production validation.",
    }
    report["markdown_report"] = render_markdown(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Fallback Policy Layer Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Scenarios evaluated: `{report['scenario_count']}`",
        f"- Fallback applied: `{report['fallback_applied_count']}`",
        f"- Fallback posture counts: `{report['fallback_posture_counts']}`",
        "",
        "| Action | Class | Proposed | Fallback | Failure | High Impact | Reasons |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in report["results"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape(result["action_id"]),
                    _escape(result["action_class"]),
                    _escape(result["proposed_posture"]),
                    _escape(result["fallback_posture"]),
                    _escape(result["failure_type"]),
                    str(result["high_impact"]),
                    _escape(", ".join(result["reason_codes"])),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).write_text(str(report["markdown_report"]) + "\n", encoding="utf-8")


def _controls(posture: str, reason_codes: list[str]) -> list[str]:
    controls = ["preserve_fallback_decision_record"]
    if posture == "THROTTLE":
        controls.extend(["limit_scope", "retry_missing_evidence_before_release"])
    elif posture == "FREEZE":
        controls.extend(["pause_execution", "collect_required_evidence", "retry_failed_dependency"])
    elif posture == "ESCALATE":
        controls.extend(["route_to_accountable_reviewer", "document_override_if_approved"])
    elif posture == "DENY":
        controls.extend(["block_execution", "require_new_request_after_fault_repair"])
    if any("SCANNER" in code for code in reason_codes):
        controls.append("replace_or_retry_content_scanner")
    if any("POLICY" in code for code in reason_codes):
        controls.append("refresh_policy_bundle")
    if any("ADAPTER" in code for code in reason_codes):
        controls.append("repair_execution_adapter")
    return sorted(set(controls))


def _summary(action_id: str, proposed: str, final: str, reasons: list[str]) -> str:
    if final == proposed and not reasons:
        return f"Fallback policy did not modify action '{action_id}'."
    return (
        f"Fallback policy changed or confirmed action '{action_id}' from {proposed} to {final} because "
        f"{', '.join(sorted(set(reasons))) or 'fail-safe controls were required'}."
    )


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    return dict(value)


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _posture(value: Any, path: str) -> str:
    posture = _text(value, path, 16)
    if posture not in POSTURE_RANK:
        raise ValueError(f"{path} must be one of {', '.join(POSTURE_RANK)}")
    return posture


def _failure_type(value: Any) -> str:
    failure_type = _text(value, "failure_type", 128)
    if failure_type not in FAILURE_TYPES:
        raise ValueError(f"failure_type is unsupported: {failure_type}")
    return failure_type


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    if not 0 <= value <= 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return float(value)


def _non_negative_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a non-negative number")
    if value < 0:
        raise ValueError(f"{path} must be non-negative")
    return float(value)


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate deterministic SMERC fallback policy scenarios.")
    parser.add_argument("--input", default="examples/fallback_policy_examples.json")
    parser.add_argument("--json-output", default="reports/fallback_policy_report.json")
    parser.add_argument("--markdown-output", default="reports/Fallback_Policy_Layer_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = build_fallback_policy_report(payload)
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

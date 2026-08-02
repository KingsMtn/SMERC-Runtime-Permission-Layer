from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


STATUS_VERSION = "smerc.operator-status.v1"
OPA_EXPORT_VERSION = "smerc.opa-decision-log-export.v1"
POSTURES = ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE", "UNAVAILABLE")


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def build_operator_status(
    *,
    pilot_readiness: Mapping[str, Any],
    customer_intake: Mapping[str, Any],
    decision_artifacts: Optional[Mapping[str, Any]] = None,
    tenant_id: str = "pilot-review",
    active_policy_version: str = "smerc.policy.reference",
    active_profile_version: str = "github_actions_strict",
) -> Dict[str, Any]:
    records = _decision_records(decision_artifacts or {})
    posture_counts = Counter(_posture(record) for record in records)
    unavailable_count = posture_counts.get("UNAVAILABLE", 0)
    top_reason_codes = Counter(
        code for record in records for code in _decision(record).get("reason_codes", [])
    ).most_common(10)
    top_controls = Counter(
        control for record in records for control in _controls(_decision(record))
    ).most_common(10)
    decision_count = len(records)
    status = "ready_for_review" if pilot_readiness.get("ready_for_week_zero") else "needs_attention"
    if customer_intake.get("ready_for_review_call") is False:
        status = "blocked"
    if unavailable_count:
        status = "degraded"

    return {
        "schema": STATUS_VERSION,
        "generated_at": _now(),
        "tenant_id": tenant_id,
        "operator_status": status,
        "active_policy_version": active_policy_version,
        "active_profile_version": active_profile_version,
        "readiness": {
            "pilot_ready_for_week_zero": bool(pilot_readiness.get("ready_for_week_zero")),
            "pilot_ready_for_customer_observe": bool(pilot_readiness.get("ready_for_customer_observe")),
            "pilot_blockers": list(pilot_readiness.get("blockers", [])),
            "pilot_warnings": list(pilot_readiness.get("warnings", [])),
            "customer_ready_for_review_call": bool(customer_intake.get("ready_for_review_call")),
            "customer_ready_for_week_zero": bool(customer_intake.get("ready_for_week_zero")),
            "customer_blockers": list(customer_intake.get("blockers", [])),
            "customer_warnings": list(customer_intake.get("warnings", [])),
        },
        "decision_activity": {
            "decision_count": decision_count,
            "posture_counts": {posture: posture_counts.get(posture, 0) for posture in POSTURES},
            "unavailable_count": unavailable_count,
            "unavailable_rate": None if decision_count == 0 else round(unavailable_count / decision_count, 4),
            "top_reason_codes": top_reason_codes,
            "top_controls": top_controls,
        },
        "operational_checks": [
            {
                "name": "policy_version_declared",
                "status": "ready" if active_policy_version else "blocker",
                "detail": "Active policy version is included in the operator report.",
            },
            {
                "name": "profile_version_declared",
                "status": "ready" if active_profile_version else "blocker",
                "detail": "Active domain/profile version is included in the operator report.",
            },
            {
                "name": "pilot_readiness",
                "status": "ready" if pilot_readiness.get("ready_for_week_zero") else "warning",
                "detail": "Week-zero readiness is generated from the GitHub Actions pilot readiness report.",
            },
            {
                "name": "customer_intake",
                "status": "ready" if customer_intake.get("ready_for_review_call") else "blocker",
                "detail": "Customer intake must be ready for a review call before pilot setup.",
            },
            {
                "name": "decision_artifacts",
                "status": "ready" if decision_count else "warning",
                "detail": "Decision artifacts are present for operator distribution and log export.",
            },
        ],
        "evidence_boundary": (
            "Operator status summarizes pilot artifacts and readiness reports. It does not prove production "
            "availability, incident reduction, compliance, or customer validation."
        ),
    }


def export_opa_decision_logs(
    decision_artifacts: Mapping[str, Any],
    *,
    tenant_id: str = "pilot-review",
    policy_path: str = "smerc/runtime/posture",
    bundle_revision: str = "smerc-reference",
) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for record in _decision_records(decision_artifacts):
        decision = _decision(record)
        action = record.get("action", {})
        replay_id = str(decision.get("replay_id") or decision.get("replay", {}).get("replay_id") or record.get("replay_id") or "")
        decision_id = replay_id or f"smerc-decision-{len(entries) + 1}"
        path = policy_path.split("/")
        entries.append(
            {
                "decision_id": decision_id,
                "timestamp": _timestamp(decision, record),
                "path": path,
                "input": {
                    "tenant_id": tenant_id,
                    "action_id": action.get("action_id") or record.get("action_id") or decision.get("action_id"),
                    "actor": action.get("actor") or record.get("actor"),
                    "tool": action.get("tool") or record.get("tool"),
                    "context": action.get("context", {}),
                },
                "result": {
                    "allow": decision.get("posture") == "ALLOW",
                    "posture": decision.get("posture", "UNAVAILABLE"),
                    "risk_score": _score(decision, "risk_score", "irreversible_exposure_score"),
                    "confidence_score": _score(decision, "confidence_score", "confidence_score"),
                    "reason_codes": decision.get("reason_codes", []),
                    "controls": _controls(decision),
                    "replay_id": replay_id,
                },
                "bundles": {
                    "smerc": {
                        "revision": bundle_revision,
                    }
                },
                "labels": {
                    "system": "smerc",
                    "export_schema": OPA_EXPORT_VERSION,
                    "compatibility": "opa_decision_log_adjacent",
                },
            }
        )
    return {
        "schema": OPA_EXPORT_VERSION,
        "generated_at": _now(),
        "tenant_id": tenant_id,
        "entry_count": len(entries),
        "entries": entries,
        "evidence_boundary": (
            "OPA-style export only. This is a compatibility shape for log pipelines; it is not OPA parity, "
            "Rego evaluation, or proof of production enforcement."
        ),
    }


def markdown_status(report: Mapping[str, Any]) -> str:
    activity = report["decision_activity"]
    readiness = report["readiness"]
    lines = [
        "# SMERC Operator Status Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Status",
        "",
        f"- Tenant: `{report['tenant_id']}`",
        f"- Operator status: `{report['operator_status']}`",
        f"- Active policy version: `{report['active_policy_version']}`",
        f"- Active profile version: `{report['active_profile_version']}`",
        "",
        "## Readiness",
        "",
        f"- Pilot ready for week zero: `{str(readiness['pilot_ready_for_week_zero']).lower()}`",
        f"- Pilot ready for customer observe: `{str(readiness['pilot_ready_for_customer_observe']).lower()}`",
        f"- Customer ready for review call: `{str(readiness['customer_ready_for_review_call']).lower()}`",
        f"- Customer ready for week zero: `{str(readiness['customer_ready_for_week_zero']).lower()}`",
        "",
        "## Decision Activity",
        "",
        f"- Decision count: `{activity['decision_count']}`",
        f"- Posture counts: `{activity['posture_counts']}`",
        f"- Unavailable count: `{activity['unavailable_count']}`",
        f"- Unavailable rate: `{activity['unavailable_rate']}`",
        f"- Top reason codes: `{activity['top_reason_codes']}`",
        f"- Top controls: `{activity['top_controls']}`",
        "",
        "## Operational Checks",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for check in report["operational_checks"]:
        lines.append(f"| `{check['name']}` | `{check['status']}` | {check['detail']} |")
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def markdown_opa_export(report: Mapping[str, Any]) -> str:
    posture_counts = Counter(entry["result"]["posture"] for entry in report["entries"])
    lines = [
        "# SMERC OPA-Style Decision Log Export",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Tenant: `{report['tenant_id']}`",
        f"- Entries: `{report['entry_count']}`",
        f"- Posture counts: `{dict(posture_counts)}`",
        "",
        "## Interpretation",
        "",
        "This export gives existing log pipelines an OPA-adjacent decision-log shape while preserving SMERC posture, recoverability scores, reason codes, controls, and replay IDs.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
    ]
    return "\n".join(lines)


def write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _decision_records(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    records = payload.get("records")
    if isinstance(records, list):
        return [record for record in records if isinstance(record, dict)]
    reports = payload.get("reports")
    if isinstance(reports, list):
        return [report for report in reports if isinstance(report, dict)]
    entries = payload.get("entries")
    if isinstance(entries, list):
        return [entry for entry in entries if isinstance(entry, dict)]
    return []


def _decision(record: Mapping[str, Any]) -> Dict[str, Any]:
    decision = record.get("decision")
    if isinstance(decision, dict):
        return decision
    if "posture" in record:
        return dict(record)
    return {"posture": "UNAVAILABLE"}


def _posture(record: Mapping[str, Any]) -> str:
    posture = _decision(record).get("posture")
    return posture if posture in POSTURES else "UNAVAILABLE"


def _score(decision: Mapping[str, Any], direct_key: str, nested_key: str) -> Optional[float]:
    value = decision.get(direct_key)
    scores = decision.get("scores")
    if value is None and isinstance(scores, dict):
        value = scores.get(nested_key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return round(float(value), 3)


def _controls(decision: Mapping[str, Any]) -> List[str]:
    for key in ("controls", "constraints"):
        values = decision.get(key)
        if isinstance(values, list):
            return [item for item in values if isinstance(item, str)]
    return []


def _timestamp(decision: Mapping[str, Any], record: Mapping[str, Any]) -> str:
    replay = decision.get("replay")
    if isinstance(replay, dict) and isinstance(replay.get("evaluated_at"), str):
        return replay["evaluated_at"]
    if isinstance(record.get("evaluated_at"), str):
        return record["evaluated_at"]
    return _now()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SMERC operator status and OPA-style decision logs.")
    parser.add_argument("--pilot-readiness", default="reports/github_actions_pilot_readiness.json")
    parser.add_argument("--customer-intake", default="reports/github_actions_customer_pilot_intake_report.json")
    parser.add_argument("--decision-artifacts", default="reports/github_actions_shadow_mode_results.json")
    parser.add_argument("--tenant", default="pilot-review")
    parser.add_argument("--policy-version", default="smerc.policy.reference")
    parser.add_argument("--profile-version", default="github_actions_strict")
    parser.add_argument("--status-json-output", default="reports/operator_status.json")
    parser.add_argument("--status-markdown-output", default="reports/Operator_Status_Report.md")
    parser.add_argument("--opa-json-output", default="reports/opa_decision_log_export.json")
    parser.add_argument("--opa-markdown-output", default="reports/OPA_Decision_Log_Export.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    decisions = load_json(args.decision_artifacts)
    status = build_operator_status(
        pilot_readiness=load_json(args.pilot_readiness),
        customer_intake=load_json(args.customer_intake),
        decision_artifacts=decisions,
        tenant_id=args.tenant,
        active_policy_version=args.policy_version,
        active_profile_version=args.profile_version,
    )
    opa_export = export_opa_decision_logs(
        decisions,
        tenant_id=args.tenant,
        bundle_revision=args.policy_version,
    )
    write_json(args.status_json_output, status)
    write_text(args.status_markdown_output, markdown_status(status))
    write_json(args.opa_json_output, opa_export)
    write_text(args.opa_markdown_output, markdown_opa_export(opa_export))
    print(json.dumps({"status": status, "opa_export": opa_export}, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


RECOVERY_AUTHORITY_VERSION = "smerc.recovery-authority-gate.v1"
RECOVERY_STATES = {"UNLOCK", "UNLOCK_CONSTRAINED", "KEEP_PAUSED", "REQUALIFY", "DENY_UNLOCK"}
PAUSED_POSTURES = {"FREEZE", "ESCALATE", "DENY"}


def load_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate_recovery_authority(request: Mapping[str, Any]) -> Dict[str, Any]:
    if request.get("version") != RECOVERY_AUTHORITY_VERSION:
        raise ValueError(f"request must have version {RECOVERY_AUTHORITY_VERSION}")

    paused_decision = _evaluate_paused_decision(request["paused_decision"])
    unlock_actor = _evaluate_unlock_actor(request["unlock_actor"], request["paused_decision"])
    unlock_evidence = _evaluate_unlock_evidence(request["unlock_evidence"])
    recovery_path = _evaluate_recovery_path(request["recovery_path"])

    final = _final_state(paused_decision, unlock_actor, unlock_evidence, recovery_path)
    report = {
        "version": RECOVERY_AUTHORITY_VERSION,
        "generated_at": _now(),
        "case_id": str(request.get("case_id", "recovery_authority_case")),
        "paused_decision": paused_decision,
        "unlock_actor": unlock_actor,
        "unlock_evidence": unlock_evidence,
        "recovery_path": recovery_path,
        "recovery_authority": final,
        "plain_english_summary": _summary(final, paused_decision, unlock_actor, unlock_evidence, recovery_path),
    }
    return report


def _evaluate_paused_decision(decision: Mapping[str, Any]) -> Dict[str, Any]:
    posture = str(decision.get("posture", ""))
    drivers = []
    if posture not in PAUSED_POSTURES:
        drivers.append("decision_not_paused")
    if not decision.get("replay_id"):
        drivers.append("missing_replay_id")
    if not decision.get("action_hash"):
        drivers.append("missing_action_hash")
    return {
        "posture": posture,
        "state": "PAUSED_DECISION_VALID" if not drivers else "PAUSED_DECISION_INVALID",
        "replay_id": str(decision.get("replay_id", "")),
        "action_hash": str(decision.get("action_hash", "")),
        "proposing_actor_id": str(decision.get("proposing_actor_id", "")),
        "drivers": drivers,
    }


def _evaluate_unlock_actor(actor: Mapping[str, Any], paused_decision: Mapping[str, Any]) -> Dict[str, Any]:
    drivers = []
    actor_id = str(actor.get("actor_id", ""))
    proposer = str(paused_decision.get("proposing_actor_id", ""))
    role = str(actor.get("role", ""))
    allowed_roles = set(actor.get("allowed_roles", []))
    if not actor_id:
        drivers.append("missing_unlock_actor")
    if actor_id and proposer and actor_id == proposer:
        drivers.append("self_unlock_attempt")
    if not actor.get("identity_verified"):
        drivers.append("unlock_identity_not_verified")
    if not actor.get("delegated_authority_valid"):
        drivers.append("delegated_authority_invalid")
    if role not in allowed_roles:
        drivers.append("role_not_allowed_to_unlock")
    if actor.get("conflict_of_interest"):
        drivers.append("conflict_of_interest")
    return {
        "actor_id": actor_id,
        "role": role,
        "state": "UNLOCK_ACTOR_VALID" if not drivers else "UNLOCK_ACTOR_INVALID",
        "drivers": drivers,
    }


def _evaluate_unlock_evidence(evidence: Mapping[str, Any]) -> Dict[str, Any]:
    drivers = []
    if not evidence.get("rollback_plan_verified"):
        drivers.append("rollback_plan_not_verified")
    if not evidence.get("blast_radius_bounded"):
        drivers.append("blast_radius_not_bounded")
    if not evidence.get("missing_evidence_resolved"):
        drivers.append("missing_evidence_unresolved")
    if not evidence.get("fresh_scan_passed"):
        drivers.append("fresh_scan_not_passed")
    if evidence.get("evidence_age_minutes", 9999) > evidence.get("max_evidence_age_minutes", 60):
        drivers.append("evidence_too_old")
    if evidence.get("override_reason_required") and not str(evidence.get("override_reason", "")).strip():
        drivers.append("override_reason_missing")
    score = round(max(0.0, 1.0 - (0.18 * len(drivers))), 3)
    return {
        "state": "UNLOCK_EVIDENCE_SUFFICIENT" if not drivers else "UNLOCK_EVIDENCE_INSUFFICIENT",
        "score": score,
        "drivers": drivers,
    }


def _evaluate_recovery_path(path: Mapping[str, Any]) -> Dict[str, Any]:
    drivers = []
    if not path.get("route_bound_to_replay"):
        drivers.append("route_not_bound_to_replay")
    if not path.get("permit_required"):
        drivers.append("action_bound_permit_not_required")
    if not path.get("permit_issuer_separate_from_proposer"):
        drivers.append("permit_issuer_not_separated")
    if not path.get("continuation_window_bounded"):
        drivers.append("continuation_window_unbounded")
    if path.get("required_reviewer_count", 1) > path.get("available_reviewer_count", 0):
        drivers.append("reviewer_quorum_missing")
    if not path.get("ledger_append_required"):
        drivers.append("ledger_append_not_required")
    if not path.get("post_unlock_monitoring_required"):
        drivers.append("post_unlock_monitoring_not_required")
    if len(drivers) >= 4:
        state = "RECOVERY_PATH_UNSAFE"
    elif drivers:
        state = "RECOVERY_PATH_CONSTRAINED"
    else:
        state = "RECOVERY_PATH_READY"
    return {"state": state, "drivers": drivers}


def _final_state(
    paused_decision: Mapping[str, Any],
    unlock_actor: Mapping[str, Any],
    unlock_evidence: Mapping[str, Any],
    recovery_path: Mapping[str, Any],
) -> Dict[str, Any]:
    drivers = []
    drivers.extend(paused_decision["drivers"])
    drivers.extend(unlock_actor["drivers"])
    drivers.extend(unlock_evidence["drivers"])
    drivers.extend(recovery_path["drivers"])

    if "decision_not_paused" in drivers:
        state = "REQUALIFY"
    elif any(
        item in drivers
        for item in [
            "self_unlock_attempt",
            "unlock_identity_not_verified",
            "delegated_authority_invalid",
            "role_not_allowed_to_unlock",
            "conflict_of_interest",
        ]
    ):
        state = "DENY_UNLOCK"
    elif recovery_path["state"] == "RECOVERY_PATH_UNSAFE":
        state = "KEEP_PAUSED"
    elif unlock_evidence["state"] == "UNLOCK_EVIDENCE_INSUFFICIENT":
        state = "KEEP_PAUSED"
    elif recovery_path["state"] == "RECOVERY_PATH_CONSTRAINED":
        state = "UNLOCK_CONSTRAINED"
    else:
        state = "UNLOCK"

    return {
        "state": state,
        "drivers": sorted(set(drivers)),
        "required_next_step": _next_step(state),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC Recovery Authority Gate Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Case: `{report['case_id']}`",
        f"- Paused posture: `{report['paused_decision']['posture']}`",
        f"- Unlock actor: `{report['unlock_actor']['actor_id']}`",
        f"- Unlock decision: `{report['recovery_authority']['state']}`",
        f"- Recovery path: `{report['recovery_path']['state']}`",
        f"- Unlock evidence: `{report['unlock_evidence']['state']}`",
        "",
        "## Drivers",
        "",
    ]
    lines.extend(f"- `{driver}`" for driver in report["recovery_authority"]["drivers"] or ["none"])
    lines.extend(
        [
            "",
            "## Required Next Step",
            "",
            str(report["recovery_authority"]["required_next_step"]),
            "",
            "## Work / Result / Impact",
            "",
            "Work: evaluate whether a paused SMERC decision can be reopened by a trusted authority path.",
            "",
            f"Result: `{report['recovery_authority']['state']}`.",
            "",
            "Impact: the same agent or workflow that caused a risky pause cannot simply unlock itself. Continuation requires verified authority, fresh recovery evidence, a bounded route, an action-bound permit, and ledger evidence.",
            "",
            "## Plain English Summary",
            "",
            str(report["plain_english_summary"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path, markdown_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_path).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_path).write_text(render_markdown(report), encoding="utf-8")


def _next_step(state: str) -> str:
    if state == "UNLOCK":
        return "Issue a short-lived action-bound permit, append DLL evidence, and continue with post-unlock monitoring."
    if state == "UNLOCK_CONSTRAINED":
        return "Issue a constrained permit only after missing route controls are added and recorded."
    if state == "KEEP_PAUSED":
        return "Keep the action paused until recovery evidence and route controls are complete."
    if state == "REQUALIFY":
        return "Re-run runtime admission and SMERC scoring because the case is not a valid paused decision."
    return "Deny unlock and require a separate accountable owner or escalation path."


def _summary(
    final: Mapping[str, Any],
    paused_decision: Mapping[str, Any],
    unlock_actor: Mapping[str, Any],
    unlock_evidence: Mapping[str, Any],
    recovery_path: Mapping[str, Any],
) -> str:
    return (
        f"The recovery authority state is {final['state']} for paused posture {paused_decision['posture']}. "
        f"The unlock actor is {unlock_actor['state']}, evidence is {unlock_evidence['state']}, and recovery path is "
        f"{recovery_path['state']}."
    )


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate whether a paused SMERC decision can be safely unlocked.")
    parser.add_argument("--case", default="examples/recovery_authority/unlock_request.json")
    parser.add_argument("--json-output", default="reports/recovery_authority_gate_report.json")
    parser.add_argument("--markdown-output", default="reports/Recovery_Authority_Gate_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = evaluate_recovery_authority(load_json(args.case))
    write_outputs(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

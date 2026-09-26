from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from reference_engine.authorization_afterlife_evidence_intake import validate_manifest
from reference_engine.authorization_afterlife_runner import build_base_inputs
from reference_engine.consequence_time_reconciliation import reconcile_consequence_time


VERSION = "smerc.authorization-afterlife-pilot-runner.v1"


def run_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    manifest = validate_manifest(payload)
    decisions = [evaluate_evidence_record(record) for record in manifest["records"]]
    names = ("SETTLE", "QUARANTINE", "COMPENSATE", "DENY")
    return {
        "version": VERSION,
        "pilot_id": manifest["pilot_id"],
        "record_count": len(decisions),
        "decision_counts": {name: sum(item["decision"] == name for item in decisions) for name in names},
        "decisions": decisions,
        "evidence_boundary": (
            "Decisions are deterministic evaluations of supplied, validated metadata. SMERC preserves the "
            "declared evidence class and source digest but does not verify upstream truth, AWS attestation, "
            "customer production safety, or complete transport enforcement."
        ),
    }


def evaluate_evidence_record(record: Mapping[str, Any]) -> dict[str, Any]:
    observation = record["observations"]
    intent = hashlib.sha256(str(observation["action_id"]).encode("utf-8")).hexdigest()
    base = build_base_inputs(intent)
    runtime = dict(base["authority_runtime"])
    runtime["current_authority_epoch"] = observation["current_authority_epoch"]
    runtime["revoked_contract_ids"] = ["authority-aws-proof"] if observation["revoked"] else []
    runtime["trigger_events"] = (
        ["authority_epoch_changed"]
        if observation["authority_epoch"] != observation["current_authority_epoch"] else []
    )
    runtime["satisfied_settlement_requirements"] = [
        name for name, satisfied in (
            ("outcome_verified", observation["outcome_verified"]),
            ("cleanup_verified", observation["cleanup_verified"]),
        ) if satisfied
    ]
    grant = dict(base["authority_grant"])
    grant["authority_epoch"] = observation["authority_epoch"]
    acquired_observation = dict(base["acquired_observation"])
    acquired_observation["current_authority_epoch"] = observation["current_authority_epoch"]
    external = observation["external_side_effect"]
    proposed_action = {
        "capability": "aws:MutateBounded" if external else "aws:Read",
        "resource": "aws:ephemeral-security-group" if external else "aws:account-summary",
        "intent_digest": intent,
        "scope_units": observation["scope_units"],
        "cost_usd": observation["cost_usd"],
        "external_side_effect": external,
        "checkpoint_present": True,
        "cleanup_plan_present": observation["rollback_available"] or not external,
    }
    result = reconcile_consequence_time(
        **{**base, "authority_grant": grant, "authority_runtime": runtime,
           "acquired_observation": acquired_observation},
        proposed_action=proposed_action,
        consumption={"actions": 0, "scope_units": 0, "cost_usd": 0},
        now=runtime["observed_at"],
        partial_effects_present=observation["partial_effects_present"],
    )
    required_actions = {
        "SETTLE": [],
        "QUARANTINE": ["hold_commit", "revalidate_authority_and_evidence"],
        "COMPENSATE": ["execute_compensation", "verify_cleanup_before_settlement"],
        "DENY": ["do_not_execute", "submit_materially_safer_action"],
    }[result["decision"]]
    return {
        "evidence_id": record["evidence_id"],
        "evidence_class": record["evidence_class"],
        "source_sha256": record["source_sha256"],
        "action_id": observation["action_id"],
        "operation": observation["operation"],
        "decision": result["decision"],
        "should_commit": result["should_commit"],
        "reasons": result["reasons"],
        "required_actions": required_actions,
        "limitations": list(record["limitations"]),
        "reconciliation": result,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = ["# Authorization-Afterlife Pilot Decisions", "", f"- Pilot: `{report['pilot_id']}`",
             f"- Records: `{report['record_count']}`", f"- Decisions: `{report['decision_counts']}`",
             "", "## Decision Records", ""]
    for item in report["decisions"]:
        lines.extend([f"### {item['evidence_id']}", "", f"- Evidence class: `{item['evidence_class']}`",
                      f"- Action: `{item['action_id']}` / `{item['operation']}`",
                      f"- Decision: `{item['decision']}`",
                      f"- Should commit: `{str(item['should_commit']).lower()}`",
                      f"- Reasons: {', '.join(item['reasons']) or 'none'}",
                      f"- Required actions: {', '.join(item['required_actions']) or 'none'}", ""])
    lines.extend(["## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run authorization-afterlife pilot evidence")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-output", default="reports/authorization_afterlife_pilot/pilot.json")
    parser.add_argument("--markdown-output", default="reports/authorization_afterlife_pilot/Pilot.md")
    args = parser.parse_args()
    report = run_manifest(json.loads(args.manifest.read_text(encoding="utf-8")))
    json_path, markdown_path = Path(args.json_output), Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"pilot_id": report["pilot_id"], "decisions": report["decision_counts"]}, indent=2))


if __name__ == "__main__":
    main()

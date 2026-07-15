from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.audit_store import AuditStore
from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.recoverability_engine import RecoverabilityEngine


CISO_REVIEW_SEED_VERSION = "smerc.ciso-review-seed.v1"
DEFAULT_TENANT_ID = "pilot-team"
DEFAULT_PRINCIPAL_ID = "ciso-review-seed"
DEFAULT_BASE_TIME = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)


def canonical_hash(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_actions(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("seed action file must contain a non-empty JSON array")
    actions: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"seed action {index} must be an object")
        action_id = item.get("action_id")
        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError(f"seed action {index} must include action_id")
        if action_id in seen:
            raise ValueError(f"duplicate seed action_id: {action_id}")
        seen.add(action_id)
        actions.append(dict(item))
    return actions


def build_decision_time_ledger(
    action: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    tenant_id: str,
    base_time: datetime = DEFAULT_BASE_TIME,
    offset_minutes: int = 0,
) -> DecisionLifecycleLedger:
    recorded = base_time + timedelta(minutes=offset_minutes)
    decision_id = f"dll:ciso-review:{action['action_id'].lower()}"
    context = action.get("context", {}) if isinstance(action.get("context"), dict) else {}
    scores = decision.get("scores", {})
    ledger = DecisionLifecycleLedger(decision_id, tenant_id=tenant_id)
    ledger.append(
        "REQUEST",
        str(action["actor"]),
        {
            "initiated_by": str(action["actor"]),
            "requested_operation": str(action["description"]),
            "environment": str(context.get("environment", "pilot_review")),
            "risk_profile": str(context.get("domain_profile", action["action_type"])),
        },
        recorded_at=recorded.isoformat(),
    )
    ledger.append(
        "EVIDENCE",
        "smerc-ciso-review-seed",
        {
            "available_evidence": [
                "structured_action_request",
                "recoverability_score_trace",
                "policy_threshold_trace",
                "reason_codes",
                "recommended_controls",
            ],
            "confidence_score": float(scores.get("confidence_score", 0.0)),
            "missing_evidence": [
                "live_execution_result",
                "human_reviewer_label",
                "customer_incident_outcome",
                "production_latency_impact",
            ],
            "external_dependencies": [str(action["tool"])],
            "model_version": "reference_engine.recoverability_engine",
            "policy_version": str(decision.get("policy", {}).get("policy_id", "smerc.policy.v1")),
        },
        recorded_at=(recorded + timedelta(seconds=2)).isoformat(),
    )
    ledger.append(
        "EVALUATION",
        "smerc-engine",
        {
            "structural_state": str(decision.get("plain_english_summary", ""))[:512],
            "entropy_indicators": list(decision.get("reason_codes") or ["NO_REASON_CODES"]),
            "recoverability_score": float(scores.get("reversible_capacity_score", 0.0)),
            "authorization_recommendation": str(decision["posture"]),
            "reason_codes": list(decision.get("reason_codes") or ["NO_REASON_CODES"]),
            "recommended_safeguards": list(decision.get("controls") or ["preserve_replay"]),
        },
        recorded_at=(recorded + timedelta(seconds=4)).isoformat(),
    )
    return ledger


def seed_ciso_review(
    actions: Iterable[Mapping[str, Any]],
    *,
    audit_db: str | Path,
    tenant_id: str = DEFAULT_TENANT_ID,
    principal_id: str = DEFAULT_PRINCIPAL_ID,
) -> Dict[str, Any]:
    store = AuditStore(audit_db)
    engine = RecoverabilityEngine()
    seeded: list[Dict[str, Any]] = []
    try:
        for index, action in enumerate(actions):
            action_payload = dict(action)
            decision = engine.evaluate(action_payload)
            request_hash = canonical_hash(action_payload)
            idempotency_key = f"ciso-review-seed:{action_payload['action_id']}"
            stored_decision = store.record(
                tenant_id,
                decision,
                request_hash,
                idempotency_key=idempotency_key,
            )
            ledger = build_decision_time_ledger(
                action_payload,
                stored_decision,
                tenant_id=tenant_id,
                offset_minutes=index,
            )
            stored_ledger = store.record_decision_lifecycle_ledger(
                tenant_id,
                ledger.to_dict(),
                principal_id=principal_id,
            )
            store.record_security_event(
                tenant_id,
                principal_id,
                "ciso_review.seeded_decision",
                stored_decision["replay_id"],
                {
                    "action_id": stored_decision["action_id"],
                    "posture": stored_decision["posture"],
                    "dll_decision_id": stored_ledger["decision_id"],
                    "evidence_boundary": "seeded walkthrough data; not customer evidence",
                },
            )
            seeded.append(
                {
                    "action_id": stored_decision["action_id"],
                    "replay_id": stored_decision["replay_id"],
                    "posture": stored_decision["posture"],
                    "scores": stored_decision["scores"],
                    "reason_codes": stored_decision["reason_codes"],
                    "controls": stored_decision["controls"],
                    "dll_decision_id": stored_ledger["decision_id"],
                    "dll_head_record_hash": stored_ledger["head_record_hash"],
                    "summary": stored_decision["plain_english_summary"],
                }
            )
        metrics = store.pilot_metrics(tenant_id)
        ledgers = store.list_decision_lifecycle_ledgers(tenant_id, limit=200)
        return {
            "version": CISO_REVIEW_SEED_VERSION,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "audit_db": str(audit_db),
            "seeded_decision_count": len(seeded),
            "stored_ledger_count": len(ledgers),
            "seeded_decisions": seeded,
            "pilot_metrics": metrics,
            "evidence_boundary": (
                "This walkthrough seeds synthetic but realistic review data. It proves the local product flow, "
                "not customer validation, production safety, or incident reduction."
            ),
            "next_steps": [
                "Start the authenticated API against the same audit database.",
                "Open the pilot console and connect with a principal that has decisions.read, reviews.read, reviews.write, metrics.read, and audit.read.",
                "Review the seeded decisions in the queue.",
                "Generate a stored DLL evidence package using one of the listed dll_decision_id values.",
            ],
        }
    finally:
        store.close()


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC CISO Evidence Walkthrough Seed Report",
        "",
        f"Version: `{report['version']}`",
        f"Generated at: `{report['generated_at']}`",
        f"Tenant: `{report['tenant_id']}`",
        f"Audit database: `{report['audit_db']}`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Seeded Decisions",
        "",
        "| Action | Posture | Replay ID | DLL decision ID |",
        "| --- | --- | --- | --- |",
    ]
    for item in report["seeded_decisions"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['posture']}` | `{item['replay_id']}` | `{item['dll_decision_id']}` |"
        )
    lines.extend(["", "## Reviewer Flow", ""])
    for index, step in enumerate(report["next_steps"], start=1):
        lines.append(f"{index}. {step}")
    lines.extend(
        [
            "",
            "## What This Demonstrates",
            "",
            "- SMERC can evaluate realistic AI-agent actions into reviewable postures.",
            "- The pilot API can expose those decisions through the review queue.",
            "- Stored DLL records can be used to generate CISO evidence packages.",
            "- The flow is replayable without claiming production validation.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed a local SMERC audit database for the CISO evidence walkthrough.")
    parser.add_argument(
        "--actions",
        default="examples/ciso_review_seed_actions.json",
        help="Path to CISO review seed actions JSON.",
    )
    parser.add_argument("--audit-db", default="./smerc_ciso_review.sqlite3", help="SQLite audit database to create or update.")
    parser.add_argument("--tenant-id", default=DEFAULT_TENANT_ID, help="Tenant ID for seeded records.")
    parser.add_argument("--principal-id", default=DEFAULT_PRINCIPAL_ID, help="Principal ID recorded in security events.")
    parser.add_argument("--json-output", default="reports/ciso_evidence_walkthrough_seed.json")
    parser.add_argument("--markdown-output", default="reports/CISO_Evidence_Walkthrough_Seed_Report.md")
    parser.add_argument("--pretty", action="store_true", help="Print the seed report JSON.")
    args = parser.parse_args()

    report = seed_ciso_review(
        load_actions(args.actions),
        audit_db=args.audit_db,
        tenant_id=args.tenant_id,
        principal_id=args.principal_id,
    )
    write_report(report, args.json_output, args.markdown_output)
    if args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from reference_engine.decision_certificate import (
    build_decision_certificate,
    verify_decision_certificate,
)
from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger


PILOT_EVIDENCE_PACKAGE_VERSION = "smerc.pilot-evidence-package.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sorted_events(events: Iterable[Mapping[str, Any]], decision_id: str, certificate_id: str) -> list[Dict[str, Any]]:
    relevant = []
    for event in events:
        if not isinstance(event, Mapping):
            continue
        metadata = event.get("metadata", {})
        if not isinstance(metadata, Mapping):
            metadata = {}
        if event.get("resource_id") in {decision_id, certificate_id} or metadata.get("decision_id") == decision_id:
            relevant.append(dict(event))
    return sorted(relevant, key=lambda item: str(item.get("created_at", "")))


def build_pilot_evidence_package(
    ledger: DecisionLifecycleLedger | Mapping[str, Any],
    *,
    certificate: Optional[Mapping[str, Any]] = None,
    route_report: Optional[Mapping[str, Any]] = None,
    security_events: Iterable[Mapping[str, Any]] = (),
    generated_by: str = "smerc-reference-engine",
    generated_at: Optional[str] = None,
) -> Dict[str, Any]:
    ledger_obj = ledger if isinstance(ledger, DecisionLifecycleLedger) else DecisionLifecycleLedger.from_dict(ledger)
    ledger_data = ledger_obj.to_dict()
    if not ledger_data["verification"]["valid"]:
        raise ValueError("source Decision Lifecycle Ledger must verify before evidence packaging")
    if certificate is None:
        certificate_data = build_decision_certificate(ledger_data, route_report=route_report, issuer=generated_by)
    else:
        certificate_data = dict(certificate)
    verification = verify_decision_certificate(certificate_data, source_ledger=ledger_data, route_report=route_report)
    if not verification["valid"]:
        raise ValueError("Decision Certificate does not verify against the source DLL")

    event_types = [record["event_type"] for record in ledger_data["records"]]
    certificate_id = str(certificate_data["certificate_id"])
    relevant_events = _sorted_events(security_events, ledger_obj.decision_id, certificate_id)
    package = {
        "version": PILOT_EVIDENCE_PACKAGE_VERSION,
        "generated_at": generated_at or _utc_now(),
        "generated_by": generated_by,
        "tenant_id": ledger_obj.tenant_id,
        "decision_id": ledger_obj.decision_id,
        "evidence_status": "pilot_review_package",
        "decision_summary": {
            "requested_operation": certificate_data.get("request", {}).get("requested_operation"),
            "environment": certificate_data.get("request", {}).get("environment"),
            "authorization_recommendation": certificate_data.get("evaluation", {}).get("authorization_recommendation"),
            "recoverability_score": certificate_data.get("evaluation", {}).get("recoverability_score"),
            "execution_status": certificate_data.get("execution", {}).get("execution_status"),
            "judged_correct": certificate_data.get("outcome", {}).get("judged_correct"),
        },
        "source_ledger": {
            "version": ledger_data["version"],
            "record_count": ledger_data["record_count"],
            "head_record_hash": ledger_data["head_record_hash"],
            "event_types": event_types,
            "verification": ledger_data["verification"],
            "stored_at": ledger_data.get("stored_at"),
            "updated_at": ledger_data.get("updated_at"),
        },
        "decision_certificate": certificate_data,
        "certificate_verification": verification,
        "audit_events": relevant_events,
        "audit_event_summary": {
            "included_event_count": len(relevant_events),
            "event_types": sorted({str(event.get("event_type")) for event in relevant_events}),
        },
        "review_focus": [
            "Confirm the source DLL hash chain verifies.",
            "Confirm the Decision Certificate digest binds to the DLL head hash.",
            "Review human override, execution, rollback, and outcome records before relying on rates.",
            "Treat learning recommendations as review-only unless separately approved.",
        ],
        "boundary": {
            "claims": [
                "packages a stored, verified pilot Decision Lifecycle Ledger for review",
                "includes a digest-verified Decision Certificate bound to the source DLL",
                "includes tenant-scoped audit/security events related to the decision when supplied",
            ],
            "limits": [
                "pilot evidence package, not production certification",
                "does not provide immutable storage or legal retention by itself",
                "does not prove source-system facts were accurate without independent source logs",
                "does not replace IAM, SIEM, approval workflows, code review, or compliance controls",
            ],
        },
    }
    package["markdown_report"] = render_markdown(package)
    return package


def render_markdown(package: Mapping[str, Any]) -> str:
    decision = package.get("decision_summary", {})
    ledger = package.get("source_ledger", {})
    certificate = package.get("decision_certificate", {})
    verification = package.get("certificate_verification", {})
    audit_summary = package.get("audit_event_summary", {})
    boundary = package.get("boundary", {})

    lines = [
        "# SMERC Pilot Evidence Package",
        "",
        f"- Tenant: `{package.get('tenant_id')}`",
        f"- Decision ID: `{package.get('decision_id')}`",
        f"- Generated: `{package.get('generated_at')}`",
        f"- Evidence status: `{package.get('evidence_status')}`",
        "",
        "## Decision Summary",
        "",
        f"- Requested operation: {decision.get('requested_operation')}",
        f"- Environment: `{decision.get('environment')}`",
        f"- Authorization recommendation: `{decision.get('authorization_recommendation')}`",
        f"- Recoverability score: `{decision.get('recoverability_score')}`",
        f"- Execution status: `{decision.get('execution_status')}`",
        f"- Judged correct: `{decision.get('judged_correct')}`",
        "",
        "## Evidence Binding",
        "",
        f"- Ledger record count: `{ledger.get('record_count')}`",
        f"- Ledger head hash: `{ledger.get('head_record_hash')}`",
        f"- Certificate ID: `{certificate.get('certificate_id')}`",
        f"- Certificate digest: `{certificate.get('certificate_digest')}`",
        f"- Certificate valid against source DLL: `{'yes' if verification.get('valid') else 'no'}`",
        "",
        "## Audit Events",
        "",
        f"- Included event count: `{audit_summary.get('included_event_count')}`",
        f"- Event types: `{', '.join(audit_summary.get('event_types', [])) or 'none'}`",
        "",
        "## Review Focus",
        "",
    ]
    lines.extend(f"- {item}" for item in package.get("review_focus", []))
    lines.extend(["", "## Boundary", ""])
    lines.extend(f"- {item}" for item in boundary.get("limits", []))
    return "\n".join(lines) + "\n"


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def write_bundle(package: Mapping[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "pilot-evidence-package.json"
    markdown_path = target / "pilot-evidence-package.md"
    json_path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(str(package["markdown_report"]), encoding="utf-8")
    return json_path, markdown_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a SMERC pilot evidence package from a DLL.")
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--route-report", type=Path)
    parser.add_argument("--security-events", type=Path)
    parser.add_argument("--generated-by", default="smerc-reference-engine")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    events_payload = load_json(args.security_events) if args.security_events else {}
    events = events_payload.get("events", []) if isinstance(events_payload.get("events", []), list) else []
    package = build_pilot_evidence_package(
        load_json(args.ledger),
        certificate=load_json(args.certificate) if args.certificate else None,
        route_report=load_json(args.route_report) if args.route_report else None,
        security_events=events,
        generated_by=args.generated_by,
    )
    if args.output_dir:
        write_bundle(package, args.output_dir)
    print(json.dumps(package, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

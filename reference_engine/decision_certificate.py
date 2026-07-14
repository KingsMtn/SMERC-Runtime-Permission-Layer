from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from reference_engine.decision_lifecycle_ledger import (
    LEDGER_VERSION,
    DecisionLifecycleLedger,
)
from reference_engine.sparta_router import SPARTA_ROUTE_VERSION, route_report_digest


CERTIFICATE_VERSION = "smerc.decision-certificate.v1"
CERTIFICATE_SIGNATURE_VERSION = "smerc.decision-certificate-signature.v1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def certificate_digest(certificate: Mapping[str, Any]) -> str:
    material = {
        key: value
        for key, value in dict(certificate).items()
        if key not in {"certificate_digest", "signature", "verification"}
    }
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def _text(value: Any, path: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _record_by_type(ledger: Mapping[str, Any], event_type: str) -> Optional[Mapping[str, Any]]:
    records = [record for record in ledger.get("records", []) if record.get("event_type") == event_type]
    return records[-1] if records else None


def _payload(ledger: Mapping[str, Any], event_type: str) -> Dict[str, Any]:
    record = _record_by_type(ledger, event_type)
    if not record:
        return {}
    payload = record.get("payload", {})
    if not isinstance(payload, dict):
        return {}
    return dict(payload)


def _route_binding(route_report: Optional[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    if route_report is None:
        return None
    if not isinstance(route_report, dict):
        raise TypeError("route_report must be an object")
    if route_report.get("version") != SPARTA_ROUTE_VERSION:
        raise ValueError(f"route_report.version must be {SPARTA_ROUTE_VERSION}")
    return {
        "route_id": route_report.get("route_id"),
        "route_report_digest": route_report_digest(route_report),
        "route_state": route_report.get("route_state"),
        "executable": route_report.get("executable"),
        "source_posture": route_report.get("source_posture"),
        "applied_controls": list(route_report.get("applied_controls", [])),
        "signature_present": isinstance(route_report.get("signature"), dict),
    }


def build_decision_certificate(
    ledger: DecisionLifecycleLedger | Mapping[str, Any],
    *,
    route_report: Optional[Mapping[str, Any]] = None,
    issuer: str = "smerc-reference-engine",
    issued_at: Optional[str] = None,
) -> Dict[str, Any]:
    ledger_obj = ledger if isinstance(ledger, DecisionLifecycleLedger) else DecisionLifecycleLedger.from_dict(ledger)
    ledger_data = ledger_obj.to_dict()
    verification = ledger_data["verification"]
    if not verification["valid"]:
        raise ValueError("source Decision Lifecycle Ledger must verify before certificate issuance")

    request = _payload(ledger_data, "REQUEST")
    evidence = _payload(ledger_data, "EVIDENCE")
    evaluation = _payload(ledger_data, "EVALUATION")
    human = _payload(ledger_data, "HUMAN_INTERACTION")
    execution = _payload(ledger_data, "EXECUTION")
    outcome = _payload(ledger_data, "OUTCOME")
    learning = _payload(ledger_data, "LEARNING_RECOMMENDATION")
    event_types = [record["event_type"] for record in ledger_data["records"]]

    certificate = {
        "version": CERTIFICATE_VERSION,
        "certificate_id": f"cert:{ledger_obj.decision_id}:{ledger_data['head_record_hash'][:16]}",
        "issued_at": issued_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "issuer": _text(issuer, "issuer", 128),
        "tenant_id": ledger_obj.tenant_id,
        "decision_id": ledger_obj.decision_id,
        "lifecycle_binding": {
            "ledger_version": LEDGER_VERSION,
            "record_count": ledger_data["record_count"],
            "head_record_hash": ledger_data["head_record_hash"],
            "event_types": event_types,
            "complete_lifecycle": all(
                event in set(event_types)
                for event in {
                    "REQUEST",
                    "EVIDENCE",
                    "EVALUATION",
                    "HUMAN_INTERACTION",
                    "EXECUTION",
                    "OUTCOME",
                    "LEARNING_RECOMMENDATION",
                }
            ),
            "ledger_verification": {
                "valid": True,
                "errors": [],
            },
        },
        "request": {
            "initiated_by": request.get("initiated_by"),
            "requested_operation": request.get("requested_operation"),
            "environment": request.get("environment"),
            "risk_profile": request.get("risk_profile"),
        },
        "evidence": {
            "confidence_score": evidence.get("confidence_score"),
            "missing_evidence": list(evidence.get("missing_evidence", [])),
            "external_dependencies": list(evidence.get("external_dependencies", [])),
            "model_version": evidence.get("model_version"),
            "policy_version": evidence.get("policy_version"),
        },
        "evaluation": {
            "authorization_recommendation": evaluation.get("authorization_recommendation"),
            "recoverability_score": evaluation.get("recoverability_score"),
            "reason_codes": list(evaluation.get("reason_codes", [])),
            "recommended_safeguards": list(evaluation.get("recommended_safeguards", [])),
        },
        "human_interaction": {
            "interaction": human.get("interaction"),
            "reviewer_id": human.get("reviewer_id"),
            "original_recommendation": human.get("original_recommendation"),
            "final_recommendation": human.get("final_recommendation"),
        },
        "execution": {
            "execution_status": execution.get("execution_status"),
            "executed_operation": execution.get("executed_operation"),
            "rollback_performed": execution.get("rollback_performed"),
            "rollback_success": execution.get("rollback_success"),
        },
        "outcome": {
            "judged_correct": outcome.get("judged_correct"),
            "unexpected_consequences": outcome.get("unexpected_consequences"),
            "controls_sufficient": outcome.get("controls_sufficient"),
            "time_to_recover_minutes": outcome.get("time_to_recover_minutes"),
            "customer_impact": outcome.get("customer_impact"),
            "security_impact": outcome.get("security_impact"),
            "financial_impact": outcome.get("financial_impact"),
        },
        "learning": {
            "activation_status": learning.get("activation_status"),
            "recommended_policy_updates": list(learning.get("recommended_policy_updates", [])),
            "confidence_calibration_changes": list(learning.get("confidence_calibration_changes", [])),
            "suggested_rule_modifications": list(learning.get("suggested_rule_modifications", [])),
        },
        "route_binding": _route_binding(route_report),
        "boundary": {
            "record_type": "pilot decision certificate",
            "claims": [
                "summarizes a verified Decision Lifecycle Ledger at issuance time",
                "detects certificate tampering through a deterministic digest",
                "can bind the certificate to a SPARTa route report digest",
            ],
            "limits": [
                "does not provide immutable storage by itself",
                "does not establish legal recordkeeping or regulatory retention by itself",
                "does not prove source-system facts were accurate unless source evidence is independently retained",
                "does not automatically activate learning recommendations",
            ],
        },
    }
    certificate["certificate_digest"] = certificate_digest(certificate)
    certificate["verification"] = verify_decision_certificate(certificate)
    return certificate


def sign_decision_certificate(
    certificate: Mapping[str, Any],
    signing_key: str,
    *,
    key_id: str = "local-decision-certificate-key",
) -> Dict[str, Any]:
    if not isinstance(signing_key, str) or len(signing_key) < 16:
        raise ValueError("signing_key must be a string of at least 16 characters")
    key_id = _text(key_id, "key_id", 128)
    signed = {key: value for key, value in dict(certificate).items() if key not in {"signature", "verification"}}
    digest = certificate_digest(signed)
    signed["certificate_digest"] = digest
    signed["signature"] = {
        "version": CERTIFICATE_SIGNATURE_VERSION,
        "algorithm": "HMAC-SHA256",
        "key_id": key_id,
        "certificate_digest": digest,
        "signature": hmac.new(signing_key.encode("utf-8"), digest.encode("ascii"), hashlib.sha256).hexdigest(),
    }
    signed["verification"] = verify_decision_certificate(signed, signing_key=signing_key)
    return signed


def verify_decision_certificate(
    certificate: Mapping[str, Any],
    *,
    signing_key: Optional[str] = None,
    source_ledger: Optional[DecisionLifecycleLedger | Mapping[str, Any]] = None,
    route_report: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    errors: list[str] = []
    if not isinstance(certificate, dict):
        return {"valid": False, "errors": ["certificate must be an object"]}
    if certificate.get("version") != CERTIFICATE_VERSION:
        errors.append("invalid certificate version")
    expected_digest = certificate_digest(certificate)
    if not hmac.compare_digest(str(certificate.get("certificate_digest", "")), expected_digest):
        errors.append("certificate digest mismatch")

    signature = certificate.get("signature")
    if signature is not None:
        if not isinstance(signature, dict):
            errors.append("signature must be an object")
        else:
            required = {"version", "algorithm", "key_id", "certificate_digest", "signature"}
            missing = sorted(required - set(signature))
            if missing:
                errors.append(f"signature missing field(s): {', '.join(missing)}")
            if signature.get("version") != CERTIFICATE_SIGNATURE_VERSION:
                errors.append("invalid signature version")
            if signature.get("algorithm") != "HMAC-SHA256":
                errors.append("invalid signature algorithm")
            if not hmac.compare_digest(str(signature.get("certificate_digest", "")), expected_digest):
                errors.append("signature digest mismatch")
            if signing_key is not None:
                expected_signature = hmac.new(
                    signing_key.encode("utf-8"),
                    expected_digest.encode("ascii"),
                    hashlib.sha256,
                ).hexdigest()
                if not hmac.compare_digest(str(signature.get("signature", "")), expected_signature):
                    errors.append("signature mismatch")
    elif signing_key is not None:
        errors.append("missing signature")

    binding = certificate.get("lifecycle_binding", {})
    if not isinstance(binding, dict):
        errors.append("lifecycle_binding must be an object")
    else:
        if binding.get("ledger_version") != LEDGER_VERSION:
            errors.append("invalid bound ledger version")
        if not binding.get("head_record_hash"):
            errors.append("missing bound head record hash")

    if source_ledger is not None:
        ledger_obj = source_ledger if isinstance(source_ledger, DecisionLifecycleLedger) else DecisionLifecycleLedger.from_dict(source_ledger)
        ledger_data = ledger_obj.to_dict()
        if not ledger_data["verification"]["valid"]:
            errors.append("source ledger does not verify")
        if certificate.get("decision_id") != ledger_obj.decision_id:
            errors.append("source ledger decision_id mismatch")
        if certificate.get("tenant_id") != ledger_obj.tenant_id:
            errors.append("source ledger tenant_id mismatch")
        if isinstance(binding, dict) and binding.get("head_record_hash") != ledger_data["head_record_hash"]:
            errors.append("source ledger head hash mismatch")

    if route_report is not None:
        expected_binding = _route_binding(route_report)
        actual_binding = certificate.get("route_binding")
        if expected_binding is None or actual_binding is None:
            errors.append("missing route binding")
        elif actual_binding.get("route_report_digest") != expected_binding["route_report_digest"]:
            errors.append("route report digest mismatch")

    return {
        "valid": not errors,
        "errors": errors,
        "certificate_digest": expected_digest,
        "signature_checked": signing_key is not None,
    }


def render_markdown(certificate: Mapping[str, Any]) -> str:
    verification = verify_decision_certificate(certificate)
    def yes_no(value: Any) -> str:
        if value is True:
            return "yes"
        if value is False:
            return "no"
        return str(value)

    lines = [
        "# SMERC Decision Certificate",
        "",
        f"Certificate ID: `{certificate.get('certificate_id')}`",
        f"Decision ID: `{certificate.get('decision_id')}`",
        f"Tenant: `{certificate.get('tenant_id')}`",
        f"Certificate digest: `{certificate.get('certificate_digest')}`",
        f"Digest valid: `{'yes' if verification['valid'] else 'no'}`",
        "",
        "## Decision",
        "",
        f"- Requested operation: {certificate.get('request', {}).get('requested_operation')}",
        f"- Environment: `{certificate.get('request', {}).get('environment')}`",
        f"- Recommendation: `{certificate.get('evaluation', {}).get('authorization_recommendation')}`",
        f"- Recoverability score: `{certificate.get('evaluation', {}).get('recoverability_score')}`",
        f"- Execution status: `{certificate.get('execution', {}).get('execution_status')}`",
        f"- Judged correct: `{yes_no(certificate.get('outcome', {}).get('judged_correct'))}`",
        "",
        "## Lifecycle Binding",
        "",
        f"- Head record hash: `{certificate.get('lifecycle_binding', {}).get('head_record_hash')}`",
        f"- Record count: `{certificate.get('lifecycle_binding', {}).get('record_count')}`",
        f"- Complete lifecycle: `{yes_no(certificate.get('lifecycle_binding', {}).get('complete_lifecycle'))}`",
        "",
    ]
    route_binding = certificate.get("route_binding")
    if isinstance(route_binding, dict):
        lines.extend(
            [
                "## Route Binding",
                "",
                f"- Route ID: `{route_binding.get('route_id')}`",
                f"- Route state: `{route_binding.get('route_state')}`",
                f"- Route report digest: `{route_binding.get('route_report_digest')}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            "This certificate is a pilot-grade, digest-bound summary of a verified Decision Lifecycle Ledger. It is not, by itself, immutable storage, legal recordkeeping, regulatory retention, or proof that source-system facts were accurate.",
        ]
    )
    return "\n".join(lines) + "\n"


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify a SMERC Decision Certificate.")
    parser.add_argument("--ledger", type=Path, required=True, help="Decision Lifecycle Ledger JSON file.")
    parser.add_argument("--route-report", type=Path, help="Optional SPARTa route report JSON file to bind.")
    parser.add_argument("--issuer", default="smerc-reference-engine")
    parser.add_argument("--signing-key", help="Optional HMAC key used to sign the certificate.")
    parser.add_argument("--key-id", default="local-decision-certificate-key")
    parser.add_argument("--verify", action="store_true", help="Verify the certificate before printing.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    certificate = build_decision_certificate(
        load_json(args.ledger),
        route_report=load_json(args.route_report) if args.route_report else None,
        issuer=args.issuer,
    )
    if args.signing_key:
        certificate = sign_decision_certificate(certificate, args.signing_key, key_id=args.key_id)
    if args.verify:
        certificate["verification"] = verify_decision_certificate(
            certificate,
            signing_key=args.signing_key,
            source_ledger=load_json(args.ledger),
            route_report=load_json(args.route_report) if args.route_report else None,
        )
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(certificate, indent=2, sort_keys=True), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(render_markdown(certificate), encoding="utf-8")
    print(json.dumps(certificate, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

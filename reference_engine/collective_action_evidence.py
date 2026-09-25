from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

VERSION = "smerc.runtime-assurance.collective-action-evidence.v1"
AA_ENVELOPE_VERSION = "smerc.collective-decision-envelope.v1"
AA_REPORT_VERSION = "smerc.collective-action-assurance.v1"


def evaluate_collective_action_evidence(
    envelope: Mapping[str, Any], *, now_ms: int, expected_resource: str,
    expected_action: str, expected_operation_id: str,
    expected_predecessor_sha256: str | None = None,
) -> dict[str, Any]:
    """Validate Collective Action Assurance evidence without treating it as authority."""
    try:
        normalized = _validate_envelope(
            envelope, now_ms=now_ms, expected_resource=expected_resource,
            expected_action=expected_action, expected_operation_id=expected_operation_id,
            expected_predecessor_sha256=expected_predecessor_sha256,
        )
    except ValueError as exc:
        return _result("REJECT", "DENY", ["AA_EVIDENCE_INVALID"],
            ["replace_collective_action_evidence_before_execution"], str(exc),
            envelope.get("envelope_id") if isinstance(envelope, Mapping) else None)
    if normalized["collective_decision"] == "ADVISE_REVIEW":
        return _result("ESCALATE", "FREEZE", ["AA_COLLECTIVE_REVIEW_ADVISED"],
            ["obtain_collective_action_review_before_execution"],
            "Collective Action Assurance (AA) found a collective consequence requiring review. "
            "Runtime Assurance (RA) preserves that constraint without treating AA as an authority grant.",
            normalized["envelope_id"])
    return _result("ACCEPT_EVIDENCE", None,
        ["AA_EVIDENCE_VERIFIED_NO_COLLECTIVE_RISK_OBSERVED"], [],
        "Collective Action Assurance (AA) evidence passed integrity and context checks. "
        "It adds no permission; Runtime Assurance (RA) must still apply its other gates.",
        normalized["envelope_id"])


def _validate_envelope(envelope: Mapping[str, Any], *, now_ms: int,
    expected_resource: str, expected_action: str, expected_operation_id: str,
    expected_predecessor_sha256: str | None) -> Mapping[str, Any]:
    if not isinstance(envelope, Mapping):
        raise ValueError("collective action envelope must be an object")
    required = {
        "contract_version", "producer_report_version", "issued_at_ms", "expires_at_ms",
        "scope", "collective_decision", "risk_group_count", "participant_ids", "quorum",
        "continuity", "evidence", "authority_effect", "advisory_only",
        "envelope_sha256", "envelope_id",
    }
    if set(envelope) != required:
        raise ValueError("collective action envelope fields do not match the v1 contract")
    if envelope["contract_version"] != AA_ENVELOPE_VERSION:
        raise ValueError("collective action envelope version is unsupported")
    if envelope["producer_report_version"] != AA_REPORT_VERSION:
        raise ValueError("Collective Action Assurance report version is unsupported")
    if envelope["collective_decision"] not in {"NO_COLLECTIVE_RISK_OBSERVED", "ADVISE_REVIEW"}:
        raise ValueError("collective action decision is invalid")
    if envelope["authority_effect"] != "NONE" or envelope["advisory_only"] is not True:
        raise ValueError("Collective Action Assurance evidence cannot grant authority")
    if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
        raise ValueError("now_ms must be a non-negative integer")
    issued_at = _integer(envelope["issued_at_ms"], "issued_at_ms")
    expires_at = _integer(envelope["expires_at_ms"], "expires_at_ms")
    if expires_at <= issued_at:
        raise ValueError("collective action evidence validity window is invalid")
    if now_ms < issued_at:
        raise ValueError("collective action evidence is not yet valid")
    if now_ms >= expires_at:
        raise ValueError("collective action evidence has expired")

    participants = envelope["participant_ids"]
    if not isinstance(participants, list) or participants != sorted(set(participants)) or not participants:
        raise ValueError("participant_ids must be non-empty, unique, and sorted")
    for participant in participants:
        _text(participant, "participant_ids")
    quorum = envelope["quorum"]
    if not isinstance(quorum, Mapping) or set(quorum) != {"required", "observed", "satisfied"}:
        raise ValueError("quorum fields do not match the v1 contract")
    required_quorum = _integer(quorum["required"], "quorum.required")
    observed = _integer(quorum["observed"], "quorum.observed")
    if required_quorum < 1 or observed != len(participants):
        raise ValueError("collective action quorum is inconsistent")
    if quorum["satisfied"] is not (observed >= required_quorum) or not quorum["satisfied"]:
        raise ValueError("collective action quorum is not satisfied")

    scope = envelope["scope"]
    if not isinstance(scope, Mapping) or set(scope) != {"resource", "action", "operation_id"}:
        raise ValueError("collective action scope fields do not match the v1 contract")
    expectations = {"resource": expected_resource, "action": expected_action,
        "operation_id": expected_operation_id}
    for key, expected in expectations.items():
        if _text(scope.get(key), f"scope.{key}") != _text(expected, f"expected_{key}"):
            raise ValueError(f"collective action scope.{key} does not match the runtime action")

    continuity = envelope["continuity"]
    if not isinstance(continuity, Mapping) or set(continuity) != {"predecessor_envelope_sha256"}:
        raise ValueError("continuity fields do not match the v1 contract")
    predecessor = continuity["predecessor_envelope_sha256"]
    if predecessor is not None:
        _digest(predecessor, "continuity.predecessor_envelope_sha256")
    if expected_predecessor_sha256 is not None:
        _digest(expected_predecessor_sha256, "expected_predecessor_sha256")
        if predecessor != expected_predecessor_sha256:
            raise ValueError("collective action continuity predecessor does not match")

    evidence = envelope["evidence"]
    if not isinstance(evidence, Mapping) or set(evidence) != {"report_sha256", "finding_ids"}:
        raise ValueError("collective action evidence fields do not match the v1 contract")
    _digest(evidence["report_sha256"], "evidence.report_sha256")
    finding_ids = evidence["finding_ids"]
    if not isinstance(finding_ids, list) or finding_ids != sorted(set(finding_ids)):
        raise ValueError("collective action finding_ids must be unique and sorted")
    supplied_digest = _digest(envelope["envelope_sha256"], "envelope_sha256")
    unsigned = {key: value for key, value in envelope.items()
        if key not in {"envelope_sha256", "envelope_id"}}
    if supplied_digest != _sha(unsigned):
        raise ValueError("collective action envelope digest does not match its content")
    if envelope["envelope_id"] != f"aa_{supplied_digest[:24]}":
        raise ValueError("collective action envelope_id does not match its digest")
    return envelope


def _result(decision: str, posture: str | None, reason_codes: list[str],
    controls: list[str], detail: str, envelope_id: Any) -> dict[str, Any]:
    return {
        "version": VERSION,
        "source_system": "Collective Action Assurance (AA)",
        "consumer_system": "Runtime Assurance (RA)",
        "decision": decision,
        "max_recommended_posture": posture,
        "reason_codes": reason_codes,
        "required_controls": controls,
        "authority_effect": "NONE",
        "envelope_id": envelope_id,
        "plain_english_summary": detail,
    }


def _integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{path} must be a non-negative integer")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(f"{path} must be non-empty text")
    return value.strip()


def _digest(value: Any, path: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(
        char not in "0123456789abcdef" for char in value
    ):
        raise ValueError(f"{path} must be a lowercase SHA-256 digest")
    return value


def _sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()

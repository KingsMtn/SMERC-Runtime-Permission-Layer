from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


LEDGER_VERSION = "smerc.decision-lifecycle-ledger.v1"
RECORD_VERSION = "smerc.dll-record.v1"
GENESIS_HASH = "0" * 64

EVENT_TYPES = {
    "REQUEST",
    "EVIDENCE",
    "EVALUATION",
    "HUMAN_INTERACTION",
    "EXECUTION",
    "OUTCOME",
    "LEARNING_RECOMMENDATION",
}

POSTURES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}
INTERACTIONS = {"accepted", "modified", "overrode", "ignored"}
EXECUTION_STATUSES = {"not_executed", "succeeded", "failed", "cancelled", "timed_out", "blocked"}

PAYLOAD_FIELDS = {
    "REQUEST": {
        "initiated_by",
        "requested_operation",
        "environment",
        "risk_profile",
    },
    "EVIDENCE": {
        "available_evidence",
        "confidence_score",
        "missing_evidence",
        "external_dependencies",
        "model_version",
        "policy_version",
    },
    "EVALUATION": {
        "structural_state",
        "entropy_indicators",
        "recoverability_score",
        "authorization_recommendation",
        "reason_codes",
        "recommended_safeguards",
    },
    "HUMAN_INTERACTION": {
        "interaction",
        "reviewer_id",
        "original_recommendation",
        "final_recommendation",
        "rationale",
    },
    "EXECUTION": {
        "executed_operation",
        "execution_status",
        "started_at",
        "duration_ms",
        "rollback_performed",
        "rollback_success",
    },
    "OUTCOME": {
        "judged_correct",
        "unexpected_consequences",
        "controls_sufficient",
        "cost_incurred",
        "time_to_recover_minutes",
        "customer_impact",
        "security_impact",
        "financial_impact",
    },
    "LEARNING_RECOMMENDATION": {
        "expected_outcome",
        "actual_outcome",
        "prediction_error",
        "human_override_effectiveness",
        "recommended_policy_updates",
        "confidence_calibration_changes",
        "suggested_rule_modifications",
        "activation_status",
    },
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _record_hash(record: Mapping[str, Any]) -> str:
    material = {key: value for key, value in record.items() if key != "record_hash"}
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def _text(value: Any, path: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _number_0_1(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    value = float(value)
    if value < 0 or value > 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return value


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _non_negative_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a non-negative number")
    value = float(value)
    if value < 0:
        raise ValueError(f"{path} must be non-negative")
    return value


def _list_of_text(value: Any, path: str, maximum_items: int = 64) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must be a list")
    if len(value) > maximum_items:
        raise ValueError(f"{path} must contain at most {maximum_items} items")
    return [_text(item, f"{path}[]", 128) for item in value]


def _object(value: Any, path: str, maximum_bytes: int = 8192) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    encoded = _canonical_json(value).encode("utf-8")
    if len(encoded) > maximum_bytes:
        raise ValueError(f"{path} must be no larger than {maximum_bytes} bytes")
    return dict(value)


def _validate_required(payload: Mapping[str, Any], event_type: str) -> Dict[str, Any]:
    required = PAYLOAD_FIELDS[event_type]
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"{event_type} payload is missing field(s): {', '.join(missing)}")
    return _object(dict(payload), f"{event_type}.payload")


def validate_payload(event_type: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"event_type must be one of {', '.join(sorted(EVENT_TYPES))}")
    parsed = _validate_required(payload, event_type)

    if event_type == "EVIDENCE":
        parsed["confidence_score"] = _number_0_1(parsed["confidence_score"], "EVIDENCE.confidence_score")
        parsed["available_evidence"] = _list_of_text(parsed["available_evidence"], "EVIDENCE.available_evidence")
        parsed["missing_evidence"] = _list_of_text(parsed["missing_evidence"], "EVIDENCE.missing_evidence")
        parsed["external_dependencies"] = _list_of_text(
            parsed["external_dependencies"], "EVIDENCE.external_dependencies"
        )
    elif event_type == "EVALUATION":
        parsed["recoverability_score"] = _number_0_1(
            parsed["recoverability_score"], "EVALUATION.recoverability_score"
        )
        if parsed["authorization_recommendation"] not in POSTURES:
            raise ValueError("EVALUATION.authorization_recommendation must be a valid SMERC posture")
        parsed["reason_codes"] = _list_of_text(parsed["reason_codes"], "EVALUATION.reason_codes")
        parsed["recommended_safeguards"] = _list_of_text(
            parsed["recommended_safeguards"], "EVALUATION.recommended_safeguards"
        )
    elif event_type == "HUMAN_INTERACTION":
        if parsed["interaction"] not in INTERACTIONS:
            raise ValueError("HUMAN_INTERACTION.interaction must be accepted, modified, overrode, or ignored")
        if parsed["original_recommendation"] not in POSTURES or parsed["final_recommendation"] not in POSTURES:
            raise ValueError("HUMAN_INTERACTION recommendation fields must be valid SMERC postures")
        _text(parsed["reviewer_id"], "HUMAN_INTERACTION.reviewer_id", 128)
        _text(parsed["rationale"], "HUMAN_INTERACTION.rationale", 1024)
    elif event_type == "EXECUTION":
        if parsed["execution_status"] not in EXECUTION_STATUSES:
            raise ValueError("EXECUTION.execution_status is invalid")
        parsed["duration_ms"] = int(_non_negative_number(parsed["duration_ms"], "EXECUTION.duration_ms"))
        parsed["rollback_performed"] = _bool(parsed["rollback_performed"], "EXECUTION.rollback_performed")
        if parsed["rollback_success"] is not None:
            parsed["rollback_success"] = _bool(parsed["rollback_success"], "EXECUTION.rollback_success")
    elif event_type == "OUTCOME":
        parsed["judged_correct"] = _bool(parsed["judged_correct"], "OUTCOME.judged_correct")
        parsed["unexpected_consequences"] = _bool(
            parsed["unexpected_consequences"], "OUTCOME.unexpected_consequences"
        )
        parsed["controls_sufficient"] = _bool(parsed["controls_sufficient"], "OUTCOME.controls_sufficient")
        parsed["cost_incurred"] = _non_negative_number(parsed["cost_incurred"], "OUTCOME.cost_incurred")
        parsed["time_to_recover_minutes"] = _non_negative_number(
            parsed["time_to_recover_minutes"], "OUTCOME.time_to_recover_minutes"
        )
    elif event_type == "LEARNING_RECOMMENDATION":
        if parsed["activation_status"] != "requires_review":
            raise ValueError("LEARNING_RECOMMENDATION.activation_status must be requires_review")
        parsed["recommended_policy_updates"] = _list_of_text(
            parsed["recommended_policy_updates"], "LEARNING_RECOMMENDATION.recommended_policy_updates"
        )
        parsed["confidence_calibration_changes"] = _list_of_text(
            parsed["confidence_calibration_changes"], "LEARNING_RECOMMENDATION.confidence_calibration_changes"
        )
        parsed["suggested_rule_modifications"] = _list_of_text(
            parsed["suggested_rule_modifications"], "LEARNING_RECOMMENDATION.suggested_rule_modifications"
        )
    return parsed


class DecisionLifecycleLedger:
    """Append-only lifecycle chain for one governed decision."""

    def __init__(
        self,
        decision_id: str,
        tenant_id: str = "default",
        records: Optional[Iterable[Mapping[str, Any]]] = None,
    ) -> None:
        self.decision_id = _text(decision_id, "decision_id", 192)
        self.tenant_id = _text(tenant_id, "tenant_id", 128)
        self.records = [dict(record) for record in (records or [])]

    def append(
        self,
        event_type: str,
        actor: str,
        payload: Mapping[str, Any],
        *,
        recorded_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        parsed_payload = validate_payload(event_type, payload)
        record = {
            "record_version": RECORD_VERSION,
            "sequence": len(self.records) + 1,
            "decision_id": self.decision_id,
            "tenant_id": self.tenant_id,
            "event_type": event_type,
            "actor": _text(actor, "actor", 128),
            "recorded_at": recorded_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "previous_record_hash": self.records[-1]["record_hash"] if self.records else GENESIS_HASH,
            "payload": parsed_payload,
        }
        record["record_hash"] = _record_hash(record)
        self.records.append(record)
        return dict(record)

    def verify(self) -> Dict[str, Any]:
        errors: list[str] = []
        previous_hash = GENESIS_HASH
        for expected_sequence, record in enumerate(self.records, start=1):
            if record.get("record_version") != RECORD_VERSION:
                errors.append(f"record {expected_sequence}: invalid record_version")
            if record.get("sequence") != expected_sequence:
                errors.append(f"record {expected_sequence}: invalid sequence")
            if record.get("decision_id") != self.decision_id:
                errors.append(f"record {expected_sequence}: decision_id mismatch")
            if record.get("tenant_id") != self.tenant_id:
                errors.append(f"record {expected_sequence}: tenant_id mismatch")
            if record.get("previous_record_hash") != previous_hash:
                errors.append(f"record {expected_sequence}: previous hash mismatch")
            if record.get("record_hash") != _record_hash(record):
                errors.append(f"record {expected_sequence}: record hash mismatch")
            previous_hash = record.get("record_hash", "")
        return {
            "valid": not errors,
            "record_count": len(self.records),
            "head_record_hash": previous_hash if self.records else GENESIS_HASH,
            "errors": errors,
        }

    def summary(self) -> Dict[str, Any]:
        counts = {event_type: 0 for event_type in sorted(EVENT_TYPES)}
        override_count = 0
        rollback_performed = False
        rollback_success = None
        judged_correct = None
        pending_learning = 0
        final_event = None
        for record in self.records:
            event_type = record["event_type"]
            counts[event_type] += 1
            final_event = event_type
            payload = record["payload"]
            if event_type == "HUMAN_INTERACTION" and payload["interaction"] == "overrode":
                override_count += 1
            elif event_type == "EXECUTION":
                rollback_performed = rollback_performed or bool(payload["rollback_performed"])
                if payload["rollback_success"] is not None:
                    rollback_success = payload["rollback_success"]
            elif event_type == "OUTCOME":
                judged_correct = payload["judged_correct"]
            elif event_type == "LEARNING_RECOMMENDATION" and payload["activation_status"] == "requires_review":
                pending_learning += 1
        return {
            "decision_id": self.decision_id,
            "tenant_id": self.tenant_id,
            "record_count": len(self.records),
            "event_counts": counts,
            "final_event_type": final_event,
            "override_count": override_count,
            "rollback_performed": rollback_performed,
            "rollback_success": rollback_success,
            "judged_correct": judged_correct,
            "pending_learning_recommendations": pending_learning,
        }

    def to_dict(self) -> Dict[str, Any]:
        verification = self.verify()
        return {
            "version": LEDGER_VERSION,
            "decision_id": self.decision_id,
            "tenant_id": self.tenant_id,
            "record_count": len(self.records),
            "head_record_hash": verification["head_record_hash"],
            "records": [dict(record) for record in self.records],
            "summary": self.summary(),
            "verification": verification,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "DecisionLifecycleLedger":
        if payload.get("version") != LEDGER_VERSION:
            raise ValueError(f"ledger.version must be {LEDGER_VERSION}")
        ledger = cls(
            decision_id=_text(payload.get("decision_id"), "decision_id", 192),
            tenant_id=_text(payload.get("tenant_id"), "tenant_id", 128),
            records=payload.get("records", []),
        )
        verification = ledger.verify()
        if payload.get("record_count") != len(ledger.records):
            raise ValueError("ledger.record_count does not match records length")
        if payload.get("head_record_hash") != verification["head_record_hash"]:
            raise ValueError("ledger.head_record_hash does not match records")
        return ledger


def build_example_ledger() -> DecisionLifecycleLedger:
    ledger = DecisionLifecycleLedger("dll_example_ai_deploy_001", tenant_id="design-partner")
    ledger.append(
        "REQUEST",
        "coding_agent",
        {
            "initiated_by": "coding_agent",
            "requested_operation": "Deploy generated authentication middleware change to production.",
            "environment": "production",
            "risk_profile": "github_actions_deployment",
        },
        recorded_at="2026-07-12T12:00:00+00:00",
    )
    ledger.append(
        "EVIDENCE",
        "smerc-api",
        {
            "available_evidence": ["pull_request_checks", "unit_tests", "review_metadata"],
            "confidence_score": 0.62,
            "missing_evidence": ["security_review", "rollback_drill"],
            "external_dependencies": ["github_actions", "deployment_adapter"],
            "model_version": "agent-model-unknown",
            "policy_version": "smerc.policy.v1:github-actions-strict",
        },
        recorded_at="2026-07-12T12:00:03+00:00",
    )
    ledger.append(
        "EVALUATION",
        "smerc-engine",
        {
            "structural_state": "high-impact production change with incomplete review evidence",
            "entropy_indicators": ["missing_security_review", "auth_boundary_change"],
            "recoverability_score": 0.48,
            "authorization_recommendation": "THROTTLE",
            "reason_codes": ["EVIDENCE_INCOMPLETE", "RECOVERY_PATH_PARTIAL"],
            "recommended_safeguards": ["limit_scope", "preview_before_execution", "require_rollback_plan"],
        },
        recorded_at="2026-07-12T12:00:04+00:00",
    )
    ledger.append(
        "HUMAN_INTERACTION",
        "security-reviewer-7",
        {
            "interaction": "accepted",
            "reviewer_id": "security-reviewer-7",
            "original_recommendation": "THROTTLE",
            "final_recommendation": "THROTTLE",
            "rationale": "Proceed only as a canary with rollback plan and preserved replay.",
        },
        recorded_at="2026-07-12T12:03:20+00:00",
    )
    ledger.append(
        "EXECUTION",
        "deployment-adapter",
        {
            "executed_operation": "Canary deploy to 10 percent of production traffic.",
            "execution_status": "succeeded",
            "started_at": "2026-07-12T12:05:00+00:00",
            "duration_ms": 184000,
            "rollback_performed": False,
            "rollback_success": None,
        },
        recorded_at="2026-07-12T12:08:10+00:00",
    )
    ledger.append(
        "OUTCOME",
        "pilot-review-lead",
        {
            "judged_correct": True,
            "unexpected_consequences": False,
            "controls_sufficient": True,
            "cost_incurred": 0,
            "time_to_recover_minutes": 0,
            "customer_impact": "none observed",
            "security_impact": "none observed",
            "financial_impact": "none observed",
        },
        recorded_at="2026-07-13T12:00:00+00:00",
    )
    ledger.append(
        "LEARNING_RECOMMENDATION",
        "smerc-dll",
        {
            "expected_outcome": "Canary deployment proceeds without material incident under constraints.",
            "actual_outcome": "Canary deployment succeeded without rollback or observed impact.",
            "prediction_error": "low",
            "human_override_effectiveness": "reviewer accepted constraint; no override occurred",
            "recommended_policy_updates": ["Keep auth-boundary production changes out of direct ALLOW."],
            "confidence_calibration_changes": ["No automatic calibration change; collect more samples."],
            "suggested_rule_modifications": ["Require rollback drill evidence before considering ALLOW."],
            "activation_status": "requires_review",
        },
        recorded_at="2026-07-13T12:05:00+00:00",
    )
    return ledger


def render_markdown(ledger: DecisionLifecycleLedger) -> str:
    data = ledger.to_dict()
    lines = [
        "# SMERC Decision Lifecycle Ledger Report",
        "",
        f"Decision ID: `{ledger.decision_id}`",
        f"Tenant: `{ledger.tenant_id}`",
        f"Record count: `{data['record_count']}`",
        f"Head record hash: `{data['head_record_hash']}`",
        f"Valid chain: `{'yes' if data['verification']['valid'] else 'no'}`",
        "",
        "## Summary",
        "",
    ]
    summary = data["summary"]
    for key in [
        "override_count",
        "rollback_performed",
        "rollback_success",
        "judged_correct",
        "pending_learning_recommendations",
    ]:
        lines.append(f"- {key}: `{summary[key]}`")
    lines.extend(["", "## Lifecycle Events", ""])
    for record in data["records"]:
        lines.extend(
            [
                f"### {record['sequence']}. {record['event_type']}",
                "",
                f"- Actor: `{record['actor']}`",
                f"- Recorded at: `{record['recorded_at']}`",
                f"- Record hash: `{record['record_hash']}`",
                "",
                "```json",
                json.dumps(record["payload"], indent=2, sort_keys=True),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Boundary",
            "",
            "This report is a pilot-grade lifecycle record. It is not a production immutable ledger, regulatory recordkeeping system, or automatic policy-update mechanism. Learning recommendations require human review before activation.",
        ]
    )
    return "\n".join(lines) + "\n"


def load_ledger(path: Path) -> DecisionLifecycleLedger:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("ledger file must contain a JSON object")
    return DecisionLifecycleLedger.from_dict(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or verify a SMERC Decision Lifecycle Ledger.")
    parser.add_argument("--input", type=Path, help="Existing DLL JSON file to verify or render.")
    parser.add_argument("--example", action="store_true", help="Generate the built-in example ledger.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    if bool(args.input) == bool(args.example):
        parser.error("choose exactly one of --input or --example")

    ledger = load_ledger(args.input) if args.input else build_example_ledger()
    data = ledger.to_dict()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(render_markdown(ledger), encoding="utf-8")
    print(json.dumps(data, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


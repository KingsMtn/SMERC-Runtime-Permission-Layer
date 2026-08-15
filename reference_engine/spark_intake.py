from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.action_language import ACTION_VERSION, canonical_json, validate_action_envelope


SPARK_EVIDENCE_VERSION = "smerc.spark-evidence.v1"

ROOT_FIELDS = {
    "version",
    "evidence_id",
    "collected_at",
    "source_systems",
    "action_metadata",
    "recoverability_signals",
    "evidence_gaps",
    "non_secret_boundary",
}
ACTION_METADATA_FIELDS = {
    "action_id",
    "description",
    "actor",
    "tool",
    "operation",
    "resource",
    "environment",
    "authority_basis",
    "authority_confidence",
    "external_side_effect",
    "sensitive_data",
}
RECOVERABILITY_SIGNAL_FIELDS = {
    "base_action_risk",
    "reversibility",
    "containment_strength",
    "rollback_latency",
    "evidence_validity",
    "anomaly_pressure",
    "impact_scope",
    "cancel_reliability",
    "rollback_method",
}
MAX_EVIDENCE_GAPS = 16


def validate_spark_evidence(payload: Mapping[str, Any]) -> Dict[str, Any]:
    root = deepcopy(_object(payload, "spark_evidence"))
    _required(root, ROOT_FIELDS, "spark_evidence")
    _strict(root, ROOT_FIELDS, "spark_evidence")
    if root["version"] != SPARK_EVIDENCE_VERSION:
        raise ValueError(f"version must be {SPARK_EVIDENCE_VERSION}")
    root["evidence_id"] = _text(root["evidence_id"], "evidence_id", 128)
    root["collected_at"] = _timestamp(root["collected_at"], "collected_at")
    root["source_systems"] = _source_systems(root["source_systems"])
    metadata = _object(root["action_metadata"], "action_metadata")
    signals = _object(root["recoverability_signals"], "recoverability_signals")
    _required(metadata, ACTION_METADATA_FIELDS, "action_metadata")
    _strict(metadata, ACTION_METADATA_FIELDS, "action_metadata")
    _required(signals, RECOVERABILITY_SIGNAL_FIELDS, "recoverability_signals")
    _strict(signals, RECOVERABILITY_SIGNAL_FIELDS, "recoverability_signals")
    for field in (
        "action_id",
        "description",
        "actor",
        "tool",
        "operation",
        "resource",
        "environment",
        "authority_basis",
    ):
        metadata[field] = _text(metadata[field], f"action_metadata.{field}", 512)
    metadata["authority_confidence"] = _score(
        metadata["authority_confidence"], "action_metadata.authority_confidence"
    )
    metadata["external_side_effect"] = _boolean(
        metadata["external_side_effect"], "action_metadata.external_side_effect"
    )
    metadata["sensitive_data"] = _boolean(metadata["sensitive_data"], "action_metadata.sensitive_data")
    for field in RECOVERABILITY_SIGNAL_FIELDS - {"rollback_method"}:
        signals[field] = _score(signals[field], f"recoverability_signals.{field}")
    signals["rollback_method"] = _text(signals["rollback_method"], "recoverability_signals.rollback_method", 512)
    root["evidence_gaps"] = _evidence_gaps(root["evidence_gaps"])
    root["non_secret_boundary"] = _boolean(root["non_secret_boundary"], "non_secret_boundary")
    if not root["non_secret_boundary"]:
        raise ValueError("non_secret_boundary must be true for pilot SPARK evidence")
    return root


def spark_evidence_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(validate_spark_evidence(payload)).encode("utf-8")).hexdigest()


def compile_spark_to_action(payload: Mapping[str, Any]) -> Dict[str, Any]:
    evidence = validate_spark_evidence(payload)
    metadata = evidence["action_metadata"]
    signals = evidence["recoverability_signals"]
    action = {
        "language_version": ACTION_VERSION,
        "action": {
            "id": metadata["action_id"],
            "description": metadata["description"],
            "actor": metadata["actor"],
            "tool": metadata["tool"],
            "type": metadata["operation"],
            "target": {
                "resource": metadata["resource"],
                "environment": metadata["environment"],
            },
            "authority": {
                "basis": metadata["authority_basis"],
                "confidence": metadata["authority_confidence"],
            },
        },
        "signals": {
            "base_action_risk": signals["base_action_risk"],
            "evidence_validity": signals["evidence_validity"],
            "anomaly_pressure": signals["anomaly_pressure"],
            "impact_scope": signals["impact_scope"],
        },
        "recoverability": {
            "reversibility": signals["reversibility"],
            "containment_strength": signals["containment_strength"],
            "rollback_latency": signals["rollback_latency"],
            "cancel_reliability": signals["cancel_reliability"],
            "rollback_method": signals["rollback_method"],
        },
        "effects": {
            "external_side_effect": metadata["external_side_effect"],
            "sensitive_data": metadata["sensitive_data"],
        },
        "context": {
            "spark": {
                "version": SPARK_EVIDENCE_VERSION,
                "evidence_id": evidence["evidence_id"],
                "evidence_hash": hashlib.sha256(canonical_json(evidence).encode("utf-8")).hexdigest(),
                "collected_at": evidence["collected_at"],
                "source_systems": evidence["source_systems"],
                "evidence_gaps": evidence["evidence_gaps"],
                "non_secret_boundary": evidence["non_secret_boundary"],
            }
        },
    }
    return validate_action_envelope(action)


def build_intake_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    evidence = validate_spark_evidence(payload)
    action = compile_spark_to_action(evidence)
    gaps = evidence["evidence_gaps"]
    return {
        "version": "smerc.spark-intake-report.v1",
        "generated_at": _now(),
        "evidence_id": evidence["evidence_id"],
        "evidence_hash": spark_evidence_hash(evidence),
        "source_systems": evidence["source_systems"],
        "evidence_gap_count": len(gaps),
        "evidence_gaps": gaps,
        "action_language": action,
        "readiness": "complete" if not gaps else "evidence_gaps_present",
        "evidence_boundary": (
            "SPARK validates and normalizes supplied non-secret pilot evidence. It does not prove upstream "
            "systems supplied truthful signals, customer production safety, or incident reduction."
        ),
    }


def write_outputs(report: Mapping[str, Any], *, json_path: str | Path) -> None:
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    return value


def _required(value: Mapping[str, Any], fields: Iterable[str], path: str) -> None:
    missing = sorted(set(fields) - set(value))
    if missing:
        raise ValueError(f"{path} is missing required field(s): {', '.join(missing)}")


def _strict(value: Mapping[str, Any], fields: Iterable[str], path: str) -> None:
    unknown = sorted(set(value) - set(fields))
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    if not 0 <= value <= 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return float(value)


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _timestamp(value: Any, path: str) -> str:
    value = _text(value, path, 64)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{path} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{path} must include a timezone")
    return value


def _source_systems(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TypeError("source_systems must be a non-empty list")
    systems = [_text(item, f"source_systems[{index}]", 128) for index, item in enumerate(value)]
    if len(set(systems)) != len(systems):
        raise ValueError("source_systems must not contain duplicates")
    return systems


def _evidence_gaps(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise TypeError("evidence_gaps must be a list")
    if len(value) > MAX_EVIDENCE_GAPS:
        raise ValueError(f"evidence_gaps may contain at most {MAX_EVIDENCE_GAPS} items")
    return [_text(item, f"evidence_gaps[{index}]", 256) for index, item in enumerate(value)]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SPARK evidence and compile it to SMERC Action Language.")
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--json-output", default="reports/spark_intake_report.json")
    args = parser.parse_args()
    payload = json.loads(args.evidence.read_text(encoding="utf-8"))
    report = build_intake_report(payload)
    write_outputs(report, json_path=args.json_output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

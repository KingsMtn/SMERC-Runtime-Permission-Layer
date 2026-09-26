from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


VERSION = "smerc.authorization-afterlife-evidence-manifest.v1"
REPORT_VERSION = "smerc.authorization-afterlife-evidence-intake-report.v1"
EVIDENCE_CLASSES = {"PUBLIC_EXAMPLE", "CONTROLLED_AWS_PROOF", "SYNTHETIC", "CUSTOMER_METADATA"}
ROOT_FIELDS = {"version", "pilot_id", "records", "non_secret_boundary"}
RECORD_FIELDS = {
    "evidence_id", "evidence_class", "collected_at", "source_system", "source_sha256",
    "observations", "limitations",
}
OBSERVATION_FIELDS = {
    "action_id", "operation", "external_side_effect", "authority_epoch",
    "current_authority_epoch", "revoked", "partial_effects_present", "outcome_verified",
    "cleanup_verified", "rollback_available", "cost_usd", "scope_units",
}
PROHIBITED_KEY_FRAGMENTS = {
    "access_key", "secret", "session_token", "password", "credential", "private_key",
    "account_id", "authorization_header", "cookie",
}
MAX_RECORDS = 25
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def validate_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    _reject_prohibited_keys(payload)
    manifest = deepcopy(_object(payload, "manifest"))
    _required(manifest, ROOT_FIELDS, "manifest")
    _strict(manifest, ROOT_FIELDS, "manifest")
    if manifest["version"] != VERSION:
        raise ValueError(f"version must be {VERSION}")
    manifest["pilot_id"] = _text(manifest["pilot_id"], "pilot_id", 128)
    if manifest["non_secret_boundary"] is not True:
        raise ValueError("non_secret_boundary must be true")
    records = manifest["records"]
    if not isinstance(records, list) or not 1 <= len(records) <= MAX_RECORDS:
        raise ValueError(f"records must contain between 1 and {MAX_RECORDS} items")
    manifest["records"] = [_record(item, index) for index, item in enumerate(records)]
    evidence_ids = [record["evidence_id"] for record in manifest["records"]]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError("evidence_id values must be unique")
    return manifest


def build_intake_report(payload: Mapping[str, Any]) -> dict[str, Any]:
    manifest = validate_manifest(payload)
    classes = {
        name: sum(record["evidence_class"] == name for record in manifest["records"])
        for name in sorted(EVIDENCE_CLASSES)
    }
    records = []
    for record in manifest["records"]:
        observations = record["observations"]
        authority_changed = observations["authority_epoch"] != observations["current_authority_epoch"]
        settlement_evidence_complete = observations["outcome_verified"] and observations["cleanup_verified"]
        requires_reconciliation = any((
            authority_changed,
            observations["revoked"],
            observations["partial_effects_present"],
            not settlement_evidence_complete,
        ))
        records.append({
            "evidence_id": record["evidence_id"],
            "evidence_class": record["evidence_class"],
            "source_sha256": record["source_sha256"],
            "authority_changed": authority_changed,
            "settlement_evidence_complete": settlement_evidence_complete,
            "requires_consequence_time_reconciliation": requires_reconciliation,
            "limitations": record["limitations"],
        })
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return {
        "version": REPORT_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "pilot_id": manifest["pilot_id"],
        "manifest_sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        "record_count": len(records),
        "evidence_class_counts": classes,
        "records_requiring_reconciliation": sum(
            record["requires_consequence_time_reconciliation"] for record in records
        ),
        "records": records,
        "readiness": "ready_for_scenario_reconciliation",
        "evidence_boundary": (
            "This intake validates metadata shape, provenance declarations, and the non-secret boundary. "
            "It does not verify source truth, AWS attestation, customer production safety, or authority itself."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Authorization-Afterlife Evidence Intake", "",
        f"- Pilot: `{report['pilot_id']}`",
        f"- Records: `{report['record_count']}`",
        f"- Reconciliation required: `{report['records_requiring_reconciliation']}`",
        f"- Readiness: `{report['readiness']}`", "", "## Records", "",
        "| Evidence | Class | Authority changed | Settlement evidence | Reconcile |",
        "|---|---|---:|---:|---:|",
    ]
    for record in report["records"]:
        lines.append(
            f"| `{record['evidence_id']}` | `{record['evidence_class']}` | "
            f"`{str(record['authority_changed']).lower()}` | "
            f"`{str(record['settlement_evidence_complete']).lower()}` | "
            f"`{str(record['requires_consequence_time_reconciliation']).lower()}` |"
        )
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def _record(value: Any, index: int) -> dict[str, Any]:
    path = f"records[{index}]"
    record = deepcopy(_object(value, path))
    _required(record, RECORD_FIELDS, path)
    _strict(record, RECORD_FIELDS, path)
    record["evidence_id"] = _text(record["evidence_id"], f"{path}.evidence_id", 128)
    if record["evidence_class"] not in EVIDENCE_CLASSES:
        raise ValueError(f"{path}.evidence_class is not recognized")
    record["collected_at"] = _text(record["collected_at"], f"{path}.collected_at", 64)
    record["source_system"] = _text(record["source_system"], f"{path}.source_system", 128)
    if not isinstance(record["source_sha256"], str) or not SHA256_RE.fullmatch(record["source_sha256"]):
        raise ValueError(f"{path}.source_sha256 must be a lowercase SHA-256 digest")
    observations = deepcopy(_object(record["observations"], f"{path}.observations"))
    _required(observations, OBSERVATION_FIELDS, f"{path}.observations")
    _strict(observations, OBSERVATION_FIELDS, f"{path}.observations")
    for name in ("action_id", "operation"):
        observations[name] = _text(observations[name], f"{path}.observations.{name}", 256)
    for name in (
        "external_side_effect", "revoked", "partial_effects_present", "outcome_verified",
        "cleanup_verified", "rollback_available",
    ):
        if not isinstance(observations[name], bool):
            raise TypeError(f"{path}.observations.{name} must be a boolean")
    for name in ("authority_epoch", "current_authority_epoch", "scope_units"):
        if isinstance(observations[name], bool) or not isinstance(observations[name], int) or observations[name] < 0:
            raise TypeError(f"{path}.observations.{name} must be a non-negative integer")
    cost = observations["cost_usd"]
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0:
        raise TypeError(f"{path}.observations.cost_usd must be a non-negative number")
    observations["cost_usd"] = float(cost)
    record["observations"] = observations
    limitations = record["limitations"]
    if not isinstance(limitations, list) or len(limitations) > 16:
        raise TypeError(f"{path}.limitations must be a list with at most 16 items")
    record["limitations"] = [_text(item, f"{path}.limitations", 512) for item in limitations]
    return record


def _reject_prohibited_keys(value: Any, path: str = "manifest") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized != "non_secret_boundary" and any(
                fragment in normalized for fragment in PROHIBITED_KEY_FRAGMENTS
            ):
                raise ValueError(f"{path}.{key} is prohibited by the non-secret boundary")
            _reject_prohibited_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_keys(child, f"{path}[{index}]")


def _object(value: Any, path: str) -> dict[str, Any]:
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
    result = value.strip()
    if len(result) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an authorization-afterlife evidence manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-output", default="reports/authorization_afterlife_intake/intake.json")
    parser.add_argument("--markdown-output", default="reports/authorization_afterlife_intake/Intake.md")
    args = parser.parse_args()
    report = build_intake_report(json.loads(args.manifest.read_text(encoding="utf-8")))
    json_path = Path(args.json_output)
    markdown_path = Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"readiness": report["readiness"], "records": report["record_count"]}, indent=2))


if __name__ == "__main__":
    main()

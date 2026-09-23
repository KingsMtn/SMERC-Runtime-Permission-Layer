from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from reference_engine.aws_external_outcome_label import verify_external_outcome_label
from reference_engine.portable_evidence import verify_portable_evidence


VERSION = "smerc.aws-outcome-evaluation.v1"
EXECUTABLE_POSTURES = {"ALLOW", "THROTTLE"}


def evaluate_record(
    record: Mapping[str, Any],
    *,
    external_label: Mapping[str, Any] | None = None,
    label_verification_key: bytes | None = None,
) -> dict[str, Any]:
    verification = verify_portable_evidence(record)
    decision = record["decision"]
    containment = record["containment"]
    call_count = record["tool_activity"]["call_count"]
    posture = decision["posture"]

    execution_observed = call_count > 0
    if execution_observed and posture not in EXECUTABLE_POSTURES:
        coherence = "INCOHERENT"
        findings = ["RESTRICTIVE_POSTURE_HAS_EXECUTION_EVIDENCE"]
    elif not execution_observed and posture == "ALLOW":
        coherence = "INDETERMINATE"
        findings = ["ALLOW_HAS_NO_EXECUTION_EVIDENCE"]
    else:
        coherence = "COHERENT"
        findings = []

    cleanup_status = containment["cleanup_status"]
    if cleanup_status == "SUCCEEDED" and containment["cleanup_verified"]:
        recovery = "VERIFIED"
    elif cleanup_status == "NOT_REQUIRED" and not containment["cleanup_verified"]:
        recovery = "NOT_APPLICABLE"
    elif cleanup_status in {"FAILED", "UNVERIFIED"}:
        recovery = "UNVERIFIED"
        findings.append("RECOVERY_NOT_VERIFIED")
    else:
        recovery = "INCOHERENT"
        findings.append("CLEANUP_CLAIM_INCOHERENT")

    label_evidence = None
    if external_label is None:
        judgment_correctness = "UNDETERMINED"
    else:
        if label_verification_key is None:
            raise ValueError("label_verification_key is required for external labels")
        label_evidence = verify_external_outcome_label(
            external_label, record, verification_key=label_verification_key
        )
        judgment_correctness = "CORRECT" if external_label["judged_correct"] else "INCORRECT"
        if external_label["unexpected_consequences"]:
            findings.append("EXTERNAL_LABEL_REPORTS_UNEXPECTED_CONSEQUENCES")
        if not external_label["controls_sufficient"]:
            findings.append("EXTERNAL_LABEL_REPORTS_INSUFFICIENT_CONTROLS")
    learning_eligibility = (
        "READY_FOR_EXTERNAL_LABEL"
        if coherence == "COHERENT" and recovery in {"VERIFIED", "NOT_APPLICABLE"}
        else "HOLD_FOR_REVIEW"
    )
    return {
        "record_id": record["record_id"],
        "verification_status": verification["status"],
        "decision_id": decision["decision_id"],
        "posture": posture,
        "execution_observed": execution_observed,
        "decision_execution_coherence": coherence,
        "recovery_evidence": recovery,
        "judgment_correctness": judgment_correctness,
        "external_label": label_evidence,
        "learning_eligibility": learning_eligibility,
        "findings": findings,
    }


def evaluate_records(
    records: Iterable[Mapping[str, Any]],
    *,
    observed_at: str | None = None,
    external_labels: Mapping[str, Mapping[str, Any]] | None = None,
    label_verification_key: bytes | None = None,
) -> dict[str, Any]:
    evaluations = [
        evaluate_record(
            record,
            external_label=(external_labels or {}).get(record["record_id"]),
            label_verification_key=label_verification_key,
        )
        for record in records
    ]
    if not evaluations:
        raise ValueError("at least one portable evidence record is required")
    coherence = Counter(item["decision_execution_coherence"] for item in evaluations)
    recovery = Counter(item["recovery_evidence"] for item in evaluations)
    eligible = sum(item["learning_eligibility"] == "READY_FOR_EXTERNAL_LABEL" for item in evaluations)
    labeled = [item for item in evaluations if item["judgment_correctness"] != "UNDETERMINED"]
    correct = sum(item["judgment_correctness"] == "CORRECT" for item in labeled)
    return {
        "version": VERSION,
        "observed_at": observed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "summary": {
            "record_count": len(evaluations),
            "coherence_counts": dict(sorted(coherence.items())),
            "recovery_counts": dict(sorted(recovery.items())),
            "ready_for_external_label_count": eligible,
            "external_label_count": len(labeled),
            "judgment_correctness_rate": round(correct / len(labeled), 4) if labeled else None,
        },
        "evaluations": evaluations,
        "evidence_boundary": [
            "Integrity, decision/execution coherence, and cleanup evidence are evaluated from SMERC records.",
            "Judgment correctness remains undetermined until independent outcome or reviewer labels are attached.",
            "This report does not establish production safety, AWS attestation, or policy calibration.",
        ],
        "recommended_next_action": (
            "Attach independent reviewer or incident-outcome labels to eligible records, then feed those labels "
            "into the Decision Lifecycle Ledger for governed calibration review."
        ),
    }


def load_records(paths: Iterable[Path]) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, Mapping) and "portable_evidence" in payload:
            payload = payload["portable_evidence"]
        if not isinstance(payload, Mapping):
            raise TypeError(f"{path} must contain an evidence record or AWS proof")
        records.append(payload)
    return records


def load_external_labels(paths: Iterable[Path]) -> dict[str, Mapping[str, Any]]:
    labels: dict[str, Mapping[str, Any]] = {}
    for path in paths:
        label = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(label, Mapping) or not isinstance(label.get("record_id"), str):
            raise TypeError(f"{path} must contain an external outcome label")
        record_id = label["record_id"]
        if record_id in labels:
            raise ValueError(f"duplicate external label for record_id {record_id}")
        labels[record_id] = label
    return labels


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate AWS portable evidence without self-labeling accuracy.")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--external-label", action="append", type=Path, default=[])
    parser.add_argument("--label-key-env", default="SMERC_EXTERNAL_LABEL_KEY")
    args = parser.parse_args()
    labels = load_external_labels(args.external_label)
    key = None
    if labels:
        raw_key = os.environ.get(args.label_key_env)
        if raw_key is None:
            parser.error(f"{args.label_key_env} is required when --external-label is used")
        key = raw_key.encode("utf-8")
    report = evaluate_records(
        load_records(args.inputs), external_labels=labels, label_verification_key=key
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "succeeded", "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

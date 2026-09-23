from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from reference_engine.aws_outcome_evaluation import evaluate_records, load_external_labels
from reference_engine.portable_evidence import verify_portable_evidence


VERSION = "smerc.aws-final-proof-package.v1"
READ_SCHEMA = "smerc.aws-mcp-enforced-live-proof.v1"
DENIAL_SCHEMA = "smerc.aws-mcp-denied-write-proof.v1"
MUTATION_SCHEMA = "smerc.aws-reversible-mutation-proof.v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _cost(proof: Mapping[str, Any]) -> float:
    value = proof.get("estimated_incremental_cost_usd")
    if value is None and isinstance(proof.get("action"), Mapping):
        value = proof["action"].get("estimated_incremental_cost_usd")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise ValueError("each proof must declare a non-negative estimated_incremental_cost_usd")
    return float(value)


def build_final_proof_package(
    read_proof: Mapping[str, Any],
    denied_write_proof: Mapping[str, Any],
    mutation_proof: Mapping[str, Any],
    *,
    cost_cap_usd: float,
    external_labels: Mapping[str, Mapping[str, Any]] | None = None,
    label_verification_key: bytes | None = None,
    observed_at: str | None = None,
) -> dict[str, Any]:
    if not isinstance(cost_cap_usd, (int, float)) or isinstance(cost_cap_usd, bool) or cost_cap_usd < 0:
        raise ValueError("cost_cap_usd must be a non-negative number")
    if read_proof.get("schema") != READ_SCHEMA:
        raise ValueError("read proof schema is invalid")
    if read_proof.get("evidence_class") != "enforced_live_read_only":
        raise ValueError("read proof evidence class is invalid")
    if read_proof.get("transport_enforced_for_observed_call") is not True:
        raise ValueError("read proof does not establish transport enforcement")

    if denied_write_proof.get("schema") != DENIAL_SCHEMA:
        raise ValueError("denied-write proof schema is invalid")
    denial = denied_write_proof.get("smerc")
    if not isinstance(denial, Mapping) or denial.get("posture") != "DENY" or denial.get("route_state") != "BLOCK":
        raise ValueError("denied-write proof does not contain a DENY/BLOCK decision")
    if denied_write_proof.get("aws_executor_called") is not False:
        raise ValueError("denied write reached the AWS executor")
    if denied_write_proof.get("aws_resource_changed") is not False:
        raise ValueError("denied write reports an AWS resource change")

    if mutation_proof.get("schema") != MUTATION_SCHEMA:
        raise ValueError("mutation proof schema is invalid")
    observation = mutation_proof.get("aws_observation")
    if not isinstance(observation, Mapping):
        raise ValueError("mutation proof has no AWS observation")
    if (
        observation.get("resource_created") is not True
        or observation.get("resource_deleted") is not True
        or observation.get("residual_count") != 0
    ):
        raise ValueError("mutation proof does not establish verified cleanup with zero residual state")

    records = []
    for name, proof in (("read", read_proof), ("mutation", mutation_proof)):
        record = proof.get("portable_evidence")
        if not isinstance(record, Mapping):
            raise ValueError(f"{name} proof has no portable evidence")
        verify_portable_evidence(record)
        records.append(record)

    labels = external_labels or {}
    unknown_labels = set(labels) - {record["record_id"] for record in records}
    if unknown_labels:
        raise ValueError("external labels include records outside this proof package")
    if labels and label_verification_key is None:
        raise ValueError("label_verification_key is required for external labels")
    evaluation = evaluate_records(
        records,
        observed_at=observed_at,
        external_labels=labels,
        label_verification_key=label_verification_key,
    )

    costs = {
        "allowed_read_usd": _cost(read_proof),
        "denied_write_usd": _cost(denied_write_proof),
        "reversible_mutation_usd": _cost(mutation_proof),
    }
    estimated_total = round(sum(costs.values()), 6)
    if estimated_total > float(cost_cap_usd):
        raise ValueError("proof package estimated cost exceeds the approved cap")

    label_count = evaluation["summary"]["external_label_count"]
    status = "INDEPENDENTLY_VALIDATED" if label_count == len(records) else "TECHNICALLY_COMPLETE_AWAITING_EXTERNAL_LABELS"
    package = {
        "version": VERSION,
        "observed_at": observed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": status,
        "proofs": {
            "allowed_read": {
                "status": "VERIFIED",
                "artifact_sha256": hashlib.sha256(_canonical(read_proof)).hexdigest(),
                "record_id": records[0]["record_id"],
            },
            "denied_write": {
                "status": "VERIFIED_BEFORE_EXECUTION",
                "artifact_sha256": hashlib.sha256(_canonical(denied_write_proof)).hexdigest(),
                "executor_called": False,
            },
            "reversible_mutation": {
                "status": "VERIFIED_CLEANUP",
                "artifact_sha256": hashlib.sha256(_canonical(mutation_proof)).hexdigest(),
                "record_id": records[1]["record_id"],
                "residual_count": 0,
                "rollback_latency_seconds": observation.get("rollback_latency_seconds"),
            },
        },
        "cost_control": {
            "approved_cap_usd": float(cost_cap_usd),
            "estimated_total_usd": estimated_total,
            "within_cap": True,
            "components": costs,
            "boundary": "Declared incremental estimates are admission evidence, not an AWS billing statement.",
        },
        "outcome_evaluation": evaluation,
        "external_validation": {
            "eligible_record_count": len(records),
            "authenticated_label_count": label_count,
            "coverage": round(label_count / len(records), 4),
            "remaining_gap": None if label_count == len(records) else "Independent labels are still required before claiming judgment accuracy.",
        },
        "evidence_boundary": [
            "The package verifies one enforced read, one pre-execution denial, and one reversible mutation with cleanup.",
            "The denied-write tripwire is local enforcement evidence and is not an AWS-issued attestation.",
            "The package does not prove that every AWS access path is mediated by SMERC or that SMERC is production-safe.",
        ],
    }
    return package


def _load(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a bounded final AWS proof package from existing artifacts.")
    parser.add_argument("--read-proof", type=Path, required=True)
    parser.add_argument("--denied-write-proof", type=Path, required=True)
    parser.add_argument("--mutation-proof", type=Path, required=True)
    parser.add_argument("--cost-cap-usd", type=float, required=True)
    parser.add_argument("--external-label", action="append", type=Path, default=[])
    parser.add_argument("--label-key-env", default="SMERC_EXTERNAL_LABEL_KEY")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    labels = load_external_labels(args.external_label)
    key = None
    if labels:
        raw_key = os.environ.get(args.label_key_env)
        if raw_key is None:
            parser.error(f"{args.label_key_env} is required when --external-label is used")
        key = raw_key.encode("utf-8")
    package = build_final_proof_package(
        _load(args.read_proof),
        _load(args.denied_write_proof),
        _load(args.mutation_proof),
        cost_cap_usd=args.cost_cap_usd,
        external_labels=labels,
        label_verification_key=key,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": package["status"], "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


LEDGER_VERSION = "smerc.evidence-ledger.v1"
ZERO_HASH = "0" * 64
AUTHENTICATION_METHODS = {"sha256_chain", "hmac_sha256_chain"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _record_digest(record_without_hash: Mapping[str, Any], key: Optional[bytes]) -> str:
    encoded = canonical_json(record_without_hash).encode("utf-8")
    return hmac.new(key, encoded, hashlib.sha256).hexdigest() if key else hashlib.sha256(encoded).hexdigest()


def build_ledger(
    observations: List[Dict[str, Any]],
    *,
    program_id: str,
    collector_id: str,
    collection_method: str,
    artifact_digests: Mapping[str, str],
    hmac_key: Optional[bytes] = None,
    recorded_at: Optional[str] = None,
) -> Dict[str, Any]:
    _identifier(program_id, "program_id")
    _identifier(collector_id, "collector_id")
    _text(collection_method, "collection_method", 256)
    timestamp = recorded_at or datetime.now(timezone.utc).isoformat()
    _timestamp(timestamp, "recorded_at")
    authentication = "hmac_sha256_chain" if hmac_key else "sha256_chain"
    previous = ZERO_HASH
    records = []
    seen = set()
    for index, observation in enumerate(observations, start=1):
        if not isinstance(observation, dict):
            raise TypeError("Each observation must be an object")
        observation_id = _identifier(observation.get("observation_id"), "observation.observation_id")
        if observation_id in seen:
            raise ValueError(f"Duplicate observation_id: {observation_id}")
        seen.add(observation_id)
        artifact_digest = artifact_digests.get(observation_id)
        _hash(artifact_digest, f"artifact_digests.{observation_id}")
        unsigned = {
            "sequence": index,
            "observation_id": observation_id,
            "observation_sha256": digest(observation),
            "source_artifact_sha256": artifact_digest,
            "collector_id": collector_id,
            "collection_method": collection_method,
            "recorded_at": timestamp,
            "previous_record_hash": previous,
            "authentication": authentication,
        }
        record_hash = _record_digest(unsigned, hmac_key)
        records.append({**unsigned, "record_hash": record_hash})
        previous = record_hash
    return {
        "version": LEDGER_VERSION,
        "program_id": program_id,
        "record_count": len(records),
        "head_record_hash": previous,
        "records": records,
    }


def verify_ledger(
    observations: List[Dict[str, Any]],
    ledger: Dict[str, Any],
    *,
    hmac_key: Optional[bytes] = None,
) -> Dict[str, Any]:
    if not isinstance(ledger, dict):
        raise TypeError("ledger must be an object")
    required = {"version", "program_id", "record_count", "head_record_hash", "records"}
    _exact(ledger, required, "ledger")
    if ledger["version"] != LEDGER_VERSION:
        raise ValueError(f"ledger.version must be {LEDGER_VERSION}")
    _identifier(ledger["program_id"], "ledger.program_id")
    if not isinstance(ledger["record_count"], int) or ledger["record_count"] < 0:
        raise ValueError("ledger.record_count must be a non-negative integer")
    _hash(ledger["head_record_hash"], "ledger.head_record_hash")
    records = ledger["records"]
    if not isinstance(records, list):
        raise TypeError("ledger.records must be an array")
    if ledger["record_count"] != len(records) or len(records) != len(observations):
        raise ValueError("Ledger, record count, and observation count must match exactly")
    observation_map = {item.get("observation_id"): item for item in observations if isinstance(item, dict)}
    if len(observation_map) != len(observations):
        raise ValueError("Observations must have unique observation_id values")

    previous = ZERO_HASH
    methods = set()
    seen = set()
    for expected_sequence, record in enumerate(records, start=1):
        path = f"ledger.records[{expected_sequence - 1}]"
        if not isinstance(record, dict):
            raise TypeError(f"{path} must be an object")
        fields = {
            "sequence", "observation_id", "observation_sha256", "source_artifact_sha256",
            "collector_id", "collection_method", "recorded_at", "previous_record_hash",
            "authentication", "record_hash",
        }
        _exact(record, fields, path)
        if record["sequence"] != expected_sequence:
            raise ValueError(f"{path}.sequence is not contiguous")
        observation_id = _identifier(record["observation_id"], f"{path}.observation_id")
        if observation_id in seen or observation_id not in observation_map:
            raise ValueError(f"{path}.observation_id is duplicate or missing from observations")
        seen.add(observation_id)
        for field in ("observation_sha256", "source_artifact_sha256", "previous_record_hash", "record_hash"):
            _hash(record[field], f"{path}.{field}")
        _identifier(record["collector_id"], f"{path}.collector_id")
        _text(record["collection_method"], f"{path}.collection_method", 256)
        _timestamp(record["recorded_at"], f"{path}.recorded_at")
        if record["authentication"] not in AUTHENTICATION_METHODS:
            raise ValueError(f"{path}.authentication is not recognized")
        methods.add(record["authentication"])
        if record["previous_record_hash"] != previous:
            raise ValueError(f"{path}.previous_record_hash breaks the ledger chain")
        if record["observation_sha256"] != digest(observation_map[observation_id]):
            raise ValueError(f"{path}.observation_sha256 does not match the observation")
        key = hmac_key if record["authentication"] == "hmac_sha256_chain" else None
        if record["authentication"] == "hmac_sha256_chain" and key is None:
            raise ValueError("An HMAC key is required to verify this ledger")
        unsigned = {name: record[name] for name in fields if name != "record_hash"}
        expected_hash = _record_digest(unsigned, key)
        if not hmac.compare_digest(record["record_hash"], expected_hash):
            raise ValueError(f"{path}.record_hash is invalid")
        previous = record["record_hash"]
    if len(methods) > 1:
        raise ValueError("A ledger cannot mix authentication methods")
    if ledger["head_record_hash"] != previous:
        raise ValueError("ledger.head_record_hash does not match the final record")
    status = "NO_OBSERVATIONS" if not records else (
        "AUTHENTICATED" if methods == {"hmac_sha256_chain"} else "HASH_VERIFIED"
    )
    return {
        "status": status,
        "program_id": ledger["program_id"],
        "record_count": len(records),
        "head_record_hash": ledger["head_record_hash"],
        "admitted_observation_ids": sorted(seen),
    }


def _exact(value: Mapping[str, Any], fields: set[str], path: str) -> None:
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields)
    if missing:
        raise ValueError(f"{path} is missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value.strip()


def _identifier(value: Any, path: str) -> str:
    result = _text(value, path, 128)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", result):
        raise ValueError(f"{path} must be a safe identifier")
    return result


def _hash(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value):
        raise ValueError(f"{path} must be a lowercase SHA-256 digest")
    return value


def _timestamp(value: Any, path: str) -> datetime:
    text = _text(value, path, 64)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{path} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{path} must include a timezone")
    return parsed


def hmac_key_from_env(name: Optional[str]) -> Optional[bytes]:
    if not name:
        return None
    value = os.environ.get(name)
    if value is None or len(value) < 32:
        raise ValueError(f"{name} must contain an HMAC key of at least 32 characters")
    return value.encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or verify a SMERC evidence provenance ledger")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("observations", type=Path)
    build.add_argument("artifact_digests", type=Path)
    build.add_argument("output", type=Path)
    build.add_argument("--program-id", required=True)
    build.add_argument("--collector-id", required=True)
    build.add_argument("--collection-method", required=True)
    build.add_argument("--hmac-key-env")
    verify = subparsers.add_parser("verify")
    verify.add_argument("observations", type=Path)
    verify.add_argument("ledger", type=Path)
    verify.add_argument("--hmac-key-env")
    args = parser.parse_args()
    observations = json.loads(args.observations.read_text(encoding="utf-8"))
    key = hmac_key_from_env(args.hmac_key_env)
    if args.command == "build":
        artifact_digests = json.loads(args.artifact_digests.read_text(encoding="utf-8"))
        ledger = build_ledger(
            observations,
            program_id=args.program_id,
            collector_id=args.collector_id,
            collection_method=args.collection_method,
            artifact_digests=artifact_digests,
            hmac_key=key,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "built", "head_record_hash": ledger["head_record_hash"]}, indent=2))
    else:
        ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
        print(json.dumps(verify_ledger(observations, ledger, hmac_key=key), indent=2))


if __name__ == "__main__":
    main()

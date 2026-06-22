from __future__ import annotations

import hashlib
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VALID_STATES = {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"}
GENESIS_HASH = "0" * 64


def _hash_record(record: Dict[str, Any]) -> str:
    material = {key: value for key, value in record.items() if key != "record_hash"}
    canonical = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class FinancialAuditChain:
    """Append-only, tamper-evident decision and override record chain."""

    def __init__(self, records: Optional[List[Dict[str, Any]]] = None) -> None:
        self.records: List[Dict[str, Any]] = [dict(record) for record in (records or [])]

    def append_decision(
        self,
        action_id: str,
        decision: Dict[str, Any],
        recorded_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not action_id.strip():
            raise ValueError("action_id must be non-empty")
        if decision.get("state") not in VALID_STATES:
            raise ValueError("decision must contain a valid state")
        if not decision.get("decision_hash"):
            raise ValueError("decision must contain a decision_hash")

        record = {
            "sequence": len(self.records) + 1,
            "event_type": "DECISION",
            "recorded_at": recorded_at or datetime.now(timezone.utc).isoformat(),
            "previous_hash": self.records[-1]["record_hash"] if self.records else GENESIS_HASH,
            "action_id": action_id,
            "state": decision["state"],
            "decision_hash": decision["decision_hash"],
            "policy": dict(decision["policy"]),
            "drivers": list(decision["drivers"]),
            "controls": list(decision["controls"]),
        }
        record["record_hash"] = _hash_record(record)
        self.records.append(record)
        return dict(record)

    def append_override(
        self,
        action_id: str,
        from_state: str,
        to_state: str,
        reviewer_id: str,
        rationale: str,
        recorded_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        if from_state not in VALID_STATES or to_state not in VALID_STATES:
            raise ValueError("override states must be valid SMERC states")
        if not reviewer_id.strip():
            raise ValueError("reviewer_id must be non-empty")
        if len(rationale.strip()) < 12:
            raise ValueError("override rationale must contain at least 12 characters")

        record = {
            "sequence": len(self.records) + 1,
            "event_type": "OVERRIDE",
            "recorded_at": recorded_at or datetime.now(timezone.utc).isoformat(),
            "previous_hash": self.records[-1]["record_hash"] if self.records else GENESIS_HASH,
            "action_id": action_id,
            "from_state": from_state,
            "to_state": to_state,
            "reviewer_id": reviewer_id,
            "rationale": rationale.strip(),
        }
        record["record_hash"] = _hash_record(record)
        self.records.append(record)
        return dict(record)

    def verify(self) -> Dict[str, Any]:
        errors: List[str] = []
        previous_hash = GENESIS_HASH
        for expected_sequence, record in enumerate(self.records, start=1):
            if record.get("sequence") != expected_sequence:
                errors.append(f"record {expected_sequence}: invalid sequence")
            if record.get("previous_hash") != previous_hash:
                errors.append(f"record {expected_sequence}: previous hash mismatch")
            if record.get("record_hash") != _hash_record(record):
                errors.append(f"record {expected_sequence}: record hash mismatch")
            previous_hash = record.get("record_hash", "")
        return {
            "valid": not errors,
            "record_count": len(self.records),
            "head_hash": previous_hash,
            "errors": errors,
        }

    def to_dict(self) -> Dict[str, Any]:
        verification = self.verify()
        return {
            "chain_version": "1.0.0",
            "record_count": len(self.records),
            "head_hash": verification["head_hash"],
            "records": [dict(record) for record in self.records],
        }


def main() -> None:
    from reference_engine.financial_permission_profile import POLICY_PROFILES, FinancialPermissionProfile

    parser = argparse.ArgumentParser(description="Create a tamper-evident SMERC-F decision audit chain.")
    parser.add_argument("path", help="Path to a JSON financial action request or list of requests.")
    parser.add_argument("--policy", choices=sorted(POLICY_PROFILES), default="balanced")
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    actions = payload if isinstance(payload, list) else [payload]
    profile = FinancialPermissionProfile(args.policy)
    chain = FinancialAuditChain()
    for action in actions:
        decision = profile.evaluate(action)
        chain.append_decision(action["action_id"], decision)
    result = chain.to_dict()
    result["verification"] = chain.verify()
    rendered = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()


from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, Mapping


VERSION = "smerc.aws-pending-mutation-cache.v1"
ACTIVE_STATUSES = {"PENDING_CLOUD_EVIDENCE", "RECONCILED_GAP", "EXPIRED_UNRECONCILED"}
SUPPORTED_STATUSES = ACTIVE_STATUSES | {"RECONCILED_PASS"}
HIGH_RISK_REASON_CODES = {
    "AWS_KMS_RECOVERY_DEAD_END",
    "AWS_AUDIT_PATH_BLINDING_RISK",
    "AWS_S3_EXPOSURE_EXPANSION",
}


class PendingMutationCache:
    """Short-lived metadata memory for cloud mutations waiting on later audit evidence."""

    def __init__(self, *, ttl_minutes: int = 30) -> None:
        if ttl_minutes < 1:
            raise ValueError("ttl_minutes must be positive")
        self.ttl_minutes = ttl_minutes
        self._records: Dict[str, Dict[str, Any]] = {}

    def record_mutation(self, record: Mapping[str, Any]) -> Dict[str, Any]:
        parsed = self._parse_record(record)
        self._records[parsed["permit_id"]] = parsed
        return dict(parsed)

    def active_unreconciled(self, *, agent_id: str | None = None) -> list[Dict[str, Any]]:
        rows = []
        for record in self._records.values():
            if agent_id and record["agent_id"] != agent_id:
                continue
            if record["reconciliation_status"] in ACTIVE_STATUSES:
                rows.append(dict(record))
        return sorted(rows, key=lambda row: row["permit_id"])

    def summary(self, *, agent_id: str | None = None) -> Dict[str, Any]:
        active = self.active_unreconciled(agent_id=agent_id)
        statuses = Counter(row["reconciliation_status"] for row in active)
        reason_codes = Counter(code for row in active for code in row["reason_codes"])
        max_risk = max((float(row["unreconciled_risk"]) for row in active), default=0.0)
        return {
            "version": VERSION,
            "ttl_minutes": self.ttl_minutes,
            "active_unreconciled_count": len(active),
            "status_counts": dict(sorted(statuses.items())),
            "highest_unreconciled_risk": round(max_risk, 3),
            "reason_code_counts": dict(sorted(reason_codes.items())),
        }

    def next_action_effect(self, *, agent_id: str | None = None) -> Dict[str, Any]:
        active = self.active_unreconciled(agent_id=agent_id)
        if not active:
            return {
                "posture_hint": "ALLOW",
                "anomaly_pressure_delta": 0.0,
                "reason_codes": [],
                "summary": self.summary(agent_id=agent_id),
            }

        reason_codes = sorted(
            {"AWS_PENDING_MUTATION_UNRECONCILED"}
            | {code for row in active for code in row["reason_codes"]}
        )
        highest_risk = max(float(row["unreconciled_risk"]) for row in active)
        has_structural_dead_end = any(
            code in HIGH_RISK_REASON_CODES for row in active for code in row["reason_codes"]
        )
        posture_hint = "FREEZE" if highest_risk >= 0.85 or has_structural_dead_end else "THROTTLE"
        return {
            "posture_hint": posture_hint,
            "anomaly_pressure_delta": 0.32 if posture_hint == "FREEZE" else 0.2,
            "reason_codes": reason_codes,
            "summary": self.summary(agent_id=agent_id),
        }

    def _parse_record(self, record: Mapping[str, Any]) -> Dict[str, Any]:
        permit_id = _text(record.get("permit_id"), "permit_id")
        status = _text(record.get("reconciliation_status"), "reconciliation_status")
        if status not in SUPPORTED_STATUSES:
            raise ValueError(f"reconciliation_status must be one of {', '.join(sorted(SUPPORTED_STATUSES))}")
        risk = _score(record.get("unreconciled_risk"), "unreconciled_risk")
        return {
            "permit_id": permit_id,
            "agent_id": _text(record.get("agent_id"), "agent_id"),
            "workflow_id": _text(record.get("workflow_id"), "workflow_id"),
            "issued_at": _text(record.get("issued_at"), "issued_at"),
            "expires_at": _text(record.get("expires_at"), "expires_at"),
            "reconciliation_status": status,
            "pending_mutations": _list(record.get("pending_mutations"), "pending_mutations"),
            "unreconciled_risk": risk,
            "required_evidence": _list(record.get("required_evidence"), "required_evidence"),
            "reason_codes": _list(record.get("reason_codes"), "reason_codes"),
        }


def build_cache_from_map(payload: Mapping[str, Any]) -> PendingMutationCache:
    cache_cfg = payload.get("pending_state_cache")
    if not isinstance(cache_cfg, dict):
        raise TypeError("pending_state_cache must be an object")
    cache = PendingMutationCache(ttl_minutes=int(cache_cfg.get("ttl_minutes", 30)))
    issued_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    expires_at = issued_at
    for rule in payload.get("structural_irreversibility_rules", []):
        if not isinstance(rule, dict):
            raise TypeError("structural_irreversibility_rules entries must be objects")
        cache.record_mutation(
            {
                "permit_id": f"permit-{str(rule['rule_id']).lower()}",
                "agent_id": "aws-agent-runtime",
                "workflow_id": "aws-audit-delay-loop",
                "issued_at": issued_at,
                "expires_at": expires_at,
                "reconciliation_status": "PENDING_CLOUD_EVIDENCE",
                "pending_mutations": list(rule.get("aws_action_patterns", [])),
                "unreconciled_risk": _risk_from_posture(str(rule.get("default_smerc_posture", ""))),
                "required_evidence": list(rule.get("required_evidence_before_release", [])),
                "reason_codes": list(rule.get("reason_codes", [])),
            }
        )
    return cache


def _risk_from_posture(posture: str) -> float:
    return {"DENY": 0.96, "FREEZE": 0.88, "ESCALATE": 0.76, "THROTTLE": 0.68}.get(posture, 0.5)


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TypeError(f"{path} must be a non-empty list")
    return [_text(item, f"{path}[]") for item in value]


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be numeric")
    score = float(value)
    if score < 0 or score > 1:
        raise ValueError(f"{path} must be between 0 and 1")
    return score

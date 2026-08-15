from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


POLICY_VERSION = "smerc.policy.v1"
MODES = {"OBSERVE", "RECOMMEND", "ENFORCE"}
EVIDENCE_CEILINGS = {"STOP", "OBSERVE", "RECOMMEND", "LIMITED_ENFORCE", "CALIBRATED_ENFORCE"}
FAIL_BEHAVIORS = {"report_unavailable", "fail_closed"}
MODE_RANK = {"OBSERVE": 0, "RECOMMEND": 1, "ENFORCE": 2}
CEILING_MODE = {
    "STOP": "OBSERVE",
    "OBSERVE": "OBSERVE",
    "RECOMMEND": "RECOMMEND",
    "LIMITED_ENFORCE": "ENFORCE",
    "CALIBRATED_ENFORCE": "ENFORCE",
}


@dataclass(frozen=True)
class PolicyThresholds:
    deny_exposure_min: float = 0.78
    deny_capacity_max: float = 0.42
    deny_confidence_max: float = 0.48
    deny_cancel_reliability_max: float = 0.30
    deny_cancel_exposure_min: float = 0.62
    escalate_stress_min: float = 0.70
    freeze_confidence_max: float = 0.45
    freeze_capacity_max: float = 0.36
    throttle_authorization_min: float = 0.62
    throttle_exposure_min: float = 0.45


@dataclass(frozen=True)
class RuntimePolicy:
    tenant_id: str
    policy_id: str
    policy_revision: str
    mode: str
    evidence_program_id: str
    evidence_ceiling: str
    fail_behavior: str
    approved_by_role: str
    effective_at: str
    thresholds: PolicyThresholds

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "RuntimePolicy":
        required = {
            "version", "tenant_id", "policy_id", "policy_revision", "mode",
            "evidence_program_id", "evidence_ceiling", "fail_behavior",
            "approved_by_role", "effective_at", "thresholds",
        }
        _exact(payload, required, "policy")
        if payload["version"] != POLICY_VERSION:
            raise ValueError(f"policy.version must be {POLICY_VERSION}")
        tenant_id = _identifier(payload["tenant_id"], "policy.tenant_id", allow_wildcard=True)
        policy_id = _identifier(payload["policy_id"], "policy.policy_id")
        policy_revision = _text(payload["policy_revision"], "policy.policy_revision", 64)
        mode = _choice(payload["mode"], MODES, "policy.mode")
        evidence_program_id = _identifier(payload["evidence_program_id"], "policy.evidence_program_id")
        evidence_ceiling = _choice(payload["evidence_ceiling"], EVIDENCE_CEILINGS, "policy.evidence_ceiling")
        fail_behavior = _choice(payload["fail_behavior"], FAIL_BEHAVIORS, "policy.fail_behavior")
        approved_by_role = _text(payload["approved_by_role"], "policy.approved_by_role", 128)
        effective_at = _text(payload["effective_at"], "policy.effective_at", 64)
        try:
            parsed_effective_at = datetime.fromisoformat(effective_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("policy.effective_at must be an ISO-8601 timestamp") from exc
        if parsed_effective_at.tzinfo is None:
            raise ValueError("policy.effective_at must include a timezone")
        if MODE_RANK[mode] > MODE_RANK[CEILING_MODE[evidence_ceiling]]:
            raise ValueError(f"policy.mode {mode} exceeds evidence ceiling {evidence_ceiling}")
        if mode == "ENFORCE" and fail_behavior != "fail_closed":
            raise ValueError("ENFORCE mode requires fail_closed behavior")

        threshold_payload = payload["thresholds"]
        if not isinstance(threshold_payload, Mapping):
            raise TypeError("policy.thresholds must be an object")
        threshold_fields = set(PolicyThresholds.__dataclass_fields__)
        _exact(threshold_payload, threshold_fields, "policy.thresholds")
        values = {name: _score(threshold_payload[name], f"policy.thresholds.{name}") for name in threshold_fields}
        thresholds = PolicyThresholds(**values)
        _validate_threshold_order(thresholds)
        return cls(
            tenant_id=tenant_id,
            policy_id=policy_id,
            policy_revision=policy_revision,
            mode=mode,
            evidence_program_id=evidence_program_id,
            evidence_ceiling=evidence_ceiling,
            fail_behavior=fail_behavior,
            approved_by_role=approved_by_role,
            effective_at=effective_at,
            thresholds=thresholds,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"version": POLICY_VERSION, **asdict(self)}

    @property
    def policy_hash(self) -> str:
        return hashlib.sha256(canonical_json(self.to_dict()).encode("utf-8")).hexdigest()

    def decision_metadata(self) -> Dict[str, str]:
        return {
            "tenant_id": self.tenant_id,
            "policy_id": self.policy_id,
            "policy_revision": self.policy_revision,
            "policy_hash": self.policy_hash,
            "mode": self.mode,
            "evidence_ceiling": self.evidence_ceiling,
        }


class PolicyRegistry:
    def __init__(self, policies: Iterable[RuntimePolicy] = ()) -> None:
        self._policies: Dict[str, list[RuntimePolicy]] = {}
        identities = set()
        for policy in policies:
            identity = (policy.tenant_id, policy.policy_id, policy.policy_revision)
            if identity in identities:
                raise ValueError(f"Duplicate policy identity: {'/'.join(identity)}")
            identities.add(identity)
            self._policies.setdefault(policy.tenant_id, []).append(policy)
        for tenant_policies in self._policies.values():
            tenant_policies.sort(key=lambda item: _effective_datetime(item.effective_at))

    def for_tenant(self, tenant_id: str, *, as_of: Optional[datetime] = None) -> RuntimePolicy:
        when = as_of or datetime.now(timezone.utc)
        configured = self._policies.get(tenant_id)
        candidates = configured if configured is not None else self._policies.get("*", [DEFAULT_POLICY])
        effective = [item for item in candidates if _effective_datetime(item.effective_at) <= when]
        if not effective:
            raise ValueError(f"No configured policy for tenant {tenant_id} is effective yet")
        return effective[-1]

    @property
    def count(self) -> int:
        return len([key for key in self._policies if key != "*"])

    @classmethod
    def from_directory(cls, directory: str | Path) -> "PolicyRegistry":
        path = Path(directory)
        if not path.is_dir():
            raise ValueError(f"Policy directory does not exist: {path}")
        policies = [RuntimePolicy.from_dict(json.loads(item.read_text(encoding="utf-8"))) for item in sorted(path.glob("*.json"))]
        if not policies:
            raise ValueError("Policy directory must contain at least one JSON policy")
        return cls(policies)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _exact(value: Mapping[str, Any], required: set[str], path: str) -> None:
    missing = sorted(required - set(value))
    unknown = sorted(set(value) - required)
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


def _identifier(value: Any, path: str, *, allow_wildcard: bool = False) -> str:
    result = _text(value, path, 128)
    if allow_wildcard and result == "*":
        return result
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", result):
        raise ValueError(f"{path} must be a safe identifier")
    return result


def _choice(value: Any, choices: set[str], path: str) -> str:
    if value not in choices:
        raise ValueError(f"{path} must be one of: {', '.join(sorted(choices))}")
    return value


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number from 0.0 through 1.0")
    if not 0 <= value <= 1:
        raise ValueError(f"{path} must be from 0.0 through 1.0")
    return float(value)


def _validate_threshold_order(value: PolicyThresholds) -> None:
    if value.deny_exposure_min < value.throttle_exposure_min:
        raise ValueError("deny_exposure_min must be at least throttle_exposure_min")
    if value.deny_cancel_exposure_min < value.throttle_exposure_min:
        raise ValueError("deny_cancel_exposure_min must be at least throttle_exposure_min")
    if value.deny_capacity_max < value.freeze_capacity_max:
        raise ValueError("deny_capacity_max must be at least freeze_capacity_max")
    if value.deny_confidence_max < value.freeze_confidence_max:
        raise ValueError("deny_confidence_max must be at least freeze_confidence_max")


def _effective_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


DEFAULT_POLICY = RuntimePolicy(
    tenant_id="*",
    policy_id="smerc-reference-recoverability",
    policy_revision="1.0.0",
    mode="OBSERVE",
    evidence_program_id="smerc-core-validation-v1",
    evidence_ceiling="OBSERVE",
    fail_behavior="report_unavailable",
    approved_by_role="reference-implementation",
    effective_at="2026-07-03T00:00:00Z",
    thresholds=PolicyThresholds(),
)


def load_policy(path: str | Path) -> RuntimePolicy:
    return RuntimePolicy.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

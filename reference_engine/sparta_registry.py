from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

from reference_engine.sparta_router import SIDE_EFFECT_LEVELS, SPARTA_PLAN_VERSION, ToolPlan


SPARTA_ADAPTER_REGISTRY_VERSION = "smerc.sparta-adapter-registry.v1"
ADAPTER_FIELDS = {
    "version",
    "adapter_id",
    "tool",
    "supported_actions",
    "supported_capabilities",
    "supports_dry_run",
    "supports_scope_limit",
    "supports_checkpoint",
    "supports_rollback",
    "supports_human_approval",
    "max_scope_units",
    "allowed_side_effect_levels",
    "metadata",
}
REGISTRY_FIELDS = {"version", "adapters"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _identifier(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,%d}" % (maximum - 1), value):
        raise ValueError(f"{path} must be a safe identifier of 1 to {maximum} characters")
    return value


def _strict(value: Any, fields: set[str], path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    missing = sorted(fields - set(value))
    if missing:
        raise ValueError(f"{path} is missing required field(s): {', '.join(missing)}")
    unknown = sorted(set(value) - fields)
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")
    return dict(value)


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _positive_int(value: Any, path: str, maximum: int = 1_000_000) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if value < 1 or value > maximum:
        raise ValueError(f"{path} must be between 1 and {maximum}")
    return value


def _identifier_list(value: Any, path: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise TypeError(f"{path} must be a non-empty list")
    parsed = tuple(_identifier(item, f"{path}[]") for item in value)
    if len(parsed) != len(set(parsed)):
        raise ValueError(f"{path} must not contain duplicates")
    return parsed


def _side_effect_levels(value: Any, path: str) -> tuple[str, ...]:
    parsed = _identifier_list(value, path)
    unknown = sorted(set(parsed) - SIDE_EFFECT_LEVELS)
    if unknown:
        raise ValueError(f"{path} contains unsupported side-effect level(s): {', '.join(unknown)}")
    return parsed


def _metadata(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    if len(_canonical_json(value).encode("utf-8")) > 4096:
        raise ValueError(f"{path} must be no larger than 4096 bytes")
    return dict(value)


@dataclass(frozen=True)
class SPARTaAdapter:
    adapter_id: str
    tool: str
    supported_actions: tuple[str, ...]
    supported_capabilities: tuple[str, ...]
    supports_dry_run: bool
    supports_scope_limit: bool
    supports_checkpoint: bool
    supports_rollback: bool
    supports_human_approval: bool
    max_scope_units: int
    allowed_side_effect_levels: tuple[str, ...]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "SPARTaAdapter":
        value = _strict(dict(payload), ADAPTER_FIELDS, "adapter")
        if value["version"] != SPARTA_ADAPTER_REGISTRY_VERSION:
            raise ValueError(f"adapter.version must be {SPARTA_ADAPTER_REGISTRY_VERSION}")
        return cls(
            adapter_id=_identifier(value["adapter_id"], "adapter.adapter_id"),
            tool=_identifier(value["tool"], "adapter.tool"),
            supported_actions=_identifier_list(value["supported_actions"], "adapter.supported_actions"),
            supported_capabilities=_identifier_list(
                value["supported_capabilities"], "adapter.supported_capabilities"
            ),
            supports_dry_run=_bool(value["supports_dry_run"], "adapter.supports_dry_run"),
            supports_scope_limit=_bool(value["supports_scope_limit"], "adapter.supports_scope_limit"),
            supports_checkpoint=_bool(value["supports_checkpoint"], "adapter.supports_checkpoint"),
            supports_rollback=_bool(value["supports_rollback"], "adapter.supports_rollback"),
            supports_human_approval=_bool(value["supports_human_approval"], "adapter.supports_human_approval"),
            max_scope_units=_positive_int(value["max_scope_units"], "adapter.max_scope_units"),
            allowed_side_effect_levels=_side_effect_levels(
                value["allowed_side_effect_levels"], "adapter.allowed_side_effect_levels"
            ),
            metadata=_metadata(value["metadata"], "adapter.metadata"),
        )

    def plan_for(
        self,
        *,
        action: str,
        requested_capability: str,
        requested_scope_units: int,
        side_effect_level: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> ToolPlan:
        action = _identifier(action, "route.action")
        requested_capability = _identifier(requested_capability, "route.requested_capability")
        requested_scope_units = _positive_int(requested_scope_units, "route.requested_scope_units")
        side_effect_level = _identifier(side_effect_level, "route.side_effect_level", 32)
        if action not in self.supported_actions:
            raise ValueError(f"adapter {self.adapter_id} does not support action {action}")
        if requested_capability not in self.supported_capabilities:
            raise ValueError(f"adapter {self.adapter_id} does not support capability {requested_capability}")
        if side_effect_level not in self.allowed_side_effect_levels:
            raise ValueError(f"adapter {self.adapter_id} does not allow side-effect level {side_effect_level}")
        if requested_scope_units > self.max_scope_units:
            raise ValueError("route.requested_scope_units cannot exceed adapter.max_scope_units")
        merged_metadata = dict(self.metadata)
        if metadata is not None:
            merged_metadata.update(_metadata(dict(metadata), "route.metadata"))
        return ToolPlan(
            plan_id=f"{self.adapter_id}:{action}:{requested_capability}",
            tool=self.tool,
            action=action,
            requested_capability=requested_capability,
            supports_dry_run=self.supports_dry_run,
            supports_scope_limit=self.supports_scope_limit,
            supports_checkpoint=self.supports_checkpoint,
            supports_rollback=self.supports_rollback,
            supports_human_approval=self.supports_human_approval,
            max_scope_units=self.max_scope_units,
            requested_scope_units=requested_scope_units,
            side_effect_level=side_effect_level,
            metadata=merged_metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": SPARTA_ADAPTER_REGISTRY_VERSION,
            "adapter_id": self.adapter_id,
            "tool": self.tool,
            "supported_actions": list(self.supported_actions),
            "supported_capabilities": list(self.supported_capabilities),
            "supports_dry_run": self.supports_dry_run,
            "supports_scope_limit": self.supports_scope_limit,
            "supports_checkpoint": self.supports_checkpoint,
            "supports_rollback": self.supports_rollback,
            "supports_human_approval": self.supports_human_approval,
            "max_scope_units": self.max_scope_units,
            "allowed_side_effect_levels": list(self.allowed_side_effect_levels),
            "metadata": dict(self.metadata),
        }


class SPARTaAdapterRegistry:
    def __init__(self, adapters: Iterable[SPARTaAdapter]) -> None:
        parsed = list(adapters)
        ids = [item.adapter_id for item in parsed]
        if len(ids) != len(set(ids)):
            raise ValueError("SPARTa adapter registry cannot contain duplicate adapter IDs")
        self._adapters = {item.adapter_id: item for item in parsed}

    @property
    def count(self) -> int:
        return len(self._adapters)

    def get(self, adapter_id: str) -> SPARTaAdapter:
        adapter_id = _identifier(adapter_id, "adapter_id")
        adapter = self._adapters.get(adapter_id)
        if adapter is None:
            raise ValueError(f"Unknown SPARTa adapter: {adapter_id}")
        return adapter

    def plan_from_request(self, payload: Mapping[str, Any]) -> ToolPlan:
        allowed = {"adapter_id", "action", "requested_capability", "requested_scope_units", "side_effect_level", "metadata"}
        value = _strict(dict(payload), allowed, "route_request")
        adapter = self.get(value["adapter_id"])
        return adapter.plan_for(
            action=value["action"],
            requested_capability=value["requested_capability"],
            requested_scope_units=value["requested_scope_units"],
            side_effect_level=value["side_effect_level"],
            metadata=value["metadata"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": SPARTA_ADAPTER_REGISTRY_VERSION,
            "adapters": [adapter.to_dict() for adapter in self._adapters.values()],
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "SPARTaAdapterRegistry":
        value = _strict(dict(payload), REGISTRY_FIELDS, "registry")
        if value["version"] != SPARTA_ADAPTER_REGISTRY_VERSION:
            raise ValueError(f"registry.version must be {SPARTA_ADAPTER_REGISTRY_VERSION}")
        adapters = value["adapters"]
        if not isinstance(adapters, list):
            raise TypeError("registry.adapters must be a list")
        return cls(SPARTaAdapter.from_dict(item) for item in adapters)


def load_sparta_adapter_registry(path: Path) -> SPARTaAdapterRegistry:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError("SPARTa adapter registry must be a JSON object")
    return SPARTaAdapterRegistry.from_dict(payload)


def plan_from_payload(
    payload: Mapping[str, Any],
    registry: Optional[SPARTaAdapterRegistry] = None,
) -> ToolPlan:
    if "plan" in payload:
        allowed = {"plan"}
        _strict(dict(payload), allowed, "route_payload")
        plan = payload["plan"]
        if not isinstance(plan, dict):
            raise TypeError("route_payload.plan must be an object")
        return ToolPlan.from_dict(plan)
    if "adapter_id" in payload:
        if registry is None:
            raise ValueError("SPARTa adapter registry is not configured")
        return registry.plan_from_request(payload)
    raise ValueError("Route payload must contain either plan or adapter_id.")

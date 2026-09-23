from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from uuid import uuid4


VERSION = "smerc.delegated-continuance-contract.v1"
DECISIONS = {"CONTINUE", "BLOCK", "EXPIRED", "CHECKPOINT_REQUIRED", "CLEANUP_REQUIRED"}


class ContinuanceContractError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _identifier(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:@/-]{0,191}", value):
        raise ContinuanceContractError(f"{path} must be a safe identifier")
    return value


def _identifiers(values: Iterable[Any], path: str) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise ContinuanceContractError(f"{path} must be a list")
    result = sorted(_identifier(value, path) for value in values)
    if len(result) != len(set(result)):
        raise ContinuanceContractError(f"{path} must not contain duplicates")
    return result


def _number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ContinuanceContractError(f"{path} must be a non-negative number")
    return float(value)


@dataclass(frozen=True)
class ContinuanceContractSigner:
    key_id: str
    secret: bytes

    def __post_init__(self) -> None:
        _identifier(self.key_id, "key_id")
        if not isinstance(self.secret, bytes) or len(self.secret) < 32:
            raise ValueError("contract signing secrets must contain at least 32 bytes")

    def issue_root(
        self,
        *,
        tenant_id: str,
        originating_user_id: str,
        agent_id: str,
        intent_digest: str,
        capabilities: Iterable[str],
        resources: Iterable[str],
        max_actions: int,
        max_scope_units: float,
        max_cost_usd: float,
        max_delegation_depth: int,
        issued_at: int,
        expires_at: int,
        checkpoint_every_actions: int,
        cleanup_obligations: Iterable[str],
    ) -> dict[str, Any]:
        body = {
            "version": VERSION,
            "contract_id": f"dcc_{uuid4().hex}",
            "parent_contract_sha256": None,
            "tenant_id": _identifier(tenant_id, "tenant_id"),
            "originating_user_id": _identifier(originating_user_id, "originating_user_id"),
            "agent_id": _identifier(agent_id, "agent_id"),
            "intent_digest": self._intent_digest(intent_digest),
            "delegation_depth": 0,
            "max_delegation_depth": self._integer(max_delegation_depth, "max_delegation_depth", minimum=0),
            "capabilities": _identifiers(capabilities, "capabilities"),
            "resources": _identifiers(resources, "resources"),
            "budget": self._budget(max_actions, max_scope_units, max_cost_usd),
            "issued_at": self._integer(issued_at, "issued_at", minimum=0),
            "expires_at": self._integer(expires_at, "expires_at", minimum=1),
            "checkpoint_every_actions": self._integer(
                checkpoint_every_actions, "checkpoint_every_actions", minimum=1
            ),
            "cleanup_obligations": _identifiers(cleanup_obligations, "cleanup_obligations"),
        }
        if body["expires_at"] <= body["issued_at"]:
            raise ContinuanceContractError("expires_at must be after issued_at")
        return self._sign(body)

    def delegate(
        self,
        parent: Mapping[str, Any],
        *,
        agent_id: str,
        capabilities: Iterable[str],
        resources: Iterable[str],
        max_actions: int,
        max_scope_units: float,
        max_cost_usd: float,
        expires_at: int,
        checkpoint_every_actions: int,
        cleanup_obligations: Iterable[str],
    ) -> dict[str, Any]:
        parent_body = self.verify(parent)
        child_capabilities = _identifiers(capabilities, "capabilities")
        child_resources = _identifiers(resources, "resources")
        child_cleanup = _identifiers(cleanup_obligations, "cleanup_obligations")
        child_budget = self._budget(max_actions, max_scope_units, max_cost_usd)
        depth = parent_body["delegation_depth"] + 1
        violations = []
        if depth > parent_body["max_delegation_depth"]:
            violations.append("delegation_depth_exceeded")
        if not set(child_capabilities) <= set(parent_body["capabilities"]):
            violations.append("capability_expansion")
        if not set(child_resources) <= set(parent_body["resources"]):
            violations.append("resource_expansion")
        if any(child_budget[key] > parent_body["budget"][key] for key in child_budget):
            violations.append("budget_expansion")
        if expires_at > parent_body["expires_at"]:
            violations.append("expiry_expansion")
        if checkpoint_every_actions > parent_body["checkpoint_every_actions"]:
            violations.append("checkpoint_weakening")
        if not set(parent_body["cleanup_obligations"]) <= set(child_cleanup):
            violations.append("cleanup_obligation_removed")
        if violations:
            raise ContinuanceContractError("delegation must attenuate authority: " + ", ".join(violations))
        body = {
            **{key: parent_body[key] for key in ("version", "tenant_id", "originating_user_id", "intent_digest", "max_delegation_depth", "issued_at")},
            "contract_id": f"dcc_{uuid4().hex}",
            "parent_contract_sha256": _digest(parent),
            "agent_id": _identifier(agent_id, "agent_id"),
            "delegation_depth": depth,
            "capabilities": child_capabilities,
            "resources": child_resources,
            "budget": child_budget,
            "expires_at": self._integer(expires_at, "expires_at", minimum=1),
            "checkpoint_every_actions": self._integer(
                checkpoint_every_actions, "checkpoint_every_actions", minimum=1
            ),
            "cleanup_obligations": child_cleanup,
        }
        return self._sign(body)

    def verify(self, contract: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(contract, Mapping) or set(contract) != {"contract", "verification"}:
            raise ContinuanceContractError("contract envelope fields are invalid")
        body = contract["contract"]
        verification = contract["verification"]
        if not isinstance(body, Mapping) or not isinstance(verification, Mapping):
            raise ContinuanceContractError("contract envelope is invalid")
        if verification.get("method") != "hmac_sha256" or verification.get("key_id") != self.key_id:
            raise ContinuanceContractError("contract verification metadata is invalid")
        expected = hmac.new(self.secret, _canonical(body), hashlib.sha256).hexdigest()
        if not isinstance(verification.get("signature"), str) or not hmac.compare_digest(
            verification["signature"], expected
        ):
            raise ContinuanceContractError("contract signature is invalid")
        self._validate_body(body)
        return dict(body)

    def _sign(self, body: Mapping[str, Any]) -> dict[str, Any]:
        self._validate_body(body)
        return {
            "contract": dict(body),
            "verification": {
                "method": "hmac_sha256",
                "key_id": self.key_id,
                "signature": hmac.new(self.secret, _canonical(body), hashlib.sha256).hexdigest(),
            },
        }

    @staticmethod
    def _integer(value: Any, path: str, *, minimum: int) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ContinuanceContractError(f"{path} must be an integer of at least {minimum}")
        return value

    @staticmethod
    def _intent_digest(value: Any) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ContinuanceContractError("intent_digest must be a lowercase SHA-256 digest")
        return value

    def _budget(self, actions: Any, scope: Any, cost: Any) -> dict[str, Any]:
        return {
            "max_actions": self._integer(actions, "max_actions", minimum=0),
            "max_scope_units": _number(scope, "max_scope_units"),
            "max_cost_usd": _number(cost, "max_cost_usd"),
        }

    def _validate_body(self, body: Mapping[str, Any]) -> None:
        fields = {
            "version", "contract_id", "parent_contract_sha256", "tenant_id", "originating_user_id",
            "agent_id", "intent_digest", "delegation_depth", "max_delegation_depth", "capabilities",
            "resources", "budget", "issued_at", "expires_at", "checkpoint_every_actions",
            "cleanup_obligations",
        }
        if set(body) != fields or body.get("version") != VERSION:
            raise ContinuanceContractError("contract fields or version are invalid")
        for field in ("contract_id", "tenant_id", "originating_user_id", "agent_id"):
            _identifier(body[field], field)
        parent_hash = body["parent_contract_sha256"]
        if parent_hash is not None and (not isinstance(parent_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", parent_hash)):
            raise ContinuanceContractError("parent_contract_sha256 is invalid")
        self._intent_digest(body["intent_digest"])
        depth = self._integer(body["delegation_depth"], "delegation_depth", minimum=0)
        maximum = self._integer(body["max_delegation_depth"], "max_delegation_depth", minimum=0)
        if depth > maximum or (depth == 0) != (parent_hash is None):
            raise ContinuanceContractError("delegation lineage is invalid")
        _identifiers(body["capabilities"], "capabilities")
        _identifiers(body["resources"], "resources")
        expected_budget = self._budget(
            body["budget"].get("max_actions"),
            body["budget"].get("max_scope_units"),
            body["budget"].get("max_cost_usd"),
        )
        if body["budget"] != expected_budget:
            raise ContinuanceContractError("budget fields are invalid")
        issued = self._integer(body["issued_at"], "issued_at", minimum=0)
        expires = self._integer(body["expires_at"], "expires_at", minimum=1)
        if expires <= issued:
            raise ContinuanceContractError("contract expiry is invalid")
        self._integer(body["checkpoint_every_actions"], "checkpoint_every_actions", minimum=1)
        _identifiers(body["cleanup_obligations"], "cleanup_obligations")


def evaluate_delegated_continuance(
    signer: ContinuanceContractSigner,
    contract: Mapping[str, Any],
    action: Mapping[str, Any],
    consumption: Mapping[str, Any],
    *,
    now: int,
) -> dict[str, Any]:
    body = signer.verify(contract)
    reasons = []
    if now >= body["expires_at"]:
        decision = "EXPIRED"
        reasons.append("contract_expired")
    else:
        capability = _identifier(action.get("capability"), "action.capability")
        resource = _identifier(action.get("resource"), "action.resource")
        action_intent = signer._intent_digest(action.get("intent_digest"))
        action_count = signer._integer(consumption.get("actions", 0), "consumption.actions", minimum=0)
        spent_scope = _number(consumption.get("scope_units", 0), "consumption.scope_units")
        spent_cost = _number(consumption.get("cost_usd", 0), "consumption.cost_usd")
        requested_scope = _number(action.get("scope_units", 0), "action.scope_units")
        requested_cost = _number(action.get("cost_usd", 0), "action.cost_usd")
        if action_intent != body["intent_digest"]:
            reasons.append("intent_drift")
        if capability not in body["capabilities"]:
            reasons.append("capability_not_delegated")
        if resource not in body["resources"]:
            reasons.append("resource_not_delegated")
        if action_count + 1 > body["budget"]["max_actions"]:
            reasons.append("action_budget_exhausted")
        if spent_scope + requested_scope > body["budget"]["max_scope_units"]:
            reasons.append("scope_budget_exhausted")
        if spent_cost + requested_cost > body["budget"]["max_cost_usd"]:
            reasons.append("cost_budget_exhausted")
        checkpoint_due = action_count > 0 and action_count % body["checkpoint_every_actions"] == 0
        cleanup_due = bool(body["cleanup_obligations"]) and action.get("external_side_effect") is True
        if reasons:
            decision = "BLOCK"
        elif checkpoint_due and action.get("checkpoint_present") is not True:
            decision = "CHECKPOINT_REQUIRED"
            reasons.append("checkpoint_missing")
        elif cleanup_due and action.get("cleanup_plan_present") is not True:
            decision = "CLEANUP_REQUIRED"
            reasons.append("cleanup_plan_missing")
        else:
            decision = "CONTINUE"
    return {
        "version": VERSION,
        "contract_id": body["contract_id"],
        "agent_id": body["agent_id"],
        "decision": decision,
        "reasons": reasons,
        "remaining": {
            "actions": max(0, body["budget"]["max_actions"] - int(consumption.get("actions", 0)) - (1 if decision == "CONTINUE" else 0)),
            "scope_units": max(0.0, body["budget"]["max_scope_units"] - float(consumption.get("scope_units", 0)) - (float(action.get("scope_units", 0)) if decision == "CONTINUE" else 0.0)),
            "cost_usd": max(0.0, body["budget"]["max_cost_usd"] - float(consumption.get("cost_usd", 0)) - (float(action.get("cost_usd", 0)) if decision == "CONTINUE" else 0.0)),
        },
        "evidence": {
            "contract_sha256": _digest(contract),
            "action_sha256": _digest(action),
            "authority_rechecked_at": now,
        },
    }

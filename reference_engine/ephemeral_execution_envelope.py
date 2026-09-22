from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Mapping


VERSION = "smerc.ephemeral-execution-envelope.v1"
TERMINAL_STATES = {"PROMOTED", "DISCARDED", "EXPIRED"}
TRANSITIONS = {
    "CREATED": {"ACTIVE", "DISCARDED", "EXPIRED"},
    "ACTIVE": {"SEALED", "DISCARDED", "EXPIRED"},
    "SEALED": {"PROMOTED", "DISCARDED", "EXPIRED"},
}
PROMOTION_FIELDS = {
    "tests_passed", "review_approved", "policy_rechecked", "isolation_verified",
    "approved_target_sha256", "sealed_commit_sha", "durable_ref",
}
ENVELOPE_FIELDS = {
    "version", "envelope_id", "namespace", "run_id", "base_ref", "base_commit_sha",
    "ephemeral_ref", "created_at", "expires_at", "state", "policy_bundle_sha256",
    "execution_target_sha256", "permit_id", "replay_id", "containment", "promotion",
    "sealed_commit_sha", "terminal_reason", "events", "envelope_sha256",
}
EVENT_FIELDS = {
    "from_state", "to_state", "at", "evidence_sha256", "prior_event_sha256", "event_sha256",
}
CONTAINMENT_FIELDS = {
    "direct_durable_writes", "network_mode", "credential_scope", "max_scope_units",
}


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _identifier(value: Any, path: str, maximum: int = 192) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,%d}" % (maximum - 1), value):
        raise ValueError(f"{path} must be a safe identifier")
    return value


def _sha256(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError(f"{path} must be a lowercase SHA-256 digest")
    return value


def _git_oid(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
        raise ValueError(f"{path} must be a lowercase Git SHA-1 or SHA-256 object ID")
    return value


def _timestamp(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{path} must be a non-negative Unix timestamp")
    return value


def _event(from_state: str | None, to_state: str, at: int, evidence: Mapping[str, Any], prior: str | None) -> dict[str, Any]:
    material = {
        "from_state": from_state,
        "to_state": to_state,
        "at": at,
        "evidence_sha256": canonical_digest(dict(evidence)),
        "prior_event_sha256": prior,
    }
    return {**material, "event_sha256": canonical_digest(material)}


def create_envelope(
    *, namespace: str, run_id: str, base_ref: str, base_commit_sha: str,
    policy_bundle_sha256: str, execution_target_sha256: str, permit_id: str,
    replay_id: str, now: int, ttl_seconds: int = 86_400,
    network_mode: str = "brokered-only", credential_scope: str = "run-bound",
    max_scope_units: int = 1,
) -> dict[str, Any]:
    now = _timestamp(now, "now")
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or not 60 <= ttl_seconds <= 1_209_600:
        raise ValueError("ttl_seconds must be between 60 seconds and 14 days")
    if isinstance(max_scope_units, bool) or not isinstance(max_scope_units, int) or max_scope_units < 1:
        raise ValueError("max_scope_units must be a positive integer")
    namespace = _identifier(namespace, "namespace", 64)
    run_id = _identifier(run_id, "run_id")
    evidence = {"base_commit_sha": _git_oid(base_commit_sha, "base_commit_sha")}
    first_event = _event(None, "CREATED", now, evidence, None)
    envelope = {
        "version": VERSION,
        "envelope_id": f"smerc-ee-{canonical_digest({'namespace': namespace, 'run_id': run_id, 'now': now})[:20]}",
        "namespace": namespace,
        "run_id": run_id,
        "base_ref": _identifier(base_ref, "base_ref"),
        "base_commit_sha": evidence["base_commit_sha"],
        "ephemeral_ref": f"refs/ephemeral/{namespace}/{run_id}",
        "created_at": now,
        "expires_at": now + ttl_seconds,
        "state": "CREATED",
        "policy_bundle_sha256": _sha256(policy_bundle_sha256, "policy_bundle_sha256"),
        "execution_target_sha256": _sha256(execution_target_sha256, "execution_target_sha256"),
        "permit_id": _identifier(permit_id, "permit_id"),
        "replay_id": _identifier(replay_id, "replay_id"),
        "containment": {
            "direct_durable_writes": False,
            "network_mode": _identifier(network_mode, "network_mode", 64),
            "credential_scope": _identifier(credential_scope, "credential_scope", 64),
            "max_scope_units": max_scope_units,
        },
        "promotion": None,
        "sealed_commit_sha": None,
        "terminal_reason": None,
        "events": [first_event],
    }
    envelope["envelope_sha256"] = envelope_digest(envelope)
    return envelope


def envelope_digest(envelope: Mapping[str, Any]) -> str:
    return canonical_digest({key: value for key, value in dict(envelope).items() if key != "envelope_sha256"})


def transition_envelope(
    envelope: Mapping[str, Any], to_state: str, *, now: int,
    evidence: Mapping[str, Any] | None = None, reason: str | None = None,
) -> dict[str, Any]:
    current = verify_envelope(envelope, now=now, allow_expired=True)
    from_state = current["state"]
    if to_state not in TRANSITIONS.get(from_state, set()):
        raise ValueError(f"invalid envelope transition: {from_state} -> {to_state}")
    now = _timestamp(now, "now")
    if now >= current["expires_at"] and to_state != "EXPIRED":
        raise ValueError("expired envelope can only transition to EXPIRED")
    transition_evidence = dict(evidence or {})
    if to_state == "SEALED":
        if set(transition_evidence) != {"sealed_commit_sha"}:
            raise ValueError("sealed transition requires exact sealed_commit_sha evidence")
        _git_oid(transition_evidence.get("sealed_commit_sha"), "sealed_commit_sha")
    if to_state == "PROMOTED":
        _validate_promotion(current, transition_evidence)
    updated = copy.deepcopy(current)
    updated["state"] = to_state
    updated["events"].append(_event(from_state, to_state, now, transition_evidence, updated["events"][-1]["event_sha256"]))
    if to_state == "SEALED":
        updated["sealed_commit_sha"] = transition_evidence["sealed_commit_sha"]
    if to_state == "PROMOTED":
        updated["promotion"] = transition_evidence
    if to_state in {"DISCARDED", "EXPIRED"}:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"{to_state} requires a terminal reason")
        updated["terminal_reason"] = reason.strip()[:256]
    updated["envelope_sha256"] = envelope_digest(updated)
    return updated


def _validate_promotion(envelope: Mapping[str, Any], evidence: Mapping[str, Any]) -> None:
    if set(evidence) != PROMOTION_FIELDS:
        raise ValueError("promotion evidence fields must match the promotion contract exactly")
    for field in ("tests_passed", "review_approved", "policy_rechecked", "isolation_verified"):
        if evidence.get(field) is not True:
            raise ValueError(f"promotion requires {field}=true")
    if _sha256(evidence.get("approved_target_sha256"), "approved_target_sha256") != envelope["execution_target_sha256"]:
        raise ValueError("promotion target does not match the execution envelope")
    if _git_oid(evidence.get("sealed_commit_sha"), "sealed_commit_sha") != envelope["sealed_commit_sha"]:
        raise ValueError("promotion sealed commit does not match the sealed envelope")
    durable_ref = _identifier(evidence.get("durable_ref"), "durable_ref")
    if durable_ref.startswith("refs/ephemeral/"):
        raise ValueError("promotion durable_ref cannot remain in the ephemeral namespace")


def verify_envelope(envelope: Mapping[str, Any], *, now: int | None = None, allow_expired: bool = False) -> dict[str, Any]:
    if not isinstance(envelope, Mapping) or envelope.get("version") != VERSION:
        raise ValueError(f"envelope.version must be {VERSION}")
    candidate = copy.deepcopy(dict(envelope))
    if set(candidate) != ENVELOPE_FIELDS:
        raise ValueError("envelope fields must match the contract exactly")
    if candidate.get("envelope_sha256") != envelope_digest(candidate):
        raise ValueError("envelope digest mismatch")
    namespace = _identifier(candidate.get("namespace"), "namespace", 64)
    run_id = _identifier(candidate.get("run_id"), "run_id")
    _identifier(candidate.get("envelope_id"), "envelope_id")
    _identifier(candidate.get("base_ref"), "base_ref")
    _git_oid(candidate.get("base_commit_sha"), "base_commit_sha")
    _sha256(candidate.get("policy_bundle_sha256"), "policy_bundle_sha256")
    _sha256(candidate.get("execution_target_sha256"), "execution_target_sha256")
    _identifier(candidate.get("permit_id"), "permit_id")
    _identifier(candidate.get("replay_id"), "replay_id")
    if candidate.get("ephemeral_ref") != f"refs/ephemeral/{namespace}/{run_id}":
        raise ValueError("ephemeral_ref does not match namespace and run_id")
    created_at = _timestamp(candidate.get("created_at"), "created_at")
    expires_at = _timestamp(candidate.get("expires_at"), "expires_at")
    if not created_at < expires_at <= created_at + 1_209_600:
        raise ValueError("envelope expiration must be after creation and within 14 days")
    state = candidate.get("state")
    if state not in set(TRANSITIONS) | TERMINAL_STATES:
        raise ValueError("envelope state is invalid")
    containment = candidate.get("containment")
    if not isinstance(containment, dict) or set(containment) != CONTAINMENT_FIELDS:
        raise ValueError("containment fields must match the contract exactly")
    if containment.get("direct_durable_writes") is not False:
        raise ValueError("ephemeral envelopes must prohibit direct durable writes")
    _identifier(containment.get("network_mode"), "containment.network_mode", 64)
    _identifier(containment.get("credential_scope"), "containment.credential_scope", 64)
    scope_units = containment.get("max_scope_units")
    if isinstance(scope_units, bool) or not isinstance(scope_units, int) or scope_units < 1:
        raise ValueError("containment.max_scope_units must be a positive integer")
    events = candidate.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("envelope requires an event chain")
    prior = None
    prior_state = None
    prior_at = None
    for index, event in enumerate(events):
        if not isinstance(event, dict) or set(event) != EVENT_FIELDS:
            raise ValueError("envelope event fields must match the contract exactly")
        material = {key: value for key, value in event.items() if key != "event_sha256"}
        if event.get("prior_event_sha256") != prior or event.get("event_sha256") != canonical_digest(material):
            raise ValueError(f"event chain mismatch at index {index}")
        _sha256(event.get("evidence_sha256"), f"events[{index}].evidence_sha256")
        event_at = _timestamp(event.get("at"), f"events[{index}].at")
        if prior_at is not None and event_at < prior_at:
            raise ValueError(f"event timestamp moved backward at index {index}")
        if index == 0:
            if event.get("from_state") is not None or event.get("to_state") != "CREATED":
                raise ValueError("event chain must begin with envelope creation")
        elif event.get("from_state") != prior_state or event.get("to_state") not in TRANSITIONS.get(prior_state, set()):
            raise ValueError(f"invalid event transition at index {index}")
        prior = event["event_sha256"]
        prior_state = event["to_state"]
        prior_at = event_at
    if events[-1].get("to_state") != candidate.get("state"):
        raise ValueError("envelope state does not match its event chain")
    promotion = candidate.get("promotion")
    sealed_commit = candidate.get("sealed_commit_sha")
    terminal_reason = candidate.get("terminal_reason")
    if state in {"SEALED", "PROMOTED"}:
        _git_oid(sealed_commit, "sealed_commit_sha")
        sealed_events = [event for event in events if event.get("to_state") == "SEALED"]
        if len(sealed_events) != 1 or sealed_events[0]["evidence_sha256"] != canonical_digest(
            {"sealed_commit_sha": sealed_commit}
        ):
            raise ValueError("sealed commit does not match its lifecycle evidence")
    elif sealed_commit is not None:
        raise ValueError("unsealed envelope cannot contain a sealed commit")
    if state == "PROMOTED":
        if not isinstance(promotion, Mapping):
            raise ValueError("promoted envelope requires promotion evidence")
        _validate_promotion(candidate, promotion)
    elif promotion is not None:
        raise ValueError("non-promoted envelope cannot contain promotion evidence")
    if state in {"DISCARDED", "EXPIRED"}:
        if not isinstance(terminal_reason, str) or not terminal_reason.strip():
            raise ValueError("discarded or expired envelope requires a terminal reason")
    elif terminal_reason is not None:
        raise ValueError("non-terminal envelope cannot contain a terminal reason")
    if now is not None and _timestamp(now, "now") >= _timestamp(candidate.get("expires_at"), "expires_at"):
        if not allow_expired and candidate.get("state") not in TERMINAL_STATES:
            raise ValueError("execution envelope expired")
    return candidate

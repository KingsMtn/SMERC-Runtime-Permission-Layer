from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping


AGENT_IDENTITY_VERSION = "smerc.agent-identity.v1"

AGENT_TYPES = {
    "llm_agent",
    "workflow_bot",
    "service_account",
    "automation_runner",
    "human_operator",
    "unknown",
}
TRUST_TIER_SCORE = {
    "unverified": 0.20,
    "sandbox": 0.45,
    "standard": 0.65,
    "trusted": 0.80,
    "critical": 0.90,
}
AUTONOMY_ORDER = {
    "observe": 0,
    "recommend": 1,
    "constrain": 2,
    "execute": 3,
}
CREDENTIAL_SCOPE_ORDER = {
    "none": 0,
    "read_only": 1,
    "scoped_write": 2,
    "production_write": 3,
    "financial_or_destructive": 4,
}
SIDE_EFFECT_MIN_SCOPE = {
    "none": "none",
    "internal": "read_only",
    "external": "production_write",
    "financial": "financial_or_destructive",
    "destructive": "financial_or_destructive",
}


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    agent_name: str
    agent_type: str
    provider: str
    owner_team: str
    trust_tier: str
    authorized_tool_families: tuple[str, ...]
    max_autonomy_level: str
    credential_scope: str
    recent_denials: int = 0
    recent_overrides: int = 0
    recent_success_rate: float = 1.0
    model: str | None = None
    last_reviewed_at: str | None = None
    context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AgentIdentity":
        required = {
            "version",
            "agent_id",
            "agent_name",
            "agent_type",
            "provider",
            "owner_team",
            "trust_tier",
            "authorized_tool_families",
            "max_autonomy_level",
            "credential_scope",
            "recent_denials",
            "recent_overrides",
            "recent_success_rate",
            "model",
            "last_reviewed_at",
            "context",
        }
        _exact_fields(payload, required, "agent_identity")
        if payload["version"] != AGENT_IDENTITY_VERSION:
            raise ValueError(f"agent_identity.version must be {AGENT_IDENTITY_VERSION}")

        agent_type = _identifier(payload["agent_type"], "agent_identity.agent_type", 48)
        if agent_type not in AGENT_TYPES:
            raise ValueError(f"agent_identity.agent_type must be one of {sorted(AGENT_TYPES)}")
        trust_tier = _identifier(payload["trust_tier"], "agent_identity.trust_tier", 48)
        if trust_tier not in TRUST_TIER_SCORE:
            raise ValueError(f"agent_identity.trust_tier must be one of {sorted(TRUST_TIER_SCORE)}")
        autonomy = _identifier(payload["max_autonomy_level"], "agent_identity.max_autonomy_level", 48)
        if autonomy not in AUTONOMY_ORDER:
            raise ValueError(f"agent_identity.max_autonomy_level must be one of {sorted(AUTONOMY_ORDER)}")
        credential_scope = _identifier(payload["credential_scope"], "agent_identity.credential_scope", 64)
        if credential_scope not in CREDENTIAL_SCOPE_ORDER:
            raise ValueError(
                f"agent_identity.credential_scope must be one of {sorted(CREDENTIAL_SCOPE_ORDER)}"
            )

        model = payload["model"]
        if model is not None:
            model = _text(model, "agent_identity.model", 160)
        last_reviewed_at = payload["last_reviewed_at"]
        if last_reviewed_at is not None:
            last_reviewed_at = _text(last_reviewed_at, "agent_identity.last_reviewed_at", 80)
        context = payload["context"]
        if not isinstance(context, dict):
            raise TypeError("agent_identity.context must be an object")

        return cls(
            agent_id=_identifier(payload["agent_id"], "agent_identity.agent_id", 128),
            agent_name=_text(payload["agent_name"], "agent_identity.agent_name", 160),
            agent_type=agent_type,
            provider=_text(payload["provider"], "agent_identity.provider", 120),
            owner_team=_text(payload["owner_team"], "agent_identity.owner_team", 120),
            trust_tier=trust_tier,
            authorized_tool_families=tuple(
                _string_list(payload["authorized_tool_families"], "agent_identity.authorized_tool_families")
            ),
            max_autonomy_level=autonomy,
            credential_scope=credential_scope,
            recent_denials=_non_negative_int(payload["recent_denials"], "agent_identity.recent_denials"),
            recent_overrides=_non_negative_int(payload["recent_overrides"], "agent_identity.recent_overrides"),
            recent_success_rate=_score(payload["recent_success_rate"], "agent_identity.recent_success_rate"),
            model=model,
            last_reviewed_at=last_reviewed_at,
            context=dict(context),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": AGENT_IDENTITY_VERSION,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "provider": self.provider,
            "owner_team": self.owner_team,
            "trust_tier": self.trust_tier,
            "authorized_tool_families": list(self.authorized_tool_families),
            "max_autonomy_level": self.max_autonomy_level,
            "credential_scope": self.credential_scope,
            "recent_denials": self.recent_denials,
            "recent_overrides": self.recent_overrides,
            "recent_success_rate": self.recent_success_rate,
            "model": self.model,
            "last_reviewed_at": self.last_reviewed_at,
            "context": dict(self.context),
        }


def evaluate_agent_identity(
    identity: Mapping[str, Any] | AgentIdentity | None,
    *,
    actor: str,
    requested_tool: str,
    requested_autonomy_level: str,
    requested_side_effect_level: str,
    required: bool = True,
) -> Dict[str, Any]:
    if identity is None:
        status = "FAIL" if required else "WATCH"
        return {
            "version": AGENT_IDENTITY_VERSION,
            "agent_id": actor,
            "status": status,
            "identity_score": 0.0 if required else 0.48,
            "trust_modifier": 0.75,
            "reason_codes": ["AGENT_IDENTITY_MISSING"],
            "recommended_controls": ["require_agent_identity_record", "route_to_human_review"],
            "plain_english_summary": f"Agent '{actor}' has no identity record for this request.",
        }

    agent = identity if isinstance(identity, AgentIdentity) else AgentIdentity.from_dict(identity)
    reasons: list[str] = []
    controls: list[str] = ["record_agent_identity", "retain_identity_evaluation"]
    score = TRUST_TIER_SCORE[agent.trust_tier]

    requested_autonomy_level = _identifier(
        requested_autonomy_level, "requested_autonomy_level", 48
    )
    requested_side_effect_level = _identifier(
        requested_side_effect_level, "requested_side_effect_level", 64
    )
    if requested_autonomy_level not in AUTONOMY_ORDER:
        raise ValueError(f"requested_autonomy_level must be one of {sorted(AUTONOMY_ORDER)}")
    if requested_side_effect_level not in SIDE_EFFECT_MIN_SCOPE:
        raise ValueError(f"requested_side_effect_level must be one of {sorted(SIDE_EFFECT_MIN_SCOPE)}")

    if agent.agent_id != actor:
        reasons.append("AGENT_ID_MISMATCH")
        controls.append("resolve_actor_identity_before_execution")
        score -= 0.25

    if not _tool_family_allowed(requested_tool, agent.authorized_tool_families, agent.trust_tier):
        reasons.append("TOOL_FAMILY_NOT_AUTHORIZED")
        controls.append("route_to_human_review")
        controls.append("deny_unlisted_tool_family")
        score -= 0.24

    if AUTONOMY_ORDER[requested_autonomy_level] > AUTONOMY_ORDER[agent.max_autonomy_level]:
        reasons.append("REQUESTED_AUTONOMY_EXCEEDS_AGENT_AUTHORITY")
        controls.append("cap_agent_to_authorized_autonomy")
        score -= 0.25

    required_scope = SIDE_EFFECT_MIN_SCOPE[requested_side_effect_level]
    if CREDENTIAL_SCOPE_ORDER[agent.credential_scope] < CREDENTIAL_SCOPE_ORDER[required_scope]:
        reasons.append("CREDENTIAL_SCOPE_TOO_WEAK_FOR_SIDE_EFFECT")
        controls.append("require_scoped_workload_credential")
        score -= 0.22

    if agent.trust_tier in {"unverified", "sandbox"} and requested_side_effect_level in {
        "external",
        "financial",
        "destructive",
    }:
        reasons.append("LOW_TRUST_AGENT_REQUESTS_HIGH_IMPACT_ACTION")
        controls.append("force_shadow_mode_or_manual_review")
        score -= 0.16

    if agent.recent_denials >= 3:
        reasons.append("RECENT_DENIAL_PATTERN")
        controls.append("inspect_recent_denial_history")
        score -= 0.10
    if agent.recent_overrides >= 3:
        reasons.append("RECENT_OVERRIDE_PATTERN")
        controls.append("inspect_override_history")
        score -= 0.08
    if agent.recent_success_rate < 0.75:
        reasons.append("LOW_RECENT_SUCCESS_RATE")
        controls.append("reduce_agent_autonomy_budget")
        score -= 0.12

    score = round(max(0.0, min(1.0, score)), 3)
    fail_reasons = {
        "AGENT_ID_MISMATCH",
        "TOOL_FAMILY_NOT_AUTHORIZED",
        "REQUESTED_AUTONOMY_EXCEEDS_AGENT_AUTHORITY",
        "CREDENTIAL_SCOPE_TOO_WEAK_FOR_SIDE_EFFECT",
        "LOW_TRUST_AGENT_REQUESTS_HIGH_IMPACT_ACTION",
    }
    if any(reason in fail_reasons for reason in reasons) or score < 0.50:
        status = "FAIL"
    elif score < 0.72 or reasons:
        status = "WATCH"
    else:
        status = "PASS"

    if status == "WATCH" and not reasons:
        reasons.append("AGENT_IDENTITY_REQUIRES_MONITORING")
    if status != "PASS":
        controls.append("preserve_identity_gate_reason_codes")
    trust_modifier = 1.04 if status == "PASS" and score >= 0.80 else (0.90 if status == "WATCH" else 0.75)

    return {
        "version": AGENT_IDENTITY_VERSION,
        "agent_id": agent.agent_id,
        "agent_name": agent.agent_name,
        "agent_type": agent.agent_type,
        "owner_team": agent.owner_team,
        "status": status,
        "identity_score": score,
        "trust_modifier": trust_modifier,
        "reason_codes": sorted(set(reasons)) or ["AGENT_IDENTITY_VERIFIED"],
        "recommended_controls": _dedupe(controls),
        "plain_english_summary": _summary(agent, requested_tool, requested_autonomy_level, requested_side_effect_level, status),
    }


def load_catalog(path: str | Path) -> Dict[str, AgentIdentity]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("agent identity catalog must be an object")
    agents = payload.get("agents")
    if not isinstance(agents, list):
        raise TypeError("agent identity catalog must contain an agents list")
    catalog: Dict[str, AgentIdentity] = {}
    for index, item in enumerate(agents):
        if not isinstance(item, dict):
            raise TypeError(f"agents[{index}] must be an object")
        agent = AgentIdentity.from_dict(item)
        if agent.agent_id in catalog:
            raise ValueError(f"duplicate agent_id: {agent.agent_id}")
        catalog[agent.agent_id] = agent
    return catalog


def _tool_family_allowed(tool: str, families: tuple[str, ...], trust_tier: str) -> bool:
    normalized = _text(tool, "requested_tool", 180).lower()
    family = normalized.split(".", 1)[0]
    allowed = {item.lower() for item in families}
    if normalized in allowed or family in allowed:
        return True
    if "*" in allowed and trust_tier in {"trusted", "critical"}:
        return True
    return False


def _summary(
    agent: AgentIdentity,
    tool: str,
    autonomy: str,
    side_effect: str,
    status: str,
) -> str:
    if status == "PASS":
        return (
            f"Agent '{agent.agent_id}' is verified for {autonomy} access to '{tool}' with "
            f"{side_effect} side-effect level under its current identity record."
        )
    if status == "WATCH":
        return (
            f"Agent '{agent.agent_id}' can be considered only with additional controls because its identity "
            f"record is incomplete, stale, or lower-confidence for '{tool}'."
        )
    return (
        f"Agent '{agent.agent_id}' should not execute this request until identity authority, tool family, "
        f"credential scope, or recent behavior concerns are resolved."
    )


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _exact_fields(value: Mapping[str, Any], fields: set[str], path: str) -> None:
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields)
    if missing:
        raise ValueError(f"{path} is missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TypeError(f"{path} must be a non-empty list")
    return [_identifier(item, f"{path}[{index}]", 120) for index, item in enumerate(value)]


def _identifier(value: Any, path: str, maximum: int) -> str:
    text = _text(value, path, maximum).lower()
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_-. *")
    if any(character not in allowed for character in text):
        raise ValueError(f"{path} may contain only letters, numbers, spaces, dots, underscores, and dashes")
    return text.replace(" ", "_")


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    text = value.strip()
    if len(text) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return text


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    if value < 0 or value > 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return float(value)


def _non_negative_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if value < 0:
        raise ValueError(f"{path} must be greater than or equal to zero")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a SMERC agent identity gate.")
    parser.add_argument("path", help="Path to one smerc.agent-identity.v1 JSON object.")
    parser.add_argument("--actor", required=True)
    parser.add_argument("--tool", required=True)
    parser.add_argument("--autonomy", default="execute")
    parser.add_argument("--side-effect", default="external")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("agents"), list):
        catalog = load_catalog(args.path)
        if args.actor not in catalog:
            raise ValueError(f"actor {args.actor} was not found in the agent identity catalog")
        payload = catalog[args.actor]
    result = evaluate_agent_identity(
        payload,
        actor=args.actor,
        requested_tool=args.tool,
        requested_autonomy_level=args.autonomy,
        requested_side_effect_level=args.side_effect,
    )
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

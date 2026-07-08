from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from reference_engine.policy import DEFAULT_POLICY, RuntimePolicy, load_policy


class RuntimePosture(str, Enum):
    ALLOW = "ALLOW"
    THROTTLE = "THROTTLE"
    FREEZE = "FREEZE"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


class EnforcementState(str, Enum):
    RELEASE = "release"
    CONSTRAIN = "constrain"
    PAUSE = "pause"
    BLOCK = "block"
    REVIEW = "review"


@dataclass(frozen=True)
class DomainProfile:
    profile_id: str
    label: str
    exposure_multiplier: float = 1.0
    capacity_multiplier: float = 1.0
    confidence_multiplier: float = 1.0
    stress_multiplier: float = 1.0
    authorization_multiplier: float = 1.0
    allow_external_side_effect_without_throttle: bool = False
    notes: tuple[str, ...] = ()


DOMAIN_PROFILES: Dict[str, DomainProfile] = {
    "general": DomainProfile("general", "General automated action"),
    "github_actions": DomainProfile(
        "github_actions",
        "GitHub Actions and software delivery",
        exposure_multiplier=1.03,
        stress_multiplier=1.04,
        notes=("Production delivery changes should preserve rollback and deployment evidence.",),
    ),
    "cloud_admin": DomainProfile(
        "cloud_admin",
        "Cloud administration",
        exposure_multiplier=1.08,
        capacity_multiplier=0.97,
        stress_multiplier=1.06,
        notes=("Cloud changes can widen blast radius quickly when containment is weak.",),
    ),
    "finance_ops": DomainProfile(
        "finance_ops",
        "Finance operations",
        exposure_multiplier=1.14,
        capacity_multiplier=0.92,
        confidence_multiplier=0.97,
        stress_multiplier=1.08,
        authorization_multiplier=0.96,
        notes=("Money movement and payment workflows require stronger recovery evidence.",),
    ),
    "security_ops": DomainProfile(
        "security_ops",
        "Security operations",
        exposure_multiplier=1.06,
        confidence_multiplier=0.96,
        stress_multiplier=1.10,
        notes=("Security automation may be urgent but can disrupt operations at scale.",),
    ),
    "customer_comms": DomainProfile(
        "customer_comms",
        "Customer communications",
        exposure_multiplier=1.12,
        capacity_multiplier=0.94,
        stress_multiplier=1.07,
        notes=("External communications are difficult to retract after release.",),
    ),
    "it_ops": DomainProfile(
        "it_ops",
        "IT operations",
        exposure_multiplier=1.04,
        stress_multiplier=1.05,
        notes=("Identity and endpoint actions need attention to rollback latency and scope.",),
    ),
}


@dataclass(frozen=True)
class RecoverabilityAction:
    action_id: str
    description: str
    actor: str
    tool: str
    action_type: str
    base_action_risk: float
    reversibility: float
    containment_strength: float
    rollback_latency: float
    evidence_validity: float
    anomaly_pressure: float
    impact_scope: float
    cancel_reliability: float
    authorization_confidence: float
    external_side_effect: bool
    sensitive_data: bool
    context: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RecoverabilityAction":
        required = [
            "action_id",
            "description",
            "actor",
            "tool",
            "action_type",
            "base_action_risk",
            "reversibility",
            "containment_strength",
            "rollback_latency",
            "evidence_validity",
            "anomaly_pressure",
            "impact_scope",
            "cancel_reliability",
            "authorization_confidence",
            "external_side_effect",
            "sensitive_data",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"Missing required recoverability field(s): {', '.join(missing)}")

        for key in ["action_id", "description", "actor", "tool", "action_type"]:
            if not isinstance(payload[key], str) or not payload[key].strip():
                raise TypeError(f"{key} must be a non-empty string")

        values: Dict[str, float] = {}
        for key in [
            "base_action_risk",
            "reversibility",
            "containment_strength",
            "rollback_latency",
            "evidence_validity",
            "anomaly_pressure",
            "impact_scope",
            "cancel_reliability",
            "authorization_confidence",
        ]:
            value = payload[key]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{key} must be a number between 0.0 and 1.0")
            if value < 0 or value > 1:
                raise ValueError(f"{key} must be between 0.0 and 1.0")
            values[key] = float(value)

        for key in ["external_side_effect", "sensitive_data"]:
            if not isinstance(payload[key], bool):
                raise TypeError(f"{key} must be a boolean")

        context = payload.get("context", {})
        if not isinstance(context, dict):
            raise TypeError("context must be an object when provided")

        return cls(
            action_id=payload["action_id"],
            description=payload["description"],
            actor=payload["actor"],
            tool=payload["tool"],
            action_type=payload["action_type"],
            base_action_risk=values["base_action_risk"],
            reversibility=values["reversibility"],
            containment_strength=values["containment_strength"],
            rollback_latency=values["rollback_latency"],
            evidence_validity=values["evidence_validity"],
            anomaly_pressure=values["anomaly_pressure"],
            impact_scope=values["impact_scope"],
            cancel_reliability=values["cancel_reliability"],
            authorization_confidence=values["authorization_confidence"],
            external_side_effect=payload["external_side_effect"],
            sensitive_data=payload["sensitive_data"],
            context=context,
        )


class RecoverabilityEngine:
    """Recoverability-aware runtime permission engine for automated actions."""

    def __init__(self, policy: RuntimePolicy = DEFAULT_POLICY, domain_profile: str = "general") -> None:
        self.policy = policy
        self.domain_profile = resolve_domain_profile(domain_profile)

    def evaluate(self, payload: Dict[str, Any] | RecoverabilityAction) -> Dict[str, Any]:
        action = payload if isinstance(payload, RecoverabilityAction) else RecoverabilityAction.from_dict(payload)
        profile = self._profile_for(action)
        trace = self._score_trace(action, profile)
        scores = trace["scores"]
        reason_codes = self._reason_codes(action, scores)
        posture, threshold_trace = self._posture(action, scores, profile)
        enforcement_state = self._enforcement_state(posture)
        controls = self._controls(action, posture, scores)
        transition_guidance = self._transition_guidance(action, posture, scores, controls)
        replay_id = (
            f"replay_{action.action_id}_{int(datetime.now(timezone.utc).timestamp() * 1000)}_"
            f"{uuid4().hex[:12]}"
        )
        summary = self._summary(action, posture, scores, controls)
        evaluated_at = datetime.now(timezone.utc).isoformat()
        policy_metadata = self.policy.decision_metadata()

        return {
            "action_id": action.action_id,
            "posture": posture.value,
            "enforcement_state": enforcement_state.value,
            "scores": {key: round(value, 3) for key, value in scores.items()},
            "reason_codes": reason_codes,
            "controls": controls,
            "domain_profile": profile_payload(profile),
            "decision_trace": {
                "profile": profile_payload(profile),
                "score_contributions": trace["score_contributions"],
                "threshold_trace": threshold_trace,
            },
            "transition_guidance": transition_guidance,
            "plain_english_summary": summary,
            "policy": policy_metadata,
            "replay_id": replay_id,
            "replay": {
                "replay_id": replay_id,
                "evaluated_at": evaluated_at,
                "actor": action.actor,
                "tool": action.tool,
                "action_type": action.action_type,
                "posture": posture.value,
                "enforcement_state": enforcement_state.value,
                "scores": {key: round(value, 3) for key, value in scores.items()},
                "reason_codes": reason_codes,
                "controls": controls,
                "domain_profile": profile_payload(profile),
                "decision_trace": {
                    "profile": profile_payload(profile),
                    "score_contributions": trace["score_contributions"],
                    "threshold_trace": threshold_trace,
                },
                "transition_guidance": transition_guidance,
                "policy": policy_metadata,
                "context": action.context,
            },
        }

    def _profile_for(self, action: RecoverabilityAction) -> DomainProfile:
        requested = action.context.get("domain_profile", self.domain_profile.profile_id)
        if requested is None:
            return self.domain_profile
        if not isinstance(requested, str):
            raise TypeError("context.domain_profile must be a string when provided")
        return resolve_domain_profile(requested)

    @staticmethod
    def _score_trace(action: RecoverabilityAction, profile: DomainProfile) -> Dict[str, Any]:
        irreversibility = 1 - action.reversibility
        rollback_risk = action.rollback_latency
        containment_gap = 1 - action.containment_strength
        cancel_gap = 1 - action.cancel_reliability
        evidence_gap = 1 - action.evidence_validity
        confidence_gap = 1 - action.authorization_confidence
        side_effect = 1.0 if action.external_side_effect else 0.0
        data_risk = 1.0 if action.sensitive_data else 0.0

        exposure_components = {
            "base_action_risk": action.base_action_risk * 0.18,
            "irreversibility": irreversibility * 0.24,
            "rollback_latency": rollback_risk * 0.17,
            "containment_gap": containment_gap * 0.13,
            "impact_scope": action.impact_scope * 0.12,
            "external_side_effect": side_effect * 0.08,
            "sensitive_data": data_risk * 0.08,
        }
        capacity_components = {
            "reversibility": action.reversibility * 0.31,
            "containment_strength": action.containment_strength * 0.24,
            "rollback_speed": (1 - action.rollback_latency) * 0.19,
            "cancel_reliability": action.cancel_reliability * 0.16,
            "evidence_validity": action.evidence_validity * 0.10,
        }
        confidence_components = {
            "evidence_validity": action.evidence_validity * 0.40,
            "authorization_confidence": action.authorization_confidence * 0.34,
            "anomaly_resistance": (1 - action.anomaly_pressure) * 0.18,
            "containment_strength": action.containment_strength * 0.08,
        }
        stress_components = {
            "base_action_risk": action.base_action_risk * 0.20,
            "anomaly_pressure": action.anomaly_pressure * 0.20,
            "impact_scope": action.impact_scope * 0.18,
            "evidence_gap": evidence_gap * 0.14,
            "confidence_gap": confidence_gap * 0.12,
            "rollback_latency": rollback_risk * 0.10,
            "cancel_gap": cancel_gap * 0.06,
        }

        irreversible_exposure = clamp(sum(exposure_components.values()) * profile.exposure_multiplier)
        reversible_capacity = clamp(sum(capacity_components.values()) * profile.capacity_multiplier)
        confidence_score = clamp(sum(confidence_components.values()) * profile.confidence_multiplier)
        operational_stress = clamp(sum(stress_components.values()) * profile.stress_multiplier)
        authorization_score = clamp(
            (
                reversible_capacity * 0.45
                + confidence_score * 0.30
                + (1 - irreversible_exposure) * 0.25
            )
            * profile.authorization_multiplier
        )
        scores = {
            "irreversible_exposure_score": irreversible_exposure,
            "reversible_capacity_score": reversible_capacity,
            "confidence_score": confidence_score,
            "operational_stress_score": operational_stress,
            "risk_adjusted_authorization_score": authorization_score,
            "cancel_reliability_score": action.cancel_reliability,
        }
        return {
            "scores": scores,
            "score_contributions": {
                "irreversible_exposure_score": round_components(exposure_components, profile.exposure_multiplier),
                "reversible_capacity_score": round_components(capacity_components, profile.capacity_multiplier),
                "confidence_score": round_components(confidence_components, profile.confidence_multiplier),
                "operational_stress_score": round_components(stress_components, profile.stress_multiplier),
                "risk_adjusted_authorization_score": {
                    "reversible_capacity": round(reversible_capacity * 0.45, 3),
                    "confidence_score": round(confidence_score * 0.30, 3),
                    "recoverability_margin": round((1 - irreversible_exposure) * 0.25, 3),
                    "profile_multiplier": profile.authorization_multiplier,
                    "total": round(authorization_score, 3),
                },
            },
        }

    @staticmethod
    def _scores(action: RecoverabilityAction) -> Dict[str, float]:
        return RecoverabilityEngine._score_trace(action, DOMAIN_PROFILES["general"])["scores"]

    @staticmethod
    def _reason_codes(action: RecoverabilityAction, scores: Dict[str, float]) -> List[str]:
        reasons: List[str] = []
        if scores["irreversible_exposure_score"] >= 0.68:
            reasons.append("IRREVERSIBLE_EXPOSURE_HIGH")
        elif scores["irreversible_exposure_score"] >= 0.48:
            reasons.append("IRREVERSIBLE_EXPOSURE_ELEVATED")
        if scores["reversible_capacity_score"] < 0.42:
            reasons.append("RECOVERY_CAPACITY_LOW")
        if action.rollback_latency >= 0.70:
            reasons.append("ROLLBACK_LATENCY_HIGH")
        if action.cancel_reliability < 0.45:
            reasons.append("CANCEL_RELIABILITY_WEAK")
        if action.containment_strength < 0.45:
            reasons.append("CONTAINMENT_WEAK")
        if action.evidence_validity < 0.50:
            reasons.append("EVIDENCE_VALIDITY_LOW")
        if action.authorization_confidence < 0.50:
            reasons.append("AUTHORIZATION_CONFIDENCE_LOW")
        if action.anomaly_pressure >= 0.65:
            reasons.append("ANOMALY_PRESSURE_HIGH")
        if action.impact_scope >= 0.70:
            reasons.append("IMPACT_SCOPE_WIDE")
        if action.external_side_effect:
            reasons.append("EXTERNAL_SIDE_EFFECT")
        if action.sensitive_data:
            reasons.append("SENSITIVE_DATA")
        return reasons or ["RECOVERABILITY_ACCEPTABLE"]

    def _posture(
        self,
        action: RecoverabilityAction,
        scores: Dict[str, float],
        profile: DomainProfile,
    ) -> tuple[RuntimePosture, List[Dict[str, Any]]]:
        exposure = scores["irreversible_exposure_score"]
        capacity = scores["reversible_capacity_score"]
        confidence = scores["confidence_score"]
        auth = scores["risk_adjusted_authorization_score"]
        stress = scores["operational_stress_score"]
        policy = self.policy.thresholds
        trace = [
            threshold_step(
                "deny_by_exposure_and_low_recovery_or_confidence",
                exposure,
                f">= {policy.deny_exposure_min}",
                exposure >= policy.deny_exposure_min
                and (capacity < policy.deny_capacity_max or confidence < policy.deny_confidence_max),
                {
                    "capacity": round(capacity, 3),
                    "capacity_rule": f"< {policy.deny_capacity_max}",
                    "confidence": round(confidence, 3),
                    "confidence_rule": f"< {policy.deny_confidence_max}",
                },
            ),
            threshold_step(
                "deny_by_unreliable_cancel_and_high_exposure",
                action.cancel_reliability,
                f"< {policy.deny_cancel_reliability_max}",
                action.cancel_reliability < policy.deny_cancel_reliability_max
                and exposure >= policy.deny_cancel_exposure_min,
                {"exposure": round(exposure, 3), "exposure_rule": f">= {policy.deny_cancel_exposure_min}"},
            ),
            threshold_step(
                "escalate_by_operational_stress",
                stress,
                f">= {policy.escalate_stress_min}",
                stress >= policy.escalate_stress_min and (action.external_side_effect or action.sensitive_data),
                {"external_side_effect": action.external_side_effect, "sensitive_data": action.sensitive_data},
            ),
            threshold_step(
                "freeze_by_low_confidence_or_capacity",
                min(confidence, capacity),
                f"confidence < {policy.freeze_confidence_max} or capacity < {policy.freeze_capacity_max}",
                confidence < policy.freeze_confidence_max or capacity < policy.freeze_capacity_max,
                {"confidence": round(confidence, 3), "capacity": round(capacity, 3)},
            ),
            threshold_step(
                "throttle_by_authorization_exposure_or_side_effect",
                auth,
                f"authorization < {policy.throttle_authorization_min} or exposure >= {policy.throttle_exposure_min}",
                auth < policy.throttle_authorization_min
                or exposure >= policy.throttle_exposure_min
                or (action.external_side_effect and not profile.allow_external_side_effect_without_throttle),
                {
                    "exposure": round(exposure, 3),
                    "external_side_effect": action.external_side_effect,
                    "profile_allows_external_side_effect_release": profile.allow_external_side_effect_without_throttle,
                },
            ),
        ]

        if trace[0]["triggered"]:
            return RuntimePosture.DENY, trace
        if trace[1]["triggered"]:
            return RuntimePosture.DENY, trace
        if trace[2]["triggered"]:
            return RuntimePosture.ESCALATE, trace
        if trace[3]["triggered"]:
            return RuntimePosture.FREEZE, trace
        if trace[4]["triggered"]:
            return RuntimePosture.THROTTLE, trace
        return RuntimePosture.ALLOW, trace

    @staticmethod
    def _enforcement_state(posture: RuntimePosture) -> EnforcementState:
        return {
            RuntimePosture.ALLOW: EnforcementState.RELEASE,
            RuntimePosture.THROTTLE: EnforcementState.CONSTRAIN,
            RuntimePosture.FREEZE: EnforcementState.PAUSE,
            RuntimePosture.DENY: EnforcementState.BLOCK,
            RuntimePosture.ESCALATE: EnforcementState.REVIEW,
        }[posture]

    @staticmethod
    def _controls(action: RecoverabilityAction, posture: RuntimePosture, scores: Dict[str, float]) -> List[str]:
        if posture == RuntimePosture.ALLOW:
            return ["execute", "record_replay", "retain_cancel_handle"]
        if posture == RuntimePosture.THROTTLE:
            controls = ["limit_scope", "preview_before_execution", "record_replay"]
            if action.rollback_latency >= 0.45:
                controls.append("require_rollback_plan")
            if action.external_side_effect:
                controls.append("rate_limit_external_side_effect")
            if scores["reversible_capacity_score"] < 0.60:
                controls.append("checkpoint_before_execution")
            return controls
        if posture == RuntimePosture.FREEZE:
            return ["pause_execution", "collect_more_evidence", "snapshot_current_state", "preserve_replay"]
        if posture == RuntimePosture.DENY:
            return ["block_execution", "explain_denial", "preserve_replay", "require_new_request"]
        return ["route_to_accountable_reviewer", "require_explicit_approval", "preserve_replay", "document_override_if_approved"]

    @staticmethod
    def _summary(
        action: RecoverabilityAction,
        posture: RuntimePosture,
        scores: Dict[str, float],
        controls: List[str],
    ) -> str:
        return (
            f"Action '{action.action_id}' received {posture.value}. "
            f"Irreversible exposure is {scores['irreversible_exposure_score']:.3f}, "
            f"reversible capacity is {scores['reversible_capacity_score']:.3f}, and "
            f"authorization score is {scores['risk_adjusted_authorization_score']:.3f}. "
            f"Controls: {', '.join(controls)}."
        )

    def _transition_guidance(
        self,
        action: RecoverabilityAction,
        posture: RuntimePosture,
        scores: Dict[str, float],
        controls: List[str],
    ) -> Dict[str, Any]:
        policy = self.policy.thresholds
        blockers: List[str] = []
        evidence_needed: List[str] = []
        control_improvements: List[str] = []
        if scores["irreversible_exposure_score"] >= policy.throttle_exposure_min:
            blockers.append("irreversible_exposure_above_release_threshold")
            control_improvements.extend(["narrow_impact_scope", "increase_containment", "prove_rollback_path"])
        if scores["reversible_capacity_score"] < 0.60:
            blockers.append("reversible_capacity_incomplete")
            evidence_needed.append("rollback test or recovery evidence")
        if scores["confidence_score"] < 0.70:
            blockers.append("confidence_below_release_target")
            evidence_needed.append("stronger authorization and evidence validity")
        if action.external_side_effect:
            control_improvements.append("rate limit or stage external side effect")
        if action.sensitive_data:
            control_improvements.append("data minimization or scoped export proof")
        if action.cancel_reliability < 0.70:
            control_improvements.append("reliable cancellation handle")

        next_posture = "ALLOW" if posture == RuntimePosture.ALLOW else "THROTTLE"
        if posture in {RuntimePosture.DENY, RuntimePosture.FREEZE, RuntimePosture.ESCALATE}:
            next_posture = "THROTTLE"
        return {
            "current_posture": posture.value,
            "target_posture": next_posture,
            "release_conditions": {
                "irreversible_exposure_below": policy.throttle_exposure_min,
                "authorization_score_at_or_above": policy.throttle_authorization_min,
                "confidence_score_target": 0.70,
                "reversible_capacity_target": 0.60,
            },
            "blocking_factors": sorted(set(blockers)),
            "evidence_needed": sorted(set(evidence_needed)),
            "control_improvements": sorted(set(control_improvements + controls)),
        }


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def resolve_domain_profile(profile_id: str) -> DomainProfile:
    if profile_id not in DOMAIN_PROFILES:
        raise ValueError(f"Unknown SMERC domain profile: {profile_id}")
    return DOMAIN_PROFILES[profile_id]


def profile_payload(profile: DomainProfile) -> Dict[str, Any]:
    return {
        "profile_id": profile.profile_id,
        "label": profile.label,
        "notes": list(profile.notes),
    }


def round_components(components: Dict[str, float], multiplier: float) -> Dict[str, Any]:
    payload: Dict[str, Any] = {key: round(value, 3) for key, value in components.items()}
    payload["profile_multiplier"] = multiplier
    payload["total"] = round(clamp(sum(components.values()) * multiplier), 3)
    return payload


def threshold_step(
    name: str,
    observed: float,
    rule: str,
    triggered: bool,
    details: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "rule": name,
        "observed": round(observed, 3),
        "threshold": rule,
        "triggered": triggered,
        "details": details,
    }


def evaluate_action(
    payload: Dict[str, Any] | RecoverabilityAction,
    policy: RuntimePolicy = DEFAULT_POLICY,
    domain_profile: str = "general",
) -> Dict[str, Any]:
    return RecoverabilityEngine(policy, domain_profile).evaluate(payload)


def evaluate_batch(
    items: List[Dict[str, Any]],
    policy: RuntimePolicy = DEFAULT_POLICY,
    domain_profile: str = "general",
) -> List[Dict[str, Any]]:
    engine = RecoverabilityEngine(policy, domain_profile)
    return [engine.evaluate(item) for item in items]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate automated actions with the SMERC recoverability engine.")
    parser.add_argument("path", help="Path to a JSON action request or JSON list of requests.")
    parser.add_argument("--policy", type=Path, help="Optional SMERC policy bundle.")
    parser.add_argument("--domain-profile", default="general", help="Optional default domain profile.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()
    payload = json.loads(Path(args.path).read_text(encoding="utf-8"))
    policy = load_policy(args.policy) if args.policy else DEFAULT_POLICY
    result = (
        evaluate_batch(payload, policy, args.domain_profile)
        if isinstance(payload, list)
        else evaluate_action(payload, policy, args.domain_profile)
    )
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

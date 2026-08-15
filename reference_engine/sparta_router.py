from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Mapping, Optional


POSTURE_ROUTE = {
    "ALLOW": "release",
    "THROTTLE": "constrained_execution",
    "FREEZE": "pause_for_evidence",
    "DENY": "block",
    "ESCALATE": "accountable_review",
}

POSTURE_PERMIT_STATUS = {
    "ALLOW": "issued",
    "THROTTLE": "issued_with_constraints",
    "FREEZE": "withheld_pending_evidence",
    "DENY": "withheld_blocked",
    "ESCALATE": "withheld_pending_approval",
}


@dataclass(frozen=True)
class SpartaRouteReport:
    route_id: str
    permit_id: str
    posture: str
    route: str
    permit_status: str
    reviewer_path: List[str]
    required_controls: List[str]
    execution_boundaries: Dict[str, Any]
    mcp_context: Dict[str, Any]
    policy_context: Dict[str, Any]
    telemetry_context: Dict[str, Any]
    decision_artifact_hash: str
    route_signature: Optional[str]
    plain_english_summary: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "permit_id": self.permit_id,
            "posture": self.posture,
            "route": self.route,
            "permit_status": self.permit_status,
            "reviewer_path": list(self.reviewer_path),
            "required_controls": list(self.required_controls),
            "execution_boundaries": dict(self.execution_boundaries),
            "mcp_context": dict(self.mcp_context),
            "policy_context": dict(self.policy_context),
            "telemetry_context": dict(self.telemetry_context),
            "decision_artifact_hash": self.decision_artifact_hash,
            "route_signature": self.route_signature,
            "plain_english_summary": self.plain_english_summary,
            "created_at": self.created_at,
        }


class SpartaRouter:
    """Route SMERC decisions into constrained execution permits and review paths."""

    def __init__(self, signing_secret: Optional[str] = None) -> None:
        self.signing_secret = signing_secret

    def route(self, action: Mapping[str, Any], decision: Mapping[str, Any]) -> Dict[str, Any]:
        posture = str(decision.get("posture", "")).upper()
        if posture not in POSTURE_ROUTE:
            raise ValueError(f"Unsupported SMERC posture: {posture}")

        action_id = _required_str(action, "action_id")
        decision_hash = artifact_hash({"action": action, "decision": decision})
        route_id = f"sparta_route_{action_id}_{decision_hash[:12]}"
        permit_id = f"smerc_permit_{action_id}_{decision_hash[12:24]}"
        reviewer_path = self._reviewer_path(action, decision, posture)
        controls = self._required_controls(action, decision, posture)
        boundaries = self._execution_boundaries(action, decision, posture)
        mcp_context = self._mcp_context(action)
        policy_context = self._policy_context(action)
        telemetry_context = self._telemetry_context(action, decision, route_id)

        signature_payload = {
            "route_id": route_id,
            "permit_id": permit_id,
            "posture": posture,
            "route": POSTURE_ROUTE[posture],
            "decision_artifact_hash": decision_hash,
            "required_controls": controls,
            "execution_boundaries": boundaries,
        }
        signature = self._signature(signature_payload)

        report = SpartaRouteReport(
            route_id=route_id,
            permit_id=permit_id,
            posture=posture,
            route=POSTURE_ROUTE[posture],
            permit_status=POSTURE_PERMIT_STATUS[posture],
            reviewer_path=reviewer_path,
            required_controls=controls,
            execution_boundaries=boundaries,
            mcp_context=mcp_context,
            policy_context=policy_context,
            telemetry_context=telemetry_context,
            decision_artifact_hash=decision_hash,
            route_signature=signature,
            plain_english_summary=self._summary(action, posture, reviewer_path, controls),
        )
        return report.to_dict()

    @staticmethod
    def _reviewer_path(action: Mapping[str, Any], decision: Mapping[str, Any], posture: str) -> List[str]:
        if posture in {"ALLOW", "DENY"}:
            return []

        scores = decision.get("scores", {})
        path: List[str] = []
        if action.get("sensitive_data") or _score(scores, "irreversible_exposure_score") >= 0.68:
            path.append("security_architect")
        if action.get("external_side_effect") or action.get("action_type") in {"production_deploy", "cloud_admin"}:
            path.append("platform_engineering")
        if _score(scores, "operational_stress_score") >= 0.65:
            path.append("sre")
        if "finance" in str(action.get("action_type", "")).lower() or "fund" in str(action.get("tool", "")).lower():
            path.append("finance_risk_owner")
        if posture == "ESCALATE":
            path.append("accountable_human_sponsor")
        if not path:
            path.append("workflow_owner")
        return _dedupe(path)

    @staticmethod
    def _required_controls(action: Mapping[str, Any], decision: Mapping[str, Any], posture: str) -> List[str]:
        controls = list(decision.get("controls", []))
        if posture == "THROTTLE":
            controls.extend(["scope_bound_permit", "execution_window", "rollback_evidence_required"])
        elif posture == "FREEZE":
            controls.extend(["human_evidence_review", "no_execution_until_reissued", "state_snapshot_required"])
        elif posture == "ESCALATE":
            controls.extend(["named_approver_required", "override_reason_required", "dual_control_if_sensitive"])
        elif posture == "DENY":
            controls.extend(["new_request_required", "blocked_action_attestation"])
        else:
            controls.extend(["permit_recorded", "trace_decision"])

        if _mcp_context(action):
            controls.append("mcp_tool_call_intercepted")
        if action.get("external_side_effect"):
            controls.append("side_effect_boundary_recorded")
        return _dedupe(controls)

    @staticmethod
    def _execution_boundaries(action: Mapping[str, Any], decision: Mapping[str, Any], posture: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        context = action.get("context", {}) if isinstance(action.get("context", {}), dict) else {}
        if posture == "ALLOW":
            expires_at = now + timedelta(minutes=30)
            max_scope = context.get("resource_scope", "requested_scope")
        elif posture == "THROTTLE":
            expires_at = now + timedelta(minutes=15)
            max_scope = context.get("constrained_scope", "reduced_scope_only")
        else:
            expires_at = now + timedelta(minutes=5)
            max_scope = "no_execution_without_new_decision"

        return {
            "permit_expires_at": expires_at.isoformat(),
            "max_execution_scope": max_scope,
            "requires_human_before_execution": posture in {"FREEZE", "ESCALATE"},
            "execution_blocked": posture == "DENY",
            "rollback_plan": context.get("rollback_plan", "required_if_external_side_effect"),
            "idempotent_replay_required": True,
        }

    @staticmethod
    def _mcp_context(action: Mapping[str, Any]) -> Dict[str, Any]:
        return _mcp_context(action)

    @staticmethod
    def _policy_context(action: Mapping[str, Any]) -> Dict[str, Any]:
        context = action.get("context", {}) if isinstance(action.get("context", {}), dict) else {}
        return {
            "opa_policy_id": context.get("opa_policy_id"),
            "cedar_policy_id": context.get("cedar_policy_id"),
            "iam_authorization": context.get("iam_authorization"),
            "policy_version": context.get("policy_version"),
            "smerc_boundary": "SMERC evaluates recoverability after authorization and before execution.",
        }

    @staticmethod
    def _telemetry_context(action: Mapping[str, Any], decision: Mapping[str, Any], route_id: str) -> Dict[str, Any]:
        context = action.get("context", {}) if isinstance(action.get("context", {}), dict) else {}
        return {
            "trace_id": context.get("trace_id"),
            "span_id": context.get("span_id"),
            "agent_invocation_id": context.get("agent_invocation_id"),
            "tool_execution_span": context.get("tool_execution_span"),
            "smerc_replay_id": decision.get("replay_id"),
            "sparta_route_id": route_id,
            "otel_semantic_target": "gen_ai.agent.tool_execution",
        }

    def _signature(self, payload: Mapping[str, Any]) -> Optional[str]:
        if not self.signing_secret:
            return None
        canonical = canonical_json(payload).encode("utf-8")
        return hmac.new(self.signing_secret.encode("utf-8"), canonical, hashlib.sha256).hexdigest()

    @staticmethod
    def _summary(
        action: Mapping[str, Any],
        posture: str,
        reviewer_path: List[str],
        controls: List[str],
    ) -> str:
        route = POSTURE_ROUTE[posture]
        reviewers = ", ".join(reviewer_path) if reviewer_path else "no reviewer required"
        return (
            f"SPARTa converted SMERC posture {posture} for action '{action.get('action_id')}' "
            f"into route '{route}'. Reviewer path: {reviewers}. "
            f"Required controls: {', '.join(controls)}."
        )


def artifact_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def route_decision(
    action: Mapping[str, Any],
    decision: Mapping[str, Any],
    signing_secret: Optional[str] = None,
) -> Dict[str, Any]:
    return SpartaRouter(signing_secret=signing_secret).route(action, decision)


def _score(scores: Mapping[str, Any], key: str) -> float:
    value = scores.get(key, 0.0)
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _mcp_context(action: Mapping[str, Any]) -> Dict[str, Any]:
    context = action.get("context", {}) if isinstance(action.get("context", {}), dict) else {}
    tool_server = context.get("tool_server")
    protocol = context.get("protocol")
    if protocol != "mcp" and not tool_server:
        return {}
    return {
        "protocol": "mcp",
        "tool_server": tool_server,
        "tool_name": context.get("tool_name", action.get("tool")),
        "requested_operation": context.get("requested_operation", action.get("action_type")),
        "resource_scope": context.get("resource_scope"),
        "agent_identity": context.get("agent_identity", action.get("actor")),
        "human_sponsor": context.get("human_sponsor"),
        "delegated_authority": context.get("delegated_authority"),
        "authority_expiration": context.get("authority_expiration"),
    }


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    output: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a SPARTa route report for a SMERC decision.")
    parser.add_argument("action_path", help="Path to the original action JSON.")
    parser.add_argument("decision_path", help="Path to the SMERC decision JSON.")
    parser.add_argument("--signing-secret", help="Optional HMAC secret for route signatures.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    action = load_json_file(args.action_path)
    decision = load_json_file(args.decision_path)
    report = route_decision(action, decision, signing_secret=args.signing_secret)
    print(json.dumps(report, indent=2 if args.pretty else None))


def load_json_file(path: str) -> Dict[str, Any]:
    last_error: Optional[Exception] = None
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            with open(path, "r", encoding=encoding) as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                raise TypeError(f"{path} must contain one JSON object")
            return payload
        except UnicodeError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    raise ValueError(f"Unable to load JSON file: {path}")


if __name__ == "__main__":
    main()

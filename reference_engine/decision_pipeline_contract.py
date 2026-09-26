from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from reference_engine.agent_permission_layer import evaluate_action
from reference_engine.authorization_afterlife_evidence_intake import validate_manifest
from reference_engine.authorization_afterlife_pilot_runner import evaluate_evidence_record


VERSION = "smerc.decision-pipeline-contract.v1"
HARD_GATES = (
    "identity_valid",
    "delegation_valid",
    "authority_current",
    "recovery_capability_present",
    "evidence_non_secret",
)
EXECUTION_ELIGIBLE_POSTURES = {"ALLOW", "THROTTLE"}


def evaluate_pipeline(payload: Mapping[str, Any]) -> dict[str, Any]:
    root = _validate_payload(payload)
    failed_gates = [name for name in HARD_GATES if not root["hard_gates"][name]]
    stages: list[dict[str, Any]] = [{
        "stage": "HARD_ADMISSION",
        "status": "FAILED" if failed_gates else "PASSED",
        "failed_gates": failed_gates,
        "non_overridable": True,
    }]
    if failed_gates:
        return _result(root, stages, final_decision="DENY", scoring=None, settlement=None,
                       controls=["reject_action", "preserve_evidence", "issue_new_request_after_remediation"])

    scoring = evaluate_action(root["action"])
    stages.append({
        "stage": "RECOVERABILITY_SCORING",
        "status": "COMPLETED",
        "posture": scoring["posture"],
        "risk_score": scoring["risk_score"],
        "mathematical": True,
    })
    eligible = scoring["posture"] in EXECUTION_ELIGIBLE_POSTURES
    controls = list(scoring["constraints"])
    stages.append({
        "stage": "EXECUTION_ROUTING",
        "status": "ROUTED" if eligible else "HELD",
        "controls": controls,
        "execution_eligible": eligible,
    })
    if not eligible:
        return _result(root, stages, final_decision=scoring["posture"], scoring=scoring,
                       settlement=None, controls=controls)

    evidence_record = validate_manifest(root["consequence_manifest"])["records"][0]
    settlement = evaluate_evidence_record(evidence_record)
    stages.append({
        "stage": "CONSEQUENCE_TIME_RECONCILIATION",
        "status": "COMPLETED",
        "decision": settlement["decision"],
        "should_commit": settlement["should_commit"],
        "non_overridable_by_score": True,
    })
    stages.append({
        "stage": "SETTLEMENT",
        "status": "COMMITTED" if settlement["decision"] == "SETTLE" else "WITHHELD",
        "decision": settlement["decision"],
        "required_actions": settlement["required_actions"],
    })
    return _result(root, stages, final_decision=settlement["decision"], scoring=scoring,
                   settlement=settlement, controls=controls + settlement["required_actions"])


def _result(
    root: Mapping[str, Any], stages: list[dict[str, Any]], *, final_decision: str,
    scoring: Mapping[str, Any] | None, settlement: Mapping[str, Any] | None,
    controls: list[str],
) -> dict[str, Any]:
    material = {"pipeline_id": root["pipeline_id"], "stages": stages, "final_decision": final_decision}
    digest = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()
    return {
        "version": VERSION,
        "pipeline_id": root["pipeline_id"],
        "final_decision": final_decision,
        "should_execute": bool(scoring and scoring["posture"] in EXECUTION_ELIGIBLE_POSTURES),
        "should_commit": bool(settlement and settlement["decision"] == "SETTLE"),
        "controls": sorted(set(controls)),
        "stages": stages,
        "scoring": dict(scoring) if scoring else None,
        "settlement": dict(settlement) if settlement else None,
        "pipeline_sha256": digest,
        "contract_rule": (
            "Hard gates cannot be overridden by mathematical scores, and execution eligibility cannot "
            "override consequence-time authority reconciliation or settlement requirements."
        ),
    }


def _validate_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TypeError("pipeline payload must be an object")
    required = {"version", "pipeline_id", "hard_gates", "action", "consequence_manifest"}
    missing = sorted(required - set(payload))
    unknown = sorted(set(payload) - required)
    if missing:
        raise ValueError(f"pipeline payload missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"pipeline payload contains unknown field(s): {', '.join(unknown)}")
    if payload["version"] != VERSION:
        raise ValueError(f"version must be {VERSION}")
    if not isinstance(payload["pipeline_id"], str) or not payload["pipeline_id"].strip():
        raise TypeError("pipeline_id must be a non-empty string")
    gates = payload["hard_gates"]
    if not isinstance(gates, dict) or set(gates) != set(HARD_GATES):
        raise ValueError("hard_gates must contain exactly the declared pipeline gates")
    if any(not isinstance(value, bool) for value in gates.values()):
        raise TypeError("hard gate values must be booleans")
    validate_manifest(payload["consequence_manifest"])
    return dict(payload)

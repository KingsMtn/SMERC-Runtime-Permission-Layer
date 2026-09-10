from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from reference_engine.decision_language_conformance import check_decision


VERSION = "smerc.decision-language-emitter.v1"


def emit_decision(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a simple external-framework action summary into SMERC Decision Language."""
    source = _object(payload, "payload")
    risk = _object(source.get("risk"), "risk")
    recoverability = _object(source.get("recoverability"), "recoverability")
    evidence = _object(source.get("evidence"), "evidence")
    action_id = _text(source.get("action_id"), "action_id")

    scores = {
        "irreversible_exposure": _score(risk.get("irreversible_exposure"), "risk.irreversible_exposure"),
        "reversible_capacity": _score(risk.get("reversible_capacity"), "risk.reversible_capacity"),
        "authorization_confidence": _score(risk.get("authorization_confidence"), "risk.authorization_confidence"),
    }
    recovery = {
        "rollback_ready": _boolean(recoverability.get("rollback_ready"), "recoverability.rollback_ready"),
        "blast_radius_bounded": _boolean(recoverability.get("blast_radius_bounded"), "recoverability.blast_radius_bounded"),
        "evidence_sufficient": _boolean(recoverability.get("evidence_sufficient"), "recoverability.evidence_sufficient"),
        "containment_strength": _score(recoverability.get("containment_strength"), "recoverability.containment_strength"),
    }
    evidence_expectation = {
        "pre_execution": _string_list(evidence.get("pre_execution"), "evidence.pre_execution"),
        "postcondition": _string_list(evidence.get("postcondition"), "evidence.postcondition"),
        "review": _string_list(evidence.get("review"), "evidence.review"),
    }

    posture = _select_posture(scores, recovery)
    required_controls = _required_controls(posture, evidence_expectation)
    decision = {
        "language_version": "smerc.decision.v1",
        "action_language_version": "smerc.action.v1",
        "action_hash": _hash(source),
        "action_id": action_id,
        "posture": posture,
        "enforcement_state": _enforcement_state(posture),
        "route_state": _route_state(posture),
        "required_controls": required_controls,
        "recoverability": recovery,
        "scores": scores,
        "reasons": _reasons(posture, scores, recovery),
        "structured_controls": [{"code": code, "title": _title(code)} for code in required_controls],
        "evidence_expectation": evidence_expectation,
        "postcondition_expectation": {
            "must_preserve_replay": True,
            "must_record_execution": posture in {"ALLOW", "THROTTLE"},
            "must_report_missing_controls": True,
        },
        "transition": _transition(posture),
        "replay_id": f"{action_id}:smerc-decision-language",
        "replay": {
            "emitter_version": VERSION,
            "source_framework": _text(source.get("framework", "external-framework"), "framework"),
            "summary": _text(source.get("summary", "External framework emitted a SMERC-compatible decision."), "summary", 1024),
        },
    }
    conformance = check_decision(decision, source=action_id)
    if conformance["status"] != "pass":
        raise ValueError(f"emitted decision failed conformance: {conformance['errors']}")
    return decision


def load_payload(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_decision(decision: Dict[str, Any], output: Path | None) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _select_posture(scores: Dict[str, float], recovery: Dict[str, Any]) -> str:
    if scores["irreversible_exposure"] >= 0.85 or scores["authorization_confidence"] < 0.4:
        return "DENY"
    if scores["irreversible_exposure"] >= 0.68 and not recovery["blast_radius_bounded"]:
        return "ESCALATE"
    if scores["reversible_capacity"] < 0.45 or not recovery["evidence_sufficient"]:
        return "FREEZE" if scores["irreversible_exposure"] >= 0.62 else "THROTTLE"
    if scores["irreversible_exposure"] >= 0.45 or recovery["containment_strength"] < 0.75:
        return "THROTTLE"
    return "ALLOW"


def _required_controls(posture: str, evidence: Dict[str, List[str]]) -> List[str]:
    base = {
        "ALLOW": ["execute", "record_execution_report", "preserve_replay"],
        "THROTTLE": ["limit_scope", "record_execution_report", "preserve_replay"],
        "FREEZE": ["pause_execution", "collect_more_evidence", "snapshot_current_state", "preserve_replay"],
        "DENY": ["block_execution", "explain_denial", "preserve_replay", "require_new_request"],
        "ESCALATE": [
            "route_to_accountable_reviewer",
            "require_explicit_approval",
            "document_override_if_approved",
            "preserve_replay",
        ],
    }[posture]
    return sorted(set(base + evidence["pre_execution"] + evidence["postcondition"] + evidence["review"]))


def _reasons(posture: str, scores: Dict[str, float], recovery: Dict[str, Any]) -> List[Dict[str, str]]:
    reasons: List[str] = []
    if scores["irreversible_exposure"] >= 0.85:
        reasons.append("IRREVERSIBLE_EXPOSURE_HIGH")
    elif scores["irreversible_exposure"] >= 0.45:
        reasons.append("IRREVERSIBLE_EXPOSURE_ELEVATED")
    if scores["authorization_confidence"] < 0.5:
        reasons.append("AUTHORIZATION_CONFIDENCE_LOW")
    if scores["reversible_capacity"] < 0.5:
        reasons.append("RECOVERY_CAPACITY_LOW")
    if not recovery["evidence_sufficient"]:
        reasons.append("EVIDENCE_VALIDITY_LOW")
    if not recovery["blast_radius_bounded"]:
        reasons.append("IMPACT_SCOPE_WIDE")
    if not reasons:
        reasons.append("RECOVERABILITY_ACCEPTABLE")
    if posture == "ESCALATE" and "IMPACT_SCOPE_WIDE" not in reasons:
        reasons.append("IMPACT_SCOPE_WIDE")
    return [{"code": code, "title": _title(code)} for code in reasons]


def _transition(posture: str) -> Dict[str, Any]:
    if posture == "ALLOW":
        return {"mode": "maintain", "eligible_target_posture": "ALLOW", "requires_new_request": False, "conditions": []}
    if posture == "DENY":
        return {
            "mode": "conditional",
            "eligible_target_posture": None,
            "requires_new_request": True,
            "conditions": [
                {
                    "code": "MATERIAL_NEW_REQUEST_REQUIRED",
                    "field": "request.action_hash",
                    "operator": "changed",
                    "value": True,
                    "description": "Submit a materially new action request.",
                }
            ],
        }
    target = "ALLOW" if posture == "THROTTLE" else "THROTTLE"
    return {
        "mode": "conditional",
        "eligible_target_posture": target,
        "requires_new_request": False,
        "conditions": [
            {
                "code": "EVIDENCE_AND_RECOVERY_READY",
                "field": "recoverability",
                "operator": "restored",
                "value": True,
                "description": "Restore evidence, rollback, and containment conditions before relaxing posture.",
            }
        ],
    }


def _enforcement_state(posture: str) -> str:
    return {"ALLOW": "release", "THROTTLE": "constrain", "FREEZE": "pause", "DENY": "block", "ESCALATE": "review"}[posture]


def _route_state(posture: str) -> str:
    return {
        "ALLOW": "EXECUTE",
        "THROTTLE": "CONSTRAINED_EXECUTE",
        "FREEZE": "PAUSE",
        "DENY": "BLOCK",
        "ESCALATE": "REVIEW_REQUIRED",
    }[posture]


def _hash(value: Dict[str, Any]) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    return value


def _text(value: Any, path: str, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return value.strip()


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    if not 0 <= value <= 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return float(value)


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be boolean")
    return value


def _string_list(value: Any, path: str) -> List[str]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must be a string array")
    output = []
    for index, item in enumerate(value):
        output.append(_text(item, f"{path}[{index}]"))
    return output


def _title(code: str) -> str:
    return code.replace("_", " ").title()


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit a SMERC Decision Language artifact from a simple external-framework action summary.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    decision = emit_decision(load_payload(args.input))
    write_decision(decision, args.output)
    print(json.dumps(decision, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()


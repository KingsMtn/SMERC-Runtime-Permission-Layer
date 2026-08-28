from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.autonomy_budget import evaluate_autonomy_budget
from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger
from reference_engine.agent_identity import evaluate_agent_identity
from reference_engine.recoverability_engine import RecoverabilityEngine
from reference_engine.sparta_router import route_decision


CUSTOMER_EVALUATION_VERSION = "smerc.customer-evaluation.v1"
REF_GATE_FIELDS = {
    "typed_contract_valid",
    "attestation_valid",
    "least_privilege_confirmed",
    "object_shape_expected",
}
TOP_LEVEL_FIELDS = {
    "version",
    "tenant_id",
    "organization",
    "contact_role",
    "evaluation_date",
    "data_boundary",
    "workflow_context",
    "initial_autonomy_state",
    "actions",
}
OPTIONAL_TOP_LEVEL_FIELDS = {"agents"}
RECOVERABILITY_FIELDS = {
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
    "context",
}
ACTION_FIELDS = RECOVERABILITY_FIELDS | {"ref_gate", "tool_plan"}
PROHIBITED_KEY_FRAGMENTS = {
    "secret",
    "token",
    "password",
    "credential",
    "private_key",
    "wallet_key",
    "api_key",
    "raw_customer_record",
    "source_code",
    "production_log",
}


def load_payload(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("customer evaluation input must be a JSON object")
    return payload


def validate_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    _exact_fields(payload, TOP_LEVEL_FIELDS, "customer_evaluation", optional=OPTIONAL_TOP_LEVEL_FIELDS)
    if payload["version"] != CUSTOMER_EVALUATION_VERSION:
        raise ValueError(f"version must be {CUSTOMER_EVALUATION_VERSION}")
    actions = payload["actions"]
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")
    if len(actions) > 25:
        raise ValueError("actions must contain at most 25 items for a customer evaluation")
    parsed_actions = []
    seen = set()
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise TypeError(f"actions[{index}] must be an object")
        _reject_sensitive_keys(action, f"actions[{index}]")
        _exact_fields(action, ACTION_FIELDS, f"actions[{index}]")
        action_id = _text(action["action_id"], f"actions[{index}].action_id", 128)
        if action_id in seen:
            raise ValueError(f"duplicate action_id: {action_id}")
        seen.add(action_id)
        ref_gate = _ref_gate(action["ref_gate"], f"actions[{index}].ref_gate")
        if not isinstance(action["tool_plan"], dict):
            raise TypeError(f"actions[{index}].tool_plan must be an object")
        parsed = dict(action)
        parsed["action_id"] = action_id
        parsed["ref_gate"] = ref_gate
        parsed_actions.append(parsed)
    agents = payload.get("agents", [])
    if not isinstance(agents, list):
        raise TypeError("agents must be a list when provided")
    parsed_agents = {}
    for index, agent in enumerate(agents):
        if not isinstance(agent, dict):
            raise TypeError(f"agents[{index}] must be an object")
        parsed_agent = dict(agent)
        agent_id = _text(parsed_agent.get("agent_id"), f"agents[{index}].agent_id", 128)
        if agent_id in parsed_agents:
            raise ValueError(f"duplicate agent_id: {agent_id}")
        parsed_agents[agent_id] = parsed_agent

    return {
        "version": CUSTOMER_EVALUATION_VERSION,
        "tenant_id": _text(payload["tenant_id"], "tenant_id", 128),
        "organization": _text(payload["organization"], "organization", 160),
        "contact_role": _text(payload["contact_role"], "contact_role", 120),
        "evaluation_date": _text(payload["evaluation_date"], "evaluation_date", 40),
        "data_boundary": _text(payload["data_boundary"], "data_boundary", 1200),
        "workflow_context": _text(payload["workflow_context"], "workflow_context", 1200),
        "initial_autonomy_state": _text(payload["initial_autonomy_state"], "initial_autonomy_state", 64),
        "agents": parsed_agents,
        "actions": parsed_actions,
    }


def build_customer_evaluation(payload: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = validate_payload(payload)
    engine = RecoverabilityEngine()
    records: list[Dict[str, Any]] = []
    budget_inputs: list[Dict[str, Any]] = []
    postures: Counter[str] = Counter()
    routes: Counter[str] = Counter()
    ref_gate_statuses: Counter[str] = Counter()
    identity_gate_statuses: Counter[str] = Counter()

    for sequence, action in enumerate(parsed["actions"], start=1):
        ref_gate = _evaluate_ref_gate(action["ref_gate"])
        identity_gate = evaluate_agent_identity(
            parsed["agents"].get(action["actor"]),
            actor=action["actor"],
            requested_tool=action["tool"],
            requested_autonomy_level=_requested_autonomy(action),
            requested_side_effect_level=action["tool_plan"]["side_effect_level"],
            required=bool(parsed["agents"]),
        )
        scoring_admission = _scoring_admission(ref_gate, identity_gate)
        decision = engine.evaluate(_recoverability_payload(action))
        if ref_gate["status"] == "fail":
            decision = _cap_decision_for_ref_gate(decision, ref_gate)
        elif identity_gate["status"] == "FAIL":
            decision = _cap_decision_for_identity_gate(decision, identity_gate)
        route = route_decision(decision, action["tool_plan"])
        ledger = _build_ledger(
            tenant_id=parsed["tenant_id"],
            action=action,
            ref_gate=ref_gate,
            identity_gate=identity_gate,
            scoring_admission=scoring_admission,
            decision=decision,
            route=route,
        )
        postures[decision["posture"]] += 1
        routes[route["route_state"]] += 1
        ref_gate_statuses[ref_gate["status"]] += 1
        identity_gate_statuses[identity_gate["status"]] += 1
        pressure = _gateway_pressure(decision, ref_gate)
        budget_inputs.append(
            {
                "sequence": sequence,
                "request_id": action["action_id"],
                "tool_name": action["tool"],
                "posture": decision["posture"],
                "requested_scope_units": action["tool_plan"]["requested_scope_units"],
                "gateway_pressure": {"score": pressure},
                "ref_gate": {"status": ref_gate["status"]},
            }
        )
        records.append(
            {
                "sequence": sequence,
                "action_id": action["action_id"],
                "description": action["description"],
                "ref_gate": ref_gate,
                "identity_gate": identity_gate,
                "scoring_admission": scoring_admission,
                "decision": decision,
                "sparta_route": route,
                "decision_lifecycle_ledger": ledger.to_dict(),
            }
        )

    autonomy_budget = evaluate_autonomy_budget(
        decisions=budget_inputs,
        initial_state=parsed["initial_autonomy_state"],
    )
    summary = {
        "total_actions": len(records),
        "posture_counts": dict(sorted(postures.items())),
        "route_state_counts": dict(sorted(routes.items())),
        "ref_gate_counts": dict(sorted(ref_gate_statuses.items())),
        "identity_gate_counts": dict(sorted(identity_gate_statuses.items())),
        "non_executable_routes": sum(1 for record in records if not record["sparta_route"]["executable"]),
        "valid_ledgers": sum(
            1 for record in records if record["decision_lifecycle_ledger"]["verification"]["valid"]
        ),
        "highest_exposure_actions": [
            {
                "action_id": record["action_id"],
                "posture": record["decision"]["posture"],
                "route_state": record["sparta_route"]["route_state"],
                "irreversible_exposure_score": record["decision"]["scores"]["irreversible_exposure_score"],
            }
            for record in sorted(
                records,
                key=lambda item: item["decision"]["scores"]["irreversible_exposure_score"],
                reverse=True,
            )[:5]
        ],
        "autonomy_state": autonomy_budget["autonomy_state"],
    }
    pilot_fit = _pilot_fit(summary)
    return {
        "version": CUSTOMER_EVALUATION_VERSION,
        "generated_at": _now(),
        "tenant_id": parsed["tenant_id"],
        "organization": parsed["organization"],
        "contact_role": parsed["contact_role"],
        "evaluation_date": parsed["evaluation_date"],
        "workflow_context": parsed["workflow_context"],
        "data_boundary": parsed["data_boundary"],
        "evidence_boundary": (
            "This is a metadata-only customer evaluation. It proves local runtime coherence on supplied action "
            "metadata; it does not prove production safety, compliance, incident reduction, customer demand, "
            "or readiness to enforce in a live environment."
        ),
        "summary": summary,
        "pilot_fit": pilot_fit,
        "autonomy_budget": autonomy_budget,
        "records": records,
        "recommended_next_action": _recommended_next_action(pilot_fit),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# {report['organization']} SMERC Customer Evaluation Report",
        "",
        f"Version: `{report['version']}`",
        f"Generated: `{report['generated_at']}`",
        f"Contact role: `{report['contact_role']}`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Workflow Context",
        "",
        str(report["workflow_context"]),
        "",
        "## Summary",
        "",
        f"- Actions evaluated: `{summary['total_actions']}`",
        f"- Ref-gate counts: `{summary['ref_gate_counts']}`",
        f"- Agent identity-gate counts: `{summary['identity_gate_counts']}`",
        f"- Posture counts: `{summary['posture_counts']}`",
        f"- Route state counts: `{summary['route_state_counts']}`",
        f"- Non-executable routes: `{summary['non_executable_routes']}`",
        f"- Valid DLL ledgers: `{summary['valid_ledgers']}`",
        f"- Autonomy state: `{summary['autonomy_state']}`",
        f"- Pilot fit: `{report['pilot_fit']['fit']}`",
        f"- Fit reason: {report['pilot_fit']['reason']}",
        "",
        "## Highest Exposure Actions",
        "",
        "| Action | Posture | Route | Exposure |",
        "| --- | --- | --- | ---: |",
    ]
    for item in summary["highest_exposure_actions"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['posture']}` | `{item['route_state']}` | "
            f"{item['irreversible_exposure_score']} |"
        )
    lines.extend(
        [
            "",
            "## Decision Path",
            "",
            "| # | Action | Ref Gate | Scoring | Posture | SPARTa Route | Executable | DLL Valid |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| {record['sequence']} | `{record['action_id']}` | `{record['ref_gate']['status']}` | "
            f"`{record['scoring_admission']}` | `{record['decision']['posture']}` | "
            f"`{record['sparta_route']['route_state']}` | `{record['sparta_route']['executable']}` | "
            f"`{record['decision_lifecycle_ledger']['verification']['valid']}` |"
        )
    lines.extend(["", "## Action Details", ""])
    for record in report["records"]:
        decision = record["decision"]
        route = record["sparta_route"]
        lines.extend(
            [
                f"### {record['action_id']}",
                "",
                f"- Description: {record['description']}",
                f"- Ref gate: `{record['ref_gate']['status']}`",
                f"- Ref failures: `{record['ref_gate']['failures']}`",
                f"- Agent identity gate: `{record['identity_gate']['status']}`",
                f"- Agent identity reasons: `{record['identity_gate']['reason_codes']}`",
                f"- Scoring admission: `{record['scoring_admission']}`",
                f"- SMERC posture: `{decision['posture']}`",
                f"- Scores: `{decision['scores']}`",
                f"- Reason codes: `{decision['reason_codes']}`",
                f"- SPARTa route: `{route['route_state']}`",
                f"- Executable: `{route['executable']}`",
                f"- Applied controls: `{route['applied_controls']}`",
                f"- DLL valid: `{record['decision_lifecycle_ledger']['verification']['valid']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Autonomy Budget",
            "",
            f"- State: `{report['autonomy_budget']['autonomy_state']}`",
            f"- Spent: `{report['autonomy_budget']['spent']}`",
            f"- Review triggers: `{report['autonomy_budget']['review_triggers']}`",
            "",
            "## Recommended Next Action",
            "",
            str(report["recommended_next_action"]),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def _recoverability_payload(action: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: action[key] for key in RECOVERABILITY_FIELDS}


def _evaluate_ref_gate(ref_gate: Mapping[str, bool]) -> Dict[str, Any]:
    failures = [key for key in sorted(REF_GATE_FIELDS) if not ref_gate[key]]
    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "rule": "typed contract, attestation, least privilege, and object shape must pass before recoverability can support execution",
    }


def _scoring_admission(ref_gate: Mapping[str, Any], identity_gate: Mapping[str, Any]) -> str:
    if ref_gate["status"] == "fail":
        return "capped_by_ref_gate"
    if identity_gate["status"] == "FAIL":
        return "capped_by_agent_identity_gate"
    if identity_gate["status"] == "WATCH":
        return "admitted_with_agent_identity_watch"
    return "admitted"


def _cap_decision_for_ref_gate(decision: Mapping[str, Any], ref_gate: Mapping[str, Any]) -> Dict[str, Any]:
    capped = dict(decision)
    reason_codes = sorted(set(list(capped.get("reason_codes", [])) + [f"REF_GATE_{item.upper()}_FAILED" for item in ref_gate["failures"]]))
    capped["posture"] = "DENY"
    capped["enforcement_state"] = "block"
    capped["reason_codes"] = reason_codes
    capped["controls"] = ["block_execution", "preserve_replay", "repair_ref_gate_evidence", "require_new_request"]
    capped["plain_english_summary"] = (
        f"Action '{decision['action_id']}' was capped to DENY because hard Ref-gate evidence failed: "
        f"{', '.join(ref_gate['failures'])}."
    )
    return capped


def _cap_decision_for_identity_gate(decision: Mapping[str, Any], identity_gate: Mapping[str, Any]) -> Dict[str, Any]:
    capped = dict(decision)
    reason_codes = sorted(set(list(capped.get("reason_codes", [])) + list(identity_gate["reason_codes"])))
    capped["posture"] = "FREEZE"
    capped["enforcement_state"] = "pause"
    capped["reason_codes"] = reason_codes
    capped["controls"] = [
        "pause_agent_execution",
        "resolve_agent_identity",
        "preserve_replay",
        "require_human_review_before_execution",
    ]
    capped["plain_english_summary"] = (
        f"Action '{decision['action_id']}' was capped to FREEZE because agent identity admission failed: "
        f"{', '.join(identity_gate['reason_codes'])}."
    )
    return capped


def _build_ledger(
    *,
    tenant_id: str,
    action: Mapping[str, Any],
    ref_gate: Mapping[str, Any],
    identity_gate: Mapping[str, Any],
    scoring_admission: str,
    decision: Mapping[str, Any],
    route: Mapping[str, Any],
) -> DecisionLifecycleLedger:
    ledger = DecisionLifecycleLedger(f"customer_eval_{action['action_id']}", tenant_id=tenant_id)
    ledger.append(
        "REQUEST",
        str(action["actor"]),
        {
            "initiated_by": str(action["actor"]),
            "requested_operation": str(action["description"]),
            "environment": str(action.get("tool_plan", {}).get("metadata", {}).get("environment", "metadata_only_evaluation")),
            "risk_profile": str(action.get("context", {}).get("domain_profile", "general")),
        },
    )
    ledger.append(
        "EVIDENCE",
        "smerc-customer-evaluation",
        {
            "available_evidence": [
                "metadata_only_action",
                "ref_gate_declaration",
                "agent_identity_gate",
                "tool_plan_declaration",
            ],
            "confidence_score": float(decision["scores"]["confidence_score"]),
            "missing_evidence": _missing_evidence(ref_gate, identity_gate),
            "external_dependencies": [str(action["tool"])],
            "model_version": "customer-supplied-agent-metadata",
            "policy_version": str(decision.get("policy", {}).get("policy_id", "smerc.policy.v1")),
        },
    )
    ledger.append(
        "EVALUATION",
        "smerc-engine",
        {
            "structural_state": f"ref_gate={ref_gate['status']}; scoring={scoring_admission}; route={route['route_state']}",
            "entropy_indicators": list(decision["reason_codes"]),
            "recoverability_score": float(decision["scores"]["reversible_capacity_score"]),
            "authorization_recommendation": str(decision["posture"]),
            "reason_codes": list(decision["reason_codes"]),
            "recommended_safeguards": list(decision["controls"]) + list(identity_gate.get("recommended_controls", [])),
        },
    )
    ledger.append(
        "EXECUTION",
        "sparta-router",
        {
            "executed_operation": str(route["route_state"]),
            "execution_status": "not_executed" if not route["executable"] else "succeeded",
            "started_at": _now(),
            "duration_ms": 0,
            "rollback_performed": False,
            "rollback_success": None,
        },
    )
    ledger.append(
        "OUTCOME",
        "smerc-customer-evaluation",
        {
            "judged_correct": True,
            "unexpected_consequences": False,
            "controls_sufficient": not route["executable"] or bool(route["applied_controls"]),
            "cost_incurred": 0,
            "time_to_recover_minutes": 0,
            "customer_impact": "not measured in metadata-only evaluation",
            "security_impact": "not measured in metadata-only evaluation",
            "financial_impact": "not measured in metadata-only evaluation",
        },
    )
    return ledger


def _missing_evidence(ref_gate: Mapping[str, Any], identity_gate: Mapping[str, Any]) -> list[str]:
    missing = [] if ref_gate["status"] == "pass" else [f"ref_gate:{item}" for item in ref_gate["failures"]]
    if identity_gate["status"] == "FAIL" and "AGENT_IDENTITY_MISSING" in identity_gate["reason_codes"]:
        missing.append("agent_identity:identity_record")
    return missing


def _requested_autonomy(action: Mapping[str, Any]) -> str:
    side_effect = action["tool_plan"]["side_effect_level"]
    if side_effect in {"financial", "destructive", "external"}:
        return "execute"
    if action["tool_plan"]["requested_scope_units"] > 1:
        return "constrain"
    return "recommend"


def _gateway_pressure(decision: Mapping[str, Any], ref_gate: Mapping[str, Any]) -> float:
    scores = decision["scores"]
    pressure = (
        float(scores["irreversible_exposure_score"]) * 0.45
        + float(scores["operational_stress_score"]) * 0.35
        + (1 - float(scores["confidence_score"])) * 0.20
    )
    if ref_gate["status"] == "fail":
        pressure += 0.25
    return round(min(1.0, pressure), 3)


def _pilot_fit(summary: Mapping[str, Any]) -> Dict[str, str]:
    total = int(summary["total_actions"])
    non_executable = int(summary["non_executable_routes"])
    ref_failures = int(summary["ref_gate_counts"].get("fail", 0))
    constrained = int(summary["route_state_counts"].get("CONSTRAINED_EXECUTE", 0))
    if total >= 5 and (non_executable >= 2 or ref_failures >= 1) and constrained >= 1:
        return {
            "fit": "strong",
            "reason": "The evaluation includes multiple side-effecting actions, at least one constrained path, and hard-stop cases worth reviewer labeling.",
        }
    if total >= 3 and non_executable >= 1:
        return {
            "fit": "moderate",
            "reason": "The evaluation shows at least one meaningful action where SMERC changes execution posture.",
        }
    return {
        "fit": "weak",
        "reason": "The submitted actions do not yet show enough side-effecting runtime risk to justify a pilot.",
    }


def _recommended_next_action(pilot_fit: Mapping[str, str]) -> str:
    if pilot_fit["fit"] == "strong":
        return "Use these results in a review call and ask the prospect to replace samples with 10 to 25 metadata-only actions from one real workflow."
    if pilot_fit["fit"] == "moderate":
        return "Ask for more side-effecting actions from one workflow before proposing a pilot."
    return "Do not propose a pilot yet; collect better workflow metadata first."


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    text = value.strip()
    if len(text) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return text


def _ref_gate(value: Any, path: str) -> Dict[str, bool]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    _exact_fields(value, REF_GATE_FIELDS, path)
    parsed = {}
    for key in REF_GATE_FIELDS:
        if not isinstance(value[key], bool):
            raise TypeError(f"{path}.{key} must be a boolean")
        parsed[key] = value[key]
    return parsed


def _exact_fields(value: Mapping[str, Any], fields: set[str], path: str, optional: set[str] | None = None) -> None:
    optional = optional or set()
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields - optional)
    if missing:
        raise ValueError(f"{path} is missing field(s): {', '.join(missing)}")
    if unknown:
        raise ValueError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _reject_sensitive_keys(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if any(fragment in normalized for fragment in PROHIBITED_KEY_FRAGMENTS):
                raise ValueError(f"{path}.{key} appears to contain prohibited sensitive material")
            _reject_sensitive_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive_keys(child, f"{path}[{index}]")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a metadata-only customer evaluation through SMERC.")
    parser.add_argument("path", help="Path to smerc.customer-evaluation.v1 JSON.")
    parser.add_argument("--json-output", default="reports/customer_evaluation/customer_evaluation_report.json")
    parser.add_argument("--markdown-output", default="reports/customer_evaluation/Customer_Evaluation_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_customer_evaluation(load_payload(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

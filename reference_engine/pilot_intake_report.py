from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.customer_evaluation import (
    CUSTOMER_EVALUATION_VERSION,
    build_customer_evaluation,
)


PILOT_INTAKE_VERSION = "smerc.pilot-intake.v1"
ACTION_FIELDS = {
    "action_id",
    "description",
    "actor",
    "system",
    "workflow_stage",
    "current_control_outcome",
    "current_control_reason",
    "possible_consequence",
    "rollback_path",
    "scores",
    "properties",
    "ref_gate",
    "tool_capabilities",
}
SCORE_FIELDS = {
    "base_action_risk",
    "reversibility",
    "containment_strength",
    "rollback_latency",
    "evidence_validity",
    "anomaly_pressure",
    "impact_scope",
    "cancel_reliability",
    "authorization_confidence",
}
PROPERTY_FIELDS = {
    "action_type",
    "domain_profile",
    "external_side_effect",
    "sensitive_data",
    "requested_scope_units",
    "max_scope_units",
    "side_effect_level",
}
TOOL_CAPABILITY_FIELDS = {
    "supports_dry_run",
    "supports_scope_limit",
    "supports_checkpoint",
    "supports_rollback",
    "supports_human_approval",
}
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
    "reviewer_role",
    "workflow_family",
    "data_boundary",
    "initial_autonomy_state",
    "actions",
}
OPTIONAL_TOP_LEVEL_FIELDS = {"agents"}
ALLOWED_CURRENT_OUTCOMES = {"ALLOW", "BLOCK", "REVIEW", "UNKNOWN"}
SENSITIVE_KEY_FRAGMENTS = {
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
        raise TypeError("pilot intake payload must be a JSON object")
    return payload


def build_pilot_intake_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = validate_payload(payload)
    customer_payload = compile_customer_evaluation_payload(parsed)
    customer_report = build_customer_evaluation(customer_payload)
    comparisons = [_comparison(record, parsed["actions"][index]) for index, record in enumerate(customer_report["records"])]
    difference_count = sum(1 for item in comparisons if item["decision_changed"])
    constrained_rather_than_blocked = sum(1 for item in comparisons if item["constrained_rather_than_blocked"])
    by_current = Counter(item["current_control_outcome"] for item in comparisons)
    by_smerc = Counter(item["smerc_posture"] for item in comparisons)
    highest_exposure = sorted(
        comparisons,
        key=lambda item: item["irreversible_exposure_score"],
        reverse=True,
    )[:5]
    total = len(comparisons)
    return {
        "version": PILOT_INTAKE_VERSION,
        "generated_at": _now(),
        "tenant_id": parsed["tenant_id"],
        "organization": parsed["organization"],
        "reviewer_role": parsed["reviewer_role"],
        "workflow_family": parsed["workflow_family"],
        "data_boundary": parsed["data_boundary"],
        "evidence_boundary": (
            "This report is based on metadata-only pilot intake. It compares current reviewer/policy posture "
            "against SMERC runtime posture for discussion. It does not prove production validation, compliance, "
            "incident reduction, customer demand, or approval to enforce."
        ),
        "summary": {
            "actions_evaluated": total,
            "current_control_counts": dict(sorted(by_current.items())),
            "smerc_posture_counts": dict(sorted(by_smerc.items())),
            "decision_difference_count": difference_count,
            "decision_difference_rate": _rate(difference_count, total),
            "constrained_rather_than_blocked_count": constrained_rather_than_blocked,
            "constrained_rather_than_blocked_rate": _rate(constrained_rather_than_blocked, total),
            "highest_exposure_actions": highest_exposure,
            "pilot_fit": customer_report["pilot_fit"],
        },
        "comparisons": comparisons,
        "customer_evaluation": customer_report,
        "recommended_next_action": _recommend(customer_report["pilot_fit"], difference_count, constrained_rather_than_blocked),
    }


def validate_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    _exact_fields(payload, TOP_LEVEL_FIELDS, "pilot_intake", optional=OPTIONAL_TOP_LEVEL_FIELDS)
    if payload["version"] != PILOT_INTAKE_VERSION:
        raise ValueError(f"version must be {PILOT_INTAKE_VERSION}")
    actions = payload["actions"]
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")
    if len(actions) > 25:
        raise ValueError("actions must contain at most 25 items")
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
        current = _text(action["current_control_outcome"], f"actions[{index}].current_control_outcome", 24).upper()
        if current not in ALLOWED_CURRENT_OUTCOMES:
            raise ValueError(f"actions[{index}].current_control_outcome must be one of {sorted(ALLOWED_CURRENT_OUTCOMES)}")
        parsed = dict(action)
        parsed["action_id"] = action_id
        parsed["description"] = _text(action["description"], f"actions[{index}].description", 500)
        parsed["actor"] = _text(action["actor"], f"actions[{index}].actor", 128)
        parsed["system"] = _text(action["system"], f"actions[{index}].system", 160)
        parsed["workflow_stage"] = _text(action["workflow_stage"], f"actions[{index}].workflow_stage", 160)
        parsed["current_control_outcome"] = current
        parsed["current_control_reason"] = _text(action["current_control_reason"], f"actions[{index}].current_control_reason", 500)
        parsed["possible_consequence"] = _text(action["possible_consequence"], f"actions[{index}].possible_consequence", 500)
        parsed["rollback_path"] = _text(action["rollback_path"], f"actions[{index}].rollback_path", 500)
        parsed["scores"] = _scores(action["scores"], f"actions[{index}].scores")
        parsed["properties"] = _properties(action["properties"], f"actions[{index}].properties")
        parsed["ref_gate"] = _booleans(action["ref_gate"], REF_GATE_FIELDS, f"actions[{index}].ref_gate")
        parsed["tool_capabilities"] = _booleans(
            action["tool_capabilities"],
            TOOL_CAPABILITY_FIELDS,
            f"actions[{index}].tool_capabilities",
        )
        parsed_actions.append(parsed)
    agents = payload.get("agents", [])
    if not isinstance(agents, list):
        raise TypeError("agents must be a list when provided")
    parsed_agents = []
    seen_agents = set()
    for index, agent in enumerate(agents):
        if not isinstance(agent, dict):
            raise TypeError(f"agents[{index}] must be an object")
        _reject_sensitive_keys(agent, f"agents[{index}]")
        agent_id = _text(agent.get("agent_id"), f"agents[{index}].agent_id", 128)
        if agent_id in seen_agents:
            raise ValueError(f"duplicate agent_id: {agent_id}")
        seen_agents.add(agent_id)
        parsed_agents.append(dict(agent))

    return {
        "version": PILOT_INTAKE_VERSION,
        "tenant_id": _text(payload["tenant_id"], "tenant_id", 128),
        "organization": _text(payload["organization"], "organization", 160),
        "reviewer_role": _text(payload["reviewer_role"], "reviewer_role", 120),
        "workflow_family": _text(payload["workflow_family"], "workflow_family", 500),
        "data_boundary": _text(payload["data_boundary"], "data_boundary", 1200),
        "initial_autonomy_state": _text(payload["initial_autonomy_state"], "initial_autonomy_state", 64),
        "agents": parsed_agents,
        "actions": parsed_actions,
    }


def compile_customer_evaluation_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    actions = []
    for action in payload["actions"]:
        scores = action["scores"]
        properties = action["properties"]
        capabilities = action["tool_capabilities"]
        actions.append(
            {
                "action_id": action["action_id"],
                "description": action["description"],
                "actor": action["actor"],
                "tool": action["system"],
                "action_type": properties["action_type"],
                "base_action_risk": scores["base_action_risk"],
                "reversibility": scores["reversibility"],
                "containment_strength": scores["containment_strength"],
                "rollback_latency": scores["rollback_latency"],
                "evidence_validity": scores["evidence_validity"],
                "anomaly_pressure": scores["anomaly_pressure"],
                "impact_scope": scores["impact_scope"],
                "cancel_reliability": scores["cancel_reliability"],
                "authorization_confidence": scores["authorization_confidence"],
                "external_side_effect": properties["external_side_effect"],
                "sensitive_data": properties["sensitive_data"],
                "context": {
                    "domain_profile": properties["domain_profile"],
                    "workflow": payload["workflow_family"],
                    "current_control_outcome": action["current_control_outcome"],
                    "possible_consequence": action["possible_consequence"],
                    "rollback_path": action["rollback_path"],
                },
                "ref_gate": action["ref_gate"],
                "tool_plan": {
                    "version": "smerc.sparta-plan.v1",
                    "plan_id": f"plan_{action['action_id'].lower()}",
                    "tool": action["system"],
                    "action": properties["action_type"],
                    "requested_capability": properties["action_type"],
                    "supports_dry_run": capabilities["supports_dry_run"],
                    "supports_scope_limit": capabilities["supports_scope_limit"],
                    "supports_checkpoint": capabilities["supports_checkpoint"],
                    "supports_rollback": capabilities["supports_rollback"],
                    "supports_human_approval": capabilities["supports_human_approval"],
                    "max_scope_units": properties["max_scope_units"],
                    "requested_scope_units": properties["requested_scope_units"],
                    "side_effect_level": properties["side_effect_level"],
                    "metadata": {
                        "workflow_stage": action["workflow_stage"],
                        "rollback_path": action["rollback_path"],
                    },
                },
            }
        )
    return {
        "version": CUSTOMER_EVALUATION_VERSION,
        "tenant_id": payload["tenant_id"],
        "organization": payload["organization"],
        "contact_role": payload["reviewer_role"],
        "evaluation_date": date.today().isoformat(),
        "data_boundary": payload["data_boundary"],
        "workflow_context": payload["workflow_family"],
        "initial_autonomy_state": payload["initial_autonomy_state"],
        "agents": list(payload.get("agents", [])),
        "actions": actions,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# {report['organization']} Pilot Intake Evaluation Report",
        "",
        f"Version: `{report['version']}`",
        f"Generated: `{report['generated_at']}`",
        f"Reviewer role: `{report['reviewer_role']}`",
        f"Workflow family: {report['workflow_family']}",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Executive Summary",
        "",
        f"- Actions evaluated: `{summary['actions_evaluated']}`",
        f"- Current control outcomes: `{summary['current_control_counts']}`",
        f"- SMERC posture counts: `{summary['smerc_posture_counts']}`",
        f"- Agent identity-gate counts: `{report['customer_evaluation']['summary']['identity_gate_counts']}`",
        f"- Decisions that differ: `{summary['decision_difference_count']}` (`{summary['decision_difference_rate']}`)",
        f"- Constrained rather than blocked: `{summary['constrained_rather_than_blocked_count']}` (`{summary['constrained_rather_than_blocked_rate']}`)",
        f"- Pilot fit: `{summary['pilot_fit']['fit']}`",
        f"- Pilot fit reason: {summary['pilot_fit']['reason']}",
        "",
        "## Why This Matters",
        "",
        "This report shows where a binary or review-only control posture may miss recoverability details. "
        "A useful SMERC result is not always a stricter result. The useful result is a more specific runtime posture: "
        "`ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`, with reason codes and controls that a reviewer can challenge.",
        "",
        "## Current Controls vs SMERC",
        "",
        "| Action | Current outcome | SMERC posture | Changed | Exposure | Capacity | Control impact |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for item in report["comparisons"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['current_control_outcome']}` | `{item['smerc_posture']}` | "
            f"`{item['decision_changed']}` | {item['irreversible_exposure_score']} | "
            f"{item['reversible_capacity_score']} | {item['control_impact']} |"
        )
    lines.extend(["", "## Highest Irreversible Exposure", ""])
    for item in summary["highest_exposure_actions"]:
        lines.append(
            f"- `{item['action_id']}`: `{item['smerc_posture']}` with exposure "
            f"`{item['irreversible_exposure_score']}`. Consequence: {item['possible_consequence']}"
        )
    lines.extend(["", "## Action Detail", ""])
    for item in report["comparisons"]:
        lines.extend(
            [
                f"### {item['action_id']}",
                "",
                f"- Description: {item['description']}",
                f"- Current control outcome: `{item['current_control_outcome']}`",
                f"- Current control reason: {item['current_control_reason']}",
                f"- Possible consequence: {item['possible_consequence']}",
                f"- Rollback path: {item['rollback_path']}",
                f"- SMERC posture: `{item['smerc_posture']}`",
                f"- SPARTa route: `{item['sparta_route_state']}`",
                f"- Agent identity gate: `{item['agent_identity_gate_status']}`",
                f"- Agent identity reasons: `{item['agent_identity_reason_codes']}`",
                f"- Reason codes: `{item['reason_codes']}`",
                f"- Recommended controls: `{item['recommended_controls']}`",
                f"- Control impact: {item['control_impact']}",
                "",
            ]
        )
    lines.extend(["## Recommended Next Action", "", str(report["recommended_next_action"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def _comparison(record: Mapping[str, Any], intake_action: Mapping[str, Any]) -> Dict[str, Any]:
    decision = record["decision"]
    route = record["sparta_route"]
    current = intake_action["current_control_outcome"]
    smerc = decision["posture"]
    return {
        "action_id": intake_action["action_id"],
        "description": intake_action["description"],
        "actor": intake_action["actor"],
        "system": intake_action["system"],
        "workflow_stage": intake_action["workflow_stage"],
        "current_control_outcome": current,
        "current_control_reason": intake_action["current_control_reason"],
        "possible_consequence": intake_action["possible_consequence"],
        "rollback_path": intake_action["rollback_path"],
        "smerc_posture": smerc,
        "sparta_route_state": route["route_state"],
        "agent_identity_gate_status": record["identity_gate"]["status"],
        "agent_identity_reason_codes": record["identity_gate"]["reason_codes"],
        "decision_changed": _decision_changed(current, smerc),
        "constrained_rather_than_blocked": current == "BLOCK" and smerc == "THROTTLE",
        "irreversible_exposure_score": decision["scores"]["irreversible_exposure_score"],
        "reversible_capacity_score": decision["scores"]["reversible_capacity_score"],
        "risk_adjusted_authorization_score": decision["scores"]["risk_adjusted_authorization_score"],
        "reason_codes": decision["reason_codes"],
        "recommended_controls": decision["controls"],
        "control_impact": _control_impact(current, smerc),
    }


def _decision_changed(current: str, smerc: str) -> bool:
    if current == "UNKNOWN":
        return True
    if current == "REVIEW":
        return smerc not in {"ESCALATE", "FREEZE"}
    if current == "BLOCK":
        return smerc not in {"DENY", "FREEZE"}
    return smerc != "ALLOW"


def _control_impact(current: str, smerc: str) -> str:
    if current == "ALLOW" and smerc == "THROTTLE":
        return "SMERC keeps the action possible but adds runtime controls."
    if current == "ALLOW" and smerc in {"DENY", "FREEZE", "ESCALATE"}:
        return "SMERC would stop or route an action current controls would allow."
    if current == "BLOCK" and smerc == "THROTTLE":
        return "SMERC may preserve useful automation through constrained execution."
    if current == "REVIEW" and smerc == "ALLOW":
        return "SMERC may reduce review burden if reviewers agree and evidence is trusted."
    if current == "UNKNOWN":
        return "SMERC gives a first structured posture where no current decision is stated."
    return "SMERC broadly agrees with the current control posture."


def _recommend(pilot_fit: Mapping[str, str], differences: int, constrained: int) -> str:
    if pilot_fit["fit"] == "strong" and differences >= 2:
        return (
            "Proceed to a bounded shadow-mode pilot only if customer reviewers agree the differences are useful. "
            "Start with one workflow, preserve existing controls, and measure reviewer agreement, false releases, "
            "false constraints, latency, and review burden."
        )
    if constrained:
        return (
            "Run a second intake pass with more actions from the same workflow. The constrained examples are the "
            "most commercially useful evidence to test with reviewers."
        )
    return (
        "Do not pitch enforcement from this report. Ask for better side-effecting examples and current-control "
        "labels before proposing a pilot."
    )


def _scores(value: Any, path: str) -> Dict[str, float]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    _exact_fields(value, SCORE_FIELDS, path)
    return {key: _score(value[key], f"{path}.{key}") for key in SCORE_FIELDS}


def _properties(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    _exact_fields(value, PROPERTY_FIELDS, path)
    parsed = {
        "action_type": _text(value["action_type"], f"{path}.action_type", 120),
        "domain_profile": _text(value["domain_profile"], f"{path}.domain_profile", 120),
        "external_side_effect": _bool(value["external_side_effect"], f"{path}.external_side_effect"),
        "sensitive_data": _bool(value["sensitive_data"], f"{path}.sensitive_data"),
        "requested_scope_units": _positive_int(value["requested_scope_units"], f"{path}.requested_scope_units"),
        "max_scope_units": _positive_int(value["max_scope_units"], f"{path}.max_scope_units"),
        "side_effect_level": _text(value["side_effect_level"], f"{path}.side_effect_level", 80),
    }
    if parsed["requested_scope_units"] > parsed["max_scope_units"]:
        raise ValueError(f"{path}.requested_scope_units cannot exceed max_scope_units")
    return parsed


def _booleans(value: Any, fields: set[str], path: str) -> Dict[str, bool]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object")
    _exact_fields(value, fields, path)
    return {key: _bool(value[key], f"{path}.{key}") for key in fields}


def _score(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    if value < 0 or value > 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return float(value)


def _positive_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} must be an integer")
    if value <= 0:
        raise ValueError(f"{path} must be greater than zero")
    return value


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _text(value: Any, path: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    text = value.strip()
    if len(text) > maximum:
        raise ValueError(f"{path} must be at most {maximum} characters")
    return text


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
            if normalized != "credential_scope" and any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS):
                raise ValueError(f"{path}.{key} appears to contain prohibited sensitive material")
            _reject_sensitive_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive_keys(child, f"{path}[{index}]")


def _rate(count: int, total: int) -> float | None:
    if total == 0:
        return None
    return round(count / total, 3)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a company pilot intake comparison report.")
    parser.add_argument("path", help="Path to smerc.pilot-intake.v1 JSON.")
    parser.add_argument("--json-output", default="reports/pilot_intake/pilot_intake_report.json")
    parser.add_argument("--markdown-output", default="reports/pilot_intake/Pilot_Intake_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_pilot_intake_report(load_payload(args.path))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

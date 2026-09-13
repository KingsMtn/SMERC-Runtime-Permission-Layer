from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.customer_evaluation import (
    CUSTOMER_EVALUATION_VERSION,
    build_customer_evaluation,
    write_outputs as write_customer_outputs,
)


VERSION = "smerc.public-agent-runtime-incident-replay.v1"
SOURCE_NAME = "Public Agent Runtime Incident Replay"
SUPPORTED_PATTERNS = {
    "credential_exfiltration_pressure",
    "trust_boundary_before_consent",
    "approved_domain_exfiltration",
    "sandbox_or_filesystem_boundary_escape",
    "overbroad_remediation_blast_radius",
    "autonomous_workflow_acceleration",
}


def load_rows(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("public agent runtime incident replay input must be a JSON object")
    if payload.get("schema_version") != "smerc.public_agent_runtime_incident_patterns.v1":
        raise ValueError("schema_version must be smerc.public_agent_runtime_incident_patterns.v1")
    if "Use public incident-pattern data" not in _text(payload.get("source_boundary"), "source_boundary"):
        raise ValueError("source_boundary must preserve the public-pattern boundary")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows must be a non-empty list")

    parsed: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise TypeError(f"rows[{index}] must be an object")
        record_id = _text(row.get("record_id"), f"rows[{index}].record_id")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)
        pattern = _text(row.get("public_pattern"), f"{record_id}.public_pattern")
        if pattern not in SUPPORTED_PATTERNS:
            raise ValueError(f"{record_id}.public_pattern is not supported: {pattern}")
        _list(row.get("reason_codes"), f"{record_id}.reason_codes")
        _list(row.get("postcondition_evidence_needed"), f"{record_id}.postcondition_evidence_needed")
        parsed.append(dict(row))
    return parsed


def normalize_rows(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    actions = [_to_customer_action(row, index) for index, row in enumerate(rows, start=1)]
    return {
        "version": CUSTOMER_EVALUATION_VERSION,
        "tenant_id": "public-agent-runtime-incident-replay",
        "organization": "Public Agent Runtime Incident Replay",
        "contact_role": "ai_agent_runtime_security_reviewer",
        "evaluation_date": datetime.now(timezone.utc).date().isoformat(),
        "data_boundary": (
            "Safe metadata-only public incident-pattern replay. Rows use public containment lessons, public security "
            "advisories, public threat reports, public cloud credential-source documentation, and public incident "
            "reporting. They do not include leaked implementation data, private prompts, raw logs, credentials, "
            "customer data, account identifiers, packet payloads, production commands, or exploit payloads."
        ),
        "workflow_context": (
            "Public AI-agent runtime failure patterns normalized into SMERC customer-evaluation actions to test "
            "recoverability-aware posture, Governance Routing Workbench routing, postcondition evidence needs, and "
            "Decision Lifecycle Ledger records."
        ),
        "initial_autonomy_state": "WATCH",
        "actions": actions,
    }


def build_report(rows: list[Mapping[str, Any]]) -> Dict[str, Any]:
    normalized = normalize_rows(rows)
    evaluation = build_customer_evaluation(normalized)
    summary = evaluation["summary"]
    patterns = Counter(str(row["public_pattern"]) for row in rows)
    source_families = Counter(str(row["source_family"]) for row in rows)
    postures = Counter(str(row["likely_smerc_posture"]) for row in rows)
    reason_codes = Counter(code for row in rows for code in _list(row.get("reason_codes"), "reason_codes"))
    deltas = [_classify_delta(row, record) for row, record in zip(rows, evaluation["records"])]
    delta_counts = Counter(item["delta"] for item in deltas)

    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_name": SOURCE_NAME,
        "source_boundary": "Use public incident-pattern data, not leaked implementation data.",
        "public_source_urls": sorted({_text(row.get("source_url"), "source_url") for row in rows}),
        "record_count": len(rows),
        "normalized_action_count": len(normalized["actions"]),
        "pattern_counts": dict(sorted(patterns.items())),
        "source_family_counts": dict(sorted(source_families.items())),
        "expected_posture_counts": dict(sorted(postures.items())),
        "incident_reason_code_counts": dict(sorted(reason_codes.items())),
        "smerc_posture_counts": summary["posture_counts"],
        "governance_route_counts": summary["route_state_counts"],
        "valid_dll_ledgers": summary["valid_ledgers"],
        "deltas": deltas,
        "delta_counts": dict(sorted(delta_counts.items())),
        "normalized_customer_evaluation": normalized,
        "customer_evaluation": evaluation,
        "work_result_impact": {
            "work": "Replay public agent-runtime incident patterns through SMERC as safe metadata-only actions.",
            "result": (
                f"Evaluated {len(normalized['actions'])} public-pattern records through admission, recoverability "
                "scoring, Governance Routing Workbench routing, autonomy budgeting, and DLL evidence."
            ),
            "impact": (
                "Reviewers can see how SMERC learns from real public agent-runtime failures while preserving the "
                "boundary against leaked source code, private prompts, raw logs, credentials, and customer data."
            ),
        },
        "evidence_boundary": (
            "This is a public-pattern metadata replay. It is not proof that SMERC evaluated Anthropic private systems, "
            "not proof that SMERC used leaked source code, not a vulnerability disclosure, not an official "
            "benchmark score, not customer validation, and not production certification."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Public Agent Runtime Incident Replay Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Source Boundary",
        "",
        str(report["source_boundary"]),
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Public Patterns",
        "",
        f"- Records: `{report['record_count']}`",
        f"- Normalized actions: `{report['normalized_action_count']}`",
        f"- Pattern counts: `{report['pattern_counts']}`",
        f"- Source family counts: `{report['source_family_counts']}`",
        f"- Expected posture counts: `{report['expected_posture_counts']}`",
        f"- Incident reason-code counts: `{report['incident_reason_code_counts']}`",
        "",
        "## SMERC Results",
        "",
        f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
        f"- Governance Routing Workbench route counts: `{report['governance_route_counts']}`",
        f"- Valid DLL ledgers: `{report['valid_dll_ledgers']}`",
        f"- Delta counts: `{report['delta_counts']}`",
        "",
        "## Decision Deltas",
        "",
        "| Record | Public pattern | Expected posture | SMERC posture | Route | Delta |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in report["deltas"]:
        lines.append(
            f"| `{item['record_id']}` | `{item['public_pattern']}` | `{item['expected_posture']}` | "
            f"`{item['smerc_posture']}` | `{item['governance_route']}` | `{item['delta']}` |"
        )
    lines.extend(
        [
            "",
            "## Public Source URLs",
            "",
        ]
    )
    for url in report["public_source_urls"]:
        lines.append(f"- {url}")
    lines.extend(
        [
            "",
            "## Reviewer Question",
            "",
            "Which public agent-runtime pattern should be converted next into customer-owned metadata: credential pressure, pre-consent trust boundaries, allowed-domain capability grants, sandbox boundaries, remediation blast radius, or autonomous workflow velocity?",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    report: Mapping[str, Any],
    *,
    normalized_output: str | Path,
    json_output: str | Path,
    markdown_output: str | Path,
    customer_json_output: str | Path,
    customer_markdown_output: str | Path,
) -> None:
    Path(normalized_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(normalized_output).write_text(
        json.dumps(report["normalized_customer_evaluation"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")
    write_customer_outputs(report["customer_evaluation"], customer_json_output, customer_markdown_output)


def _to_customer_action(row: Mapping[str, Any], index: int) -> Dict[str, Any]:
    record_id = _text(row.get("record_id"), "record_id")
    pattern = _text(row.get("public_pattern"), "public_pattern")
    reason_codes = _list(row.get("reason_codes"), "reason_codes")
    exposure = _exposure_flags(pattern)
    return {
        "action_id": f"PUBLIC_AGENT_RUNTIME_{index:03d}_{record_id.lower()}",
        "description": f"{SOURCE_NAME} for {record_id}: {_text(row.get('metadata_only_action'), 'metadata_only_action')}",
        "actor": "agent_runtime",
        "tool": _tool_family(pattern),
        "action_type": f"public_incident_{pattern}",
        "base_action_risk": _risk(pattern),
        "reversibility": _reversibility(pattern),
        "containment_strength": _containment(pattern),
        "rollback_latency": _rollback_latency(pattern),
        "evidence_validity": _evidence_validity(pattern),
        "anomaly_pressure": _anomaly_pressure(pattern),
        "impact_scope": _impact_scope(pattern),
        "cancel_reliability": _cancel_reliability(pattern),
        "authorization_confidence": _authorization_confidence(pattern),
        "external_side_effect": exposure["external_side_effect"],
        "sensitive_data": exposure["sensitive_data"],
        "context": {
            "domain_profile": "security_ops",
            "source_name": SOURCE_NAME,
            "public_pattern": pattern,
            "source_family": _text(row.get("source_family"), "source_family"),
            "source_url": _text(row.get("source_url"), "source_url"),
            "metadata_only": True,
            "source_boundary": "public incident-pattern data, not leaked implementation data",
            "incident_reason_codes": reason_codes,
            "recoverability_question": _text(row.get("recoverability_question"), "recoverability_question"),
            "postcondition_evidence_needed": _list(row.get("postcondition_evidence_needed"), "postcondition_evidence_needed"),
            "non_claim": _text(row.get("non_claim"), "non_claim"),
        },
        "ref_gate": {
            "typed_contract_valid": pattern
            not in {"trust_boundary_before_consent", "sandbox_or_filesystem_boundary_escape"},
            "attestation_valid": pattern not in {"agent_runtime_provenance_weak", "autonomous_workflow_acceleration"},
            "least_privilege_confirmed": pattern
            not in {
                "credential_exfiltration_pressure",
                "approved_domain_exfiltration",
                "sandbox_or_filesystem_boundary_escape",
            },
            "object_shape_expected": pattern != "trust_boundary_before_consent",
        },
        "tool_plan": {
            "version": "smerc.sparta-plan.v1",
            "plan_id": f"plan_public_agent_runtime_{record_id.lower()}",
            "tool": _tool_family(pattern),
            "action": f"public_incident_{pattern}",
            "requested_capability": _requested_capability(pattern),
            "supports_dry_run": pattern in {"overbroad_remediation_blast_radius", "autonomous_workflow_acceleration"},
            "supports_scope_limit": pattern
            in {"overbroad_remediation_blast_radius", "autonomous_workflow_acceleration", "approved_domain_exfiltration"},
            "supports_checkpoint": pattern
            in {"overbroad_remediation_blast_radius", "autonomous_workflow_acceleration", "approved_domain_exfiltration"},
            "supports_rollback": pattern in {"overbroad_remediation_blast_radius"},
            "supports_human_approval": True,
            "max_scope_units": _max_scope(pattern),
            "requested_scope_units": _requested_scope(pattern),
            "side_effect_level": "destructive" if pattern == "sandbox_or_filesystem_boundary_escape" else "external",
            "metadata": {
                "source_name": SOURCE_NAME,
                "record_id": record_id,
                "public_pattern": pattern,
                "reason_codes": reason_codes,
            },
        },
    }


def _classify_delta(row: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    expected = _text(row.get("likely_smerc_posture"), "likely_smerc_posture")
    posture = str(record["decision"]["posture"])
    route = str(record["sparta_route"]["route_state"])
    if expected == posture:
        delta = "SMERC_MATCHES_PUBLIC_PATTERN_EXPECTATION"
    elif expected == "DENY" and posture in {"FREEZE", "ESCALATE"}:
        delta = "SMERC_RESTRAINS_PUBLIC_PATTERN"
    elif expected == "FREEZE" and posture in {"DENY", "ESCALATE"}:
        delta = "SMERC_RESTRAINS_PUBLIC_PATTERN"
    elif expected == "ESCALATE" and posture in {"FREEZE", "DENY"}:
        delta = "SMERC_RESTRAINS_PUBLIC_PATTERN"
    elif expected == "THROTTLE" and posture in {"FREEZE", "DENY", "ESCALATE"}:
        delta = "SMERC_CONSTRAINS_PUBLIC_PATTERN"
    else:
        delta = "NEEDS_HUMAN_LABEL_REVIEW"
    return {
        "record_id": str(row["record_id"]),
        "public_pattern": str(row["public_pattern"]),
        "expected_posture": expected,
        "smerc_action_id": str(record["action_id"]),
        "smerc_posture": posture,
        "governance_route": route,
        "delta": delta,
    }


def _risk(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.96,
        "trust_boundary_before_consent": 0.9,
        "approved_domain_exfiltration": 0.88,
        "sandbox_or_filesystem_boundary_escape": 0.94,
        "overbroad_remediation_blast_radius": 0.78,
        "autonomous_workflow_acceleration": 0.72,
    }[pattern]


def _reversibility(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.08,
        "trust_boundary_before_consent": 0.18,
        "approved_domain_exfiltration": 0.12,
        "sandbox_or_filesystem_boundary_escape": 0.16,
        "overbroad_remediation_blast_radius": 0.42,
        "autonomous_workflow_acceleration": 0.5,
    }[pattern]


def _containment(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.16,
        "trust_boundary_before_consent": 0.22,
        "approved_domain_exfiltration": 0.26,
        "sandbox_or_filesystem_boundary_escape": 0.14,
        "overbroad_remediation_blast_radius": 0.46,
        "autonomous_workflow_acceleration": 0.52,
    }[pattern]


def _rollback_latency(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.94,
        "trust_boundary_before_consent": 0.82,
        "approved_domain_exfiltration": 0.88,
        "sandbox_or_filesystem_boundary_escape": 0.86,
        "overbroad_remediation_blast_radius": 0.7,
        "autonomous_workflow_acceleration": 0.58,
    }[pattern]


def _evidence_validity(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.24,
        "trust_boundary_before_consent": 0.18,
        "approved_domain_exfiltration": 0.28,
        "sandbox_or_filesystem_boundary_escape": 0.2,
        "overbroad_remediation_blast_radius": 0.46,
        "autonomous_workflow_acceleration": 0.48,
    }[pattern]


def _anomaly_pressure(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.94,
        "trust_boundary_before_consent": 0.84,
        "approved_domain_exfiltration": 0.86,
        "sandbox_or_filesystem_boundary_escape": 0.9,
        "overbroad_remediation_blast_radius": 0.72,
        "autonomous_workflow_acceleration": 0.78,
    }[pattern]


def _impact_scope(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.92,
        "trust_boundary_before_consent": 0.76,
        "approved_domain_exfiltration": 0.86,
        "sandbox_or_filesystem_boundary_escape": 0.9,
        "overbroad_remediation_blast_radius": 0.82,
        "autonomous_workflow_acceleration": 0.74,
    }[pattern]


def _cancel_reliability(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.2,
        "trust_boundary_before_consent": 0.32,
        "approved_domain_exfiltration": 0.24,
        "sandbox_or_filesystem_boundary_escape": 0.22,
        "overbroad_remediation_blast_radius": 0.48,
        "autonomous_workflow_acceleration": 0.46,
    }[pattern]


def _authorization_confidence(pattern: str) -> float:
    return {
        "credential_exfiltration_pressure": 0.28,
        "trust_boundary_before_consent": 0.18,
        "approved_domain_exfiltration": 0.34,
        "sandbox_or_filesystem_boundary_escape": 0.3,
        "overbroad_remediation_blast_radius": 0.56,
        "autonomous_workflow_acceleration": 0.5,
    }[pattern]


def _exposure_flags(pattern: str) -> Dict[str, bool]:
    return {
        "external_side_effect": True,
        "sensitive_data": pattern
        in {
            "credential_exfiltration_pressure",
            "approved_domain_exfiltration",
            "sandbox_or_filesystem_boundary_escape",
        },
    }


def _tool_family(pattern: str) -> str:
    return {
        "credential_exfiltration_pressure": "agent_filesystem_and_network_tool",
        "trust_boundary_before_consent": "agent_project_configuration_loader",
        "approved_domain_exfiltration": "agent_egress_proxy_or_files_api",
        "sandbox_or_filesystem_boundary_escape": "agent_sandbox_or_workspace_runtime",
        "overbroad_remediation_blast_radius": "repository_remediation_or_takedown_tool",
        "autonomous_workflow_acceleration": "multi_agent_workflow_orchestration",
    }[pattern]


def _requested_capability(pattern: str) -> str:
    return {
        "credential_exfiltration_pressure": "credential_read_and_egress",
        "trust_boundary_before_consent": "pre_consent_configuration_execution",
        "approved_domain_exfiltration": "approved_domain_data_transfer",
        "sandbox_or_filesystem_boundary_escape": "workspace_boundary_escape",
        "overbroad_remediation_blast_radius": "broad_remediation_action",
        "autonomous_workflow_acceleration": "parallel_agent_workflow_execution",
    }[pattern]


def _max_scope(pattern: str) -> int:
    return {
        "credential_exfiltration_pressure": 3,
        "trust_boundary_before_consent": 2,
        "approved_domain_exfiltration": 5,
        "sandbox_or_filesystem_boundary_escape": 4,
        "overbroad_remediation_blast_radius": 75,
        "autonomous_workflow_acceleration": 40,
    }[pattern]


def _requested_scope(pattern: str) -> int:
    return {
        "credential_exfiltration_pressure": 3,
        "trust_boundary_before_consent": 2,
        "approved_domain_exfiltration": 5,
        "sandbox_or_filesystem_boundary_escape": 4,
        "overbroad_remediation_blast_radius": 75,
        "autonomous_workflow_acceleration": 40,
    }[pattern]


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TypeError(f"{path} must be a non-empty list")
    return [_text(item, f"{path}[]") for item in value]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay public agent-runtime incident patterns through SMERC.")
    parser.add_argument("path", help="Path to public agent runtime incident patterns JSON.")
    parser.add_argument(
        "--normalized-output",
        default="examples/public_agent_runtime_incident_normalized_customer_eval_actions.json",
    )
    parser.add_argument("--json-output", default="reports/public_agent_runtime_incident_replay_report.json")
    parser.add_argument("--markdown-output", default="reports/Public_Agent_Runtime_Incident_Replay_Report.md")
    parser.add_argument(
        "--customer-json-output",
        default="reports/public_agent_runtime_incident_customer_evaluation/customer_evaluation_report.json",
    )
    parser.add_argument(
        "--customer-markdown-output",
        default="reports/public_agent_runtime_incident_customer_evaluation/Customer_Evaluation_Report.md",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    report = build_report(load_rows(args.path))
    write_outputs(
        report,
        normalized_output=args.normalized_output,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
        customer_json_output=args.customer_json_output,
        customer_markdown_output=args.customer_markdown_output,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

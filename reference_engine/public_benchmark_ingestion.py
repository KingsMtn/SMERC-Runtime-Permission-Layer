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


VERSION = "smerc.public-benchmark-ingestion.v1"

SUPPORTED_BENCHMARK_FAMILIES = {
    "agent_action_boundary_drift",
    "agent_action_boundary_safe_baseline",
    "agentgovbench_cross_tenant_isolation",
    "agentgovbench_fail_mode",
    "agentgovbench_identity_propagation",
    "agentic_redteam_trajectory_drift",
    "cloud_admin_iac_change",
    "consequencebench_external_state",
    "financial_runtime_action",
    "mcp_benign_baseline",
    "mcp_tool_poisoning",
}

EXPECTED_GOVERNANCE_NEEDS = {"allow", "block", "constrain", "review"}
BASELINE_OUTCOMES = {"ALLOW", "REVIEW", "BLOCK", "UNKNOWN"}


def load_benchmark_examples(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("public benchmark ingestion input must be a non-empty JSON array")

    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"benchmark row {index} must be an object")
        record_id = _text(item.get("record_id"), f"benchmark row {index} record_id")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)

        family = _text(item.get("benchmark_family"), f"{record_id} benchmark_family")
        if family not in SUPPORTED_BENCHMARK_FAMILIES:
            raise ValueError(f"{record_id} benchmark_family is not supported: {family}")
        _expected_need(item)
        _baseline(item)
        rows.append(dict(item))
    return rows


def normalize_benchmark_examples(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    actions = []
    for index, row in enumerate(rows, start=1):
        actions.append(_to_customer_action(row, index))
    return {
        "version": CUSTOMER_EVALUATION_VERSION,
        "tenant_id": "public-benchmark-ingestion-review",
        "organization": "Public Benchmark Ingestion Review",
        "contact_role": "agent_governance_reviewer",
        "evaluation_date": datetime.now(timezone.utc).date().isoformat(),
        "data_boundary": (
            "Representative public benchmark-shaped examples only. Inputs are metadata summaries inspired by public "
            "agent governance, MCP security, action-boundary, consequence, cloud-admin, and financial runtime test "
            "categories. They are not copied private customer data, official benchmark scores, secrets, credentials, "
            "source code, raw logs, raw transactions, or production events."
        ),
        "workflow_context": (
            "Public benchmark patterns normalized into SMERC customer-evaluation actions to test whether "
            "recoverability-before-execution adds useful runtime judgment across external action surfaces."
        ),
        "initial_autonomy_state": "HEALTHY",
        "actions": actions,
    }


def build_public_benchmark_ingestion_report(rows: list[Mapping[str, Any]]) -> Dict[str, Any]:
    payload = normalize_benchmark_examples(rows)
    evaluation = build_customer_evaluation(payload)
    summary = evaluation["summary"]
    baseline_counts = Counter(_baseline(row) for row in rows)
    family_counts = Counter(str(row["benchmark_family"]) for row in rows)
    expected_counts = Counter(_expected_need(row) for row in rows)
    deltas = [_classify_delta(row, record) for row, record in zip(rows, evaluation["records"])]
    delta_counts = Counter(item["delta"] for item in deltas)

    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_example_count": len(rows),
        "normalized_action_count": len(payload["actions"]),
        "benchmark_family_counts": dict(sorted(family_counts.items())),
        "expected_governance_counts": dict(sorted(expected_counts.items())),
        "baseline_outcome_counts": dict(sorted(baseline_counts.items())),
        "smerc_posture_counts": summary["posture_counts"],
        "smerc_route_counts": summary["route_state_counts"],
        "valid_dll_ledgers": summary["valid_ledgers"],
        "deltas": deltas,
        "delta_counts": dict(sorted(delta_counts.items())),
        "normalized_customer_evaluation": payload,
        "customer_evaluation": evaluation,
        "evidence_boundary": (
            "This pack proves adapter readiness and local runtime coherence on representative benchmark-shaped "
            "metadata. It does not claim official scores for AgentGovBench, Agent Action Boundary Benchmark, "
            "AgentDefense-Bench, MCPTox, Agentic Redteam Benchmark, ConsequenceBench, Microsoft AGT, or any other "
            "upstream benchmark until license-compatible datasets and their official runners are used."
        ),
        "work_result_impact": {
            "work": "Map public agent-governance, MCP, action-boundary, consequence, cloud, and financial benchmark shapes into SMERC actions.",
            "result": (
                f"Evaluated {len(payload['actions'])} normalized actions through hard gates, recoverability scoring, "
                "SPARTa routing, autonomy budgeting, and Decision Lifecycle Ledger evidence."
            ),
            "impact": (
                "Reviewers can see how SMERC would sit beside public benchmark families and where it adds "
                "recoverability-aware restraint before live customer data or formal benchmark certification."
            ),
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Public Benchmark Ingestion Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This report shows how public agent-governance and MCP-security benchmark categories can be translated into SMERC runtime-evaluation metadata.",
        "",
        "It is a bridge, not a benchmark victory lap: the rows are representative examples shaped like public benchmark problems, not official upstream datasets or scores.",
        "",
        "## Work / Result / Impact",
        "",
        f"- Work: {report['work_result_impact']['work']}",
        f"- Result: {report['work_result_impact']['result']}",
        f"- Impact: {report['work_result_impact']['impact']}",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Benchmark Families Represented",
        "",
        "| Public pattern family | Rows |",
        "| --- | ---: |",
    ]
    for family, count in report["benchmark_family_counts"].items():
        lines.append(f"| `{family}` | {count} |")

    lines.extend(
        [
            "",
            "## Baseline vs SMERC",
            "",
            f"- Baseline outcome counts: `{report['baseline_outcome_counts']}`",
            f"- Expected governance counts: `{report['expected_governance_counts']}`",
            f"- SMERC posture counts: `{report['smerc_posture_counts']}`",
            f"- SPARTa route counts: `{report['smerc_route_counts']}`",
            f"- Valid DLL ledgers: `{report['valid_dll_ledgers']}`",
            f"- Delta counts: `{report['delta_counts']}`",
            "",
            "## Decision Deltas",
            "",
            "| Record | Family | Baseline | Expected need | SMERC posture | SPARTa route | Delta |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report["deltas"]:
        lines.append(
            f"| `{item['record_id']}` | `{item['benchmark_family']}` | `{item['baseline_outcome']}` | "
            f"`{item['expected_governance_need']}` | `{item['smerc_posture']}` | "
            f"`{item['sparta_route']}` | `{item['delta']}` |"
        )

    lines.extend(
        [
            "",
            "## Reviewer Question",
            "",
            "Which upstream public benchmark rows should be mapped next, and can they be used under a license-compatible test harness without claiming more than the data proves?",
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
    normalized_path = Path(normalized_output)
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.write_text(
        json.dumps(report["normalized_customer_evaluation"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    write_customer_outputs(report["customer_evaluation"], customer_json_output, customer_markdown_output)


def _to_customer_action(row: Mapping[str, Any], index: int) -> Dict[str, Any]:
    action_type = _action_type(row)
    action_id = f"PUBLIC_BENCH_{index:03d}_{_slug(str(row['proposed_action']))}"
    return {
        "action_id": action_id,
        "description": (
            f"{row['benchmark_family']} representative scenario: "
            f"{_text(row.get('scenario_summary'), 'scenario_summary')}"
        ),
        "actor": _text(row.get("actor"), "actor"),
        "tool": _text(row.get("tool"), "tool"),
        "action_type": action_type,
        "base_action_risk": _risk(row, action_type),
        "reversibility": _ratio(row.get("reversibility"), "reversibility"),
        "containment_strength": _ratio(row.get("containment_strength"), "containment_strength"),
        "rollback_latency": _ratio(row.get("rollback_latency"), "rollback_latency"),
        "evidence_validity": _ratio(row.get("evidence_quality"), "evidence_quality"),
        "anomaly_pressure": _ratio(row.get("anomaly_pressure"), "anomaly_pressure"),
        "impact_scope": _ratio(row.get("impact_scope"), "impact_scope"),
        "cancel_reliability": _ratio(row.get("cancel_reliability"), "cancel_reliability"),
        "authorization_confidence": _ratio(row.get("authorization_confidence"), "authorization_confidence"),
        "external_side_effect": _side_effect(row) in {"external", "destructive", "financial"},
        "sensitive_data": _boolean(row.get("sensitive_data"), "sensitive_data"),
        "context": {
            "domain_profile": _domain_profile(row),
            "benchmark_family": _text(row.get("benchmark_family"), "benchmark_family"),
            "source_reference": _text(row.get("source_reference"), "source_reference"),
            "runtime_surface": _text(row.get("runtime_surface"), "runtime_surface"),
            "expected_governance_need": _expected_need(row),
            "current_baseline_outcome": _baseline(row),
            "identity_confidence": _ratio(row.get("identity_confidence"), "identity_confidence"),
            "authority_clarity": _ratio(row.get("authority_clarity"), "authority_clarity"),
        },
        "ref_gate": {
            "typed_contract_valid": _boolean(row.get("typed_contract"), "typed_contract"),
            "attestation_valid": _boolean(row.get("attestation"), "attestation"),
            "least_privilege_confirmed": _ratio(row.get("least_privilege"), "least_privilege") >= 0.6,
            "object_shape_expected": _boolean(row.get("object_shape"), "object_shape"),
        },
        "tool_plan": {
            "version": "smerc.sparta-plan.v1",
            "plan_id": f"plan_{action_id.lower()}",
            "tool": _text(row.get("tool"), "tool"),
            "action": action_type,
            "requested_capability": _text(row.get("proposed_action"), "proposed_action"),
            "supports_dry_run": _boolean(row.get("supports_dry_run"), "supports_dry_run"),
            "supports_scope_limit": _boolean(row.get("supports_scope_limit"), "supports_scope_limit"),
            "supports_checkpoint": _boolean(row.get("supports_checkpoint"), "supports_checkpoint"),
            "supports_rollback": _boolean(row.get("supports_rollback"), "supports_rollback"),
            "supports_human_approval": _boolean(row.get("supports_human_approval"), "supports_human_approval"),
            "max_scope_units": int(_positive_number(row.get("max_scope_units"), "max_scope_units")),
            "requested_scope_units": int(_positive_number(row.get("requested_scope_units"), "requested_scope_units")),
            "side_effect_level": _side_effect(row),
            "metadata": {
                "benchmark_family": _text(row.get("benchmark_family"), "benchmark_family"),
                "source_record_id": _text(row.get("record_id"), "record_id"),
                "runtime_surface": _text(row.get("runtime_surface"), "runtime_surface"),
            },
        },
    }


def _classify_delta(row: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    baseline = _baseline(row)
    posture = str(record["decision"]["posture"])
    route = str(record["sparta_route"]["route_state"])
    expected = _expected_need(row)

    if baseline == "ALLOW" and posture in {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}:
        delta = "BASELINE_ALLOW_SMERC_ADDS_RESTRAINT"
    elif baseline in {"REVIEW", "UNKNOWN"} and posture in {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}:
        delta = "BASELINE_REVIEW_SMERC_STRUCTURES_DECISION"
    elif baseline == "BLOCK" and posture in {"ALLOW", "THROTTLE"}:
        delta = "BASELINE_BLOCK_SMERC_FINDS_BOUNDED_PATH"
    elif expected == "allow" and posture == "ALLOW":
        delta = "BOTH_ALLOW_LOW_RISK"
    elif expected == "block" and posture in {"DENY", "FREEZE"}:
        delta = "BOTH_RESTRAIN_HIGH_RISK"
    else:
        delta = "NEEDS_REVIEW"

    return {
        "record_id": str(row["record_id"]),
        "benchmark_family": str(row["benchmark_family"]),
        "baseline_outcome": baseline,
        "expected_governance_need": expected,
        "smerc_action_id": str(record["action_id"]),
        "smerc_posture": posture,
        "sparta_route": route,
        "delta": delta,
    }


def _action_type(row: Mapping[str, Any]) -> str:
    family = _text(row.get("benchmark_family"), "benchmark_family")
    mapping = {
        "agent_action_boundary_drift": "action_boundary_expansion",
        "agent_action_boundary_safe_baseline": "bounded_read_or_preview",
        "agentgovbench_fail_mode": "continue_after_failed_precheck",
        "agentgovbench_identity_propagation": "cross_tenant_data_export",
        "mcp_benign_baseline": "mcp_read_only_context",
        "mcp_tool_poisoning": "mcp_untrusted_instruction_followup",
        "agentic_redteam_trajectory_drift": "multi_step_scope_accumulation",
        "consequencebench_external_state": "external_state_change",
        "cloud_admin_iac_change": "cloud_iac_apply",
        "financial_runtime_action": "financial_liquidity_movement",
    }
    return mapping.get(family, _slug(_text(row.get("proposed_action"), "proposed_action")))


def _domain_profile(row: Mapping[str, Any]) -> str:
    surface = _text(row.get("runtime_surface"), "runtime_surface")
    if "financial" in surface:
        return "finance_ops"
    if surface in {"cloud_admin", "github_actions", "ci_cd_agent"}:
        return "github_actions" if surface in {"github_actions", "ci_cd_agent"} else "cloud_admin"
    if surface == "mcp_gateway":
        return "security_ops"
    if surface == "external_state_action":
        return "customer_comms"
    return "general"


def _risk(row: Mapping[str, Any], action_type: str) -> float:
    impact = _ratio(row.get("impact_scope"), "impact_scope")
    reversibility_gap = 1.0 - _ratio(row.get("reversibility"), "reversibility")
    evidence_gap = 1.0 - _ratio(row.get("evidence_quality"), "evidence_quality")
    anomaly = _ratio(row.get("anomaly_pressure"), "anomaly_pressure")
    authority_gap = 1.0 - _ratio(row.get("authority_clarity"), "authority_clarity")
    risk = impact * 0.28 + reversibility_gap * 0.24 + evidence_gap * 0.16 + anomaly * 0.2 + authority_gap * 0.12
    if "poisoning" in action_type or "cross_tenant" in action_type or _side_effect(row) in {"destructive", "financial"}:
        risk += 0.1
    return round(min(1.0, risk), 3)


def _expected_need(row: Mapping[str, Any]) -> str:
    value = _text(row.get("expected_governance_need"), "expected_governance_need").lower()
    if value not in EXPECTED_GOVERNANCE_NEEDS:
        raise ValueError("expected_governance_need must be allow, block, constrain, or review")
    return value


def _baseline(row: Mapping[str, Any]) -> str:
    value = _text(row.get("current_baseline_outcome"), "current_baseline_outcome").upper()
    if value not in BASELINE_OUTCOMES:
        raise ValueError("current_baseline_outcome must be ALLOW, REVIEW, BLOCK, or UNKNOWN")
    return value


def _side_effect(row: Mapping[str, Any]) -> str:
    value = _text(row.get("side_effect_level"), "side_effect_level")
    if value not in {"internal", "external", "destructive", "financial"}:
        raise ValueError("side_effect_level must be internal, external, destructive, or financial")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{path} must be a boolean")
    return value


def _ratio(value: Any, path: str) -> float:
    numeric = _positive_number(value, path)
    if numeric > 1.0:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return round(numeric, 3)


def _positive_number(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{path} must be a number")
    numeric = float(value)
    if numeric < 0:
        raise ValueError(f"{path} must be non-negative")
    return numeric


def _slug(value: str) -> str:
    clean = [char.lower() if char.isalnum() else "_" for char in value]
    return "_".join(part for part in "".join(clean).split("_") if part)[:72]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize public benchmark-shaped examples into SMERC evaluation actions.")
    parser.add_argument("path", help="Path to public benchmark-shaped JSON examples.")
    parser.add_argument("--normalized-output", default="examples/public_benchmark_normalized_customer_eval_actions.json")
    parser.add_argument("--json-output", default="reports/public_benchmark_ingestion_report.json")
    parser.add_argument("--markdown-output", default="reports/Public_Benchmark_Ingestion_Report.md")
    parser.add_argument("--customer-json-output", default="reports/public_benchmark_customer_evaluation/customer_evaluation_report.json")
    parser.add_argument("--customer-markdown-output", default="reports/public_benchmark_customer_evaluation/Customer_Evaluation_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_public_benchmark_ingestion_report(load_benchmark_examples(args.path))
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

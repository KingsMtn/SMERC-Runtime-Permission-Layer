from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.customer_evaluation import build_customer_evaluation, load_payload


VERSION = "smerc.cloud-admin-proof-pack.v1"

CLOUD_REASON_CODE_LABELS = {
    "AUTONOMY_SCOPE_PRESSURE": "The requested scope is broad enough that autonomy should be constrained or reviewed.",
    "BACKUP_RETENTION_RECOVERY_RISK": "Backup or retention changes can reduce the recovery path after later failure.",
    "CANCEL_RELIABILITY_WEAK": "The action may not stop cleanly once execution starts.",
    "DATA_PLANE_DESTRUCTIVE_ACTION": "The action can delete or materially alter production data-plane resources.",
    "DNS_TRAFFIC_CUTOVER": "DNS or traffic-routing changes can create externally visible service impact.",
    "EVIDENCE_INCOMPLETE": "The action lacks enough trusted evidence to support confident execution.",
    "IAM_SCOPE_EXPANSION": "Identity or permission changes may increase who or what can act later.",
    "KUBERNETES_ROLLOUT_UNDER_PRESSURE": "Deployment automation is acting while reliability or error-budget pressure is present.",
    "NETWORK_BOUNDARY_WIDENING": "Network access or boundary changes can widen exposure quickly.",
    "PRODUCTION_BLAST_RADIUS_WIDE": "Production impact scope is wide enough to create meaningful blast radius.",
    "ROLLBACK_UNCERTAIN": "Rollback, reversibility, or checkpoint support is weak for the proposed action.",
    "SECRET_OR_AUTH_ROTATION": "Authentication material changes can interrupt dependent services if coordination fails.",
}


def build_cloud_admin_proof_pack(payload: Mapping[str, Any]) -> Dict[str, Any]:
    expanded_payload = _expand_payload(payload)
    report = build_customer_evaluation(expanded_payload)
    reason_counts: Counter[str] = Counter()
    work_items: list[Dict[str, str]] = []

    for record in report["records"]:
        action = _action_by_id(expanded_payload, record["action_id"])
        codes = cloud_reason_codes(action, record)
        reason_counts.update(codes)
        record["cloud_reason_codes"] = codes
        record["cloud_reason_labels"] = {code: CLOUD_REASON_CODE_LABELS[code] for code in codes}
        record["work_result_impact"] = work_result_impact(action, record, codes)
        work_items.append(record["work_result_impact"])

    report["version"] = VERSION
    report["source_version"] = "smerc.customer-evaluation.v1"
    report["generated_at"] = _now()
    report["cloud_reason_code_counts"] = dict(sorted(reason_counts.items()))
    report["cloud_reason_code_labels"] = CLOUD_REASON_CODE_LABELS
    report["proof_pack_boundary"] = (
        "Cloud-admin proof pack uses metadata-only simulated infrastructure actions. It does not connect to AWS, "
        "Azure, Google Cloud, Cloudflare, Kubernetes clusters, Terraform state, DNS providers, databases, secrets "
        "managers, production logs, or customer infrastructure."
    )
    report["work_result_impact_examples"] = work_items[:8]
    report["strategic_fit"] = {
        "buyer_question": (
            "Can a cloud, platform, or infrastructure team let AI/devops agents move faster while still freezing, "
            "throttling, denying, or escalating actions that are not recoverable enough to execute?"
        ),
        "strongest_fit": [
            "cloud platform teams",
            "SRE and infrastructure teams",
            "DevOps automation owners",
            "CI/CD platform owners",
            "AI-agent platform teams",
        ],
        "not_claimed": [
            "cloud-provider certification",
            "production enforcement readiness",
            "incident reduction proof",
            "replacement for IAM, OPA, Terraform policy, Kubernetes RBAC, CI approvals, SIEM, or human accountability",
        ],
    }
    return report


def cloud_reason_codes(action: Mapping[str, Any], record: Mapping[str, Any]) -> list[str]:
    action_type = str(action["action_type"]).lower()
    tool = str(action["tool"]).lower()
    plan = action["tool_plan"]
    metadata = plan.get("metadata", {})
    change_family = str(metadata.get("change_family", "")).lower()
    environment = str(metadata.get("environment", "")).lower()
    decision = record["decision"]
    ref_gate = record["ref_gate"]

    codes: list[str] = []
    if "iam" in action_type or "iam" in tool or "identity" in change_family or "access" in change_family:
        codes.append("IAM_SCOPE_EXPANSION")
    if "network" in action_type or "security_group" in action_type or "network" in tool:
        codes.append("NETWORK_BOUNDARY_WIDENING")
    if "delete" in action_type or plan.get("side_effect_level") == "destructive":
        codes.append("DATA_PLANE_DESTRUCTIVE_ACTION")
    if "kubernetes" in tool or "rollout" in action_type:
        codes.append("KUBERNETES_ROLLOUT_UNDER_PRESSURE")
    if "dns" in tool or "cutover" in action_type or "traffic" in change_family:
        codes.append("DNS_TRAFFIC_CUTOVER")
    if "rotation" in action_type or "secret" in tool or "auth" in action_type:
        codes.append("SECRET_OR_AUTH_ROTATION")
    if "capacity" in action_type or "autoscaling" in tool:
        codes.append("KUBERNETES_ROLLOUT_UNDER_PRESSURE")
    if "backup" in action_type or "retention" in action_type or "resilience" in change_family:
        codes.append("BACKUP_RETENTION_RECOVERY_RISK")
    if "production" in environment and float(action["impact_scope"]) >= 0.65:
        codes.append("PRODUCTION_BLAST_RADIUS_WIDE")
    if float(action["reversibility"]) < 0.45 or float(action["rollback_latency"]) > 0.65 or not plan.get("supports_rollback", False):
        codes.append("ROLLBACK_UNCERTAIN")
    if float(action["evidence_validity"]) < 0.60 or ref_gate["status"] == "fail":
        codes.append("EVIDENCE_INCOMPLETE")
    if float(action["cancel_reliability"]) < 0.55:
        codes.append("CANCEL_RELIABILITY_WEAK")
    if float(plan["requested_scope_units"]) / max(float(plan["max_scope_units"]), 1.0) >= 0.65:
        codes.append("AUTONOMY_SCOPE_PRESSURE")
    if decision["posture"] == "DENY" and "ROLLBACK_UNCERTAIN" not in codes:
        codes.append("ROLLBACK_UNCERTAIN")

    return sorted(set(codes)) or ["EVIDENCE_INCOMPLETE"]


def work_result_impact(action: Mapping[str, Any], record: Mapping[str, Any], codes: list[str]) -> Dict[str, str]:
    posture = record["decision"]["posture"]
    route = record["sparta_route"]["route_state"]
    exposure = record["decision"]["scores"]["irreversible_exposure_score"]
    action_type = action["action_type"]
    work = f"Evaluate `{action_type}` before cloud execution using Ref-gate checks, recoverability scoring, SPARTa routing, and DLL evidence."
    result = f"SMERC returned `{posture}`, SPARTa routed `{route}`, and cloud reason codes were {', '.join(codes)}."
    if posture == "DENY":
        impact = "Execution is blocked until the request is repaired, narrowed, or resubmitted with stronger evidence."
    elif posture == "FREEZE":
        impact = "Automation pauses so a responsible reviewer can decide whether the action should continue."
    elif posture == "THROTTLE":
        impact = "Automation can continue only through a constrained route such as reduced scope, checkpointing, or additional approval."
    elif posture == "ESCALATE":
        impact = "The action is routed to accountable review because evidence, authority, or recovery confidence is not enough for routine execution."
    else:
        impact = "The action is allowed with replay evidence because recovery and containment are strong enough for this simulated case."
    return {
        "work": work,
        "result": result,
        "impact": f"{impact} Irreversible exposure score: {exposure}.",
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Cloud Admin Proof Pack",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This proof pack shows how SMERC evaluates AI/devops cloud-administration actions before they change infrastructure, permissions, routing, production data, or recovery posture.",
        "",
        "The buyer question is practical: can infrastructure teams move faster with autonomous agents while still constraining actions that are not recoverable enough to execute?",
        "",
        "## Evidence Boundary",
        "",
        str(report["proof_pack_boundary"]),
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Actions evaluated: `{summary['total_actions']}`",
        f"- Posture counts: `{summary['posture_counts']}`",
        f"- Route state counts: `{summary['route_state_counts']}`",
        f"- Ref-gate counts: `{summary['ref_gate_counts']}`",
        f"- Non-executable routes: `{summary['non_executable_routes']}`",
        f"- Valid DLL ledgers: `{summary['valid_ledgers']}`",
        f"- Autonomy state: `{summary['autonomy_state']}`",
        f"- Pilot fit: `{report['pilot_fit']['fit']}`",
        "",
        "## Cloud Reason Codes",
        "",
        "| Reason code | Count | Meaning |",
        "| --- | ---: | --- |",
    ]
    for code, count in report["cloud_reason_code_counts"].items():
        lines.append(f"| `{code}` | {count} | {report['cloud_reason_code_labels'][code]} |")

    lines.extend(
        [
            "",
            "## Highest Exposure Actions",
            "",
            "| Action | Posture | Route | Exposure | Cloud reason codes |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for item in summary["highest_exposure_actions"]:
        record = next(record for record in report["records"] if record["action_id"] == item["action_id"])
        codes = ", ".join(f"`{code}`" for code in record["cloud_reason_codes"][:5])
        lines.append(
            f"| `{item['action_id']}` | `{item['posture']}` | `{item['route_state']}` | "
            f"{item['irreversible_exposure_score']} | {codes} |"
        )

    lines.extend(["", "## Work / Result / Impact", "", "| Work | Result | Impact |", "| --- | --- | --- |"])
    for item in report["work_result_impact_examples"]:
        lines.append(f"| {item['work']} | {item['result']} | {item['impact']} |")

    lines.extend(
        [
            "",
            "## Strategic Fit",
            "",
            str(report["strategic_fit"]["buyer_question"]),
            "",
            "Strongest first reviewers:",
        ]
    )
    for reviewer in report["strategic_fit"]["strongest_fit"]:
        lines.append(f"- {reviewer}")
    lines.extend(["", "Not claimed:"])
    for non_claim in report["strategic_fit"]["not_claimed"]:
        lines.append(f"- {non_claim}")

    lines.extend(
        [
            "",
            "## Recommended Next Step",
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


def _expand_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    expanded = copy.deepcopy(dict(payload))
    actions = []
    for action in payload["actions"]:
        actions.append(_variant(action, "base", 0.0, 0))
        actions.append(_variant(action, "degraded_evidence", 0.08, 1))
        actions.append(_variant(action, "expanded_scope", 0.12, 2))
    expanded["actions"] = actions
    expanded["workflow_context"] = (
        "Twenty-four metadata-only cloud administration proof scenarios expanded from IAM, network, database, "
        "Kubernetes, DNS, rotation, capacity, and backup-policy actions."
    )
    return expanded


def _variant(action: Mapping[str, Any], name: str, pressure: float, index: int) -> Dict[str, Any]:
    variant = copy.deepcopy(dict(action))
    variant["action_id"] = f"{action['action_id']}_{name}".upper()
    variant["description"] = f"{action['description']} Scenario variant: {name.replace('_', ' ')}."
    variant["base_action_risk"] = round(min(1.0, float(variant["base_action_risk"]) + pressure), 3)
    if name == "degraded_evidence":
        variant["evidence_validity"] = round(max(0.0, float(variant["evidence_validity"]) - 0.18), 3)
        variant["anomaly_pressure"] = round(min(1.0, float(variant["anomaly_pressure"]) + 0.12), 3)
        variant["authorization_confidence"] = round(max(0.0, float(variant["authorization_confidence"]) - 0.10), 3)
    elif name == "expanded_scope":
        variant["impact_scope"] = round(min(1.0, float(variant["impact_scope"]) + 0.12), 3)
        variant["containment_strength"] = round(max(0.0, float(variant["containment_strength"]) - 0.12), 3)
        variant["cancel_reliability"] = round(max(0.0, float(variant["cancel_reliability"]) - 0.08), 3)
        plan = variant["tool_plan"]
        plan["requested_scope_units"] = min(
            int(plan["max_scope_units"]),
            int(plan["requested_scope_units"]) + max(1, int(plan["max_scope_units"] * 0.12)),
        )
    variant["context"] = dict(variant["context"])
    variant["context"]["scenario_variant"] = name
    variant["tool_plan"] = dict(variant["tool_plan"])
    variant["tool_plan"]["plan_id"] = f"{variant['tool_plan']['plan_id']}_{name}_{index}"
    variant["tool_plan"]["metadata"] = dict(variant["tool_plan"].get("metadata", {}))
    variant["tool_plan"]["metadata"]["scenario_variant"] = name
    return variant


def _action_by_id(payload: Mapping[str, Any], action_id: str) -> Mapping[str, Any]:
    return next(action for action in payload["actions"] if action["action_id"] == action_id)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a cloud-admin proof pack from metadata-only SMERC actions.")
    parser.add_argument("--input", default="examples/cloud_admin_customer_eval_actions.json")
    parser.add_argument("--json-output", default="reports/cloud_admin_proof_pack/cloud_admin_proof_pack.json")
    parser.add_argument("--markdown-output", default="reports/cloud_admin_proof_pack/Cloud_Admin_Proof_Pack.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_cloud_admin_proof_pack(load_payload(args.input))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

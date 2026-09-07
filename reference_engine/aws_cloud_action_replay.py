from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.customer_evaluation import build_customer_evaluation, load_payload


VERSION = "smerc.aws-cloud-action-replay.v1"

AWS_REASON_CODE_LABELS = {
    "AGENTCORE_GATEWAY_BYPASS_RISK": "The request shape suggests an agent runtime path that bypasses a governed gateway, interceptor, or policy choke point.",
    "AGENTCORE_TOOL_SIDE_EFFECT": "The action invokes an agent tool target that can create external or customer-facing side effects.",
    "AUTOMATED_REMEDIATION_PRESSURE": "The action is triggered by operational pressure, where speed is useful but evidence and rollback still matter.",
    "CLOUDFORMATION_REPLACEMENT_RISK": "The infrastructure change may replace or recreate resources rather than only update reversible configuration.",
    "COST_VELOCITY_SPIKE": "The action can increase spend velocity faster than confidence in task completion or containment.",
    "CROSS_ACCOUNT_DELEGATION_RISK": "The action can extend trust or invocation authority across account boundaries.",
    "DRIFT_RECONCILIATION_RISK": "The action remediates drift where the live state may contain unmodeled operational intent.",
    "ECS_CAPACITY_SHIFT": "The action changes service capacity or regional placement while reliability evidence matters.",
    "EVIDENCE_INCOMPLETE": "Trusted evidence is not strong enough to support confident execution.",
    "IAM_SCOPE_EXPANSION": "The action can expand what a principal, role, runtime, or workload may do later.",
    "PRODUCTION_BLAST_RADIUS_WIDE": "The action targets production with broad enough scope to create meaningful blast radius.",
    "RDS_DATA_PLANE_RECOVERY_RISK": "The action touches stateful database resources where recovery path, snapshots, and rollback latency matter.",
    "ROLLBACK_UNCERTAIN": "Rollback, cancellation, or checkpoint support is weak for the proposed action.",
    "S3_POLICY_EXPOSURE": "The action can widen object, bucket, or data-access exposure.",
    "SECRETS_ROTATION_IMPACT": "Authentication material changes can interrupt dependent services if coordination or rollback fails.",
}

AWS_ALIGNMENT_LABELS = {
    "bedrock_agentcore_gateway": "Amazon Bedrock AgentCore Gateway-style governed entry point, policy, guardrail, and interceptor path.",
    "bedrock_agentcore_runtime": "Amazon Bedrock AgentCore Runtime-style session, invocation, identity, and runtime isolation path.",
    "cloudformation": "AWS CloudFormation change set and drift-aware change-management path.",
    "cloudwatch": "Amazon CloudWatch-style alarm, telemetry, and automated-remediation path.",
    "cost_management": "AWS cost-management and FinOps-style spend-velocity path.",
    "ecs": "Amazon ECS/Fargate-style service capacity and deployment-control path.",
    "iam": "AWS IAM least-privilege and role-policy path.",
    "rds": "Amazon RDS-style stateful data-plane administration path.",
    "resource_policy": "AWS resource-based policy and cross-account access path.",
    "s3": "Amazon S3-style data access and bucket-policy path.",
    "secrets_manager": "AWS Secrets Manager-style rotation and service-authentication path.",
}


def build_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    evaluation = build_customer_evaluation(payload)
    action_index = {action["action_id"]: action for action in payload["actions"]}
    reason_counts: Counter[str] = Counter()
    surface_counts: Counter[str] = Counter()
    work_items: list[Dict[str, str]] = []

    for record in evaluation["records"]:
        action = action_index[record["action_id"]]
        codes = aws_reason_codes(action, record)
        reason_counts.update(codes)
        alignment = aws_alignment(action)
        surface_counts[alignment["aws_surface"]] += 1
        record["aws_reason_codes"] = codes
        record["aws_reason_labels"] = {code: AWS_REASON_CODE_LABELS[code] for code in codes}
        record["aws_alignment"] = alignment
        record["work_result_impact"] = work_result_impact(action, record, codes)
        work_items.append(record["work_result_impact"])

    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_version": evaluation["version"],
        "scenario_count": len(evaluation["records"]),
        "summary": evaluation["summary"],
        "pilot_fit": evaluation["pilot_fit"],
        "autonomy_budget": evaluation["autonomy_budget"],
        "aws_reason_code_counts": dict(sorted(reason_counts.items())),
        "aws_reason_code_labels": AWS_REASON_CODE_LABELS,
        "aws_surface_counts": dict(sorted(surface_counts.items())),
        "aws_alignment_labels": AWS_ALIGNMENT_LABELS,
        "evidence_boundary": (
            "AWS Cloud Action Replay uses metadata-only AWS-style examples. It does not connect to AWS, invoke "
            "AgentCore, read CloudTrail, inspect CloudFormation stacks, call IAM, access S3, change RDS, execute "
            "CloudWatch remediation, rotate credentials, move funds, create infrastructure, or use customer telemetry. "
            "It is not AWS endorsement, AWS certification, production-readiness proof, or incident-reduction proof."
        ),
        "work_result_impact_examples": work_items[:8],
        "customer_evaluation": evaluation,
        "records": evaluation["records"],
        "strategic_fit": {
            "buyer_question": (
                "Can AWS-style platform teams let agentic cloud automation move faster while still constraining "
                "actions that are authorized but not recoverable enough to execute now?"
            ),
            "where_smerc_adds_a_question": (
                "AWS-style controls can govern who may call a runtime, gateway, target, role, change set, or "
                "remediation path. SMERC adds a pre-execution judgment about rollback, containment, evidence, "
                "blast radius, cost velocity, and the route to ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE."
            ),
            "strongest_first_reviewers": [
                "AWS platform engineering teams",
                "cloud security architecture teams",
                "SRE and incident automation owners",
                "AI-agent platform teams",
                "FinOps and cloud cost automation owners",
                "infrastructure-as-code governance teams",
            ],
            "not_claimed": [
                "AWS partnership",
                "AWS certification",
                "AWS production integration",
                "replacement for IAM, AgentCore Gateway, Bedrock Guardrails, CloudFormation, CloudTrail, CloudWatch, AWS Config, or human accountability",
            ],
        },
        "recommended_next_action": (
            "Ask an AWS-style reviewer to replace these examples with 5 to 25 metadata-only actions from one real "
            "workflow, then compare whether SMERC's recoverability posture changes their execution judgment."
        ),
    }


def aws_reason_codes(action: Mapping[str, Any], record: Mapping[str, Any]) -> list[str]:
    tool = str(action["tool"]).lower()
    action_type = str(action["action_type"]).lower()
    metadata = action["tool_plan"].get("metadata", {})
    surface = str(metadata.get("aws_surface", "")).lower()
    family = str(metadata.get("change_family", "")).lower()
    environment = str(metadata.get("environment", "")).lower()
    decision = record["decision"]
    ref_gate = record["ref_gate"]

    codes: list[str] = []
    if "agentcore" in tool or "agentcore" in surface:
        codes.append("AGENTCORE_TOOL_SIDE_EFFECT")
    if "bypass" in family or "direct_runtime" in action_type:
        codes.append("AGENTCORE_GATEWAY_BYPASS_RISK")
    if "iam" in tool or surface == "iam" or "identity" in family or "permission" in action_type:
        codes.append("IAM_SCOPE_EXPANSION")
    if "s3" in tool or surface == "s3" or "bucket" in action_type:
        codes.append("S3_POLICY_EXPOSURE")
    if "cloudformation" in tool and ("replace" in family or "changeset" in action_type):
        codes.append("CLOUDFORMATION_REPLACEMENT_RISK")
    if "drift" in tool or "drift" in family:
        codes.append("DRIFT_RECONCILIATION_RISK")
    if "ecs" in surface or "capacity" in family:
        codes.append("ECS_CAPACITY_SHIFT")
    if "rds" in surface or "database" in family or "cluster_delete" in action_type:
        codes.append("RDS_DATA_PLANE_RECOVERY_RISK")
    if "cloudwatch" in surface or "remediation" in family:
        codes.append("AUTOMATED_REMEDIATION_PRESSURE")
    if "cost" in surface or "cost_velocity" in family or action["tool_plan"]["side_effect_level"] == "financial":
        codes.append("COST_VELOCITY_SPIKE")
    if "secret" in tool or "auth_rotation" in action_type or surface == "secrets_manager":
        codes.append("SECRETS_ROTATION_IMPACT")
    if "cross_account" in family or "delegation" in action_type or surface == "resource_policy":
        codes.append("CROSS_ACCOUNT_DELEGATION_RISK")
    if "production" in environment and float(action["impact_scope"]) >= 0.65:
        codes.append("PRODUCTION_BLAST_RADIUS_WIDE")
    if float(action["reversibility"]) < 0.45 or float(action["rollback_latency"]) > 0.65 or not action["tool_plan"].get("supports_rollback", False):
        codes.append("ROLLBACK_UNCERTAIN")
    if float(action["evidence_validity"]) < 0.6 or ref_gate["status"] == "fail":
        codes.append("EVIDENCE_INCOMPLETE")
    if decision["posture"] == "DENY" and "ROLLBACK_UNCERTAIN" not in codes:
        codes.append("ROLLBACK_UNCERTAIN")

    return sorted(set(codes)) or ["EVIDENCE_INCOMPLETE"]


def aws_alignment(action: Mapping[str, Any]) -> Dict[str, str]:
    metadata = action["tool_plan"].get("metadata", {})
    surface = str(metadata.get("aws_surface", "aws_cloud_action"))
    return {
        "cloud_provider": str(metadata.get("cloud_provider", "aws")),
        "aws_surface": surface,
        "aws_alignment": AWS_ALIGNMENT_LABELS.get(surface, "AWS-style cloud automation or platform-governance path."),
        "change_family": str(metadata.get("change_family", "unknown")),
        "environment": str(metadata.get("environment", "unknown")),
    }


def work_result_impact(action: Mapping[str, Any], record: Mapping[str, Any], codes: list[str]) -> Dict[str, str]:
    posture = record["decision"]["posture"]
    route = record["sparta_route"]["route_state"]
    exposure = record["decision"]["scores"]["irreversible_exposure_score"]
    surface = aws_alignment(action)["aws_surface"]
    work = (
        f"Evaluate AWS-style `{surface}` action `{action['action_id']}` before execution using hard evidence gates, "
        "recoverability scoring, Governance Routing Workbench routes, and Decision Lifecycle Ledger evidence."
    )
    result = f"SMERC returned `{posture}`, routed `{route}`, and assigned AWS reason codes {', '.join(codes)}."
    if posture == "DENY":
        impact = "The action is blocked until the request is repaired, narrowed, or resubmitted with stronger evidence."
    elif posture == "FREEZE":
        impact = "The action pauses so accountable review can decide whether a governed unlock is appropriate."
    elif posture == "THROTTLE":
        impact = "The action can continue only through constrained execution such as scope limits, preview, checkpointing, or rate limits."
    elif posture == "ESCALATE":
        impact = "The action moves to accountable review because pressure, authority, or recovery confidence is not routine."
    else:
        impact = "The action is allowed with replay evidence because recovery and containment are strong enough for this metadata-only case."
    return {
        "work": work,
        "result": result,
        "impact": f"{impact} Irreversible exposure score: {exposure}.",
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# AWS Cloud Action Replay",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This proof pack shows how SMERC evaluates AWS-style cloud and AI-agent infrastructure actions before they change runtime behavior, permissions, data access, infrastructure state, database resources, remediation paths, cross-account trust, or spend velocity.",
        "",
        "The useful question is narrow: after normal authorization says an action can be attempted, is this specific action recoverable, bounded, evidenced, and safe to proceed right now?",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Work / Result / Impact",
        "",
        "Work: run twelve AWS-style metadata actions through SMERC's customer-evaluation contract, hard evidence gates, recoverability scoring, Governance Routing Workbench routes, autonomy budgeting, and Decision Lifecycle Ledger proof.",
        "",
        f"Result: `{summary['total_actions']}` actions evaluated with posture counts `{summary['posture_counts']}`, route counts `{summary['route_state_counts']}`, and `{summary['valid_ledgers']}` valid ledgers.",
        "",
        "Impact: a reviewer can see where authorized cloud or agent actions should be allowed, slowed, paused, blocked, or escalated before side effects occur. This turns the AWS discussion into a runnable proof instead of a pitch.",
        "",
        "## Summary",
        "",
        f"- Actions evaluated: `{summary['total_actions']}`",
        f"- Posture counts: `{summary['posture_counts']}`",
        f"- Route state counts: `{summary['route_state_counts']}`",
        f"- Ref-gate counts: `{summary['ref_gate_counts']}`",
        f"- Agent identity-gate counts: `{summary['identity_gate_counts']}`",
        f"- Non-executable routes: `{summary['non_executable_routes']}`",
        f"- Valid DLL ledgers: `{summary['valid_ledgers']}`",
        f"- Autonomy state: `{summary['autonomy_state']}`",
        f"- Pilot fit: `{report['pilot_fit']['fit']}`",
        "",
        "## AWS-Style Surfaces",
        "",
        "| Surface | Count | Alignment |",
        "| --- | ---: | --- |",
    ]
    for surface, count in report["aws_surface_counts"].items():
        lines.append(f"| `{surface}` | {count} | {report['aws_alignment_labels'].get(surface, 'AWS-style cloud action')} |")

    lines.extend(["", "## AWS Reason Codes", "", "| Reason code | Count | Meaning |", "| --- | ---: | --- |"])
    for code, count in report["aws_reason_code_counts"].items():
        lines.append(f"| `{code}` | {count} | {report['aws_reason_code_labels'][code]} |")

    lines.extend(
        [
            "",
            "## Scenario Results",
            "",
            "| Action | Surface | Posture | Route | Exposure | Reason codes |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for record in report["records"]:
        alignment = record["aws_alignment"]
        codes = ", ".join(f"`{code}`" for code in record["aws_reason_codes"][:5])
        lines.append(
            f"| `{record['action_id']}` | `{alignment['aws_surface']}` | `{record['decision']['posture']}` | "
            f"`{record['sparta_route']['route_state']}` | "
            f"{record['decision']['scores']['irreversible_exposure_score']} | {codes} |"
        )

    lines.extend(["", "## Reviewer Examples", "", "| Work | Result | Impact |", "| --- | --- | --- |"])
    for item in report["work_result_impact_examples"]:
        lines.append(f"| {item['work']} | {item['result']} | {item['impact']} |")

    lines.extend(
        [
            "",
            "## Strategic Fit",
            "",
            str(report["strategic_fit"]["buyer_question"]),
            "",
            str(report["strategic_fit"]["where_smerc_adds_a_question"]),
            "",
            "Strongest first reviewers:",
        ]
    )
    for reviewer in report["strategic_fit"]["strongest_first_reviewers"]:
        lines.append(f"- {reviewer}")
    lines.extend(["", "Not claimed:"])
    for item in report["strategic_fit"]["not_claimed"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Recommended Next Step", "", str(report["recommended_next_action"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an AWS-style cloud action replay report from metadata-only SMERC actions.")
    parser.add_argument("--input", default="examples/aws_cloud_action_replay_actions.json")
    parser.add_argument("--json-output", default="reports/aws_cloud_action_replay/aws_cloud_action_replay.json")
    parser.add_argument("--markdown-output", default="reports/aws_cloud_action_replay/AWS_Cloud_Action_Replay.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_report(load_payload(args.input))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

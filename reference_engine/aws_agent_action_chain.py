from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from reference_engine.customer_evaluation import build_customer_evaluation, load_payload


VERSION = "smerc.aws-agent-action-chain.v1"


CHAIN_STAGE_LABELS = {
    "agent_action": "AI agent proposes an action.",
    "bedrock_guardrail": "Bedrock-style content/model guardrail reviews the prompt, response, or tool intent.",
    "smerc_recoverability_gate": "SMERC checks recoverability, blast radius, rollback, evidence, anomaly pressure, and cost velocity.",
    "dynamic_iam_or_ssm": "Dynamic IAM, Systems Manager, CloudFormation, CloudWatch, or another execution path receives only the route SMERC allows.",
    "cloud_execution_evidence": "CloudTrail-, CloudWatch-, change-set-, runtime-, or tool-result-shaped evidence proves what actually happened.",
}


def build_report(payload: Mapping[str, Any]) -> Dict[str, Any]:
    evaluation = build_customer_evaluation(payload)
    action_index = {action["action_id"]: action for action in payload["actions"]}
    chain_records: list[Dict[str, Any]] = []
    surface_counts: Counter[str] = Counter()
    guardrail_counts: Counter[str] = Counter()
    checkpoint_counts: Counter[str] = Counter()

    for record in evaluation["records"]:
        action = action_index[record["action_id"]]
        metadata = action["tool_plan"].get("metadata", {})
        surface = str(metadata.get("aws_surface", "aws_cloud_action"))
        guardrail_status = str(metadata.get("bedrock_guardrail_status", "unknown"))
        checkpoint_state = str(metadata.get("rollback_checkpoint_state", "unknown"))
        surface_counts[surface] += 1
        guardrail_counts[guardrail_status] += 1
        checkpoint_counts[checkpoint_state] += 1
        chain_records.append(build_chain_record(action, record))

    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_version": evaluation["version"],
        "scenario_count": len(chain_records),
        "summary": {
            "posture_counts": evaluation["summary"]["posture_counts"],
            "route_state_counts": evaluation["summary"]["route_state_counts"],
            "valid_ledgers": evaluation["summary"]["valid_ledgers"],
            "bedrock_guardrail_counts": dict(sorted(guardrail_counts.items())),
            "rollback_checkpoint_counts": dict(sorted(checkpoint_counts.items())),
            "aws_surface_counts": dict(sorted(surface_counts.items())),
        },
        "chain_stage_labels": CHAIN_STAGE_LABELS,
        "evidence_boundary": (
            "AWS Agent Action Chain is metadata-only AWS-style proof. It does not connect to AWS, invoke Amazon "
            "Bedrock, modify Bedrock Guardrails, call IAM, run Systems Manager, apply CloudFormation, read "
            "CloudTrail, read CloudWatch, create infrastructure, change permissions, or prove AWS endorsement. "
            "It shows where SMERC could sit as a recoverability gate after content/model guardrails and before "
            "cloud execution."
        ),
        "positioning": {
            "plain_language": (
                "Bedrock-style guardrails can answer whether the agent content or model behavior appears allowed. "
                "IAM can answer whether the caller is authorized. SMERC adds the missing pre-execution question: "
                "is this authorized action recoverable, bounded, evidenced, and safe to execute right now?"
            ),
            "recommended_phrasing": (
                "SMERC fits between Bedrock-style guardrails and AWS execution paths as a recoverability-aware "
                "action gate for AI agents, Dynamic IAM, Systems Manager automation, CloudFormation changes, "
                "CloudWatch remediation, and cost-sensitive cloud actions."
            ),
            "not_claimed": [
                "native AWS integration",
                "AWS endorsement",
                "AWS certification",
                "production enforcement",
                "replacement for Bedrock Guardrails, IAM, Systems Manager, CloudTrail, CloudWatch, CloudFormation, or human accountability",
            ],
        },
        "customer_evaluation": evaluation,
        "records": chain_records,
        "recommended_next_action": (
            "Ask an AWS-style platform reviewer for 5 to 25 safe metadata-only action-chain examples that include "
            "guardrail status, authorization state, rollback checkpoint state, expected evidence, and whether the "
            "action created an irreversible or cost-sensitive side effect."
        ),
    }


def build_chain_record(action: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    metadata = action["tool_plan"].get("metadata", {})
    posture = record["decision"]["posture"]
    route_state = record["sparta_route"]["route_state"]
    return {
        "action_id": record["action_id"],
        "description": action["description"],
        "aws_surface": metadata.get("aws_surface", "aws_cloud_action"),
        "bedrock_guardrail_status": metadata.get("bedrock_guardrail_status", "unknown"),
        "iam_authorized": metadata.get("iam_authorized", "unknown"),
        "dynamic_iam_policy_state": metadata.get("dynamic_iam_policy_state", "unknown"),
        "rollback_checkpoint_state": metadata.get("rollback_checkpoint_state", "unknown"),
        "expected_evidence": metadata.get("expected_evidence", []),
        "smerc_posture": posture,
        "smerc_route_state": route_state,
        "irreversible_exposure_score": record["decision"]["scores"]["irreversible_exposure_score"],
        "ref_gate_status": record["ref_gate"]["status"],
        "valid_ledger": record["decision_lifecycle_ledger"]["verification"]["valid"],
        "work_result_impact": chain_work_result_impact(action, record),
    }


def chain_work_result_impact(action: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, str]:
    metadata = action["tool_plan"].get("metadata", {})
    surface = metadata.get("aws_surface", "aws_cloud_action")
    posture = record["decision"]["posture"]
    route_state = record["sparta_route"]["route_state"]
    checkpoint = metadata.get("rollback_checkpoint_state", "unknown")
    guardrail = metadata.get("bedrock_guardrail_status", "unknown")
    evidence = ", ".join(metadata.get("expected_evidence", [])[:3])
    return {
        "work": (
            f"Evaluate `{action['action_id']}` through the chain: agent action, Bedrock-style guardrail `{guardrail}`, "
            f"SMERC recoverability gate, `{surface}` execution path, and expected evidence."
        ),
        "result": f"SMERC returned `{posture}` and routed `{route_state}` with rollback checkpoint `{checkpoint}`.",
        "impact": (
            "The reviewer can see whether content/model approval and IAM authorization are enough, or whether the "
            f"action should be slowed, paused, blocked, or escalated before execution. Expected evidence begins with: {evidence}."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# AWS Agent Action Chain",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Version: `{report['version']}`",
        "",
        "## Purpose",
        "",
        "This proof shows where SMERC fits in an AWS-style AI-agent action path:",
        "",
        "`AI Agent Action -> Bedrock-style Guardrail -> SMERC Recoverability Gate -> Dynamic IAM / Systems Manager / Cloud Execution -> Postcondition Evidence`",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Work / Result / Impact",
        "",
        f"Work: run `{report['scenario_count']}` metadata-only AWS-style agent action chains through SMERC after a Bedrock-style guardrail result and before IAM, Systems Manager, CloudFormation, CloudWatch, S3 policy changes, cross-account delegation, retry loops, cost-scaling, or cloud execution.",
        "",
        f"Result: `{report['scenario_count']}` chains evaluated with posture counts `{report['summary']['posture_counts']}`, route counts `{report['summary']['route_state_counts']}`, and `{report['summary']['valid_ledgers']}` valid ledgers.",
        "",
        "Impact: this makes the AWS story concrete. SMERC does not replace guardrails or IAM; it adds recoverability judgment before an already-authorized action creates side effects.",
        "",
        "## Chain Stages",
        "",
    ]
    for stage, label in report["chain_stage_labels"].items():
        lines.append(f"- `{stage}`: {label}")

    lines.extend(["", "## Positioning", "", report["positioning"]["plain_language"], "", report["positioning"]["recommended_phrasing"], "", "Not claimed:"])
    for item in report["positioning"]["not_claimed"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Summary", ""])
    for key, value in report["summary"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(
        [
            "",
            "## Scenario Results",
            "",
            "| Action | Surface | Guardrail | IAM | Checkpoint | SMERC | Route | Ref gate |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in report["records"]:
        lines.append(
            f"| `{record['action_id']}` | `{record['aws_surface']}` | `{record['bedrock_guardrail_status']}` | "
            f"`{record['iam_authorized']}` | `{record['rollback_checkpoint_state']}` | "
            f"`{record['smerc_posture']}` | `{record['smerc_route_state']}` | `{record['ref_gate_status']}` |"
        )

    lines.extend(["", "## Reviewer Examples", "", "| Work | Result | Impact |", "| --- | --- | --- |"])
    for record in report["records"]:
        item = record["work_result_impact"]
        lines.append(f"| {item['work']} | {item['result']} | {item['impact']} |")

    lines.extend(["", "## Recommended Next Action", "", str(report["recommended_next_action"]), ""])
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
    parser = argparse.ArgumentParser(description="Build an AWS-style agent action chain report from metadata-only SMERC actions.")
    parser.add_argument("--input", default="examples/aws_agent_action_chain.json")
    parser.add_argument("--json-output", default="reports/aws_agent_action_chain/aws_agent_action_chain.json")
    parser.add_argument("--markdown-output", default="reports/aws_agent_action_chain/AWS_Agent_Action_Chain.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_report(load_payload(args.input))
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

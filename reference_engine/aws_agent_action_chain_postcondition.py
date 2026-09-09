from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from reference_engine.aws_agent_action_chain import build_report as build_chain_report
from reference_engine.aws_postcondition_evidence import (
    build_aws_postcondition_report,
    load_aws_observations,
    render_markdown as render_aws_postcondition_markdown,
    write_outputs as write_aws_postcondition_outputs,
)
from reference_engine.customer_evaluation import load_payload


VERSION = "smerc.aws-agent-action-chain-postcondition.v1"


def build_report(action_payload: Mapping[str, Any], observations_path: str | Path) -> dict[str, Any]:
    chain_report = build_chain_report(action_payload)
    postcondition = build_aws_postcondition_report(
        chain_report["customer_evaluation"],
        load_aws_observations(observations_path),
    )
    return {
        **postcondition,
        "version": VERSION,
        "source_chain_version": chain_report["version"],
        "chain_summary": chain_report["summary"],
        "chain_positioning": chain_report["positioning"],
        "work_result_impact": {
            "work": (
                "Run AWS-style agent action chains through SMERC, then compare the required route controls with "
                "safe postcondition observations modeled on guardrail, IAM, Systems Manager, CloudFormation, "
                "CloudWatch, cost, CloudTrail, runtime, and tool-result evidence."
            ),
            "result": (
                f"Evaluated {chain_report['scenario_count']} action chains and assessed "
                f"{postcondition['observed_actions']} postcondition observation sets with statuses "
                f"{postcondition['aws_postcondition_status_counts']}."
            ),
            "impact": (
                "SMERC can show not only where the recoverability gate sits, but also what evidence would prove "
                "that slowed, blocked, or constrained AWS-style actions actually followed the required route."
            ),
        },
        "recommended_next_action": (
            "Ask an AWS-style reviewer for 5 to 25 safe action-chain examples and matching observation summaries "
            "so SMERC can compare guardrail status, IAM authorization, route controls, and postcondition evidence "
            "without live AWS access."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    base = render_aws_postcondition_markdown(report)
    return base.replace(
        "# AWS Postcondition Evidence Report",
        "# AWS Agent Action Chain Postcondition Evidence",
        1,
    ).replace(
        "This report shows how AWS-style observation metadata could prove whether SMERC-required controls actually happened after a route decision.",
        "This report shows whether AWS-style action-chain observation metadata can prove that SMERC-required controls actually happened after the recoverability route.",
        1,
    )


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build AWS agent action chain postcondition evidence from metadata-only examples.")
    parser.add_argument("--actions", default="examples/aws_agent_action_chain.json")
    parser.add_argument("--observations", default="examples/aws_agent_action_chain_observations.json")
    parser.add_argument("--json-output", default="reports/aws_agent_action_chain_postcondition/aws_agent_action_chain_postcondition.json")
    parser.add_argument("--markdown-output", default="reports/aws_agent_action_chain_postcondition/AWS_Agent_Action_Chain_Postcondition_Evidence.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_report(load_payload(args.actions), args.observations)
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

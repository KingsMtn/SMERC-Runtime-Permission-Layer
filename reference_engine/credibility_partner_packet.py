from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.credibility-partner-review-packet.v1"
DEFAULT_ATLAS = Path("reports/governance_pattern_atlas.json")
PUBLIC_LINKS = {
    "github_repository": "https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer",
    "public_demo_home": "https://admirable-sorbet-9986d5.netlify.app/",
    "ciso_review_page": "https://admirable-sorbet-9986d5.netlify.app/ciso.html",
    "github_actions_pilot_page": "https://admirable-sorbet-9986d5.netlify.app/github-action.html",
}


def load_atlas(path: str | Path = DEFAULT_ATLAS) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("governance pattern atlas must be a JSON object")
    required = {"version", "total_scenarios", "total_delta_count", "weighted_delta_rate", "patterns"}
    missing = sorted(required - set(payload))
    if missing:
        raise ValueError(f"governance pattern atlas missing field(s): {', '.join(missing)}")
    if not isinstance(payload["patterns"], list) or not payload["patterns"]:
        raise ValueError("governance pattern atlas must contain at least one pattern")
    return payload


def build_packet(atlas: Mapping[str, Any]) -> Dict[str, Any]:
    review_questions = [
        "Do the GitHub Actions and automation scenarios resemble actions your team sees or expects to see?",
        "Where would SMERC create useful restraint versus unnecessary noise?",
        "Which inputs would need customer-specific calibration before you would trust the scores?",
        "Which workflow should be tested first in shadow mode?",
        "What existing controls already solve this problem for you?",
        "Would replayable decision evidence help security, platform, audit, or incident review?",
        "What result would make you willing to continue from review into a bounded pilot?",
    ]
    pilot_fit_questions = [
        {
            "question": "Do AI agents or automation create deployment, infrastructure, security, data, finance, or customer-communication side effects?",
            "strong_fit_signal": "Yes, and those actions are increasing.",
            "weak_fit_signal": "No meaningful automated side effects exist yet.",
        },
        {
            "question": "Can the first pilot run in shadow mode without blocking production?",
            "strong_fit_signal": "Yes, scoring can observe and compare against reviewer judgment.",
            "weak_fit_signal": "No, the organization requires immediate enforcement or no access at all.",
        },
        {
            "question": "Can the prospect provide metadata-only examples without secrets or customer data?",
            "strong_fit_signal": "Yes, action descriptions and risk metadata can be shared safely.",
            "weak_fit_signal": "No, even sanitized workflow metadata cannot be shared.",
        },
        {
            "question": "Is there an accountable security, platform, or AI-governance reviewer?",
            "strong_fit_signal": "Yes, a named reviewer can label agreement, false release, false restraint, and useful restraint.",
            "weak_fit_signal": "No owner exists for review labels or go/no-go decisions.",
        },
        {
            "question": "Would recoverability scoring be judged separately from existing allow/deny policy?",
            "strong_fit_signal": "Yes, the team wants to test whether recovery capacity changes decisions.",
            "weak_fit_signal": "No, the team only wants identity/access policy or generic AI guardrails.",
        },
    ]
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "public_links": PUBLIC_LINKS,
        "positioning": {
            "one_sentence": (
                "SMERC is runtime permission infrastructure that scores whether automated actions are "
                "recoverable enough to execute before they create real side effects."
            ),
            "primary_wedge": "GitHub Actions and AI-assisted software delivery shadow-mode pilot",
            "credibility_partner_ask": (
                "Review the evidence package, challenge the scenarios, and decide whether a metadata-only "
                "shadow-mode pilot is worth testing."
            ),
        },
        "atlas_summary": {
            "version": atlas["version"],
            "pattern_count": atlas.get("pattern_count"),
            "total_scenarios": atlas["total_scenarios"],
            "total_delta_count": atlas["total_delta_count"],
            "weighted_delta_rate": atlas["weighted_delta_rate"],
            "patterns": [
                {
                    "discipline": pattern["discipline"],
                    "scenario_count": pattern["scenario_count"],
                    "delta_count": pattern["delta_count"],
                    "delta_rate": pattern["delta_rate"],
                    "smerc_adds": pattern["smerc_adds"],
                    "does_not_replace": pattern["does_not_replace"],
                    "strongest_example": pattern["strongest_example"],
                    "benchmark_report_path": pattern["benchmark_report_path"],
                }
                for pattern in atlas["patterns"]
            ],
        },
        "review_path": [
            {
                "minutes": "0-5",
                "step": "Read the claim and limits.",
                "evidence": ["docs/Plain_English_Product_Overview.md", "docs/Governance_Pattern_Atlas.md"],
            },
            {
                "minutes": "5-10",
                "step": "Inspect the consolidated benchmark evidence.",
                "evidence": ["reports/Governance_Pattern_Atlas.md"],
            },
            {
                "minutes": "10-15",
                "step": "Inspect the recoverability scoring engine and action boundary.",
                "evidence": ["reference_engine/recoverability_engine.py", "specification/SMERC_Action_Language_v1.md"],
            },
            {
                "minutes": "15-20",
                "step": "Inspect GitHub Actions pilot path and execution controls.",
                "evidence": ["pilot_package/GitHub_Actions_Pilot_Launch_Runbook.md", "docs/SPARTa_Router_Operations.md"],
            },
            {
                "minutes": "20-25",
                "step": "Inspect replay and audit evidence.",
                "evidence": ["docs/Decision_Lifecycle_Ledger.md", "docs/Governance_Report_Generator.md"],
            },
            {
                "minutes": "25-30",
                "step": "Answer pilot-fit questions and decide whether a credibility review should continue.",
                "evidence": ["pilot_package/Pilot_Evaluation_Checklist.md", "pilot_package/Pilot_Handoff_Checklist.md"],
            },
        ],
        "review_questions": review_questions,
        "pilot_fit_questions": pilot_fit_questions,
        "not_claiming": [
            "SMERC is not production-certified.",
            "SMERC is not customer-validated yet.",
            "SMERC is not a replacement for OPA, IAM, GRC, SIEM, SOAR, EDR, ServiceNow, Jira, AML, or model-risk systems.",
            "SMERC is not claiming incident reduction, compliance attestation, or product-market fit.",
            "SMERC should begin in shadow mode before any enforcement pilot.",
        ],
        "desired_partner_response": [
            "The scenarios resemble a real workflow we care about.",
            "The deltas are useful enough to test rather than only interesting on paper.",
            "We can provide metadata-only examples for shadow-mode scoring.",
            "A named reviewer can compare SMERC output against human judgment.",
            "A 30-day or 90-day bounded pilot is worth discussing.",
        ],
    }


def render_markdown(packet: Mapping[str, Any]) -> str:
    links = packet["public_links"]
    positioning = packet["positioning"]
    atlas = packet["atlas_summary"]
    lines = [
        "# SMERC Credibility Partner Review Packet",
        "",
        f"Generated at: `{packet['generated_at']}`",
        "",
        "## Purpose",
        "",
        "This packet is for a serious external reviewer: CISO, security architect, platform engineering leader, reliability leader, or AI-governance lead.",
        "",
        "The review question is narrow:",
        "",
        "> Is SMERC credible enough to test in shadow mode against real workflow metadata?",
        "",
        "## Positioning",
        "",
        f"- One sentence: {positioning['one_sentence']}",
        f"- Primary wedge: `{positioning['primary_wedge']}`",
        f"- Credibility partner ask: {positioning['credibility_partner_ask']}",
        "",
        "## Public Links",
        "",
        f"- GitHub repository: {links['github_repository']}",
        f"- Public demo home: {links['public_demo_home']}",
        f"- CISO review page: {links['ciso_review_page']}",
        f"- GitHub Actions pilot page: {links['github_actions_pilot_page']}",
        "",
        "## What The Atlas Shows",
        "",
        f"- Pattern count: `{atlas['pattern_count']}`",
        f"- Total scenarios: `{atlas['total_scenarios']}`",
        f"- Total deltas: `{atlas['total_delta_count']}`",
        f"- Weighted delta rate: `{atlas['weighted_delta_rate']}`",
        "",
        "| Discipline | Scenarios | Deltas | Delta Rate | Strongest Example |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for pattern in atlas["patterns"]:
        example = pattern["strongest_example"]
        lines.append(
            f"| {pattern['discipline']} | {pattern['scenario_count']} | {pattern['delta_count']} | "
            f"{pattern['delta_rate']} | `{example['scenario_id']}` -> `{example['smerc_posture']}` |"
        )
    lines.extend(
        [
            "",
            "## 30-Minute Review Path",
            "",
            "| Time | Step | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for item in packet["review_path"]:
        evidence = ", ".join(f"`{path}`" for path in item["evidence"])
        lines.append(f"| {item['minutes']} | {item['step']} | {evidence} |")
    lines.extend(["", "## Questions For The Reviewer", ""])
    for question in packet["review_questions"]:
        lines.append(f"- {question}")
    lines.extend(["", "## Pilot-Fit Questions", ""])
    for item in packet["pilot_fit_questions"]:
        lines.extend(
            [
                f"### {item['question']}",
                "",
                f"- Strong fit signal: {item['strong_fit_signal']}",
                f"- Weak fit signal: {item['weak_fit_signal']}",
                "",
            ]
        )
    lines.extend(["## What SMERC Is Not Claiming", ""])
    for item in packet["not_claiming"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Desired Partner Response", ""])
    for item in packet["desired_partner_response"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Suggested Outreach Paragraph",
            "",
            "I am looking for a credibility review of SMERC, a runtime permission layer for AI-agent and automation actions. The current prototype scores whether proposed actions are recoverable enough to allow, throttle, freeze, deny, or escalate before execution. The first pilot wedge is GitHub Actions shadow-mode scoring for AI-assisted code, deployment, and infrastructure workflows. I am not asking you to treat this as production-ready. I am asking whether the evidence package is credible enough to test against metadata-only examples from a real workflow.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(packet: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(packet), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC credibility partner review packet.")
    parser.add_argument("--atlas", default=str(DEFAULT_ATLAS))
    parser.add_argument("--json-output", default="reports/credibility_partner_review_packet.json")
    parser.add_argument("--markdown-output", default="reports/Credibility_Partner_Review_Packet.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    packet = build_packet(load_atlas(args.atlas))
    write_outputs(packet, args.json_output, args.markdown_output)
    print(json.dumps(packet, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

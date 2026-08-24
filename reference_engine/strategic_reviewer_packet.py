from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


VERSION = "smerc.strategic-reviewer-evidence-packet.v1"
DEFAULT_OUTPUT_DIR = Path("reports/strategic_reviewer_packet")

PUBLIC_LINKS = {
    "strategic_review_page": "https://admirable-sorbet-9986d5.netlify.app/strategic-review.html",
    "github_repository": "https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer",
    "github_actions_ci": "https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions?query=branch%3Amain",
    "github_actions_pilot": "https://admirable-sorbet-9986d5.netlify.app/github-action.html",
    "mcp_governance": "https://admirable-sorbet-9986d5.netlify.app/mcp-governance.html",
}

EVIDENCE_ITEMS = [
    {
        "id": "strategic_positioning",
        "source": "docs/Strategic_Acquisition_Positioning.md",
        "category": "strategic",
        "why_it_matters": "Frames SMERC as a platform control pattern rather than a small standalone app.",
    },
    {
        "id": "strategic_buyer_map",
        "source": "docs/Strategic_Buyer_Map.md",
        "category": "strategic",
        "why_it_matters": "Maps likely strategic buyer categories and the main objections each would raise.",
    },
    {
        "id": "platform_fit",
        "source": "docs/Why_SMERC_Fits_Strategic_Platforms.md",
        "category": "strategic",
        "why_it_matters": "Explains where SMERC fits beside IAM, OPA, AI gateways, approvals, and audit logs.",
    },
    {
        "id": "ip_asset_map",
        "source": "docs/IP_Asset_Map.md",
        "category": "ip",
        "why_it_matters": "Separates potentially stronger technical mechanisms from weak broad claims.",
    },
    {
        "id": "technical_diligence_index",
        "source": "docs/Technical_Diligence_Index.md",
        "category": "technical",
        "why_it_matters": "Gives reviewers a short implementation inspection path.",
    },
    {
        "id": "github_actions_pilot_readiness",
        "source": "reports/GitHub_Actions_Pilot_Readiness.md",
        "category": "pilot",
        "why_it_matters": "Shows the first narrow pilot path and readiness criteria.",
    },
    {
        "id": "mcp_governance_gateway",
        "source": "reports/MCP_Governance_Gateway_Report.md",
        "category": "mcp",
        "why_it_matters": "Shows MCP-style tool-call governance output.",
    },
    {
        "id": "ref_gated_runtime_proof",
        "source": "reports/Ref_Gated_Runtime_Proof.md",
        "category": "runtime",
        "why_it_matters": "Shows hard Ref gates before SMERC scoring, SPARTa routing, autonomy budget, and DLL evidence.",
    },
    {
        "id": "autonomy_continuance",
        "source": "reports/Autonomy_Continuance_Report.md",
        "category": "autonomy",
        "why_it_matters": "Shows Authority Provenance, Intent Integrity, Consequence Horizon, Collective Autonomy, and Right To Continue.",
    },
    {
        "id": "smerc_f_pilot_evidence",
        "source": "reports/SMERC_F_Pilot_Evidence_Packet.md",
        "category": "financial",
        "why_it_matters": "Shows the financial-action profile while preserving strict non-claim boundaries.",
    },
    {
        "id": "runtime_evidence_trust",
        "source": "reports/Runtime_Evidence_Trust_Gate_Report.md",
        "category": "trust",
        "why_it_matters": "Shows how SMERC limits weak agent-supplied metadata before recoverability scoring.",
    },
    {
        "id": "decision_lifecycle_ledger",
        "source": "reports/Decision_Lifecycle_Ledger_Example.md",
        "category": "ledger",
        "why_it_matters": "Shows request, evidence, decision, execution, outcome, and review memory.",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _copy_if_present(source: Path, output_dir: Path) -> Dict[str, Any]:
    if not source.exists():
        return {"source": source.as_posix(), "present": False, "copied_to": None}
    target = output_dir / source.name
    shutil.copy2(source, target)
    return {"source": source.as_posix(), "present": True, "copied_to": target.as_posix()}


def collect_evidence(
    *,
    evidence_items: Iterable[Mapping[str, str]] = EVIDENCE_ITEMS,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> Dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    collected = []
    for item in evidence_items:
        result = _copy_if_present(Path(item["source"]), output)
        collected.append(
            {
                "id": item["id"],
                "category": item["category"],
                "why_it_matters": item["why_it_matters"],
                **result,
            }
        )

    present_count = sum(1 for item in collected if item["present"])
    missing = [item["source"] for item in collected if not item["present"]]

    return {
        "version": VERSION,
        "generated_at": _utc_now(),
        "public_links": PUBLIC_LINKS,
        "review_question": (
            "Does SMERC fill a strategic runtime-control gap between access policy and real-world AI/automation execution?"
        ),
        "one_command": "python -m reference_engine.strategic_reviewer_packet --pretty",
        "output_dir": Path(output_dir).as_posix(),
        "summary": {
            "evidence_items": len(collected),
            "present_count": present_count,
            "missing_count": len(missing),
            "missing_sources": missing,
        },
        "evidence": collected,
        "strategic_reviewer_questions": [
            "Where would this sit in your platform or security stack?",
            "Which part would you build internally instead of buying?",
            "Does recoverability scoring change reviewer judgment or only repackage existing approval logic?",
            "Which workflow would be safest to test in shadow mode?",
            "What evidence would make this partnership- or acquisition-relevant?",
            "What existing product already solves enough of this problem?",
        ],
        "claim_boundaries": [
            "SMERC is pilot-grade, not production-certified.",
            "SMERC is not customer-proven to reduce incidents.",
            "SMERC does not replace IAM, OPA, AI gateways, approval workflows, SIEM, SOAR, GRC, code review, or human accountability.",
            "SMERC-F is not AML compliance, sanctions screening, custody, settlement, trading, or payment execution.",
            "Strategic value depends on external reviewer or pilot evidence, not repository size.",
        ],
        "requested_reviewer_signal": [
            "useful_gap_identified",
            "overlap_or_obviousness_identified",
            "pilot_workflow_named",
            "evidence_required_before_next_step",
        ],
    }


def render_markdown(packet: Mapping[str, Any]) -> str:
    summary = packet["summary"]
    links = packet["public_links"]
    lines = [
        "# SMERC Strategic Reviewer Evidence Packet",
        "",
        f"Version: `{packet['version']}`",
        f"Generated at: `{packet['generated_at']}`",
        "",
        "## Review Question",
        "",
        str(packet["review_question"]),
        "",
        "## Public Entry Points",
        "",
        f"- Strategic review page: {links['strategic_review_page']}",
        f"- GitHub repository: {links['github_repository']}",
        f"- Current GitHub Actions CI: {links['github_actions_ci']}",
        f"- GitHub Actions pilot page: {links['github_actions_pilot']}",
        f"- MCP governance page: {links['mcp_governance']}",
        "",
        "## Evidence Bundle",
        "",
        f"- Evidence items declared: `{summary['evidence_items']}`",
        f"- Evidence items copied: `{summary['present_count']}`",
        f"- Missing items: `{summary['missing_count']}`",
        "",
        "| Evidence | Category | Present | Copied To | Why It Matters |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in packet["evidence"]:
        copied = item["copied_to"] or ""
        lines.append(
            f"| `{item['source']}` | `{item['category']}` | `{item['present']}` | `{copied}` | {item['why_it_matters']} |"
        )
    lines.extend(["", "## Strategic Reviewer Questions", ""])
    lines.extend(f"- {question}" for question in packet["strategic_reviewer_questions"])
    lines.extend(["", "## Claim Boundaries", ""])
    lines.extend(f"- {boundary}" for boundary in packet["claim_boundaries"])
    lines.extend(["", "## Requested Reviewer Signal", ""])
    lines.extend(f"- `{signal}`" for signal in packet["requested_reviewer_signal"])
    lines.extend(
        [
            "",
            "## Suggested Outbound Message",
            "",
            "> I am looking for a skeptical strategic review of SMERC, a pilot-grade runtime permission layer for AI agents, MCP tool calls, GitHub Actions, cloud automation, and high-impact workflows. The specific question is whether recoverability-aware permissioning fills a real platform gap between access policy and execution. The public strategic review page and GitHub evidence packet are linked above. I am not claiming production certification or incident reduction; I am looking for feedback on whether this is worth a shadow-mode workflow review.",
            "",
        ]
    )
    if summary["missing_sources"]:
        lines.extend(["## Missing Sources", ""])
        lines.extend(f"- `{source}`" for source in summary["missing_sources"])
        lines.append("")
    return "\n".join(lines)


def write_outputs(packet: Mapping[str, Any], output_dir: str | Path = DEFAULT_OUTPUT_DIR) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "strategic_reviewer_packet.json").write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "Strategic_Reviewer_Evidence_Packet.md").write_text(render_markdown(packet), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC strategic reviewer evidence packet.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    packet = collect_evidence(output_dir=args.output_dir)
    write_outputs(packet, output_dir=args.output_dir)
    print(json.dumps(packet, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

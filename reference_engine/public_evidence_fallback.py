from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc.public-evidence-fallback.v1"
SOURCE_NAME = "SMERC Public Evidence Fallback"


SOURCE_PROFILES = [
    {
        "source_id": "lakmus_agent_failures",
        "name": "Lakmus Agent Failures",
        "url": "https://github.com/lakmus-ai/agent-failures",
        "metadata_origin": "realistic generated tasks run across multiple LLM APIs, then labeled with failure taxonomy and judge evidence",
        "useful_fields": ["task_domain", "failure_type", "subtype", "judge_evidence", "model_comparison", "pass_fail"],
        "smerc_mapping": "Map failure labels into missing evidence, wrong-tool selection, goal drift, unsupported claim, or constraint violation pressure before execution.",
        "source_class": "public_dataset",
        "priority": 2,
    },
    {
        "source_id": "agent_action_boundary_benchmark",
        "name": "Agent Action Boundary Benchmark",
        "url": "https://github.com/OndCo/Agent-Action-Boundary-Benchmark",
        "metadata_origin": "synthetic runtime-boundary corpus with approved_action, executed_action, policy, drift class, expected control outcome, runtime surface, and scenario family",
        "useful_fields": ["approved_action", "executed_action", "policy", "drift_class", "runtime_surface", "expected_control"],
        "smerc_mapping": "Map approval-execution drift into SMERC posture, route, rollback-path, and evidence-boundary decisions.",
        "source_class": "synthetic_benchmark_corpus",
        "priority": 1,
    },
    {
        "source_id": "agentshield_bench",
        "name": "AgentShield-Bench",
        "url": "https://huggingface.co/datasets/alirezaaminzadeh/agentshield-bench",
        "metadata_origin": "structured adversarial and benign tool-calling/MCP scenarios with trusted instructions, untrusted content, tools, canary secrets, expected safe behaviors, and attack success conditions",
        "useful_fields": ["attack_category", "tools", "expected_safe_behavior", "attack_success_conditions", "trusted_untrusted_boundary"],
        "smerc_mapping": "Derive metadata-only tool risk, trusted/untrusted evidence, expected safe behavior, and hard-deny conditions for Dynamic Schema Gate and MCP governance.",
        "source_class": "public_dataset",
        "priority": 1,
    },
    {
        "source_id": "crossmcp_bench",
        "name": "CrossMCP-Bench",
        "url": "https://huggingface.co/datasets/MLZoo/CrossMCP-Bench",
        "metadata_origin": "authorization-conditioned MCP scenarios across multi-server MCP architectures with attack and benign cases",
        "useful_fields": ["policy_category", "server_context", "tool_context", "attack_or_benign", "authorization_condition"],
        "smerc_mapping": "Map multi-server MCP authorization conditions into pre-execution posture and gateway route behavior.",
        "source_class": "public_dataset",
        "priority": 2,
    },
    {
        "source_id": "wetriedai_failure_repair",
        "name": "WeTriedAI Failure-Repair Corpus",
        "url": "https://wetriedai.com/dataset",
        "metadata_origin": "selected synthetic failures with prompt, first failed result, one correction, checks, scores, evidence notes, and limitations",
        "useful_fields": ["failure_check", "correction", "score_before", "score_after", "evidence_notes", "limitations"],
        "smerc_mapping": "Borrow the failure-to-correction audit shape for SMERC calibration reports and transition guidance.",
        "source_class": "synthetic_failure_repair_corpus",
        "priority": 3,
    },
    {
        "source_id": "agent_reliability_lab",
        "name": "Agent Reliability Lab",
        "url": "https://github.com/Hai-qq/agent-reliability-lab",
        "metadata_origin": "project-owned synthetic states in deterministic local environments with fault injection, state evaluators, runtime comparisons, and evidence bundles",
        "useful_fields": ["state_transition", "fault_injection", "runtime_intervention", "state_evidence", "verifiable_bundle"],
        "smerc_mapping": "Use fault-injected state transitions to test rollback evidence, cancellation reliability, and postcondition proof.",
        "source_class": "local_synthetic_runtime",
        "priority": 3,
    },
    {
        "source_id": "nika_network_incidents",
        "name": "NIKA Network Incidents Benchmark",
        "url": "https://sands-lab.github.io/nika/",
        "metadata_origin": "curated network incidents from emulated network scenarios with injectable root causes, telemetry, CLI interaction, traces, ground truth, and submissions",
        "useful_fields": ["incident_type", "root_cause", "telemetry_signal", "agent_trace", "ground_truth", "submission"],
        "smerc_mapping": "Map incident-remediation actions into recoverability posture, rollback evidence, and escalation when live network state is uncertain.",
        "source_class": "emulated_incident_benchmark",
        "priority": 4,
    },
    {
        "source_id": "mcp_attackbench",
        "name": "MCP-AttackBench",
        "url": "https://www.emergentmind.com/topics/mcp-attackbench",
        "metadata_origin": "MCP-specific samples from public data, real-world metadata, and GPT-augmented content for LLM-tool interactions",
        "useful_fields": ["attack_type", "tool_metadata", "invocation_context", "protocol_content", "manual_review_signal"],
        "smerc_mapping": "Map MCP attack metadata into schema, content-evidence, and tool-call route controls without importing operational exploit payloads.",
        "source_class": "mixed_public_augmented_benchmark",
        "priority": 4,
    },
]


def build_report() -> Dict[str, Any]:
    classes = Counter(profile["source_class"] for profile in SOURCE_PROFILES)
    priority = Counter(str(profile["priority"]) for profile in SOURCE_PROFILES)
    return {
        "version": VERSION,
        "generated_at": _now(),
        "source_name": SOURCE_NAME,
        "source_count": len(SOURCE_PROFILES),
        "source_class_counts": dict(sorted(classes.items())),
        "priority_counts": dict(sorted(priority.items())),
        "profiles": SOURCE_PROFILES,
        "recommended_build_order": [
            "Implement source registry and provenance report before importing any upstream rows.",
            "Map Agent Action Boundary Benchmark and AgentShield-Bench first because their metadata directly matches action boundary and tool-call governance.",
            "Use Lakmus Agent Failures for calibration language and failure taxonomy, not direct cloud-action proof.",
            "Use NIKA later for infrastructure remediation and rollback evidence once SMERC has a stronger live/sandbox story.",
            "Keep asking for customer-owned metadata, but do not block public-pattern progress on silence.",
        ],
        "work_result_impact": {
            "work": "Inspect public agent-failure, action-boundary, MCP-security, reliability, and incident benchmarks for metadata provenance.",
            "result": "SMERC has a fallback evidence map showing where adjacent projects obtained useful metadata and how SMERC can safely learn from their shapes.",
            "impact": "If outside reviewers do not provide 5 to 25 workflow actions, SMERC can keep building from public-pattern evidence while stating clearly that it is not customer validation.",
        },
        "evidence_boundary": (
            "This report is source-provenance planning, not an official benchmark run, endorsement, customer validation, "
            "production proof, or permission to copy upstream data. Each source needs license and version checks before "
            "any row-level replay. SMERC should prefer derived metadata and cite source boundaries."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Public Evidence Fallback Plan",
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
        "## Short Finding",
        "",
        "Adjacent projects are moving forward by building structured public, synthetic, generated, emulated, or benchmark-shaped datasets with explicit provenance. SMERC should do the same if no reviewer provides private metadata.",
        "",
        "## Source Provenance",
        "",
        "| Source | Metadata origin | What SMERC can learn | Priority |",
        "| --- | --- | --- | ---: |",
    ]
    for profile in report["profiles"]:
        lines.append(
            f"| [{profile['name']}]({profile['url']}) | {profile['metadata_origin']} | "
            f"{profile['smerc_mapping']} | {profile['priority']} |"
        )
    lines.extend(
        [
            "",
            "## Build Order",
            "",
        ]
    )
    for index, item in enumerate(report["recommended_build_order"], start=1):
        lines.append(f"{index}. {item}")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
            "## Outreach Bridge",
            "",
            "Public-pattern evidence should end with the same ask: replace these examples with 5 to 25 metadata-only actions from one real workflow.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], *, json_output: str | Path, markdown_output: str | Path) -> None:
    Path(json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(markdown_output).parent.mkdir(parents=True, exist_ok=True)
    Path(json_output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(markdown_output).write_text(render_markdown(report), encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC public evidence fallback provenance report.")
    parser.add_argument("--json-output", default="reports/public_evidence_fallback.json")
    parser.add_argument("--markdown-output", default="reports/Public_Evidence_Fallback_Plan.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_report()
    write_outputs(report, json_output=args.json_output, markdown_output=args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


VERSION = "smerc-f.pilot-evidence-packet.v1"

BOUNDARY_PHRASES = [
    "AML compliance",
    "legal compliance",
    "fraud detection",
    "sanctions screening",
    "custody",
    "settlement",
    "payment execution",
    "production certification",
]


def load_json(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def build_packet(
    *,
    source_ingestion: Mapping[str, Any],
    regulatory_context: Mapping[str, Any],
    public_replay: Mapping[str, Any],
) -> Dict[str, Any]:
    _require_version(source_ingestion, "smerc-f.source-ingestion.v1", "source_ingestion")
    _require_version(regulatory_context, "smerc-f.regulatory-context.v1", "regulatory_context")
    _require_version(public_replay, "smerc-f.public-data-replay.v1", "public_replay")

    public_scenarios = int(public_replay["scenario_count"])
    source_scenarios = int(source_ingestion["scenario_count"])
    context_scenarios = int(regulatory_context["scenario_count"])
    packet = {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "audience": [
            "CISO",
            "financial-services security reviewer",
            "payments risk owner",
            "treasury operations reviewer",
            "stablecoin or tokenized-finance infrastructure reviewer",
            "AI governance owner",
        ],
        "review_positioning": (
            "SMERC-F is a metadata-only shadow-mode recoverability review layer for automated financial actions. "
            "It asks whether an action that may be authorized by existing systems is recoverable enough to proceed."
        ),
        "artifact_summary": {
            "source_export_rows": int(source_ingestion["source_export_count"]),
            "source_normalized_rows": int(source_ingestion["normalized_row_count"]),
            "source_replay_scenarios": source_scenarios,
            "source_restraint_rate": float(source_ingestion["restraint_rate"]),
            "regulatory_context_rows": int(regulatory_context["regulatory_context_count"]),
            "regulatory_context_scenarios": context_scenarios,
            "regulatory_state_change_count": int(regulatory_context["state_change_count"]),
            "regulatory_state_change_rate": float(regulatory_context["state_change_rate"]),
            "baseline_restraint_rate": float(regulatory_context["baseline_restraint_rate"]),
            "context_enriched_restraint_rate": float(regulatory_context["context_enriched_restraint_rate"]),
            "public_replay_source_rows": int(public_replay["source_row_count"]),
            "public_replay_scenarios": public_scenarios,
            "public_replay_restraint_rate": float(public_replay["restraint_rate"]),
            "public_replay_decision_delta_rate": float(public_replay["decision_delta_rate"]),
        },
        "evidence_chain": [
            {
                "step": "source_export",
                "meaning": "Public-data-shaped source exports represent the kind of metadata a financial workflow or vendor system could provide.",
                "artifact": "examples/smerc_f_source_exports.json",
            },
            {
                "step": "normalization",
                "meaning": "Source exports are converted into SMERC-F replay rows without private customer data, wallet keys, or live execution instructions.",
                "artifact": "examples/smerc_f_normalized_source_rows.json",
            },
            {
                "step": "regulatory_context_overlay",
                "meaning": "Legislation-inspired operational context can adjust recoverability posture without interpreting law or determining compliance.",
                "artifact": "reports/SMERC_F_Regulatory_Context_Report.md",
            },
            {
                "step": "public_replay",
                "meaning": "SMERC-F expands source rows into replay variants and returns ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE with drivers and controls.",
                "artifact": "reports/SMERC_F_Public_Data_Replay_Report.md",
            },
            {
                "step": "reviewer_decision",
                "meaning": "A financial-services reviewer compares SMERC-F posture against current controls and human judgment before any enforcement discussion.",
                "artifact": "pilot_package/Fortune_500_Financial_Services_Review_Checklist.md",
            },
        ],
        "most_useful_examples": _top_examples(regulatory_context, public_replay),
        "pilot_go_no_go": {
            "go_conditions": [
                "one automated financial workflow family is available for metadata-only review",
                "reviewers can label whether SMERC-F posture is useful",
                "metadata excludes customer identifiers, raw regulated payloads, wallet keys, secrets, and live execution instructions",
                "existing financial controls remain source-of-truth during shadow mode",
                "reviewers accept the boundary that SMERC-F is not AML, sanctions, fraud, custody, settlement, or payment execution",
            ],
            "stop_conditions": [
                "safe metadata cannot be provided",
                "reviewers cannot compare posture with human judgment",
                "recoverability does not change review behavior",
                "the prospect wants production enforcement immediately",
                "the prospect expects SMERC-F to replace compliance, AML, fraud, sanctions, custody, settlement, or payment systems",
            ],
            "success_metrics": [
                "reviewer agreement rate",
                "false release candidates",
                "false restraint candidates",
                "useful THROTTLE decisions",
                "useful FREEZE decisions",
                "useful ESCALATE decisions",
                "metadata gaps",
                "posture distribution",
                "median and p95 scoring latency",
                "reviewer time impact",
            ],
        },
        "review_questions": [
            "Would SMERC-F have changed how your team reviewed any of these actions?",
            "Which metadata fields would your systems already provide?",
            "Which posture changes look useful versus noisy?",
            "Which actions should never be constrained because delay creates more harm?",
            "Which actions require stronger recoverability controls before automation proceeds?",
            "What evidence would be required before moving from observe mode to recommend mode?",
        ],
        "claim_boundaries": [
            "This packet is not AML compliance.",
            "This packet is not legal compliance.",
            "This packet is not fraud detection.",
            "This packet is not sanctions screening.",
            "This packet is not custody software.",
            "This packet is not settlement infrastructure.",
            "This packet is not payment execution.",
            "This packet is not production certification.",
            "This packet does not prove customer demand, incident reduction, regulatory approval, or production safety.",
        ],
        "recommended_next_action": (
            "Offer a 30-day metadata-only shadow-mode review for one financial workflow family, using reviewer labels "
            "to test whether recoverability posture changes review behavior."
        ),
    }
    packet["evidence_boundary"] = (
        "Pilot evidence packet only. It combines existing public-data-shaped SMERC-F artifacts into a review package. "
        "It does not prove customer demand, production suitability, incident reduction, legal compliance, AML compliance, "
        "fraud detection, sanctions screening, custody, settlement, payment execution, or production certification."
    )
    return packet


def render_markdown(packet: Mapping[str, Any]) -> str:
    summary = packet["artifact_summary"]
    lines = [
        "# SMERC-F Pilot Evidence Packet",
        "",
        f"Generated at: `{packet['generated_at']}`",
        "",
        "## Executive Summary",
        "",
        str(packet["review_positioning"]),
        "",
        "This packet connects source ingestion, regulatory-context overlay, public-data replay, and reviewer go/no-go criteria into one financial-services review path.",
        "",
        "## What The Current Evidence Shows",
        "",
        f"- Source export rows: `{summary['source_export_rows']}`",
        f"- Normalized SMERC-F rows: `{summary['source_normalized_rows']}`",
        f"- Source-ingestion replay scenarios: `{summary['source_replay_scenarios']}`",
        f"- Source-ingestion restraint rate: `{summary['source_restraint_rate']}`",
        f"- Regulatory context rows: `{summary['regulatory_context_rows']}`",
        f"- Regulatory-context state changes: `{summary['regulatory_state_change_count']}` of `{summary['regulatory_context_scenarios']}`",
        f"- Baseline restraint rate: `{summary['baseline_restraint_rate']}`",
        f"- Context-enriched restraint rate: `{summary['context_enriched_restraint_rate']}`",
        f"- Public replay scenarios: `{summary['public_replay_scenarios']}`",
        f"- Public replay decision-delta rate: `{summary['public_replay_decision_delta_rate']}`",
        "",
        "## Evidence Chain",
        "",
        "| Step | Meaning | Artifact |",
        "| --- | --- | --- |",
    ]
    for item in packet["evidence_chain"]:
        lines.append(f"| `{item['step']}` | {item['meaning']} | `{item['artifact']}` |")
    lines.extend(
        [
            "",
            "## Most Useful Review Examples",
            "",
            "| Action | Source | Current control | SMERC-F | Exposure | Capacity | Why it matters |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for item in packet["most_useful_examples"]:
        lines.append(
            f"| `{item['action_id']}` | `{item['source_type']}` | `{item['current_control_outcome']}` | "
            f"`{item['smerc_f_state']}` | {item['irreversible_exposure']} | {item['reversible_capacity']} | {item['review_reason']} |"
        )
    lines.extend(["", "## Pilot Go Conditions", ""])
    lines.extend(f"- {item}" for item in packet["pilot_go_no_go"]["go_conditions"])
    lines.extend(["", "## Stop Conditions", ""])
    lines.extend(f"- {item}" for item in packet["pilot_go_no_go"]["stop_conditions"])
    lines.extend(["", "## Success Metrics", ""])
    lines.extend(f"- {item}" for item in packet["pilot_go_no_go"]["success_metrics"])
    lines.extend(["", "## Reviewer Questions", ""])
    lines.extend(f"- {item}" for item in packet["review_questions"])
    lines.extend(["", "## Claim Boundaries", ""])
    lines.extend(f"- {item}" for item in packet["claim_boundaries"])
    lines.extend(
        [
            "",
            "## Recommended Next Action",
            "",
            str(packet["recommended_next_action"]),
            "",
            "## Evidence Boundary",
            "",
            str(packet["evidence_boundary"]),
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


def _require_version(payload: Mapping[str, Any], version: str, name: str) -> None:
    if payload.get("version") != version:
        raise ValueError(f"{name} must have version {version}")


def _top_examples(regulatory_context: Mapping[str, Any], public_replay: Mapping[str, Any]) -> list[Dict[str, Any]]:
    examples: list[Dict[str, Any]] = []
    for change in regulatory_context.get("state_changes", [])[:3]:
        examples.append(
            {
                "action_id": change["action_id"],
                "source_type": "regulatory_context_overlay",
                "current_control_outcome": "baseline",
                "smerc_f_state": change["context_enriched_state"],
                "irreversible_exposure": change["context_enriched_exposure"],
                "reversible_capacity": "-",
                "review_reason": (
                    f"Regulatory-context overlay changed posture from {change['baseline_state']} "
                    f"to {change['context_enriched_state']}."
                ),
            }
        )
    for record in public_replay.get("highest_exposure_records", [])[:5]:
        examples.append(
            {
                "action_id": record["action_id"],
                "source_type": record["source_type"],
                "current_control_outcome": record["current_control_outcome"],
                "smerc_f_state": record["smerc_f_state"],
                "irreversible_exposure": record["irreversible_exposure"],
                "reversible_capacity": record["reversible_capacity"],
                "review_reason": "High irreversible exposure with explicit drivers and controls.",
            }
        )
    return examples[:8]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SMERC-F financial pilot evidence packet.")
    parser.add_argument("--source-ingestion", default="reports/smerc_f_source_ingestion_report.json")
    parser.add_argument("--regulatory-context", default="reports/smerc_f_regulatory_context_report.json")
    parser.add_argument("--public-replay", default="reports/smerc_f_public_data_replay_report.json")
    parser.add_argument("--json-output", default="reports/smerc_f_pilot_evidence_packet.json")
    parser.add_argument("--markdown-output", default="reports/SMERC_F_Pilot_Evidence_Packet.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    packet = build_packet(
        source_ingestion=load_json(args.source_ingestion),
        regulatory_context=load_json(args.regulatory_context),
        public_replay=load_json(args.public_replay),
    )
    write_outputs(packet, args.json_output, args.markdown_output)
    print(json.dumps(packet, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.smerc_f_public_data_replay import build_replay_report, write_outputs as write_replay_outputs
from reference_engine.smerc_f_source_ingestion import load_source_exports, normalize_source_exports


VERSION = "smerc-f.regulatory-context.v1"

ISSUER_STATUS_PRESSURE = {
    "permitted": 0.08,
    "state_qualified": 0.18,
    "foreign_comparable": 0.28,
    "unknown": 0.48,
    "not_permitted": 0.86,
    "not_applicable": 0.22,
}

CONTEXT_WEIGHTS = {
    "issuer_status_pressure": 0.16,
    "reserve_sensitivity": 0.13,
    "redemption_pressure": 0.13,
    "custody_dependency": 0.14,
    "lawful_order_gap": 0.14,
    "jurisdiction_complexity": 0.12,
    "customer_impact_radius": 0.12,
    "disclosure_gap": 0.06,
}


def load_regulatory_contexts(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("SMERC-F regulatory context input must be a non-empty JSON array")
    contexts: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"regulatory context row {index} must be an object")
        action_id = _text(item.get("action_id"), f"regulatory context row {index} action_id").upper()
        if action_id in seen:
            raise ValueError(f"duplicate regulatory context action_id: {action_id}")
        seen.add(action_id)
        status = _text(item.get("permitted_issuer_status"), f"{action_id} permitted_issuer_status")
        if status not in ISSUER_STATUS_PRESSURE:
            raise ValueError(f"{action_id} permitted_issuer_status must be one of {', '.join(sorted(ISSUER_STATUS_PRESSURE))}")
        _text(item.get("regulatory_source"), f"{action_id} regulatory_source")
        _text(item.get("context_note"), f"{action_id} context_note")
        for field in [
            "reserve_sensitivity",
            "redemption_pressure",
            "custody_dependency",
            "lawful_order_compliance_capability",
            "jurisdiction_complexity",
            "customer_impact_radius",
            "disclosure_gap",
        ]:
            _ratio(item.get(field), f"{action_id} {field}")
        normalized = dict(item)
        normalized["action_id"] = action_id
        contexts.append(normalized)
    return contexts


def score_regulatory_context(context: Mapping[str, Any]) -> Dict[str, Any]:
    status = _text(context.get("permitted_issuer_status"), "permitted_issuer_status")
    lawful_order_capability = _ratio(context.get("lawful_order_compliance_capability"), "lawful_order_compliance_capability")
    signals = {
        "issuer_status_pressure": ISSUER_STATUS_PRESSURE[status],
        "reserve_sensitivity": _ratio(context.get("reserve_sensitivity"), "reserve_sensitivity"),
        "redemption_pressure": _ratio(context.get("redemption_pressure"), "redemption_pressure"),
        "custody_dependency": _ratio(context.get("custody_dependency"), "custody_dependency"),
        "lawful_order_gap": 1.0 - lawful_order_capability,
        "jurisdiction_complexity": _ratio(context.get("jurisdiction_complexity"), "jurisdiction_complexity"),
        "customer_impact_radius": _ratio(context.get("customer_impact_radius"), "customer_impact_radius"),
        "disclosure_gap": _ratio(context.get("disclosure_gap"), "disclosure_gap"),
    }
    score = sum(signals[key] * weight for key, weight in CONTEXT_WEIGHTS.items())
    if score >= 0.72:
        tier = "critical"
    elif score >= 0.56:
        tier = "elevated"
    elif score >= 0.38:
        tier = "watch"
    else:
        tier = "low"
    reason_codes = [
        code
        for key, code in [
            ("issuer_status_pressure", "ISSUER_STATUS_UNCERTAIN_OR_RESTRICTED"),
            ("reserve_sensitivity", "RESERVE_SENSITIVITY"),
            ("redemption_pressure", "REDEMPTION_PRESSURE"),
            ("custody_dependency", "CUSTODY_DEPENDENCY"),
            ("lawful_order_gap", "LAWFUL_ORDER_CAPABILITY_GAP"),
            ("jurisdiction_complexity", "JURISDICTION_COMPLEXITY"),
            ("customer_impact_radius", "CUSTOMER_IMPACT_RADIUS"),
            ("disclosure_gap", "DISCLOSURE_GAP"),
        ]
        if signals[key] >= 0.55
    ]
    return {
        "regulatory_context_score": round(score, 3),
        "regulatory_context_tier": tier,
        "regulatory_reason_codes": reason_codes or ["LOW_REGULATORY_CONTEXT_PRESSURE"],
        "regulatory_signals": {key: round(value, 3) for key, value in signals.items()},
    }


def enrich_rows_with_regulatory_context(
    normalized_rows: Iterable[Mapping[str, Any]],
    contexts: Iterable[Mapping[str, Any]],
) -> list[Dict[str, Any]]:
    context_lookup = {str(context["action_id"]).upper(): context for context in contexts}
    enriched: list[Dict[str, Any]] = []
    for row in normalized_rows:
        output = dict(row)
        context = context_lookup.get(str(row["source_id"]).upper())
        if not context:
            output["regulatory_context_score"] = 0.0
            output["regulatory_context_tier"] = "not_supplied"
            output["regulatory_reason_codes"] = ["REGULATORY_CONTEXT_NOT_SUPPLIED"]
            enriched.append(output)
            continue
        scored = score_regulatory_context(context)
        score = scored["regulatory_context_score"]
        pressure = min(0.22, score * 0.24)
        if scored["regulatory_context_tier"] == "critical":
            pressure += 0.08
        output["evidence_source_quality"] = round(max(0.0, float(output["evidence_source_quality"]) - pressure * 0.52), 3)
        output["market_stress_observed"] = round(min(1.0, float(output["market_stress_observed"]) + pressure * 0.72), 3)
        output["anomaly_observed"] = round(min(1.0, float(output["anomaly_observed"]) + pressure * 0.86), 3)
        output["counterparty_concentration_observed"] = round(
            min(1.0, float(output["counterparty_concentration_observed"]) + pressure * 0.60),
            3,
        )
        if "RESERVE_SENSITIVITY" in scored["regulatory_reason_codes"] or "REDEMPTION_PRESSURE" in scored["regulatory_reason_codes"]:
            output["liquidity_concentration_observed"] = round(
                min(1.0, float(output["liquidity_concentration_observed"]) + pressure * 0.65),
                3,
            )
        output.update(scored)
        output["regulatory_source"] = context["regulatory_source"]
        output["regulatory_context_note"] = context["context_note"]
        enriched.append(output)
    return enriched


def build_regulatory_context_report(
    source_exports: list[Mapping[str, Any]],
    regulatory_contexts: list[Mapping[str, Any]],
    *,
    policy: str = "balanced",
) -> Dict[str, Any]:
    baseline_rows = normalize_source_exports(source_exports)
    enriched_rows = enrich_rows_with_regulatory_context(baseline_rows, regulatory_contexts)
    baseline_replay = build_replay_report(baseline_rows, policy=policy)
    enriched_replay = build_replay_report(enriched_rows, policy=policy)
    context_tiers = Counter(str(row["regulatory_context_tier"]) for row in enriched_rows)
    changed_records = _changed_records(baseline_replay["records"], enriched_replay["records"])
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "policy": policy,
        "source_export_count": len(source_exports),
        "regulatory_context_count": len(regulatory_contexts),
        "normalized_row_count": len(enriched_rows),
        "scenario_count": enriched_replay["scenario_count"],
        "regulatory_context_tiers": dict(sorted(context_tiers.items())),
        "baseline_state_counts": baseline_replay["smerc_f_state_counts"],
        "context_enriched_state_counts": enriched_replay["smerc_f_state_counts"],
        "baseline_restraint_rate": baseline_replay["restraint_rate"],
        "context_enriched_restraint_rate": enriched_replay["restraint_rate"],
        "state_change_count": len(changed_records),
        "state_change_rate": round(len(changed_records) / enriched_replay["scenario_count"], 3) if enriched_replay["scenario_count"] else 0.0,
        "state_changes": changed_records[:12],
        "highest_exposure_records": enriched_replay["highest_exposure_records"],
        "enriched_rows": enriched_rows,
        "context_enriched_replay_report": enriched_replay,
        "evidence_boundary": (
            "Regulatory context overlay only. The profile uses legislation-inspired operational metadata as risk context. "
            "It does not interpret law, provide legal advice, determine compliance, screen AML or sanctions, classify illicit activity, "
            "or authorize financial execution."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC-F Regulatory Context Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Policy: `{report['policy']}`",
        "",
        "## Purpose",
        "",
        "This report shows how legislation-inspired operational context can inform SMERC-F recoverability scoring without claiming legal compliance.",
        "",
        "The overlay is designed for financial-services review of stablecoin, tokenized-finance, custody, treasury, and settlement-adjacent automation.",
        "",
        "## Summary",
        "",
        f"- Source export rows: `{report['source_export_count']}`",
        f"- Regulatory context rows: `{report['regulatory_context_count']}`",
        f"- Normalized rows: `{report['normalized_row_count']}`",
        f"- Replay scenarios: `{report['scenario_count']}`",
        f"- Baseline state counts: `{report['baseline_state_counts']}`",
        f"- Context-enriched state counts: `{report['context_enriched_state_counts']}`",
        f"- Baseline restraint rate: `{report['baseline_restraint_rate']}`",
        f"- Context-enriched restraint rate: `{report['context_enriched_restraint_rate']}`",
        f"- State change count: `{report['state_change_count']}`",
        f"- State change rate: `{report['state_change_rate']}`",
        "",
        "## Regulatory Context Tiers",
        "",
        "| Tier | Rows |",
        "| --- | ---: |",
    ]
    for tier, count in report["regulatory_context_tiers"].items():
        lines.append(f"| `{tier}` | {count} |")
    lines.extend(["", "## State Changes After Context Overlay", "", "| Action | Baseline | Context-enriched | Exposure delta | Drivers |", "| --- | --- | --- | ---: | --- |"])
    if report["state_changes"]:
        for change in report["state_changes"]:
            drivers = ", ".join(f"`{driver}`" for driver in change["context_enriched_drivers"][:4])
            lines.append(
                f"| `{change['action_id']}` | `{change['baseline_state']}` | `{change['context_enriched_state']}` | "
                f"{change['exposure_delta']} | {drivers} |"
            )
    else:
        lines.append("| None | - | - | 0 | - |")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
            "## How To Use This",
            "",
            "Use this profile to discuss whether regulatory-context metadata should make an automated financial action more cautious before execution. Do not use it as legal advice or as a substitute for compliance, legal, risk, AML, sanctions, custody, settlement, or payment-control systems.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    report: Mapping[str, Any],
    *,
    enriched_output: str | Path,
    json_output: str | Path,
    markdown_output: str | Path,
    replay_json_output: str | Path,
    replay_markdown_output: str | Path,
) -> None:
    enriched_path = Path(enriched_output)
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    enriched_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    enriched_path.write_text(json.dumps(report["enriched_rows"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    write_replay_outputs(report["context_enriched_replay_report"], replay_json_output, replay_markdown_output)


def _changed_records(baseline_records: Iterable[Mapping[str, Any]], enriched_records: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    baseline = {str(record["action_id"]): record for record in baseline_records}
    changes: list[Dict[str, Any]] = []
    for record in enriched_records:
        action_id = str(record["action_id"])
        before = baseline[action_id]
        if before["smerc_f_state"] != record["smerc_f_state"]:
            changes.append(
                {
                    "action_id": action_id,
                    "baseline_state": before["smerc_f_state"],
                    "context_enriched_state": record["smerc_f_state"],
                    "baseline_exposure": before["irreversible_exposure"],
                    "context_enriched_exposure": record["irreversible_exposure"],
                    "exposure_delta": round(record["irreversible_exposure"] - before["irreversible_exposure"], 3),
                    "context_enriched_drivers": record["drivers"],
                }
            )
    return sorted(changes, key=lambda item: item["exposure_delta"], reverse=True)


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _ratio(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{path} must be a number between 0.0 and 1.0")
    numeric = float(value)
    if numeric < 0 or numeric > 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return numeric


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a bounded regulatory-context overlay to SMERC-F source exports.")
    parser.add_argument("--source-exports", default="examples/smerc_f_source_exports.json")
    parser.add_argument("--regulatory-contexts", default="examples/smerc_f_regulatory_context_examples.json")
    parser.add_argument("--policy", default="balanced")
    parser.add_argument("--enriched-output", default="examples/smerc_f_regulatory_enriched_rows.json")
    parser.add_argument("--json-output", default="reports/smerc_f_regulatory_context_report.json")
    parser.add_argument("--markdown-output", default="reports/SMERC_F_Regulatory_Context_Report.md")
    parser.add_argument("--replay-json-output", default="reports/smerc_f_regulatory_context_replay_report.json")
    parser.add_argument("--replay-markdown-output", default="reports/SMERC_F_Regulatory_Context_Replay_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_regulatory_context_report(
        load_source_exports(args.source_exports),
        load_regulatory_contexts(args.regulatory_contexts),
        policy=args.policy,
    )
    write_outputs(
        report,
        enriched_output=args.enriched_output,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
        replay_json_output=args.replay_json_output,
        replay_markdown_output=args.replay_markdown_output,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

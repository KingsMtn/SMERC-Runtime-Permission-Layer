from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.financial_permission_profile import FinancialPermissionProfile


VERSION = "smerc-f.public-data-replay.v1"
RESTRAINT_STATES = {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}
FINANCIAL_REASON_CODE_LABELS = {
    "AUTOMATION_VELOCITY_HIGH": "Automation speed is high enough that a bad action could compound before review.",
    "COUNTERPARTY_CONCENTRATION_HIGH": "Counterparty or recipient concentration creates a larger correlated exposure.",
    "FINANCIAL_EVIDENCE_WEAK": "The evidence available before execution is too thin for an automated financial action.",
    "GOVERNANCE_CHANGE_AUTHORITY_RISK": "A governance or authority-changing action may alter who can act later.",
    "LIQUIDITY_ROUTE_FRAGILE": "Liquidity and market stress suggest the action may not unwind cleanly.",
    "MARKET_STRESS_ELEVATED": "Market stress is high enough to make ordinary routing assumptions less reliable.",
    "NO_FINANCIAL_REASON_CODE_TRIGGERED": "No financial reason code triggered.",
    "REDEMPTION_PRESSURE_HIGH": "Stablecoin or reserve movement pressure suggests execution should slow or pause.",
    "REPORTED_ADDRESS_RISK": "A reported-address or incident signal should be preserved before action.",
    "SETTLEMENT_REVERSIBILITY_LOW": "Settlement finality or low reversibility limits recovery after execution.",
    "TOKENIZED_COLLATERAL_EXPOSURE_HIGH": "Collateral or tokenized-asset pressure raises the cost of acting too quickly.",
}
PUBLIC_SOURCE_TYPES = {
    "chainabuse_report",
    "defillama_hack_incident",
    "dune_stablecoin_transfer",
    "elliptic_bitcoin_graph",
    "ethereum_bigquery_transfer",
}


def load_public_rows(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("SMERC-F public-data replay input must be a non-empty JSON array")
    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"public-data row {index} must be an object")
        required = {
            "source_id",
            "source_type",
            "source_name",
            "source_url",
            "chain",
            "asset",
            "proposed_action",
            "actor_type",
            "current_control_outcome",
            "evidence_source_quality",
            "settlement_finality",
            "recipient_reputation",
            "liquidity_concentration_observed",
            "counterparty_concentration_observed",
            "market_stress_observed",
            "anomaly_observed",
            "automation_velocity_observed",
        }
        missing = sorted(required - set(item))
        if missing:
            raise ValueError(f"public-data row {index} missing field(s): {', '.join(missing)}")
        source_id = _text(item["source_id"], f"public-data row {index} source_id")
        if source_id in seen:
            raise ValueError(f"duplicate source_id: {source_id}")
        seen.add(source_id)
        source_type = _text(item["source_type"], f"{source_id} source_type")
        if source_type not in PUBLIC_SOURCE_TYPES:
            raise ValueError(f"{source_id} source_type must be one of {', '.join(sorted(PUBLIC_SOURCE_TYPES))}")
        if item["current_control_outcome"] not in {"ALLOW", "REVIEW", "ALERT", "BLOCK"}:
            raise ValueError(f"{source_id} current_control_outcome must be ALLOW, REVIEW, ALERT, or BLOCK")
        for key in [
            "evidence_source_quality",
            "settlement_finality",
            "recipient_reputation",
            "liquidity_concentration_observed",
            "counterparty_concentration_observed",
            "market_stress_observed",
            "anomaly_observed",
            "automation_velocity_observed",
        ]:
            _ratio(item[key], f"{source_id} {key}")
        rows.append(dict(item))
    return rows


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


def _money_scale(row: Mapping[str, Any]) -> float:
    value = row.get("amount_usd", row.get("loss_usd", 0))
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{row.get('source_id', 'row')} amount_usd/loss_usd must be a non-negative number")
    if value <= 0:
        return 0.0
    return min(1.0, math.log10(float(value) + 1.0) / 9.0)


def row_to_financial_action(row: Mapping[str, Any], *, variant: str = "base", variant_index: int = 0) -> Dict[str, Any]:
    source_id = _text(row["source_id"], "source_id")
    money_pressure = _money_scale(row)
    finality = _ratio(row["settlement_finality"], f"{source_id} settlement_finality")
    reputation = _ratio(row["recipient_reputation"], f"{source_id} recipient_reputation")
    evidence_quality = _ratio(row["evidence_source_quality"], f"{source_id} evidence_source_quality")
    anomaly = _ratio(row["anomaly_observed"], f"{source_id} anomaly_observed")
    velocity = _ratio(row["automation_velocity_observed"], f"{source_id} automation_velocity_observed")
    liquidity = _ratio(row["liquidity_concentration_observed"], f"{source_id} liquidity_concentration_observed")
    counterparty = _ratio(row["counterparty_concentration_observed"], f"{source_id} counterparty_concentration_observed")
    market = _ratio(row["market_stress_observed"], f"{source_id} market_stress_observed")

    if variant == "reduced_scope":
        variant_pressure = -0.10
    elif variant == "missing_evidence":
        variant_pressure = 0.08
        evidence_quality = max(0.0, evidence_quality - 0.22)
        anomaly = min(1.0, anomaly + 0.08)
    elif variant == "accelerated_automation":
        variant_pressure = 0.12
        velocity = min(1.0, velocity + 0.22)
        finality = min(1.0, finality + 0.06)
    elif variant == "market_stress":
        variant_pressure = 0.16
        market = min(1.0, market + 0.22)
        liquidity = min(1.0, liquidity + 0.14)
    else:
        variant_pressure = min(0.10, variant_index * 0.03)

    source_type = str(row["source_type"])
    source_type_pressure = {
        "chainabuse_report": 0.16,
        "defillama_hack_incident": 0.18,
        "dune_stablecoin_transfer": 0.04,
        "elliptic_bitcoin_graph": 0.12,
        "ethereum_bigquery_transfer": 0.06,
    }[source_type]
    current = str(row["current_control_outcome"])
    authorization_support = {"ALLOW": 0.86, "REVIEW": 0.68, "ALERT": 0.50, "BLOCK": 0.18}[current]
    if source_type == "chainabuse_report" and row.get("checked") is True and row.get("trusted") is True:
        authorization_support = min(authorization_support, 0.44)
    if source_type == "defillama_hack_incident":
        authorization_support = min(authorization_support, 0.64)

    pressure = max(0.0, variant_pressure)
    reversibility = max(0.02, min(1.0, 1.0 - (finality * 0.55 + money_pressure * 0.30 + source_type_pressure + pressure)))
    settlement_anomaly = min(1.0, anomaly * 0.70 + finality * 0.18 + source_type_pressure)
    stablecoin_imbalance = min(1.0, liquidity * 0.38 + money_pressure * 0.34 + market * 0.18 + source_type_pressure)
    collateral_stress = min(1.0, market * 0.45 + liquidity * 0.25 + anomaly * 0.16 + source_type_pressure)
    model_disagreement = min(1.0, (1.0 - evidence_quality) * 0.56 + anomaly * 0.26 + source_type_pressure)

    return {
        "action_id": f"{source_id}_{variant}".upper(),
        "description": (
            f"Replay {row['proposed_action']} from {row['source_name']} on {row['chain']} "
            f"for {row['asset']} using {variant} assumptions."
        ),
        "action_type": str(row["proposed_action"]),
        "actor": str(row["actor_type"]),
        "authorization_support": round(authorization_support, 3),
        "evidence_validity": round(evidence_quality, 3),
        "reversibility": round(reversibility, 3),
        "liquidity_concentration": round(min(1.0, liquidity + pressure), 3),
        "collateral_stress": round(collateral_stress, 3),
        "settlement_anomaly": round(settlement_anomaly, 3),
        "stablecoin_imbalance": round(stablecoin_imbalance, 3),
        "counterparty_concentration": round(min(1.0, counterparty + pressure), 3),
        "market_instability": round(min(1.0, market + pressure), 3),
        "model_disagreement": round(model_disagreement, 3),
        "agent_velocity": round(velocity, 3),
    }


def expand_public_rows(rows: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    variants = ["base", "reduced_scope", "missing_evidence", "accelerated_automation", "market_stress"]
    return [
        row_to_financial_action(row, variant=variant, variant_index=index)
        for row in rows
        for index, variant in enumerate(variants)
    ]


def classify_delta(current_control_outcome: str, smerc_state: str) -> str:
    if current_control_outcome == "ALLOW" and smerc_state in RESTRAINT_STATES:
        return "CONTROL_ALLOW_SMERC_RESTRAINT"
    if current_control_outcome in {"REVIEW", "ALERT"} and smerc_state == "ALLOW":
        return "CONTROL_REVIEW_SMERC_ALLOW"
    if current_control_outcome in {"REVIEW", "ALERT"} and smerc_state in RESTRAINT_STATES:
        return "CONTROL_REVIEW_SMERC_RESTRAINT"
    if current_control_outcome == "BLOCK" and smerc_state != "DENY":
        return "CONTROL_BLOCK_SMERC_NON_DENY"
    return "CONTROL_AND_SMERC_ALIGNED"


def financial_reason_codes(source: Mapping[str, Any], action: Mapping[str, Any], decision: Mapping[str, Any]) -> list[str]:
    action_type = str(action["action_type"]).lower()
    source_type = str(source["source_type"])
    codes: list[str] = []

    if action["stablecoin_imbalance"] >= 0.70 and (
        "redemption" in action_type or "stablecoin" in str(source["asset"]).lower() or source_type == "dune_stablecoin_transfer"
    ):
        codes.append("REDEMPTION_PRESSURE_HIGH")
    if action["evidence_validity"] < 0.60 or "EVIDENCE_VALIDITY_WEAK" in decision["drivers"]:
        codes.append("FINANCIAL_EVIDENCE_WEAK")
    if action["reversibility"] < 0.35 or _ratio(source["settlement_finality"], f"{source['source_id']} settlement_finality") >= 0.80:
        codes.append("SETTLEMENT_REVERSIBILITY_LOW")
    if action["counterparty_concentration"] >= 0.65 or _ratio(source["recipient_reputation"], f"{source['source_id']} recipient_reputation") <= 0.25:
        codes.append("COUNTERPARTY_CONCENTRATION_HIGH")
    if action["liquidity_concentration"] >= 0.65 and action["market_instability"] >= 0.50:
        codes.append("LIQUIDITY_ROUTE_FRAGILE")
    if "collateral" in action_type or action["collateral_stress"] >= 0.72:
        codes.append("TOKENIZED_COLLATERAL_EXPOSURE_HIGH")
    if action["agent_velocity"] >= 0.70:
        codes.append("AUTOMATION_VELOCITY_HIGH")
    if action["market_instability"] >= 0.65:
        codes.append("MARKET_STRESS_ELEVATED")
    if source_type == "chainabuse_report" and (source.get("trusted") is True or action["settlement_anomaly"] >= 0.75):
        codes.append("REPORTED_ADDRESS_RISK")
    if "governance" in action_type or "policy" in action_type:
        codes.append("GOVERNANCE_CHANGE_AUTHORITY_RISK")

    return codes or ["NO_FINANCIAL_REASON_CODE_TRIGGERED"]


def work_result_impact(source: Mapping[str, Any], action: Mapping[str, Any], decision: Mapping[str, Any], delta: str, codes: list[str]) -> Dict[str, str]:
    work = (
        f"Replay {action['action_type']} from {source['source_type']} metadata and compare the current "
        f"`{source['current_control_outcome']}` control outcome with SMERC-F `{decision['state']}`."
    )
    result = (
        f"SMERC-F returned `{decision['state']}` with irreversible exposure {decision['irreversible_exposure']} "
        f"and financial reason codes: {', '.join(codes)}."
    )
    if delta == "CONTROL_ALLOW_SMERC_RESTRAINT":
        impact = "Candidate proof point: recoverability would add restraint before an action an existing control shape allowed."
    elif delta == "CONTROL_REVIEW_SMERC_RESTRAINT":
        impact = "Candidate proof point: existing review/alert context can be converted into a clearer pre-execution route."
    elif delta == "CONTROL_REVIEW_SMERC_ALLOW":
        impact = "Candidate proof point: strong recovery evidence may help avoid unnecessary friction for bounded actions."
    elif delta == "CONTROL_BLOCK_SMERC_NON_DENY":
        impact = "Reviewer question: a block may be stricter than the recoverability posture, so policy calibration matters."
    else:
        impact = "Alignment case: SMERC-F preserved replay evidence without changing the current control direction."
    return {"work": work, "result": result, "impact": impact}


def build_replay_report(rows: list[Mapping[str, Any]], *, policy: str = "balanced") -> Dict[str, Any]:
    engine = FinancialPermissionProfile(policy)
    records: list[Dict[str, Any]] = []
    state_counts: Counter[str] = Counter()
    delta_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    source_lookup = {str(row["source_id"]).upper(): row for row in rows}

    for action in expand_public_rows(rows):
        source = next(row for key, row in source_lookup.items() if action["action_id"].startswith(key))
        decision = engine.evaluate(action)
        delta = classify_delta(str(source["current_control_outcome"]), decision["state"])
        reason_codes = financial_reason_codes(source, action, decision)
        state_counts[decision["state"]] += 1
        delta_counts[delta] += 1
        source_counts[str(source["source_type"])] += 1
        reason_counts.update(reason_codes)
        records.append(
            {
                "source_id": source["source_id"],
                "source_type": source["source_type"],
                "source_url": source["source_url"],
                "action_id": action["action_id"],
                "chain": source["chain"],
                "asset": source["asset"],
                "current_control_outcome": source["current_control_outcome"],
                "smerc_f_state": decision["state"],
                "irreversible_exposure": decision["irreversible_exposure"],
                "reversible_capacity": decision["reversible_capacity"],
                "confidence": decision["confidence"],
                "drivers": decision["drivers"],
                "controls": decision["controls"],
                "financial_reason_codes": reason_codes,
                "financial_reason_labels": {code: FINANCIAL_REASON_CODE_LABELS.get(code, "No financial reason code triggered.") for code in reason_codes},
                "delta_type": delta,
                "work_result_impact": work_result_impact(source, action, decision, delta, reason_codes),
                "decision_hash": decision["decision_hash"],
            }
        )

    total = len(records)
    restraint_count = sum(state_counts[state] for state in RESTRAINT_STATES)
    delta_count = sum(count for delta, count in delta_counts.items() if delta != "CONTROL_AND_SMERC_ALIGNED")
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "policy": policy,
        "source_row_count": len(rows),
        "scenario_count": total,
        "source_type_counts": dict(sorted(source_counts.items())),
        "smerc_f_state_counts": {state: state_counts.get(state, 0) for state in ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")},
        "delta_counts": dict(sorted(delta_counts.items())),
        "financial_reason_code_counts": dict(sorted(reason_counts.items())),
        "financial_reason_code_labels": FINANCIAL_REASON_CODE_LABELS,
        "decision_delta_count": delta_count,
        "decision_delta_rate": round(delta_count / total, 3) if total else 0.0,
        "restraint_count": restraint_count,
        "restraint_rate": round(restraint_count / total, 3) if total else 0.0,
        "highest_exposure_records": sorted(records, key=lambda item: item["irreversible_exposure"], reverse=True)[:10],
        "evidence_boundary": (
            "Public-data-shaped replay only. Source records are normalized examples derived from public dataset schemas, "
            "public incident categories, and public documentation. The replay does not reconstruct customer telemetry, "
            "prove prevention, detect AML violations, screen sanctions, move funds, or certify production financial controls."
        ),
        "records": records,
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC-F Financial Public-Data Replay Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Policy: `{report['policy']}`",
        "",
        "## Purpose",
        "",
        "This report shows how SMERC-F can ingest public-data-shaped financial, stablecoin, blockchain, and incident records and convert them into recoverability-aware pre-execution action postures.",
        "",
        "It is designed for Fortune 500 financial-services review. It is not customer validation, AML compliance, fraud detection, sanctions screening, custody, settlement, trading, payment execution, or production certification.",
        "",
        "## Evidence Boundary",
        "",
        str(report["evidence_boundary"]),
        "",
        "## Summary",
        "",
        f"- Public source rows: `{report['source_row_count']}`",
        f"- Replay scenarios: `{report['scenario_count']}`",
        f"- State counts: `{report['smerc_f_state_counts']}`",
        f"- Decision delta count: `{report['decision_delta_count']}`",
        f"- Decision delta rate: `{report['decision_delta_rate']}`",
        f"- Restraint count: `{report['restraint_count']}`",
        f"- Restraint rate: `{report['restraint_rate']}`",
        "",
        "## Source Types",
        "",
        "| Source type | Scenario count |",
        "| --- | ---: |",
    ]
    for source_type, count in report["source_type_counts"].items():
        lines.append(f"| `{source_type}` | {count} |")
    lines.extend(["", "## Delta Types", "", "| Delta | Count |", "| --- | ---: |"])
    for delta, count in report["delta_counts"].items():
        lines.append(f"| `{delta}` | {count} |")
    lines.extend(["", "## Financial Reason Code Library", "", "| Reason code | Count | Meaning |", "| --- | ---: | --- |"])
    for code, count in report["financial_reason_code_counts"].items():
        label = report["financial_reason_code_labels"].get(code, "No financial reason code triggered.")
        lines.append(f"| `{code}` | {count} | {label} |")
    lines.extend(["", "## Current Control Vs SMERC-F", "", "| Current control | SMERC-F posture | Delta | Example impact |", "| --- | --- | --- | --- |"])
    for record in report["records"][:12]:
        impact = record["work_result_impact"]["impact"]
        lines.append(
            f"| `{record['current_control_outcome']}` | `{record['smerc_f_state']}` | `{record['delta_type']}` | {impact} |"
        )
    lines.extend(["", "## Highest Irreversible Exposure Records", "", "| Action | Source | Current control | SMERC-F | Exposure | Capacity | Financial codes | Key drivers |", "| --- | --- | --- | --- | ---: | ---: | --- | --- |"])
    for record in report["highest_exposure_records"]:
        drivers = ", ".join(f"`{driver}`" for driver in record["drivers"][:4])
        codes = ", ".join(f"`{code}`" for code in record["financial_reason_codes"][:4])
        lines.append(
            f"| `{record['action_id']}` | `{record['source_type']}` | `{record['current_control_outcome']}` | "
            f"`{record['smerc_f_state']}` | {record['irreversible_exposure']} | {record['reversible_capacity']} | {codes} | {drivers} |"
        )
    lines.extend(["", "## Work / Result / Impact Examples", "", "| Work | Result | Impact |", "| --- | --- | --- |"])
    for record in report["highest_exposure_records"][:5]:
        summary = record["work_result_impact"]
        lines.append(f"| {summary['work']} | {summary['result']} | {summary['impact']} |")
    lines.extend(
        [
            "",
            "## Fortune 500 Review Interpretation",
            "",
            "The useful question is not whether SMERC-F replaces financial-crime, blockchain-analytics, IAM, OPA, or approval systems. It does not. The useful question is whether those systems can provide risk or policy context while SMERC-F adds a recoverability-aware action posture before automation executes.",
            "",
            "A financial reviewer should inspect scenarios where the current control outcome is `ALLOW` but SMERC-F returns `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`. Those are the candidate cases where recoverability may add a governance signal.",
            "",
            "## Public Data Sources Represented",
            "",
            "- Dune stablecoin transfer and balance schema documentation",
            "- Google BigQuery Ethereum public dataset documentation",
            "- Chainabuse reported-address API documentation",
            "- DefiLlama public hacks database categories",
            "- Elliptic public Bitcoin transaction graph dataset description",
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay public-data-shaped financial records through SMERC-F.")
    parser.add_argument("path", help="Path to public-data-shaped SMERC-F replay input JSON.")
    parser.add_argument("--policy", default="balanced")
    parser.add_argument("--json-output", default="reports/smerc_f_public_data_replay_report.json")
    parser.add_argument("--markdown-output", default="reports/SMERC_F_Public_Data_Replay_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_replay_report(load_public_rows(args.path), policy=args.policy)
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

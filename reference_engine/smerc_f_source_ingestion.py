from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.smerc_f_public_data_replay import build_replay_report, write_outputs as write_replay_outputs


VERSION = "smerc-f.source-ingestion.v1"

SUPPORTED_SOURCE_FORMATS = {
    "chainabuse_address_report",
    "defillama_hack_incident",
    "dune_stablecoin_transfer_export",
    "elliptic_bitcoin_graph_row",
    "ethereum_bigquery_token_transfer",
}


def load_source_exports(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("SMERC-F source export input must be a non-empty JSON array")
    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"source export row {index} must be an object")
        record_id = _text(item.get("record_id"), f"source export row {index} record_id")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)
        source_format = _text(item.get("source_format"), f"{record_id} source_format")
        if source_format not in SUPPORTED_SOURCE_FORMATS:
            raise ValueError(f"{record_id} source_format must be one of {', '.join(sorted(SUPPORTED_SOURCE_FORMATS))}")
        rows.append(dict(item))
    return rows


def normalize_source_exports(rows: Iterable[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    normalized: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        source_format = _text(row.get("source_format"), "source_format")
        if source_format == "dune_stablecoin_transfer_export":
            item = _normalize_dune(row)
        elif source_format == "ethereum_bigquery_token_transfer":
            item = _normalize_bigquery(row)
        elif source_format == "chainabuse_address_report":
            item = _normalize_chainabuse(row)
        elif source_format == "defillama_hack_incident":
            item = _normalize_defillama(row)
        elif source_format == "elliptic_bitcoin_graph_row":
            item = _normalize_elliptic(row)
        else:
            raise ValueError(f"Unsupported source_format: {source_format}")
        if item["source_id"] in seen:
            raise ValueError(f"duplicate normalized source_id: {item['source_id']}")
        seen.add(item["source_id"])
        normalized.append(item)
    return normalized


def build_ingestion_report(rows: list[Mapping[str, Any]], *, policy: str = "balanced") -> Dict[str, Any]:
    normalized = normalize_source_exports(rows)
    replay = build_replay_report(normalized, policy=policy)
    source_counts = Counter(str(row["source_format"]) for row in rows)
    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "policy": policy,
        "source_export_count": len(rows),
        "normalized_row_count": len(normalized),
        "source_format_counts": dict(sorted(source_counts.items())),
        "normalized_source_type_counts": replay["source_type_counts"],
        "scenario_count": replay["scenario_count"],
        "smerc_f_state_counts": replay["smerc_f_state_counts"],
        "decision_delta_rate": replay["decision_delta_rate"],
        "restraint_rate": replay["restraint_rate"],
        "highest_exposure_records": replay["highest_exposure_records"],
        "normalized_rows": normalized,
        "replay_report": replay,
        "evidence_boundary": (
            "Source export ingestion only. The adapter accepts public-data-shaped exports and normalizes them "
            "into SMERC-F metadata rows. It does not call vendor APIs, enrich addresses, determine illicit activity, "
            "screen sanctions, move funds, or certify financial controls."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC-F Source Ingestion Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Policy: `{report['policy']}`",
        "",
        "## Purpose",
        "",
        "This report shows how exported financial, stablecoin, blockchain, and incident rows can be normalized into SMERC-F replay inputs before recoverability scoring.",
        "",
        "It is an ingestion and replay proof, not customer validation, AML compliance, sanctions screening, fraud detection, custody, settlement, trading, payment execution, or production certification.",
        "",
        "## Summary",
        "",
        f"- Source export rows: `{report['source_export_count']}`",
        f"- Normalized SMERC-F rows: `{report['normalized_row_count']}`",
        f"- Replay scenarios: `{report['scenario_count']}`",
        f"- State counts: `{report['smerc_f_state_counts']}`",
        f"- Decision delta rate: `{report['decision_delta_rate']}`",
        f"- Restraint rate: `{report['restraint_rate']}`",
        "",
        "## Source Export Formats",
        "",
        "| Source export format | Rows |",
        "| --- | ---: |",
    ]
    for source_format, count in report["source_format_counts"].items():
        lines.append(f"| `{source_format}` | {count} |")
    lines.extend(["", "## Normalized Source Types", "", "| Normalized source type | Rows |", "| --- | ---: |"])
    for source_type, count in report["normalized_source_type_counts"].items():
        lines.append(f"| `{source_type}` | {count} |")
    lines.extend(
        [
            "",
            "## Highest Exposure Records",
            "",
            "| Action | Source | Current control | SMERC-F | Exposure | Capacity |",
            "| --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for record in report["highest_exposure_records"][:8]:
        lines.append(
            f"| `{record['action_id']}` | `{record['source_type']}` | `{record['current_control_outcome']}` | "
            f"`{record['smerc_f_state']}` | {record['irreversible_exposure']} | {record['reversible_capacity']} |"
        )
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            str(report["evidence_boundary"]),
            "",
            "## Financial-Services Interpretation",
            "",
            "The useful review question is whether exported metadata from existing systems can feed a recoverability checkpoint before automated financial actions execute. Existing AML, fraud, blockchain analytics, identity, policy, and approval systems remain the source systems. SMERC-F adds a pre-execution recoverability posture and replay evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    report: Mapping[str, Any],
    *,
    normalized_output: str | Path,
    json_output: str | Path,
    markdown_output: str | Path,
    replay_json_output: str | Path,
    replay_markdown_output: str | Path,
) -> None:
    normalized_path = Path(normalized_output)
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.write_text(json.dumps(report["normalized_rows"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    write_replay_outputs(report["replay_report"], replay_json_output, replay_markdown_output)


def _normalize_dune(row: Mapping[str, Any]) -> Dict[str, Any]:
    amount = _money(row, "amount_usd")
    concentration = _ratio(row.get("concentration_score"), "concentration_score")
    return _base_row(
        row,
        source_type="dune_stablecoin_transfer",
        chain=_text(row.get("blockchain"), "blockchain"),
        asset=_text(row.get("symbol"), "symbol"),
        amount_usd=amount,
        proposed_action=_action_for_transfer(row),
        actor_type="treasury_automation",
        evidence_source_quality=_ratio(row.get("evidence_quality"), "evidence_quality"),
        settlement_finality=_ratio(row.get("finality"), "finality"),
        recipient_reputation=_ratio(row.get("recipient_reputation"), "recipient_reputation"),
        liquidity_concentration_observed=concentration,
        counterparty_concentration_observed=max(0.0, 1.0 - _ratio(row.get("recipient_reputation"), "recipient_reputation")),
        market_stress_observed=_ratio(row.get("market_stress"), "market_stress"),
        anomaly_observed=_ratio(row.get("anomaly_score"), "anomaly_score"),
        automation_velocity_observed=_ratio(row.get("automation_velocity"), "automation_velocity"),
    )


def _normalize_bigquery(row: Mapping[str, Any]) -> Dict[str, Any]:
    tx_count = _number(row.get("transaction_count", 1), "transaction_count")
    contract_pressure = 0.18 if row.get("contract_creation_recent") is True else 0.0
    return _base_row(
        row,
        source_type="ethereum_bigquery_transfer",
        chain=_text(row.get("blockchain"), "blockchain"),
        asset=_text(row.get("token_symbol"), "token_symbol"),
        amount_usd=_money(row, "value_usd"),
        proposed_action="token_transfer_batch_review",
        actor_type="settlement_automation",
        evidence_source_quality=_ratio(row.get("evidence_quality"), "evidence_quality"),
        settlement_finality=_ratio(row.get("block_finality"), "block_finality"),
        recipient_reputation=_ratio(row.get("recipient_reputation"), "recipient_reputation"),
        liquidity_concentration_observed=_ratio(row.get("wallet_concentration"), "wallet_concentration"),
        counterparty_concentration_observed=min(1.0, math.log10(tx_count + 1) / 2.0 + contract_pressure),
        market_stress_observed=_ratio(row.get("network_stress"), "network_stress"),
        anomaly_observed=_ratio(row.get("anomaly_score"), "anomaly_score"),
        automation_velocity_observed=_ratio(row.get("automation_velocity"), "automation_velocity"),
    )


def _normalize_chainabuse(row: Mapping[str, Any]) -> Dict[str, Any]:
    report_count = _number(row.get("report_count", 1), "report_count")
    report_pressure = min(1.0, math.log10(report_count + 1) / 1.4)
    return _base_row(
        row,
        source_type="chainabuse_report",
        chain=_text(row.get("blockchain"), "blockchain"),
        asset=_text(row.get("asset"), "asset"),
        loss_usd=_money(row, "reported_loss_usd"),
        proposed_action=f"reported_address_{_text(row.get('report_category'), 'report_category')}_review",
        actor_type="risk_automation",
        evidence_source_quality=_ratio(row.get("evidence_quality"), "evidence_quality"),
        settlement_finality=_ratio(row.get("settlement_finality"), "settlement_finality"),
        recipient_reputation=_ratio(row.get("recipient_reputation"), "recipient_reputation"),
        liquidity_concentration_observed=report_pressure,
        counterparty_concentration_observed=_ratio(row.get("counterparty_concentration"), "counterparty_concentration"),
        market_stress_observed=_ratio(row.get("market_stress"), "market_stress"),
        anomaly_observed=max(_ratio(row.get("anomaly_score"), "anomaly_score"), report_pressure),
        automation_velocity_observed=_ratio(row.get("automation_velocity"), "automation_velocity"),
        extra={"checked": row.get("checked") is True, "trusted": row.get("trusted") is True},
    )


def _normalize_defillama(row: Mapping[str, Any]) -> Dict[str, Any]:
    loss = _money(row, "loss_usd")
    recovered = _money(row, "recovered_funds_usd")
    recovery_gap = 1.0 - min(1.0, recovered / loss) if loss else 0.0
    return _base_row(
        row,
        source_type="defillama_hack_incident",
        chain=_text(row.get("chain"), "chain"),
        asset=_text(row.get("asset"), "asset"),
        loss_usd=loss,
        proposed_action=f"{_text(row.get('incident_type'), 'incident_type')}_response_replay",
        actor_type="incident_response_automation",
        evidence_source_quality=_ratio(row.get("evidence_quality"), "evidence_quality"),
        settlement_finality=_ratio(row.get("settlement_finality"), "settlement_finality"),
        recipient_reputation=_ratio(row.get("recipient_reputation"), "recipient_reputation"),
        liquidity_concentration_observed=_ratio(row.get("liquidity_concentration"), "liquidity_concentration"),
        counterparty_concentration_observed=max(recovery_gap, _ratio(row.get("collateral_stress"), "collateral_stress")),
        market_stress_observed=_ratio(row.get("market_stress"), "market_stress"),
        anomaly_observed=_ratio(row.get("anomaly_score"), "anomaly_score"),
        automation_velocity_observed=_ratio(row.get("automation_velocity"), "automation_velocity"),
    )


def _normalize_elliptic(row: Mapping[str, Any]) -> Dict[str, Any]:
    graph_risk = _ratio(row.get("graph_neighborhood_risk"), "graph_neighborhood_risk")
    cluster_pressure = _ratio(row.get("temporal_cluster_pressure"), "temporal_cluster_pressure")
    class_label = _text(row.get("class_label"), "class_label")
    reputation = min(_ratio(row.get("recipient_reputation"), "recipient_reputation"), 0.42 if class_label == "unknown" else 1.0)
    return _base_row(
        row,
        source_type="elliptic_bitcoin_graph",
        chain=_text(row.get("blockchain"), "blockchain"),
        asset=_text(row.get("asset"), "asset"),
        amount_usd=_money(row, "value_usd"),
        proposed_action=f"bitcoin_graph_{class_label}_counterparty_review",
        actor_type="risk_automation",
        evidence_source_quality=_ratio(row.get("evidence_quality"), "evidence_quality"),
        settlement_finality=_ratio(row.get("settlement_finality"), "settlement_finality"),
        recipient_reputation=reputation,
        liquidity_concentration_observed=cluster_pressure,
        counterparty_concentration_observed=graph_risk,
        market_stress_observed=_ratio(row.get("market_stress"), "market_stress"),
        anomaly_observed=max(graph_risk, _ratio(row.get("anomaly_score"), "anomaly_score")),
        automation_velocity_observed=_ratio(row.get("automation_velocity"), "automation_velocity"),
    )


def _base_row(
    row: Mapping[str, Any],
    *,
    source_type: str,
    chain: str,
    asset: str,
    proposed_action: str,
    actor_type: str,
    evidence_source_quality: float,
    settlement_finality: float,
    recipient_reputation: float,
    liquidity_concentration_observed: float,
    counterparty_concentration_observed: float,
    market_stress_observed: float,
    anomaly_observed: float,
    automation_velocity_observed: float,
    amount_usd: float | None = None,
    loss_usd: float | None = None,
    extra: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    output = {
        "source_id": _text(row.get("record_id"), "record_id").upper().replace("-", "_"),
        "source_type": source_type,
        "source_name": _text(row.get("source_format"), "source_format"),
        "source_url": _text(row.get("source_url"), "source_url"),
        "chain": chain,
        "asset": asset,
        "proposed_action": proposed_action,
        "actor_type": actor_type,
        "current_control_outcome": _current_control(row),
        "evidence_source_quality": round(evidence_source_quality, 3),
        "settlement_finality": round(settlement_finality, 3),
        "recipient_reputation": round(recipient_reputation, 3),
        "liquidity_concentration_observed": round(liquidity_concentration_observed, 3),
        "counterparty_concentration_observed": round(counterparty_concentration_observed, 3),
        "market_stress_observed": round(market_stress_observed, 3),
        "anomaly_observed": round(anomaly_observed, 3),
        "automation_velocity_observed": round(automation_velocity_observed, 3),
    }
    if amount_usd is not None:
        output["amount_usd"] = round(amount_usd, 2)
    if loss_usd is not None:
        output["loss_usd"] = round(loss_usd, 2)
    if extra:
        output.update(dict(extra))
    return output


def _action_for_transfer(row: Mapping[str, Any]) -> str:
    transfer_type = _text(row.get("transfer_type"), "transfer_type")
    if "bridge" in transfer_type:
        return "stablecoin_bridge_transfer"
    if "liquidity" in transfer_type:
        return "stablecoin_liquidity_transfer"
    return "stablecoin_transfer_review"


def _current_control(row: Mapping[str, Any]) -> str:
    value = _text(row.get("existing_control"), "existing_control").upper()
    if value not in {"ALLOW", "REVIEW", "ALERT", "BLOCK"}:
        raise ValueError("existing_control must be ALLOW, REVIEW, ALERT, or BLOCK")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _number(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{path} must be a number")
    numeric = float(value)
    if numeric < 0:
        raise ValueError(f"{path} must be non-negative")
    return numeric


def _money(row: Mapping[str, Any], key: str) -> float:
    return _number(row.get(key), key)


def _ratio(value: Any, path: str) -> float:
    numeric = _number(value, path)
    if numeric > 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return numeric


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize public-data-shaped financial source exports into SMERC-F replay inputs.")
    parser.add_argument("path", help="Path to source export JSON.")
    parser.add_argument("--policy", default="balanced")
    parser.add_argument("--normalized-output", default="examples/smerc_f_normalized_source_rows.json")
    parser.add_argument("--json-output", default="reports/smerc_f_source_ingestion_report.json")
    parser.add_argument("--markdown-output", default="reports/SMERC_F_Source_Ingestion_Report.md")
    parser.add_argument("--replay-json-output", default="reports/smerc_f_source_ingestion_replay_report.json")
    parser.add_argument("--replay-markdown-output", default="reports/SMERC_F_Source_Ingestion_Replay_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_ingestion_report(load_source_exports(args.path), policy=args.policy)
    write_outputs(
        report,
        normalized_output=args.normalized_output,
        json_output=args.json_output,
        markdown_output=args.markdown_output,
        replay_json_output=args.replay_json_output,
        replay_markdown_output=args.replay_markdown_output,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

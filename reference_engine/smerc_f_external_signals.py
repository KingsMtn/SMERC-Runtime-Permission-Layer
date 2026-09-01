from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.financial_permission_profile import FinancialPermissionProfile


VERSION = "smerc-f.external-signals.v1"

SUPPORTED_SIGNAL_PROVIDERS = {
    "blockchain_analytics",
    "transaction_monitoring",
    "wallet_screening",
    "travel_rule",
    "fraud_engine",
    "treasury_risk",
    "stablecoin_reserve_monitor",
    "smart_contract_risk",
}

FINANCIAL_ACTION_TAXONOMY = {
    "customer_refund_batch": {
        "label": "Customer refund batch",
        "default_actor": "finance_ops_agent",
        "base_authorization": 0.78,
        "base_reversibility": 0.62,
        "base_side_effect": "external_funds",
    },
    "payment_release": {
        "label": "Payment release",
        "default_actor": "payment_ops_agent",
        "base_authorization": 0.76,
        "base_reversibility": 0.40,
        "base_side_effect": "external_funds",
    },
    "payment_retry": {
        "label": "Payment retry",
        "default_actor": "payment_ops_agent",
        "base_authorization": 0.72,
        "base_reversibility": 0.45,
        "base_side_effect": "external_funds",
    },
    "treasury_rebalance": {
        "label": "Treasury rebalance",
        "default_actor": "treasury_agent",
        "base_authorization": 0.82,
        "base_reversibility": 0.70,
        "base_side_effect": "internal_or_external_funds",
    },
    "stablecoin_mint": {
        "label": "Stablecoin mint",
        "default_actor": "stablecoin_ops_agent",
        "base_authorization": 0.68,
        "base_reversibility": 0.30,
        "base_side_effect": "token_supply",
    },
    "stablecoin_burn": {
        "label": "Stablecoin burn",
        "default_actor": "stablecoin_ops_agent",
        "base_authorization": 0.70,
        "base_reversibility": 0.34,
        "base_side_effect": "token_supply",
    },
    "stablecoin_redemption": {
        "label": "Stablecoin redemption",
        "default_actor": "stablecoin_ops_agent",
        "base_authorization": 0.72,
        "base_reversibility": 0.28,
        "base_side_effect": "reserve_liquidity",
    },
    "stablecoin_bridge_transfer": {
        "label": "Stablecoin bridge transfer",
        "default_actor": "treasury_agent",
        "base_authorization": 0.64,
        "base_reversibility": 0.20,
        "base_side_effect": "cross_chain_transfer",
    },
    "wallet_permission_update": {
        "label": "Wallet permission update",
        "default_actor": "custody_ops_agent",
        "base_authorization": 0.58,
        "base_reversibility": 0.48,
        "base_side_effect": "authority_change",
    },
    "tokenized_collateral_move": {
        "label": "Tokenized collateral move",
        "default_actor": "collateral_agent",
        "base_authorization": 0.70,
        "base_reversibility": 0.32,
        "base_side_effect": "collateral_position",
    },
    "transaction_limit_change": {
        "label": "Transaction limit change",
        "default_actor": "risk_ops_agent",
        "base_authorization": 0.76,
        "base_reversibility": 0.74,
        "base_side_effect": "policy_change",
    },
    "reserve_status_publish": {
        "label": "Reserve status publish",
        "default_actor": "reporting_agent",
        "base_authorization": 0.66,
        "base_reversibility": 0.24,
        "base_side_effect": "public_reporting",
    },
    "smart_contract_admin_change": {
        "label": "Smart-contract admin change",
        "default_actor": "protocol_ops_agent",
        "base_authorization": 0.56,
        "base_reversibility": 0.18,
        "base_side_effect": "protocol_authority",
    },
}


def load_external_signal_actions(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("SMERC-F external signal input must be a non-empty JSON array")
    seen: set[str] = set()
    rows: list[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise TypeError(f"external signal row {index} must be an object")
        action_id = _text(item.get("action_id"), f"row {index} action_id")
        if action_id in seen:
            raise ValueError(f"duplicate action_id: {action_id}")
        seen.add(action_id)
        action_type = _text(item.get("action_type"), f"{action_id} action_type")
        if action_type not in FINANCIAL_ACTION_TAXONOMY:
            raise ValueError(f"{action_id} action_type must be one of {', '.join(sorted(FINANCIAL_ACTION_TAXONOMY))}")
        signals = item.get("external_signals")
        if not isinstance(signals, list) or not signals:
            raise ValueError(f"{action_id} external_signals must be a non-empty array")
        for signal_index, signal in enumerate(signals):
            if not isinstance(signal, dict):
                raise TypeError(f"{action_id} external_signals[{signal_index}] must be an object")
            provider = _text(signal.get("provider"), f"{action_id} external_signals[{signal_index}] provider")
            if provider not in SUPPORTED_SIGNAL_PROVIDERS:
                raise ValueError(f"{action_id} provider must be one of {', '.join(sorted(SUPPORTED_SIGNAL_PROVIDERS))}")
            _ratio(signal.get("risk_score"), f"{action_id} {provider} risk_score")
            _ratio(signal.get("confidence"), f"{action_id} {provider} confidence")
        rows.append(dict(item))
    return rows


def external_signals_to_financial_action(row: Mapping[str, Any]) -> Dict[str, Any]:
    action_id = _text(row["action_id"], "action_id")
    action_type = _text(row["action_type"], f"{action_id} action_type")
    taxonomy = FINANCIAL_ACTION_TAXONOMY[action_type]
    signals = list(row["external_signals"])
    amount_scale = _amount_scale(row.get("amount_usd", 0))
    provider_risk = _provider_risk(signals)
    evidence_validity = _evidence_validity(signals, row)
    high_risk_signal = max((float(signal["risk_score"]) for signal in signals), default=0.0)
    authorization_support = _authorization_support(row, taxonomy, high_risk_signal)

    finality = _ratio(row.get("settlement_finality", _default_finality(action_type)), f"{action_id} settlement_finality")
    liquidity = max(
        _ratio(row.get("liquidity_pressure", 0.0), f"{action_id} liquidity_pressure"),
        provider_risk.get("stablecoin_reserve_monitor", 0.0),
        provider_risk.get("treasury_risk", 0.0) * 0.65,
    )
    counterparty = max(
        _ratio(row.get("counterparty_concentration", 0.0), f"{action_id} counterparty_concentration"),
        provider_risk.get("wallet_screening", 0.0),
        provider_risk.get("blockchain_analytics", 0.0) * 0.82,
        provider_risk.get("travel_rule", 0.0) * 0.55,
    )
    market = max(
        _ratio(row.get("market_stress", 0.0), f"{action_id} market_stress"),
        provider_risk.get("treasury_risk", 0.0),
        provider_risk.get("smart_contract_risk", 0.0) * 0.45,
    )
    velocity = max(
        _ratio(row.get("automation_velocity", 0.0), f"{action_id} automation_velocity"),
        provider_risk.get("fraud_engine", 0.0) * 0.72,
    )
    model_disagreement = min(
        1.0,
        (1.0 - evidence_validity) * 0.58
        + high_risk_signal * 0.20
        + _signal_disagreement(signals) * 0.34,
    )

    reversibility = min(float(taxonomy["base_reversibility"]), _ratio(row.get("reversibility", taxonomy["base_reversibility"]), f"{action_id} reversibility"))
    reversibility = max(0.02, reversibility - finality * 0.22 - amount_scale * 0.14 - provider_risk.get("smart_contract_risk", 0.0) * 0.18)
    stablecoin_imbalance = 0.0
    if action_type.startswith("stablecoin") or "stablecoin" in _text(row.get("asset", "asset_unknown"), f"{action_id} asset").lower():
        stablecoin_imbalance = min(1.0, liquidity * 0.46 + amount_scale * 0.32 + provider_risk.get("stablecoin_reserve_monitor", 0.0) * 0.36)

    return {
        "action_id": action_id,
        "description": _text(row.get("description"), f"{action_id} description"),
        "action_type": action_type,
        "actor": _text(row.get("actor", taxonomy["default_actor"]), f"{action_id} actor"),
        "authorization_support": round(authorization_support, 3),
        "evidence_validity": round(evidence_validity, 3),
        "reversibility": round(reversibility, 3),
        "liquidity_concentration": round(min(1.0, liquidity), 3),
        "collateral_stress": round(min(1.0, _ratio(row.get("collateral_stress", 0.0), f"{action_id} collateral_stress") + provider_risk.get("smart_contract_risk", 0.0) * 0.46 + market * 0.28), 3),
        "settlement_anomaly": round(min(1.0, finality * 0.35 + high_risk_signal * 0.38 + provider_risk.get("transaction_monitoring", 0.0) * 0.30), 3),
        "stablecoin_imbalance": round(stablecoin_imbalance, 3),
        "counterparty_concentration": round(min(1.0, counterparty), 3),
        "market_instability": round(min(1.0, market), 3),
        "model_disagreement": round(min(1.0, model_disagreement), 3),
        "agent_velocity": round(min(1.0, velocity), 3),
    }


def build_external_signal_report(rows: list[Mapping[str, Any]], *, policy: str = "balanced") -> Dict[str, Any]:
    engine = FinancialPermissionProfile(policy)
    records: list[Dict[str, Any]] = []
    posture_counts: Counter[str] = Counter()
    action_type_counts: Counter[str] = Counter()
    provider_counts: Counter[str] = Counter()
    restrained_authorized = 0

    for row in rows:
        action = external_signals_to_financial_action(row)
        decision = engine.evaluate(action)
        posture_counts[decision["state"]] += 1
        action_type_counts[action["action_type"]] += 1
        providers = sorted({str(signal["provider"]) for signal in row["external_signals"]})
        provider_counts.update(providers)
        current = _text(row.get("existing_control", "ALLOW"), f"{row['action_id']} existing_control").upper()
        if current == "ALLOW" and decision["state"] in {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}:
            restrained_authorized += 1
        records.append(
            {
                "action_id": action["action_id"],
                "action_type": action["action_type"],
                "existing_control": current,
                "providers": providers,
                "normalized_action": action,
                "smerc_f_state": decision["state"],
                "irreversible_exposure": decision["irreversible_exposure"],
                "reversible_capacity": decision["reversible_capacity"],
                "confidence": decision["confidence"],
                "drivers": decision["drivers"],
                "controls": decision["controls"],
                "decision_hash": decision["decision_hash"],
                "work_result_impact": _work_result_impact(row, action, decision, current),
            }
        )

    return {
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "policy": policy,
        "input_action_count": len(rows),
        "taxonomy_action_count": len(FINANCIAL_ACTION_TAXONOMY),
        "supported_signal_providers": sorted(SUPPORTED_SIGNAL_PROVIDERS),
        "action_type_counts": dict(sorted(action_type_counts.items())),
        "provider_counts": dict(sorted(provider_counts.items())),
        "smerc_f_state_counts": {state: posture_counts.get(state, 0) for state in ("ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE")},
        "authorized_restraint_count": restrained_authorized,
        "authorized_restraint_rate": round(restrained_authorized / len(rows), 3) if rows else 0.0,
        "highest_exposure_records": sorted(records, key=lambda item: item["irreversible_exposure"], reverse=True)[:8],
        "records": records,
        "evidence_boundary": (
            "External signal adapter only. SMERC-F consumes vendor-style AML/KYT, wallet, travel-rule, fraud, treasury, "
            "reserve, and smart-contract risk outputs as pre-execution evidence. It does not perform AML compliance, "
            "sanctions screening, address attribution, Travel Rule compliance, custody, settlement, transaction execution, "
            "legal determination, or production certification."
        ),
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC-F External Financial Signal Adapter Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Policy: `{report['policy']}`",
        "",
        "## Purpose",
        "",
        "This report shows how SMERC-F can consume external financial-risk and compliance-style signals as evidence before automated financial actions execute.",
        "",
        "The point is not to replace AML, KYT, wallet screening, fraud, Travel Rule, custody, settlement, or compliance systems. The point is to use their outputs as evidence while SMERC-F adds recoverability-aware pre-execution posture.",
        "",
        "## Summary",
        "",
        f"- Input actions: `{report['input_action_count']}`",
        f"- Taxonomy action types: `{report['taxonomy_action_count']}`",
        f"- State counts: `{report['smerc_f_state_counts']}`",
        f"- Authorized actions restrained by SMERC-F: `{report['authorized_restraint_count']}`",
        f"- Authorized restraint rate: `{report['authorized_restraint_rate']}`",
        "",
        "## Supported External Signal Providers",
        "",
    ]
    for provider in report["supported_signal_providers"]:
        lines.append(f"- `{provider}`")
    lines.extend(["", "## Financial Action Taxonomy", "", "| Action type | Count in sample |", "| --- | ---: |"])
    for action_type in sorted(FINANCIAL_ACTION_TAXONOMY):
        lines.append(f"| `{action_type}` | {report['action_type_counts'].get(action_type, 0)} |")
    lines.extend(["", "## Provider Counts", "", "| Provider | Actions |", "| --- | ---: |"])
    for provider, count in report["provider_counts"].items():
        lines.append(f"| `{provider}` | {count} |")
    lines.extend(["", "## Highest Exposure Records", "", "| Action | Existing control | SMERC-F | Exposure | Capacity | Providers | Drivers |", "| --- | --- | --- | ---: | ---: | --- | --- |"])
    for record in report["highest_exposure_records"]:
        providers = ", ".join(f"`{provider}`" for provider in record["providers"])
        drivers = ", ".join(f"`{driver}`" for driver in record["drivers"][:4])
        lines.append(
            f"| `{record['action_id']}` | `{record['existing_control']}` | `{record['smerc_f_state']}` | "
            f"{record['irreversible_exposure']} | {record['reversible_capacity']} | {providers} | {drivers} |"
        )
    lines.extend(["", "## Work / Result / Impact", "", "| Work | Result | Impact |", "| --- | --- | --- |"])
    for record in report["highest_exposure_records"][:5]:
        item = record["work_result_impact"]
        lines.append(f"| {item['work']} | {item['result']} | {item['impact']} |")
    lines.extend(["", "## Evidence Boundary", "", str(report["evidence_boundary"]), ""])
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any], json_output: str | Path, markdown_output: str | Path) -> None:
    json_path = Path(json_output)
    markdown_path = Path(markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")


def _work_result_impact(row: Mapping[str, Any], action: Mapping[str, Any], decision: Mapping[str, Any], current: str) -> Dict[str, str]:
    providers = ", ".join(sorted({str(signal["provider"]) for signal in row["external_signals"]}))
    work = f"Normalize `{action['action_type']}` with external signals from {providers} into SMERC-F recoverability fields."
    result = f"Existing control was `{current}`; SMERC-F returned `{decision['state']}` with exposure {decision['irreversible_exposure']} and capacity {decision['reversible_capacity']}."
    if current == "ALLOW" and decision["state"] in {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}:
        impact = "This is the target proof: existing systems allowed the action, but recoverability evidence supports restraint before execution."
    elif current in {"REVIEW", "ALERT"} and decision["state"] in {"THROTTLE", "FREEZE", "DENY", "ESCALATE"}:
        impact = "SMERC-F converts review or alert evidence into a concrete pre-execution route and retained decision proof."
    elif decision["state"] == "ALLOW":
        impact = "SMERC-F preserves evidence while allowing a bounded action to proceed."
    else:
        impact = "Reviewer calibration is needed because the source-system outcome and recoverability posture differ."
    return {"work": work, "result": result, "impact": impact}


def _provider_risk(signals: Iterable[Mapping[str, Any]]) -> Dict[str, float]:
    output: Dict[str, float] = {}
    for signal in signals:
        provider = str(signal["provider"])
        risk = float(signal["risk_score"])
        confidence = float(signal["confidence"])
        output[provider] = max(output.get(provider, 0.0), min(1.0, risk * (0.70 + confidence * 0.30)))
    return output


def _evidence_validity(signals: Iterable[Mapping[str, Any]], row: Mapping[str, Any]) -> float:
    confidences = [float(signal["confidence"]) for signal in signals]
    if not confidences:
        return 0.0
    source_quality = _ratio(row.get("source_quality", 0.76), f"{row['action_id']} source_quality")
    stale_penalty = min(0.28, _number(row.get("signal_age_minutes", 0), f"{row['action_id']} signal_age_minutes") / 1440.0)
    return round(max(0.0, min(1.0, sum(confidences) / len(confidences) * 0.72 + source_quality * 0.28 - stale_penalty)), 3)


def _authorization_support(row: Mapping[str, Any], taxonomy: Mapping[str, Any], high_risk_signal: float) -> float:
    current = _text(row.get("existing_control", "ALLOW"), f"{row['action_id']} existing_control").upper()
    if current not in {"ALLOW", "REVIEW", "ALERT", "BLOCK"}:
        raise ValueError(f"{row['action_id']} existing_control must be ALLOW, REVIEW, ALERT, or BLOCK")
    base = float(taxonomy["base_authorization"])
    current_support = {"ALLOW": 0.88, "REVIEW": 0.66, "ALERT": 0.48, "BLOCK": 0.16}[current]
    return max(0.0, min(1.0, base * 0.42 + current_support * 0.46 + (1.0 - high_risk_signal) * 0.12))


def _signal_disagreement(signals: Iterable[Mapping[str, Any]]) -> float:
    risks = [float(signal["risk_score"]) for signal in signals]
    if len(risks) < 2:
        return 0.0
    mean = sum(risks) / len(risks)
    variance = sum((risk - mean) ** 2 for risk in risks) / len(risks)
    return min(1.0, math.sqrt(variance) * 2.4)


def _amount_scale(value: Any) -> float:
    amount = _number(value, "amount_usd")
    if amount <= 0:
        return 0.0
    return min(1.0, math.log10(amount + 1.0) / 9.0)


def _default_finality(action_type: str) -> float:
    if action_type in {"stablecoin_bridge_transfer", "stablecoin_redemption", "stablecoin_mint", "stablecoin_burn", "smart_contract_admin_change"}:
        return 0.86
    if action_type in {"payment_release", "payment_retry", "tokenized_collateral_move"}:
        return 0.72
    return 0.46


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    return value.strip()


def _number(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{path} must be a non-negative number")
    numeric = float(value)
    if numeric < 0:
        raise ValueError(f"{path} must be non-negative")
    return numeric


def _ratio(value: Any, path: str) -> float:
    numeric = _number(value, path)
    if numeric > 1:
        raise ValueError(f"{path} must be between 0.0 and 1.0")
    return numeric


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate SMERC-F actions with external financial signal evidence.")
    parser.add_argument("path", help="Path to external-signal action JSON.")
    parser.add_argument("--policy", default="balanced")
    parser.add_argument("--json-output", default="reports/smerc_f_external_signal_report.json")
    parser.add_argument("--markdown-output", default="reports/SMERC_F_External_Signal_Report.md")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_external_signal_report(load_external_signal_actions(args.path), policy=args.policy)
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

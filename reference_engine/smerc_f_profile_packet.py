from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from reference_engine.financial_permission_profile import POLICY_PROFILES, FinancialPermissionProfile


SMERC_F_PROFILE_PACKET_VERSION = "smerc-f.profile-packet.v1"

SIGNAL_TAXONOMY = {
    "treasury": ["liquidity_concentration", "collateral_stress"],
    "settlement": ["settlement_anomaly"],
    "stablecoin": ["stablecoin_imbalance"],
    "counterparty": ["counterparty_concentration"],
    "market": ["market_instability"],
    "behavioral": ["model_disagreement"],
    "agent": ["agent_velocity"],
    "governance": ["authorization_support", "evidence_validity", "reversibility"],
}

COMMERCIAL_LIMITS = [
    "SMERC-F is not a bank, broker-dealer, exchange, custodian, token, stablecoin, cryptocurrency, trading system, or investment product.",
    "The current profile is a reference governance profile, not institution-calibrated financial risk infrastructure.",
    "The profile does not predict market prices, solvency, depegs, liquidity events, or settlement failures.",
    "Production use requires institution-specific calibration, model-risk review, security review, compliance review, legal review, and accountable human ownership.",
]


def _load_actions(path: str | Path) -> list[Dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return [payload]
    if not isinstance(payload, list) or not payload:
        raise ValueError("financial action packet input must be a non-empty object or list")
    if any(not isinstance(item, dict) for item in payload):
        raise TypeError("financial action packet input must contain only objects")
    return payload


def build_profile_packet(actions_path: str | Path, *, policies: Iterable[str] = ("balanced",)) -> Dict[str, Any]:
    actions = _load_actions(actions_path)
    selected_policies = list(policies)
    if not selected_policies:
        raise ValueError("at least one policy must be selected")
    unknown = sorted(set(selected_policies) - set(POLICY_PROFILES))
    if unknown:
        raise ValueError(f"unknown financial policy profile(s): {', '.join(unknown)}")

    evaluations = []
    state_distribution: Dict[str, Dict[str, int]] = {}
    for policy_name in selected_policies:
        profile = FinancialPermissionProfile(policy_name)
        state_distribution[policy_name] = {}
        for action in actions:
            result = profile.evaluate(action)
            state_distribution[policy_name][result["state"]] = state_distribution[policy_name].get(result["state"], 0) + 1
            evaluations.append(
                {
                    "policy": policy_name,
                    "action_id": action["action_id"],
                    "action_type": action["action_type"],
                    "state": result["state"],
                    "confidence": result["confidence"],
                    "signal_risk": result["signal_risk"],
                    "irreversible_exposure": result["irreversible_exposure"],
                    "reversible_capacity": result["reversible_capacity"],
                    "drivers": result["drivers"],
                    "controls": result["controls"],
                    "recommended_action": result["recommended_action"],
                    "decision_hash": result["decision_hash"],
                }
            )

    high_restraint = [
        item
        for item in evaluations
        if item["state"] in {"FREEZE", "DENY", "ESCALATE"}
    ]
    return {
        "version": SMERC_F_PROFILE_PACKET_VERSION,
        "profile": "SMERC-F",
        "positioning": "Pre-execution permission governance for proposed autonomous-capital actions.",
        "action_count": len(actions),
        "policies": selected_policies,
        "signal_taxonomy": SIGNAL_TAXONOMY,
        "state_distribution": state_distribution,
        "high_restraint_count": len(high_restraint),
        "evaluations": evaluations,
        "recommended_pilot_scope": [
            "Historical replay and synthetic scenario review before live workflow use.",
            "Shadow-mode scoring only for first financial workflow pilot.",
            "No automated money movement, custody action, settlement instruction, or production blocking without legal, compliance, security, and operational approval.",
        ],
        "commercial_limits": COMMERCIAL_LIMITS,
    }


def render_markdown(packet: Mapping[str, Any]) -> str:
    lines = [
        "# SMERC-F Profile Packet",
        "",
        packet["positioning"],
        "",
        "This packet is a financial-governance profile review artifact. It is not a banking product, not a cryptocurrency, not a trading product, not a token, and not a production-certified financial control.",
        "",
        "## Summary",
        "",
        f"- Actions evaluated: `{packet['action_count']}`",
        f"- Policies: `{', '.join(packet['policies'])}`",
        f"- High-restraint outcomes: `{packet['high_restraint_count']}`",
        "",
        "## Signal Taxonomy",
        "",
    ]
    for category, signals in packet["signal_taxonomy"].items():
        lines.append(f"- `{category}`: {', '.join(f'`{signal}`' for signal in signals)}")
    lines.extend(["", "## State Distribution", "", "| Policy | State | Count |", "| --- | --- | --- |"])
    for policy, states in packet["state_distribution"].items():
        for state, count in sorted(states.items()):
            lines.append(f"| `{policy}` | `{state}` | `{count}` |")
    lines.extend(["", "## Evaluations", "", "| Policy | Action | State | Exposure | Capacity | Key drivers |", "| --- | --- | --- | --- | --- | --- |"])
    for item in packet["evaluations"]:
        drivers = ", ".join(f"`{driver}`" for driver in item["drivers"][:4])
        lines.append(
            f"| `{item['policy']}` | `{item['action_id']}` | `{item['state']}` | "
            f"`{item['irreversible_exposure']}` | `{item['reversible_capacity']}` | {drivers} |"
        )
    lines.extend(["", "## Recommended Pilot Scope", ""])
    lines.extend(f"- {item}" for item in packet["recommended_pilot_scope"])
    lines.extend(["", "## Commercial Limits", ""])
    lines.extend(f"- {item}" for item in packet["commercial_limits"])
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a SMERC-F financial governance profile packet.")
    parser.add_argument("actions", help="Path to financial action request JSON.")
    parser.add_argument("--policies", nargs="+", default=["balanced"], choices=sorted(POLICY_PROFILES))
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--json-output")
    parser.add_argument("--markdown-output")
    args = parser.parse_args()
    packet = build_profile_packet(args.actions, policies=args.policies)
    if args.json_output:
        _write_json(Path(args.json_output), packet)
    if args.markdown_output:
        _write_text(Path(args.markdown_output), render_markdown(packet))
    print(json.dumps(packet, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

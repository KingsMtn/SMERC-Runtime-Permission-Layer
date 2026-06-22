from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from reference_engine.financial_permission_profile import POLICY_PROFILES, FinancialPermissionProfile


STATE_SEVERITY = {
    "ALLOW": 0,
    "THROTTLE": 1,
    "ESCALATE": 2,
    "FREEZE": 3,
    "DENY": 4,
}


class FinancialReplayEngine:
    """Replay analyst-assigned financial signals through SMERC-F chronologically."""

    def __init__(self, policy: str = "balanced") -> None:
        self.profile = FinancialPermissionProfile(policy)

    def replay_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        self._validate_scenario(scenario)
        decisions: List[Dict[str, Any]] = []

        for index, event in enumerate(scenario["timeline"]):
            action = dict(event["action"])
            action["action_id"] = f"{scenario['scenario_id']}_{index + 1}"
            result = self.profile.evaluate(action)
            decisions.append(
                {
                    "sequence": index + 1,
                    "phase": event["phase"],
                    "historical_context": event["historical_context"],
                    "signal_basis": event["signal_basis"],
                    "state": result["state"],
                    "confidence": result["confidence"],
                    "irreversible_exposure": result["irreversible_exposure"],
                    "reversible_capacity": result["reversible_capacity"],
                    "drivers": result["drivers"],
                    "controls": result["controls"],
                    "recommended_action": result["recommended_action"],
                }
            )

        transitions = []
        for previous, current in zip(decisions, decisions[1:]):
            if previous["state"] != current["state"]:
                transitions.append(
                    {
                        "from": previous["state"],
                        "to": current["state"],
                        "at_phase": current["phase"],
                    }
                )

        peak = max(decisions, key=lambda item: STATE_SEVERITY[item["state"]])
        final = decisions[-1]
        return {
            "scenario_id": scenario["scenario_id"],
            "title": scenario["title"],
            "event_date": scenario["event_date"],
            "sources": scenario["sources"],
            "replay_disclaimer": scenario["replay_disclaimer"],
            "decisions": decisions,
            "metrics": {
                "events_replayed": len(decisions),
                "transition_count": len(transitions),
                "peak_state": peak["state"],
                "peak_phase": peak["phase"],
                "peak_irreversible_exposure": max(item["irreversible_exposure"] for item in decisions),
                "minimum_reversible_capacity": min(item["reversible_capacity"] for item in decisions),
                "final_state": final["state"],
                "state_distribution": dict(Counter(item["state"] for item in decisions)),
            },
            "transitions": transitions,
        }

    def replay_dataset(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("Replay dataset must be a non-empty list")
        results = [self.replay_scenario(scenario) for scenario in scenarios]
        all_decisions = [decision for result in results for decision in result["decisions"]]
        restrictive = [decision for decision in all_decisions if decision["state"] != "ALLOW"]
        return {
            "method": "historical-context replay with analyst-assigned SMERC-F signals",
            "prediction_claim": False,
            "policy": {"name": self.profile.policy.name, "version": self.profile.policy.version},
            "scenario_count": len(results),
            "event_count": len(all_decisions),
            "state_distribution": dict(Counter(item["state"] for item in all_decisions)),
            "restrictive_posture_rate": round(len(restrictive) / len(all_decisions), 3),
            "average_irreversible_exposure": round(
                sum(item["irreversible_exposure"] for item in all_decisions) / len(all_decisions), 3
            ),
            "average_reversible_capacity": round(
                sum(item["reversible_capacity"] for item in all_decisions) / len(all_decisions), 3
            ),
            "scenarios": results,
        }

    @staticmethod
    def _validate_scenario(scenario: Dict[str, Any]) -> None:
        required = ["scenario_id", "title", "event_date", "sources", "replay_disclaimer", "timeline"]
        missing = [key for key in required if key not in scenario]
        if missing:
            raise ValueError(f"Missing replay scenario field(s): {', '.join(missing)}")
        if not isinstance(scenario["sources"], list) or not scenario["sources"]:
            raise ValueError("Replay scenario must include at least one source")
        if not isinstance(scenario["timeline"], list) or len(scenario["timeline"]) < 2:
            raise ValueError("Replay scenario must contain at least two chronological events")
        for event in scenario["timeline"]:
            event_missing = [key for key in ["phase", "historical_context", "signal_basis", "action"] if key not in event]
            if event_missing:
                raise ValueError(f"Missing replay event field(s): {', '.join(event_missing)}")


def render_markdown_report(dataset: Dict[str, Any]) -> str:
    lines = [
        "# SMERC-F Replay Validation Report",
        "",
        "## Method",
        "",
        "Historical event context is sourced. Numerical SMERC-F inputs are analyst-assigned replay signals, not measured historical telemetry. This report evaluates state-transition coherence and makes no prediction claim.",
        "",
        "## Summary",
        "",
        f"- Scenarios: {dataset['scenario_count']}",
        f"- Policy: {dataset['policy']['name']} {dataset['policy']['version']}",
        f"- Timeline events: {dataset['event_count']}",
        f"- Restrictive posture rate: {dataset['restrictive_posture_rate']:.1%}",
        f"- Average irreversible exposure: {dataset['average_irreversible_exposure']:.3f}",
        f"- Average reversible capacity: {dataset['average_reversible_capacity']:.3f}",
        f"- State distribution: {json.dumps(dataset['state_distribution'], sort_keys=True)}",
        "",
    ]
    for scenario in dataset["scenarios"]:
        metrics = scenario["metrics"]
        lines.extend(
            [
                f"## {scenario['title']}",
                "",
                f"Event date: {scenario['event_date']}",
                "",
                f"Peak state: `{metrics['peak_state']}` during **{metrics['peak_phase']}**.",
                "",
                "| Phase | State | Exposure | Capacity | Primary drivers |",
                "| --- | --- | ---: | ---: | --- |",
            ]
        )
        for decision in scenario["decisions"]:
            lines.append(
                f"| {decision['phase']} | `{decision['state']}` | "
                f"{decision['irreversible_exposure']:.3f} | {decision['reversible_capacity']:.3f} | "
                f"{', '.join(decision['drivers'][:3])} |"
            )
        lines.extend(["", "Sources:"])
        for source in scenario["sources"]:
            lines.append(f"- [{source['title']}]({source['url']})")
        lines.extend(["", f"Replay limitation: {scenario['replay_disclaimer']}", ""])

    lines.extend(
        [
            "## Interpretation",
            "",
            "These outputs demonstrate deterministic state transitions under the supplied replay assumptions. They do not establish predictive accuracy, causal risk reduction, regulatory compliance, or production readiness. Real validation requires institution-specific telemetry and reviewer comparison in shadow mode.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay financial stress scenarios through SMERC-F.")
    parser.add_argument("path", help="Path to a JSON list of replay scenarios.")
    parser.add_argument("--policy", choices=sorted(POLICY_PROFILES), default="balanced")
    parser.add_argument("--json-output", help="Optional path for the replay result JSON.")
    parser.add_argument("--report", help="Optional path for a Markdown validation report.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print result JSON to stdout.")
    args = parser.parse_args()

    scenarios = json.loads(Path(args.path).read_text(encoding="utf-8"))
    result = FinancialReplayEngine(args.policy).replay_dataset(scenarios)
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.report:
        Path(args.report).write_text(render_markdown_report(result), encoding="utf-8")
    if not args.json_output and not args.report:
        print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()


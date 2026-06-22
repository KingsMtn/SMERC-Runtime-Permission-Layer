from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from reference_engine.financial_permission_profile import POLICY_PROFILES, FinancialPermissionProfile


STATE_SEVERITY = {"ALLOW": 0, "THROTTLE": 1, "ESCALATE": 2, "FREEZE": 3, "DENY": 4}


def compare_policies(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(actions, list) or not actions:
        raise ValueError("actions must be a non-empty list")

    rows = []
    distributions = {name: Counter() for name in POLICY_PROFILES}
    for action in actions:
        decisions = {
            name: FinancialPermissionProfile(name).evaluate(action)
            for name in POLICY_PROFILES
        }
        for name, decision in decisions.items():
            distributions[name][decision["state"]] += 1
        rows.append(
            {
                "action_id": action["action_id"],
                "description": action["description"],
                "decisions": {
                    name: {
                        "state": decision["state"],
                        "irreversible_exposure": decision["irreversible_exposure"],
                        "reversible_capacity": decision["reversible_capacity"],
                        "decision_hash": decision["decision_hash"],
                    }
                    for name, decision in decisions.items()
                },
                "policy_difference": len({decision["state"] for decision in decisions.values()}) > 1,
            }
        )

    difference_count = sum(1 for row in rows if row["policy_difference"])
    monotonic_count = sum(
        1
        for row in rows
        if STATE_SEVERITY[row["decisions"]["conservative"]["state"]]
        >= STATE_SEVERITY[row["decisions"]["balanced"]["state"]]
        >= STATE_SEVERITY[row["decisions"]["permissive"]["state"]]
    )
    return {
        "action_count": len(rows),
        "policy_difference_count": difference_count,
        "policy_difference_rate": round(difference_count / len(rows), 3),
        "monotonic_restraint_count": monotonic_count,
        "monotonic_restraint_rate": round(monotonic_count / len(rows), 3),
        "state_distributions": {name: dict(counter) for name, counter in distributions.items()},
        "actions": rows,
    }


def render_policy_report(result: Dict[str, Any]) -> str:
    lines = [
        "# SMERC-F Policy Comparison Report",
        "",
        "## Purpose",
        "",
        "Compare identical proposed financial actions under conservative, balanced, and permissive reference policies. The profiles demonstrate calibration behavior; they are not institution-approved limits.",
        "",
        "## Summary",
        "",
        f"- Actions evaluated: {result['action_count']}",
        f"- Actions with different policy outcomes: {result['policy_difference_count']} ({result['policy_difference_rate']:.1%})",
        f"- Actions preserving monotonic restraint: {result['monotonic_restraint_count']} ({result['monotonic_restraint_rate']:.1%})",
        "",
        "| Action | Conservative | Balanced | Permissive | Different? |",
        "| --- | --- | --- | --- | --- |",
    ]
    for action in result["actions"]:
        decisions = action["decisions"]
        lines.append(
            f"| {action['action_id']} | `{decisions['conservative']['state']}` | "
            f"`{decisions['balanced']['state']}` | `{decisions['permissive']['state']}` | "
            f"{'Yes' if action['policy_difference'] else 'No'} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A conservative policy should never be less restrictive than the balanced profile for the same input, and the balanced profile should never be less restrictive than the permissive profile. Differences identify actions that require institution-specific calibration and reviewer testing.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare SMERC-F policy profiles.")
    parser.add_argument("path", help="Path to a JSON list of financial actions.")
    parser.add_argument("--json-output", help="Optional path for comparison JSON.")
    parser.add_argument("--report", help="Optional path for a Markdown report.")
    args = parser.parse_args()
    actions = json.loads(Path(args.path).read_text(encoding="utf-8"))
    result = compare_policies(actions)
    if args.json_output:
        Path(args.json_output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.report:
        Path(args.report).write_text(render_policy_report(result), encoding="utf-8")
    if not args.json_output and not args.report:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()


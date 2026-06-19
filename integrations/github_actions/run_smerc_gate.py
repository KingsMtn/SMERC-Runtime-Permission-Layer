from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from reference_engine.agent_permission_layer import RuntimePermissionEngine  # noqa: E402


VALID_MODES = {"observe", "recommend", "enforce"}


def _load_action(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Action request file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("GitHub Action integration expects one JSON action request object.")
    return payload


def _write_github_output(values: Dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def _summary_lines(decision: Dict[str, Any], mode: str) -> Iterable[str]:
    yield "# SMERC Runtime Permission Decision"
    yield ""
    yield f"- Mode: `{mode}`"
    yield f"- Posture: `{decision['posture']}`"
    yield f"- Risk score: `{decision['risk_score']}`"
    yield f"- Confidence score: `{decision['confidence_score']}`"
    yield f"- Replay ID: `{decision['replay_id']}`"
    yield ""
    yield "## Constraints"
    for control in decision["constraints"]:
        yield f"- `{control}`"
    yield ""
    yield "## Reason Codes"
    for reason in decision["reason_codes"]:
        yield f"- `{reason}`"
    yield ""
    yield "## Summary"
    yield decision["plain_english_summary"]


def _write_step_summary(decision: Dict[str, Any], mode: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    Path(summary_path).write_text("\n".join(_summary_lines(decision, mode)) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SMERC as a GitHub Actions permission gate.")
    parser.add_argument("--action-file", required=True, help="Path to a JSON action request.")
    parser.add_argument("--mode", default="observe", choices=sorted(VALID_MODES))
    parser.add_argument("--output-file", default="smerc-decision.json")
    parser.add_argument("--fail-on", default="DENY,FREEZE")
    args = parser.parse_args()

    action_path = Path(args.action_file)
    output_path = Path(args.output_file)
    fail_on = {item.strip().upper() for item in args.fail_on.split(",") if item.strip()}

    decision = RuntimePermissionEngine().evaluate(_load_action(action_path))
    report = {
        "mode": args.mode,
        "enforcement": {
            "fail_on": sorted(fail_on),
            "would_fail": decision["posture"] in fail_on,
            "active": args.mode == "enforce",
        },
        "decision": decision,
    }

    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_step_summary(decision, args.mode)
    _write_github_output(
        {
            "posture": decision["posture"],
            "risk-score": str(decision["risk_score"]),
            "replay-id": decision["replay_id"],
        }
    )

    print(json.dumps(report, indent=2))

    if args.mode == "enforce" and decision["posture"] in fail_on:
        print(f"SMERC enforce mode failed on posture {decision['posture']}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


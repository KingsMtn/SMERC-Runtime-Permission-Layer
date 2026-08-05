from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from smerc_sdk import SMERCClient


INTEGRATION_VERSION = "smerc.agent-handshake-runner.v1"

POSTURE_RULES: dict[str, dict[str, Any]] = {
    "ALLOW": {
        "runner_state": "execute",
        "may_execute": True,
        "requires_controls": False,
        "requires_human_review": False,
    },
    "THROTTLE": {
        "runner_state": "constrained_execute",
        "may_execute": True,
        "requires_controls": True,
        "requires_human_review": False,
    },
    "FREEZE": {
        "runner_state": "pause",
        "may_execute": False,
        "requires_controls": True,
        "requires_human_review": True,
    },
    "DENY": {
        "runner_state": "block",
        "may_execute": False,
        "requires_controls": False,
        "requires_human_review": False,
    },
    "ESCALATE": {
        "runner_state": "escalate",
        "may_execute": False,
        "requires_controls": True,
        "requires_human_review": True,
    },
}


def build_runner_report(handshake: Mapping[str, Any]) -> dict[str, Any]:
    posture = handshake.get("handshake_posture")
    if posture not in POSTURE_RULES:
        raise ValueError("handshake_posture must be one of ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE")
    replay = handshake.get("replay")
    if not isinstance(replay, Mapping):
        raise TypeError("handshake response must include a replay object")

    rule = POSTURE_RULES[posture]
    controls = list(handshake.get("controls") or [])
    required_controls = controls if rule["requires_controls"] else []
    runner_state = rule["runner_state"]
    return {
        "integration_version": INTEGRATION_VERSION,
        "handshake_id": handshake.get("handshake_id"),
        "replay_id": handshake.get("replay_id"),
        "agent_id": handshake.get("agent_id"),
        "handshake_posture": posture,
        "runner_state": runner_state,
        "may_execute": rule["may_execute"],
        "requires_controls": rule["requires_controls"],
        "requires_human_review": rule["requires_human_review"],
        "required_controls": required_controls,
        "recommended_executor": handshake.get("recommended_executor"),
        "executor_posture": handshake.get("executor_posture"),
        "action_posture": handshake.get("action_posture"),
        "reason_codes": list(handshake.get("reason_codes") or []),
        "plain_english_summary": _summary(handshake, runner_state, required_controls),
        "replay": {
            "handshake_replay_id": handshake.get("replay_id"),
            "fitness_replay_id": replay.get("fitness_replay_id"),
            "action_replay_id": replay.get("action_replay_id"),
        },
    }


def _summary(handshake: Mapping[str, Any], runner_state: str, required_controls: list[str]) -> str:
    posture = handshake.get("handshake_posture")
    agent_id = handshake.get("agent_id")
    if runner_state == "execute":
        return f"SMERC returned ALLOW for agent {agent_id}; the runner may proceed while retaining the replay record."
    if runner_state == "constrained_execute":
        return (
            f"SMERC returned THROTTLE for agent {agent_id}; the runner may proceed only after applying "
            f"the required controls: {', '.join(required_controls)}."
        )
    if runner_state == "pause":
        return f"SMERC returned FREEZE for agent {agent_id}; the runner must pause automation and obtain review."
    if runner_state == "block":
        return f"SMERC returned DENY for agent {agent_id}; the runner must block automated execution."
    return f"SMERC returned {posture} for agent {agent_id}; the runner must escalate before execution."


def run_handshake(api_url: str, token: str | None, handshake_request: Mapping[str, Any]) -> dict[str, Any]:
    client = SMERCClient(api_url, token=token)
    handshake = client.agent_handshake(handshake_request)
    return build_runner_report(handshake)


def main() -> int:
    parser = argparse.ArgumentParser(description="Call SMERC Agent Handshake API and produce a safe runner report.")
    parser.add_argument("--api-url", default=os.environ.get("SMERC_API_URL", "http://127.0.0.1:8788"))
    parser.add_argument("--token", default=os.environ.get("SMERC_API_TOKEN"))
    parser.add_argument("--handshake-file", type=Path, required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    request = json.loads(args.handshake_file.read_text(encoding="utf-8"))
    report = run_handshake(args.api_url, args.token, request)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

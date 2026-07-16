import copy
import json
import unittest
from pathlib import Path

from integrations.agent_handshake.agent_handshake_runner import build_runner_report
from reference_engine.agent_handshake import AgentHandshakeEngine


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "examples" / "agent_handshake_request.json").read_text(encoding="utf-8"))


class AgentHandshakeIntegrationTests(unittest.TestCase):
    def test_throttle_maps_to_constrained_execution_with_controls(self):
        handshake = AgentHandshakeEngine().evaluate(EXAMPLE)
        report = build_runner_report(handshake)

        self.assertEqual(report["integration_version"], "smerc.agent-handshake-runner.v1")
        self.assertEqual(report["handshake_posture"], "THROTTLE")
        self.assertEqual(report["runner_state"], "constrained_execute")
        self.assertTrue(report["may_execute"])
        self.assertTrue(report["requires_controls"])
        self.assertIn("record_agent_handshake", report["required_controls"])
        self.assertIn("fitness_replay_id", report["replay"])
        self.assertIn("action_replay_id", report["replay"])

    def test_freeze_maps_to_pause_and_review(self):
        request = copy.deepcopy(EXAMPLE)
        request["agent"]["capabilities"] = ["summarization"]
        handshake = AgentHandshakeEngine().evaluate(request)
        report = build_runner_report(handshake)

        self.assertEqual(report["handshake_posture"], "FREEZE")
        self.assertEqual(report["runner_state"], "pause")
        self.assertFalse(report["may_execute"])
        self.assertTrue(report["requires_human_review"])
        self.assertIn("pause_agent_execution", report["required_controls"])

    def test_deny_blocks_without_required_controls(self):
        handshake = AgentHandshakeEngine().evaluate(EXAMPLE)
        handshake["handshake_posture"] = "DENY"
        report = build_runner_report(handshake)

        self.assertEqual(report["runner_state"], "block")
        self.assertFalse(report["may_execute"])
        self.assertFalse(report["requires_controls"])
        self.assertEqual(report["required_controls"], [])

    def test_escalate_requires_review_before_execution(self):
        handshake = AgentHandshakeEngine().evaluate(EXAMPLE)
        handshake["handshake_posture"] = "ESCALATE"
        report = build_runner_report(handshake)

        self.assertEqual(report["runner_state"], "escalate")
        self.assertFalse(report["may_execute"])
        self.assertTrue(report["requires_human_review"])

    def test_unknown_posture_is_rejected(self):
        handshake = AgentHandshakeEngine().evaluate(EXAMPLE)
        handshake["handshake_posture"] = "MAYBE"

        with self.assertRaises(ValueError):
            build_runner_report(handshake)


if __name__ == "__main__":
    unittest.main()

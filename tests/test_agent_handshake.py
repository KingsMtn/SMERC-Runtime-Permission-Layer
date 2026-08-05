import copy
import json
import unittest
from pathlib import Path

from reference_engine.agent_handshake import AgentHandshakeEngine


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "agent_handshake_request.json"


class AgentHandshakeTests(unittest.TestCase):
    def setUp(self):
        self.engine = AgentHandshakeEngine()
        self.request = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_valid_handshake_combines_beacon_fitness_and_action_posture(self):
        result = self.engine.evaluate(self.request)
        self.assertTrue(result["beacon_valid"])
        self.assertEqual(result["recommended_executor"], "github_deployment_agent")
        self.assertEqual(result["executor_posture"], "THROTTLE")
        self.assertEqual(result["action_posture"], "THROTTLE")
        self.assertEqual(result["handshake_posture"], "THROTTLE")
        self.assertIn("BEACON_VALIDATED", result["reason_codes"])
        self.assertIn("record_agent_handshake", result["controls"])
        self.assertIn("fitness_replay_id", result["replay"])
        self.assertIn("action_replay_id", result["replay"])

    def test_agent_capability_gap_freezes_handshake(self):
        request = copy.deepcopy(self.request)
        request["agent"]["capabilities"] = ["summarization"]
        result = self.engine.evaluate(request)
        self.assertEqual(result["handshake_posture"], "FREEZE")
        self.assertIn("AGENT_DECLARED_CAPABILITY_GAP", result["agent_issues"])
        self.assertIn("pause_agent_execution", result["controls"])

    def test_agent_data_access_gap_freezes_handshake(self):
        request = copy.deepcopy(self.request)
        request["agent"]["requested_data_access"] = ["public", "internal"]
        result = self.engine.evaluate(request)
        self.assertEqual(result["handshake_posture"], "FREEZE")
        self.assertIn("AGENT_DATA_ACCESS_TOO_NARROW", result["agent_issues"])

    def test_invalid_beacon_is_rejected(self):
        request = copy.deepcopy(self.request)
        request["beacon"]["schema_version"] = "wrong.version"
        with self.assertRaises(ValueError):
            self.engine.evaluate(request)

    def test_validation_rejects_missing_schema(self):
        request = copy.deepcopy(self.request)
        request.pop("schema_version")
        with self.assertRaises(ValueError):
            self.engine.evaluate(request)


if __name__ == "__main__":
    unittest.main()

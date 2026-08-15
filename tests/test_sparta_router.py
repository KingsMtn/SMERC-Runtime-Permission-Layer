import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.recoverability_engine import RecoverabilityEngine
from reference_engine.sparta_router import SpartaRouter, load_json_file, route_decision


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "recoverability_action_requests.json"
MCP_EXAMPLE = ROOT / "examples" / "mcp_tool_call_action.json"


class SpartaRouterTests(unittest.TestCase):
    def setUp(self):
        self.engine = RecoverabilityEngine()
        self.actions = json.loads(EXAMPLES.read_text(encoding="utf-8"))

    def by_id(self, action_id):
        return next(action for action in self.actions if action["action_id"] == action_id)

    def test_throttled_action_gets_constrained_execution_permit(self):
        action = self.by_id("AGENT_DEPLOY_PROD_CONFIG")
        decision = self.engine.evaluate(action)
        route = route_decision(action, decision)

        self.assertEqual(route["posture"], "THROTTLE")
        self.assertEqual(route["route"], "constrained_execution")
        self.assertEqual(route["permit_status"], "issued_with_constraints")
        self.assertIn("platform_engineering", route["reviewer_path"])
        self.assertIn("scope_bound_permit", route["required_controls"])
        self.assertFalse(route["execution_boundaries"]["execution_blocked"])

    def test_frozen_action_requires_evidence_before_execution(self):
        action = self.by_id("AGENT_DELETE_AUDIT_LOGS")
        decision = self.engine.evaluate(action)
        route = route_decision(action, decision)

        self.assertEqual(route["posture"], "FREEZE")
        self.assertEqual(route["route"], "pause_for_evidence")
        self.assertEqual(route["permit_status"], "withheld_pending_evidence")
        self.assertTrue(route["execution_boundaries"]["requires_human_before_execution"])
        self.assertIn("human_evidence_review", route["required_controls"])

    def test_denied_action_blocks_execution_and_withholds_permit(self):
        action = self.by_id("AGENT_EXPORT_CUSTOMER_DATA")
        decision = self.engine.evaluate(action)
        route = route_decision(action, decision)

        self.assertEqual(route["posture"], "DENY")
        self.assertEqual(route["route"], "block")
        self.assertEqual(route["permit_status"], "withheld_blocked")
        self.assertTrue(route["execution_boundaries"]["execution_blocked"])
        self.assertIn("blocked_action_attestation", route["required_controls"])

    def test_mcp_context_and_telemetry_are_preserved(self):
        action = json.loads(MCP_EXAMPLE.read_text(encoding="utf-8"))
        decision = self.engine.evaluate(action)
        route = SpartaRouter(signing_secret="test-secret").route(action, decision)

        self.assertEqual(route["mcp_context"]["protocol"], "mcp")
        self.assertEqual(route["mcp_context"]["tool_server"], "prod-database-mcp")
        self.assertEqual(route["mcp_context"]["agent_identity"], "agent://support-triage-prod")
        self.assertEqual(route["telemetry_context"]["trace_id"], "trace-mcp-001")
        self.assertEqual(route["telemetry_context"]["otel_semantic_target"], "gen_ai.agent.tool_execution")
        self.assertIn("mcp_tool_call_intercepted", route["required_controls"])
        self.assertIsNotNone(route["route_signature"])

    def test_route_hash_is_stable_for_same_action_and_decision(self):
        action = self.by_id("AGENT_DEPLOY_PROD_CONFIG")
        decision = self.engine.evaluate(action)
        first = route_decision(action, decision)
        second = route_decision(action, decision)

        self.assertEqual(first["route_id"], second["route_id"])
        self.assertEqual(first["decision_artifact_hash"], second["decision_artifact_hash"])

    def test_cli_loader_accepts_utf16_json_from_powershell_redirect(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-16", delete=False) as handle:
            json.dump({"action_id": "UTF16_REDIRECT"}, handle)
            path = handle.name

        self.assertEqual(load_json_file(path)["action_id"], "UTF16_REDIRECT")


if __name__ == "__main__":
    unittest.main()

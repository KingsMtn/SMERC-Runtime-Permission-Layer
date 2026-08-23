import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.mcp_governance_gateway import (
    MCP_GOVERNANCE_GATEWAY_VERSION,
    evaluate_gateway_session,
    load_json,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "examples" / "mcp" / "governance_gateway_registry.json"
SESSION = ROOT / "examples" / "mcp" / "governance_gateway_session.json"
DOC = ROOT / "docs" / "MCP_Governance_Gateway.md"
TEST_OUTPUTS = ROOT / "test_outputs"
TEST_OUTPUTS.mkdir(exist_ok=True)


class MCPGovernanceGatewayTests(unittest.TestCase):
    def test_gateway_evaluates_session_with_financial_profile(self):
        report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="enforce")

        self.assertEqual(report["version"], MCP_GOVERNANCE_GATEWAY_VERSION)
        self.assertEqual(report["request_count"], 4)
        self.assertEqual(report["registered_tool_count"], 3)
        self.assertGreater(report["blocked_or_held_count"], 0)
        self.assertEqual(report["ref_gate_failure_count"], 1)
        self.assertIn("smerc_f", {item["profile"] for item in report["decisions"]})
        self.assertTrue(any("high_risk_tool_tier" in item["gateway_pressure"]["drivers"] for item in report["decisions"]))
        self.assertTrue(any(item["tool_name"] == "stablecoin_treasury_transfer" for item in report["decisions"]))

    def test_gateway_tracks_scope_loop_and_budget_pressure(self):
        report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="enforce")
        drivers = {driver for item in report["decisions"] for driver in item["gateway_pressure"]["drivers"]}

        self.assertIn("scope_exceeds_registry_limit", drivers)
        self.assertIn("session_budget_pressure", drivers)
        self.assertIn("object_shape_unexpected", drivers)
        self.assertGreater(report["cumulative_cost_units"], 8.0)
        highest = report["highest_pressure_calls"][0]
        self.assertEqual(highest["gateway_pressure"]["score"], 1.0)
        self.assertEqual(highest["ref_gate"]["status"], "fail")

    def test_gateway_fails_closed_on_ref_gate_failure(self):
        report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="enforce")
        failed = [item for item in report["decisions"] if item["ref_gate"]["status"] == "fail"]

        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["mcp_request_id"], "MCP_STABLECOIN_TRANSFER_004")
        self.assertIn("object_shape_unexpected", failed[0]["ref_gate"]["drivers"])
        self.assertFalse(failed[0]["should_forward_tool_call"])
        self.assertIn(failed[0]["posture"], {"DENY", "FREEZE"})

    def test_markdown_and_docs_are_bounded(self):
        report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="enforce")
        markdown = render_markdown(report)
        docs = DOC.read_text(encoding="utf-8")

        self.assertIn("SMERC MCP Governance Gateway Report", markdown)
        self.assertIn("Highest Pressure Calls", markdown)
        self.assertIn("Ref Gate", markdown)
        self.assertIn("SMERC-F", docs)
        for phrase in ["OAuth", "mTLS", "payment rails", "x402", "prompt-injection defense", "production billing"]:
            self.assertIn(phrase, docs)
            self.assertIn(phrase, markdown)

    def test_writes_outputs(self):
        report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="shadow")
        json_path = TEST_OUTPUTS / "mcp_gateway_test.json"
        markdown_path = TEST_OUTPUTS / "mcp_gateway_test.md"
        write_outputs(report, json_path=json_path, markdown_path=markdown_path)
        self.assertIn(MCP_GOVERNANCE_GATEWAY_VERSION, json_path.read_text(encoding="utf-8"))
        self.assertIn("SMERC MCP Governance Gateway Report", markdown_path.read_text(encoding="utf-8"))

    def test_cli_generates_gateway_report(self):
        json_path = TEST_OUTPUTS / "mcp_gateway_cli_test.json"
        markdown_path = TEST_OUTPUTS / "mcp_gateway_cli_test.md"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "reference_engine.mcp_governance_gateway",
                "--registry",
                str(REGISTRY),
                "--session",
                str(SESSION),
                "--mode",
                "enforce",
                "--json-output",
                str(json_path),
                "--markdown-output",
                str(markdown_path),
                "--pretty",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(report["version"], MCP_GOVERNANCE_GATEWAY_VERSION)
        self.assertIn("SMERC MCP Governance Gateway Report", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

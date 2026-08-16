import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from reference_engine.mcp_proxy_runner import MCP_PROXY_RUNNER_VERSION, render_markdown, run_mcp_proxy, write_outputs


ROOT = Path(__file__).resolve().parents[1]
DELETE_CALL = ROOT / "examples" / "mcp" / "tool_call_delete_customer_records.json"
SEARCH_CALL = ROOT / "examples" / "mcp" / "tool_call_search_docs.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MCPProxyRunnerTests(unittest.TestCase):
    def test_shadow_mode_observes_and_forwards_destructive_call(self):
        report = run_mcp_proxy(load(DELETE_CALL), mode="shadow")
        response = report["proxy_response"]

        self.assertEqual(report["version"], MCP_PROXY_RUNNER_VERSION)
        self.assertEqual(response["proxy_action"], "observe_and_forward_tool_call")
        self.assertTrue(response["should_forward_tool_call"])
        self.assertEqual(report["governance_report"]["recommended_mcp_result"], "block_tool_call")
        self.assertEqual(report["governance_report"]["decision"]["posture"], "DENY")
        self.assertTrue(report["decision_lifecycle_ledger"]["verification"]["valid"])
        self.assertEqual(report["decision_lifecycle_ledger"]["record_count"], 7)
        evidence_record = report["decision_lifecycle_ledger"]["records"][1]
        self.assertEqual(
            evidence_record["payload"]["confidence_score"],
            report["governance_report"]["decision"]["scores"]["confidence_score"],
        )

    def test_enforce_mode_blocks_destructive_call(self):
        report = run_mcp_proxy(load(DELETE_CALL), mode="enforce")
        response = report["proxy_response"]

        self.assertEqual(response["proxy_action"], "block_tool_call")
        self.assertFalse(response["should_forward_tool_call"])
        self.assertEqual(response["decision_reference"]["route_state"], "BLOCK")
        self.assertIn("Block the tool call.", response["proxy_instructions"])

    def test_enforce_mode_forwards_safe_read_call(self):
        report = run_mcp_proxy(load(SEARCH_CALL), mode="enforce")
        response = report["proxy_response"]

        self.assertEqual(response["proxy_action"], "forward_tool_call")
        self.assertTrue(response["should_forward_tool_call"])
        self.assertFalse(response["constraint_applied"])
        self.assertEqual(response["decision_reference"]["posture"], "ALLOW")

    def test_invalid_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "mode must be"):
            run_mcp_proxy(load(SEARCH_CALL), mode="observe")

    def test_markdown_and_outputs_are_reviewable(self):
        report = run_mcp_proxy(load(DELETE_CALL), mode="enforce")
        markdown = render_markdown(report)

        self.assertIn("SMERC MCP Proxy Runner Report", markdown)
        self.assertIn("Proxy Decision", markdown)
        self.assertIn("block_tool_call", markdown)
        self.assertIn("Decision Lifecycle Ledger", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "proxy.json"
            markdown_path = Path(directory) / "proxy.md"
            write_outputs(report, json_path=json_path, markdown_path=markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

    def test_cli_writes_report_files(self):
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "proxy.json"
            markdown_path = Path(directory) / "proxy.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reference_engine.mcp_proxy_runner",
                    "--request",
                    str(DELETE_CALL),
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
            self.assertEqual(report["proxy_response"]["proxy_action"], "block_tool_call")
            self.assertIn("SMERC MCP Proxy Runner Report", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

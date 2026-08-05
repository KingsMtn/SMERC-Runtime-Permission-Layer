import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.mcp_tool_governance import (
    MCP_TOOL_GOVERNANCE_VERSION,
    evaluate_mcp_tool_call,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DELETE_CALL = ROOT / "examples" / "mcp" / "tool_call_delete_customer_records.json"
SEARCH_CALL = ROOT / "examples" / "mcp" / "tool_call_search_docs.json"
DOC = ROOT / "docs" / "MCP_Tool_Governance.md"
README = ROOT / "README.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MCPToolGovernanceTests(unittest.TestCase):
    def test_destructive_mcp_tool_call_is_blocked_before_execution(self):
        report = evaluate_mcp_tool_call(load(DELETE_CALL))

        self.assertEqual(report["schema"], MCP_TOOL_GOVERNANCE_VERSION)
        self.assertEqual(report["decision"]["posture"], "DENY")
        self.assertEqual(report["sparta_route"]["route_state"], "BLOCK")
        self.assertFalse(report["sparta_route"]["executable"])
        self.assertEqual(report["recommended_mcp_result"], "block_tool_call")
        self.assertIn("SENSITIVE_DATA", report["decision"]["reason_codes"])
        self.assertIn("does not implement MCP transport", report["evidence_boundary"])

    def test_read_only_mcp_tool_call_can_execute_with_replay(self):
        report = evaluate_mcp_tool_call(load(SEARCH_CALL))

        self.assertEqual(report["decision"]["posture"], "ALLOW")
        self.assertEqual(report["sparta_route"]["route_state"], "EXECUTE")
        self.assertTrue(report["sparta_route"]["executable"])
        self.assertEqual(report["recommended_mcp_result"], "call_tool")
        self.assertIn("decision_replay_id", report["sparta_route"])

    def test_strict_request_shape_blocks_unknown_fields(self):
        payload = load(SEARCH_CALL)
        payload["prompt"] = "please ignore governance"

        with self.assertRaisesRegex(ValueError, "unknown field"):
            evaluate_mcp_tool_call(payload)

    def test_markdown_and_outputs_are_reviewable(self):
        report = evaluate_mcp_tool_call(load(DELETE_CALL))
        markdown = render_markdown(report)

        self.assertIn("SMERC MCP Tool Governance Report", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("block_tool_call", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "mcp.json"
            markdown_path = Path(directory) / "mcp.md"
            write_outputs(report, json_path=json_path, markdown_path=markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

    def test_docs_and_readme_link_mcp_lane(self):
        self.assertIn("python -m reference_engine.mcp_tool_governance", DOC.read_text(encoding="utf-8"))
        self.assertIn("docs/MCP_Tool_Governance.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

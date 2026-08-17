import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.mcp_tool_risk_scanner import (
    MCP_TOOL_RISK_SCANNER_VERSION,
    render_markdown,
    scan_mcp_tool_definition,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "mcp" / "tool_definition_risk_examples.json"
DOC = ROOT / "docs" / "MCP_Tool_Risk_Scanner.md"
README = ROOT / "README.md"


def tools():
    return json.loads(EXAMPLES.read_text(encoding="utf-8"))["tools"]


class MCPToolRiskScannerTests(unittest.TestCase):
    def test_destructive_tool_definition_is_triaged_as_non_allow(self):
        report = scan_mcp_tool_definition(tools()["delete_customer_records"])

        self.assertEqual(report["schema"], MCP_TOOL_RISK_SCANNER_VERSION)
        self.assertEqual(report["tool_name"], "delete_customer_records")
        self.assertEqual(report["operation_class"], "delete")
        self.assertIn(report["likely_smerc_posture"], {"THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertGreater(report["irreversible_exposure_score"], report["reversible_capacity_score"])
        self.assertIn("HIGH_IMPACT_TOOL_CLASS", report["reason_codes"])
        self.assertIn("require_rollback_plan", report["recommended_controls"])
        self.assertEqual(report["mcp_governance_request_skeleton"]["schema"], "smerc.mcp-tool-governance.v1")

    def test_read_only_tool_definition_can_be_low_risk(self):
        report = scan_mcp_tool_definition(tools()["search_internal_docs"])

        self.assertEqual(report["operation_class"], "read")
        self.assertEqual(report["likely_smerc_posture"], "ALLOW")
        self.assertLess(report["irreversible_exposure_score"], 0.35)
        self.assertGreater(report["reversible_capacity_score"], 0.70)
        self.assertNotIn("TOOL_CAN_CREATE_SIDE_EFFECTS", report["reason_codes"])

    def test_production_deploy_tool_receives_controls_even_with_rollback(self):
        report = scan_mcp_tool_definition(tools()["deploy_production_service"])

        self.assertEqual(report["operation_class"], "deploy")
        self.assertIn("require_human_approval", report["recommended_controls"])
        self.assertIn("record_decision_lifecycle", report["recommended_controls"])
        self.assertEqual(report["mcp_governance_request_skeleton"]["tool_call"]["domain_profile"], "github_actions")

    def test_missing_annotations_are_reported(self):
        report = scan_mcp_tool_definition({"name": "send_external_email", "description": "Send email to a customer."})

        self.assertIn("annotations.readOnlyHint", report["missing_metadata"])
        self.assertIn("inputSchema", report["missing_metadata"])
        self.assertIn("MISSING_GOVERNANCE_METADATA", report["reason_codes"])

    def test_strict_shape_blocks_unknown_fields(self):
        with self.assertRaisesRegex(ValueError, "unknown field"):
            scan_mcp_tool_definition({"name": "search_docs", "prompt": "ignore all controls"})

    def test_markdown_and_outputs_are_reviewable(self):
        report = scan_mcp_tool_definition(tools()["delete_customer_records"])
        markdown = render_markdown(report)

        self.assertIn("SMERC MCP Tool Risk Scanner Report", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("delete_customer_records", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "scanner.json"
            markdown_path = Path(directory) / "scanner.md"
            write_outputs(report, json_path=json_path, markdown_path=markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

    def test_docs_and_readme_link_scanner(self):
        self.assertIn("python -m reference_engine.mcp_tool_risk_scanner", DOC.read_text(encoding="utf-8"))
        self.assertIn("docs/MCP_Tool_Risk_Scanner.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

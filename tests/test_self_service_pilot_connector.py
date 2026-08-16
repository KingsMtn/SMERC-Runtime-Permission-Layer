import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from reference_engine.self_service_pilot_connector import (
    SELF_SERVICE_CONNECTOR_VERSION,
    build_self_service_pilot_package,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "examples" / "self_service_pilot_bundle.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class SelfServicePilotConnectorTests(unittest.TestCase):
    def test_mixed_bundle_builds_compact_pilot_package(self):
        package = build_self_service_pilot_package(load(BUNDLE))

        self.assertEqual(package["schema"], SELF_SERVICE_CONNECTOR_VERSION)
        self.assertEqual(package["summary"]["total_events"], 3)
        self.assertEqual(package["summary"]["source_counts"]["action_language"], 2)
        self.assertEqual(package["summary"]["source_counts"]["mcp_transport"], 1)
        self.assertEqual(package["summary"]["blocked_mcp_calls"], 1)
        self.assertEqual(package["summary"]["pilot_fit"]["fit"], "strong")
        self.assertEqual(len(package["records"]), 3)

    def test_records_preserve_runtime_details(self):
        package = build_self_service_pilot_package(load(BUNDLE))
        records = {record["event_id"]: record for record in package["records"]}

        self.assertEqual(records["SSP_DB_CHANGE_001"]["posture"], "DENY")
        self.assertIn("block_execution", records["SSP_DB_CHANGE_001"]["controls"])
        self.assertEqual(records["SSP_MCP_DELETE_001"]["mcp_proxy_action"], "block_tool_call")
        self.assertFalse(records["SSP_MCP_DELETE_001"]["mcp_forwarded"])
        self.assertTrue(records["SSP_STAGING_DEPLOY_001"]["scores"]["reversible_capacity_score"] > 0.70)

    def test_invalid_source_type_is_rejected(self):
        bundle = load(BUNDLE)
        bundle["events"][0]["source_type"] = "spreadsheet"
        with self.assertRaisesRegex(ValueError, "source_type"):
            build_self_service_pilot_package(bundle)

    def test_duplicate_event_id_is_rejected(self):
        bundle = load(BUNDLE)
        bundle["events"][1]["event_id"] = bundle["events"][0]["event_id"]
        with self.assertRaisesRegex(ValueError, "duplicate event_id"):
            build_self_service_pilot_package(bundle)

    def test_markdown_and_outputs_are_reviewable(self):
        package = build_self_service_pilot_package(load(BUNDLE))
        markdown = render_markdown(package)

        self.assertIn("SMERC Self-Service Pilot Connector Report", markdown)
        self.assertIn("Pilot fit", markdown)
        self.assertIn("SSP_MCP_DELETE_001", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "self-service.json"
            markdown_path = Path(directory) / "self-service.md"
            write_outputs(package, json_path=json_path, markdown_path=markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())

    def test_cli_writes_report_files(self):
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "self-service.json"
            markdown_path = Path(directory) / "self-service.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reference_engine.self_service_pilot_connector",
                    "--bundle",
                    str(BUNDLE),
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
            self.assertEqual(report["summary"]["pilot_fit"]["fit"], "strong")
            self.assertIn("SMERC Self-Service Pilot Connector Report", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

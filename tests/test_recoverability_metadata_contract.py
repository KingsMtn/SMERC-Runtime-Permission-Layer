import unittest
from pathlib import Path

from reference_engine.recoverability_metadata_contract import (
    build_contract_report,
    load_records,
    render_markdown,
    validate_record,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "recoverability_metadata_examples.json"


class RecoverabilityMetadataContractTests(unittest.TestCase):
    def test_examples_validate(self):
        report = build_contract_report(load_records(EXAMPLES))

        self.assertEqual(report["version"], "smerc.recoverability-metadata-contract.v0")
        self.assertEqual(report["record_count"], 3)
        self.assertEqual(report["valid_record_count"], 3)
        self.assertEqual(report["invalid_record_count"], 0)
        self.assertIn("THROTTLE", report["posture_counts"])
        self.assertIn("bedrock_action_group", report["environment_boundary_counts"])
        self.assertIn("dedicated_account", report["host_isolation_counts"])
        self.assertIn("sandbox_escape_or_credential_surface", report["risk_hint_counts"])

    def test_invalid_record_fails_closed(self):
        result = validate_record(
            {
                "version": "smerc.recoverability-metadata.v0",
                "action_id": "BAD-001",
                "action_type": "tool_call",
            }
        )

        self.assertFalse(result["valid"])
        self.assertIn("missing fields", result["errors"][0])
        self.assertEqual(result["risk_hint"], "invalid")

    def test_environment_boundary_fields_validate_and_fail_closed(self):
        result = validate_record(
            {
                "version": "smerc.recoverability-metadata.v0",
                "action_id": "BAD-ISO-001",
                "action_type": "tool_call",
                "tool_system": "mcp.shell",
                "reversible": True,
                "rollback_latency_seconds": 10,
                "external_side_effect": True,
                "blast_radius_scope": "developer workstation",
                "evidence_available": "operator note",
                "tooling_isolation": "root_everywhere",
                "host_isolation": "container",
                "network_isolation": "internet",
                "sandbox_escape_surface": ["none_known", "docker_socket"],
                "execution_environment_boundary": "mcp_server",
                "recommended_posture": "THROTTLE",
            }
        )

        self.assertFalse(result["valid"])
        self.assertIn("tooling_isolation must be one of", "; ".join(result["errors"]))
        self.assertIn(
            "sandbox_escape_surface cannot combine none_known with other surfaces",
            "; ".join(result["errors"]),
        )

    def test_markdown_and_docs_reference_boundary(self):
        markdown = render_markdown(build_contract_report(load_records(EXAMPLES)))
        docs = (ROOT / "docs" / "Recoverability_Metadata_Contract.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Recoverability Metadata Contract Report", markdown)
        self.assertIn("Environment boundary counts", markdown)
        self.assertIn("hint contract", markdown)
        self.assertIn("Optional Environment Boundary Evidence", docs)
        self.assertIn("sandbox_escape_surface", docs)
        self.assertIn("python -m reference_engine.recoverability_metadata_contract", docs)
        self.assertIn("docs/Recoverability_Metadata_Contract.md", readme)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "recoverability_metadata_contract"
        report = build_contract_report(load_records(EXAMPLES))
        json_output = scratch / "report.json"
        markdown_output = scratch / "report.md"

        write_outputs(report, json_output=json_output, markdown_output=markdown_output)

        self.assertTrue(json_output.exists())
        self.assertIn("Recoverability Metadata Contract Report", markdown_output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

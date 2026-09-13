import unittest
from pathlib import Path

from reference_engine.dynamic_schema_gate import build_report, evaluate_tool_call, load_payload, render_markdown


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "dynamic_schema_gate_examples.json"


class DynamicSchemaGateTests(unittest.TestCase):
    def test_builds_dynamic_schema_gate_report(self):
        report = build_report(load_payload(INPUTS))

        self.assertEqual(report["version"], "smerc.dynamic-schema-gate.v1")
        self.assertEqual(report["registry_count"], 5)
        self.assertEqual(report["tool_call_count"], 7)
        self.assertEqual(report["classification_counts"]["VALID"], 1)
        self.assertIn("UNKNOWN_SCHEMA", report["classification_counts"])
        self.assertIn("DRIFTED", report["classification_counts"])
        self.assertIn("STRUCTURAL_MISMATCH", report["classification_counts"])
        self.assertIn("UNSAFE", report["classification_counts"])
        self.assertIn("UNDER_SPECIFIED", report["classification_counts"])

    def test_valid_call_allows_but_risky_shapes_fail_closed(self):
        report = build_report(load_payload(INPUTS))
        by_id = {decision["call_id"]: decision for decision in report["decisions"]}

        self.assertEqual(by_id["DSG-001"]["smerc_posture"], "ALLOW")
        self.assertEqual(by_id["DSG-002"]["smerc_posture"], "ESCALATE")
        self.assertEqual(by_id["DSG-003"]["smerc_posture"], "THROTTLE")
        self.assertEqual(by_id["DSG-004"]["smerc_posture"], "DENY")
        self.assertEqual(by_id["DSG-005"]["smerc_posture"], "DENY")
        self.assertEqual(by_id["DSG-006"]["smerc_posture"], "ESCALATE")
        self.assertEqual(by_id["DSG-007"]["smerc_posture"], "DENY")

    def test_direct_evaluation_unknown_schema(self):
        payload = load_payload(INPUTS)
        registry = {f"{row['tool_name']}@{row['schema_version']}": row for row in payload["schema_registry"]}

        result = evaluate_tool_call(
            {
                "call_id": "DSG-UNKNOWN",
                "tool_name": "unknown.tool",
                "schema_version": "2026-09-01",
                "arguments": {},
            },
            registry,
        )

        self.assertEqual(result["classification"], "UNKNOWN_SCHEMA")
        self.assertEqual(result["smerc_posture"], "ESCALATE")
        self.assertIn("SCHEMA_NOT_IN_GATE_INDEX", result["reason_codes"])

    def test_markdown_and_docs_are_reviewer_readable(self):
        markdown = render_markdown(build_report(load_payload(INPUTS)))
        doc = (ROOT / "docs" / "Dynamic_Schema_Gate.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("SMERC Dynamic Schema Gate Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("python -m reference_engine.dynamic_schema_gate", doc)
        self.assertIn("docs/Dynamic_Schema_Gate.md", readme)


if __name__ == "__main__":
    unittest.main()

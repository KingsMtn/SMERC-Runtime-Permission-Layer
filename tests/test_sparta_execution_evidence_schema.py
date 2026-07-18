import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "smerc-sparta-execution-evidence-v1.schema.json"
EXECUTION_SCHEMA = ROOT / "schemas" / "smerc-execution-report-v1.schema.json"
EXAMPLE_REPORT = ROOT / "reports" / "execution_report_example.json"


class SPARTaExecutionEvidenceSchemaTests(unittest.TestCase):
    def test_schema_exists_and_defines_verified_binding_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["version"]["const"], "smerc.sparta-execution-evidence.v1")
        self.assertIn("route_report_digest", schema["required"])
        binding = schema["properties"]["binding"]
        self.assertEqual(binding["properties"]["valid"]["const"], True)
        checks = binding["properties"]["checks"]["properties"]
        self.assertEqual(checks["replay_id_matches"]["const"], True)
        self.assertEqual(checks["posture_matches"]["const"], True)
        self.assertEqual(checks["route_is_executable"]["const"], True)
        self.assertEqual(checks["required_controls_declared_by_route"]["const"], True)

    def test_execution_report_schema_references_sparta_evidence_schema(self):
        schema = json.loads(EXECUTION_SCHEMA.read_text(encoding="utf-8"))
        sparta_property = schema["properties"]["sparta"]
        self.assertIn({"$ref": "smerc-sparta-execution-evidence-v1.schema.json"}, sparta_property["oneOf"])
        self.assertIn({"type": "null"}, sparta_property["oneOf"])

    def test_example_execution_report_uses_verified_sparta_evidence_shape(self):
        report = json.loads(EXAMPLE_REPORT.read_text(encoding="utf-8"))
        sparta = report["sparta"]
        self.assertEqual(sparta["version"], "smerc.sparta-execution-evidence.v1")
        self.assertRegex(sparta["route_report_digest"], r"^[0-9a-f]{64}$")
        self.assertTrue(sparta["binding"]["valid"])
        self.assertEqual(sparta["binding"]["missing_required_controls"], [])
        self.assertTrue(all(sparta["binding"]["checks"].values()))


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.schema_conformance import (
    SchemaConformanceUnavailable,
    validate_instance,
    validate_schema_catalog,
    validate_schema_document,
)


try:
    import jsonschema  # noqa: F401
except ImportError:
    jsonschema = None


@unittest.skipIf(jsonschema is None, "optional jsonschema dependency is not installed")
class SchemaConformanceTests(unittest.TestCase):
    def test_repository_schema_catalog_is_valid(self):
        report = validate_schema_catalog()
        self.assertEqual(report["status"], "PASS")
        self.assertGreater(report["schema_count"], 20)
        self.assertEqual(report["invalid_count"], 0)

    def test_invalid_schema_is_reported_without_stopping_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "valid.schema.json").write_text(
                json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object"}),
                encoding="utf-8",
            )
            (root / "invalid.schema.json").write_text(
                json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "type": 7}),
                encoding="utf-8",
            )
            report = validate_schema_catalog(root)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["valid_count"], 1)
        self.assertEqual(report["invalid_count"], 1)

    def test_instance_validation_rejects_contract_drift(self):
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["version"],
            "properties": {"version": {"const": "smerc.example.v1"}},
            "additionalProperties": False,
        }
        validate_instance({"version": "smerc.example.v1"}, schema)
        with self.assertRaises(Exception):
            validate_instance({"version": "smerc.example.v2"}, schema)


class SchemaConformanceDependencyTests(unittest.TestCase):
    def test_missing_dependency_has_install_guidance(self):
        if jsonschema is not None:
            self.skipTest("optional jsonschema dependency is installed")
        with self.assertRaisesRegex(SchemaConformanceUnavailable, "requirements-schema-validation.txt"):
            validate_schema_document({"type": "object"})


if __name__ == "__main__":
    unittest.main()

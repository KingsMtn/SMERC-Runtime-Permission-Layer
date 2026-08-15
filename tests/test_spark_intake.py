import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.action_language import ACTION_VERSION, evaluate_language_action
from reference_engine.spark_intake import (
    SPARK_EVIDENCE_VERSION,
    build_intake_report,
    compile_spark_to_action,
    spark_evidence_hash,
    validate_spark_evidence,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
GITHUB_SPARK = ROOT / "examples" / "spark" / "github_actions_spark_evidence.json"
MCP_SPARK = ROOT / "examples" / "spark" / "mcp_tool_spark_evidence.json"
SCHEMA = ROOT / "schemas" / "smerc-spark-evidence-v1.schema.json"


class SparkIntakeTests(unittest.TestCase):
    def test_schema_and_examples_exist(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["version"]["const"], SPARK_EVIDENCE_VERSION)
        self.assertTrue(GITHUB_SPARK.exists())
        self.assertTrue(MCP_SPARK.exists())

    def test_validates_and_hashes_spark_evidence(self):
        payload = json.loads(GITHUB_SPARK.read_text(encoding="utf-8"))
        evidence = validate_spark_evidence(payload)
        self.assertEqual(evidence["version"], SPARK_EVIDENCE_VERSION)
        digest = spark_evidence_hash(payload)
        self.assertEqual(len(digest), 64)

    def test_compiles_spark_to_action_language_and_evaluates(self):
        payload = json.loads(GITHUB_SPARK.read_text(encoding="utf-8"))
        action = compile_spark_to_action(payload)
        self.assertEqual(action["language_version"], ACTION_VERSION)
        self.assertEqual(action["action"]["id"], "deploy-prod-canary")
        self.assertEqual(action["context"]["spark"]["evidence_id"], "spark-gha-001")
        decision = evaluate_language_action(action)
        self.assertIn(decision["posture"], {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})

    def test_evidence_gaps_reduce_readiness_but_still_compile(self):
        payload = json.loads(MCP_SPARK.read_text(encoding="utf-8"))
        report = build_intake_report(payload)
        self.assertEqual(report["readiness"], "evidence_gaps_present")
        self.assertEqual(report["evidence_gap_count"], 3)
        self.assertEqual(report["action_language"]["effects"]["sensitive_data"], True)

    def test_rejects_secret_boundary_false(self):
        payload = json.loads(GITHUB_SPARK.read_text(encoding="utf-8"))
        payload["non_secret_boundary"] = False
        with self.assertRaisesRegex(ValueError, "non_secret_boundary"):
            validate_spark_evidence(payload)

    def test_writes_intake_report(self):
        payload = json.loads(GITHUB_SPARK.read_text(encoding="utf-8"))
        report = build_intake_report(payload)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "spark.json"
            write_outputs(report, json_path=output)
            parsed = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(parsed["evidence_id"], "spark-gha-001")


if __name__ == "__main__":
    unittest.main()

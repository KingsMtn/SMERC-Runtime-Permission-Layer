import json
import unittest
from pathlib import Path

from reference_engine.timing_evidence import (
    TIMING_EVIDENCE_VERSION,
    TIMING_REPORT_VERSION,
    build_timing_report,
    render_markdown,
    validate_timing_evidence,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
TIMING = ROOT / "examples" / "timing" / "github_actions_timing_evidence.json"
SCHEMA = ROOT / "schemas" / "smerc-timing-evidence-v1.schema.json"


class TimingEvidenceTests(unittest.TestCase):
    def test_schema_and_example_exist(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["version"]["const"], TIMING_EVIDENCE_VERSION)
        self.assertTrue(TIMING.exists())

    def test_validates_timing_evidence(self):
        payload = json.loads(TIMING.read_text(encoding="utf-8"))
        evidence = validate_timing_evidence(payload)
        self.assertEqual(evidence["version"], TIMING_EVIDENCE_VERSION)
        self.assertEqual(len(evidence["records"]), 3)

    def test_builds_latency_and_resilience_report(self):
        payload = json.loads(TIMING.read_text(encoding="utf-8"))
        report = build_timing_report(payload, latency_slo_ms=250)
        self.assertEqual(report["version"], TIMING_REPORT_VERSION)
        self.assertEqual(report["record_count"], 3)
        self.assertEqual(report["operational_status"], "ready")
        self.assertEqual(report["resilience"]["cancel_success_rate"], 1.0)
        self.assertEqual(report["resilience"]["rollback_success_rate"], 1.0)
        self.assertLess(report["decision_latency"]["p95_ms"], 250)

    def test_unavailable_rate_can_block(self):
        payload = json.loads(TIMING.read_text(encoding="utf-8"))
        payload["records"][0]["posture"] = "UNAVAILABLE"
        payload["records"][0]["unavailable_evaluation"] = True
        report = build_timing_report(payload, latency_slo_ms=250)
        self.assertEqual(report["operational_status"], "blocker")

    def test_rejects_cancel_success_without_attempt(self):
        payload = json.loads(TIMING.read_text(encoding="utf-8"))
        payload["records"][0]["cancel_success"] = True
        with self.assertRaisesRegex(ValueError, "cancel_success"):
            validate_timing_evidence(payload)

    def test_writes_json_and_markdown(self):
        payload = json.loads(TIMING.read_text(encoding="utf-8"))
        report = build_timing_report(payload, latency_slo_ms=250)
        scratch = ROOT / "tests" / "_tmp" / "timing_evidence"
        json_path = scratch / "timing.json"
        markdown_path = scratch / "timing.md"

        write_outputs(report, json_path=json_path, markdown_path=markdown_path)
        parsed = json.loads(json_path.read_text(encoding="utf-8"))
        markdown = markdown_path.read_text(encoding="utf-8")

        self.assertEqual(parsed["version"], TIMING_REPORT_VERSION)
        self.assertIn("# SMERC Timing Evidence Report", markdown)
        self.assertIn("Evidence Boundary", render_markdown(report))


if __name__ == "__main__":
    unittest.main()

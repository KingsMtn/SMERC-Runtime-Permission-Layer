import json
import unittest
from pathlib import Path

from reference_engine.dll_intelligence import (
    DLL_INTELLIGENCE_VERSION,
    analyze_ledgers,
    build_example_bundle,
    render_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


class DLLIntelligenceTests(unittest.TestCase):
    def test_example_bundle_produces_governance_intelligence(self):
        bundle = build_example_bundle()
        report = analyze_ledgers(bundle["ledgers"])
        self.assertEqual(report["version"], DLL_INTELLIGENCE_VERSION)
        self.assertEqual(report["summary"]["ledger_count"], 6)
        self.assertEqual(report["summary"]["near_miss_count"], 4)
        self.assertEqual(report["summary"]["recovery_failure_count"], 1)
        self.assertEqual(report["summary"]["override_harmful_count"], 1)
        self.assertIn("rollback_drill", report["top_missing_evidence"])

    def test_policy_review_queue_never_auto_activates(self):
        report = analyze_ledgers(build_example_bundle()["ledgers"])
        self.assertGreater(len(report["policy_review_queue"]), 0)
        for item in report["policy_review_queue"]:
            self.assertEqual(item["activation_status"], "requires_review")

    def test_recurring_missing_evidence_becomes_review_queue_item(self):
        report = analyze_ledgers(build_example_bundle()["ledgers"])
        recommendations = [item["recommendation"] for item in report["policy_review_queue"]]
        self.assertIn("Require or explain missing evidence item: rollback_drill", recommendations)

    def test_markdown_preserves_evidence_boundary(self):
        report = analyze_ledgers(build_example_bundle()["ledgers"])
        markdown = render_markdown(report)
        self.assertIn("SMERC DLL Intelligence Report", markdown)
        self.assertIn("not automatic policy activation", markdown)
        self.assertIn("does not prove incident reduction", markdown)

    def test_schema_and_generated_report_share_version(self):
        schema = json.loads((ROOT / "schemas" / "smerc-dll-intelligence-v1.schema.json").read_text(encoding="utf-8"))
        report = json.loads((ROOT / "reports" / "dll_intelligence_report.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["version"]["const"], DLL_INTELLIGENCE_VERSION)
        self.assertEqual(report["version"], DLL_INTELLIGENCE_VERSION)
        self.assertEqual(report["summary"]["ledger_count"], 6)


if __name__ == "__main__":
    unittest.main()

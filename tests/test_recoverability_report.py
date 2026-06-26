import json
import unittest
from pathlib import Path

from reference_engine.recoverability_report import load_actions, markdown, summarize, write_bundle
from reference_engine.recoverability_engine import evaluate_batch


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "recoverability_action_requests.json"
TEST_DIR = ROOT / "test_outputs"


class RecoverabilityReportTests(unittest.TestCase):
    def test_report_summary_and_markdown(self):
        records = evaluate_batch(load_actions(EXAMPLES))
        summary = summarize(records)
        report = markdown(records, summary)
        self.assertEqual(summary["total_actions"], 5)
        self.assertIn("# SMERC Recoverability Engine Report", report)
        self.assertIn("AGENT_EXPORT_CUSTOMER_DATA", report)

    def test_write_bundle_outputs_json_and_markdown(self):
        TEST_DIR.mkdir(exist_ok=True)
        json_output = TEST_DIR / "recoverability_results.json"
        markdown_output = TEST_DIR / "recoverability_report.md"
        summary = write_bundle(EXAMPLES, json_output, markdown_output)
        payload = json.loads(json_output.read_text(encoding="utf-8"))
        self.assertEqual(summary["total_actions"], payload["summary"]["total_actions"])
        self.assertIn("Recoverability Engine", markdown_output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

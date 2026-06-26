import json
import unittest
from pathlib import Path

from reference_engine.pilot_report import evaluate_actions, load_actions, markdown_report, summarize, write_json, write_markdown


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "github_actions_shadow_mode_scenarios.json"
TEST_DIR = ROOT / "test_outputs"


class PilotReportTests(unittest.TestCase):
    def test_shadow_mode_scenarios_generate_summary(self):
        actions = load_actions(SCENARIOS)
        records = evaluate_actions(actions)
        summary = summarize(records)

        self.assertEqual(summary["total_actions"], 10)
        self.assertEqual(sum(summary["posture_counts"].values()), 10)
        self.assertGreater(summary["non_allow_rate"], 0)
        self.assertGreater(summary["average_risk_score"], 0)

    def test_markdown_report_contains_pilot_caveat_and_decisions(self):
        records = evaluate_actions(load_actions(SCENARIOS))
        report = markdown_report(records, summarize(records))

        self.assertIn("synthetic pilot evidence", report)
        self.assertIn("AI_MODIFY_AUTH_MIDDLEWARE", report)
        self.assertIn("What This Does Not Prove Yet", report)

    def test_report_writers_create_json_and_markdown_outputs(self):
        records = evaluate_actions(load_actions(SCENARIOS))
        summary = summarize(records)
        TEST_DIR.mkdir(exist_ok=True)

        json_path = TEST_DIR / "pilot_report_results.json"
        markdown_path = TEST_DIR / "pilot_report.md"
        write_json(json_path, records, summary)
        write_markdown(markdown_path, records, summary)

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["summary"]["total_actions"], 10)
        self.assertIn("# SMERC GitHub Actions Shadow-Mode Pilot Report", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

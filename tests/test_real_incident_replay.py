import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.real_incident_replay import (
    build_report,
    evaluate_scenarios,
    load_scenarios,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "real_public_incident_replay_scenarios.json"
REPORT = ROOT / "reports" / "real_public_incident_replay_report.json"
MARKDOWN = ROOT / "reports" / "Real_Public_Incident_Replay_Report.md"
DOC = ROOT / "docs" / "Real_Public_Incident_Replay.md"


class RealIncidentReplayTests(unittest.TestCase):
    def test_real_public_scenarios_load_with_source_boundaries(self):
        scenarios = load_scenarios(SCENARIOS)
        self.assertEqual(len(scenarios), 6)
        for scenario in scenarios:
            self.assertTrue(scenario["source"]["url"].startswith("https://"))
            self.assertGreater(len(scenario["source"]["source_facts"]), 0)
            self.assertTrue(scenario["action"]["context"]["analyst_assigned_signals"])

    def test_replay_report_has_useful_outcome_spread_and_limits(self):
        report = build_report(evaluate_scenarios(load_scenarios(SCENARIOS)))
        postures = {record["smerc_posture"] for record in report["records"]}
        self.assertIn("THROTTLE", postures)
        self.assertIn("DENY", postures)
        self.assertIn("ESCALATE", postures)
        self.assertGreater(report["summary"]["decision_difference_rate"], 0)
        self.assertIn("does not prove SMERC would have prevented the public incident", report["boundary"]["limits"])
        self.assertIn("analyst-assigned replay inputs", report["markdown_report"])

    def test_output_writers_and_checked_in_docs_exist(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        markdown = MARKDOWN.read_text(encoding="utf-8")
        doc = DOC.read_text(encoding="utf-8")
        self.assertEqual(report["version"], "smerc.real-public-incident-replay.v1")
        self.assertIn("Real Public Incident Replay Report", markdown)
        self.assertIn("source-fact versus analyst-assigned-signal boundary", doc)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "replay.json"
            markdown_path = Path(directory) / "replay.md"
            write_outputs(report, json_path, markdown_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())


if __name__ == "__main__":
    unittest.main()

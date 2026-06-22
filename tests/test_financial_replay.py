import json
import unittest
from pathlib import Path

from reference_engine.financial_replay import FinancialReplayEngine, render_markdown_report


ROOT = Path(__file__).resolve().parents[1]


class FinancialReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios = json.loads(
            (ROOT / "examples" / "financial_replay_scenarios.json").read_text(encoding="utf-8")
        )
        cls.engine = FinancialReplayEngine()

    def test_replays_all_scenarios(self):
        result = self.engine.replay_dataset(self.scenarios)
        self.assertEqual(result["scenario_count"], 3)
        self.assertEqual(result["event_count"], 9)
        self.assertFalse(result["prediction_claim"])

    def test_each_scenario_has_source_and_transitions(self):
        result = self.engine.replay_dataset(self.scenarios)
        for scenario in result["scenarios"]:
            self.assertTrue(scenario["sources"])
            self.assertGreaterEqual(scenario["metrics"]["events_replayed"], 2)
            self.assertGreaterEqual(scenario["metrics"]["transition_count"], 1)

    def test_acute_phases_do_not_allow(self):
        result = self.engine.replay_dataset(self.scenarios)
        acute = [
            decision
            for scenario in result["scenarios"]
            for decision in scenario["decisions"]
            if any(word in decision["phase"].lower() for word in ["acute", "deterioration", "uncertainty"])
        ]
        self.assertTrue(acute)
        self.assertTrue(all(decision["state"] != "ALLOW" for decision in acute))

    def test_report_discloses_signal_method(self):
        report = render_markdown_report(self.engine.replay_dataset(self.scenarios))
        self.assertIn("analyst-assigned replay signals", report)
        self.assertIn("makes no prediction claim", report)
        self.assertIn("Federal Reserve", report)

    def test_rejects_scenario_without_sources(self):
        scenario = dict(self.scenarios[0])
        scenario["sources"] = []
        with self.assertRaises(ValueError):
            self.engine.replay_scenario(scenario)


if __name__ == "__main__":
    unittest.main()


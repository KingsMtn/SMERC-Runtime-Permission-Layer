import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.proxy_evidence_benchmark import (
    evaluate_scenarios,
    load_scenarios,
    markdown_report,
    summarize,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "proxy_incident_replay_scenarios.json"


class ProxyEvidenceBenchmarkTests(unittest.TestCase):
    def test_proxy_scenarios_generate_decision_difference_metrics(self):
        records = evaluate_scenarios(load_scenarios(SCENARIOS))
        summary = summarize(records)

        self.assertEqual(summary["total_scenarios"], 14)
        self.assertGreater(summary["decision_difference_rate"], 0)
        self.assertGreater(summary["constrained_rather_than_blocked_count"], 0)
        self.assertEqual(sum(summary["smerc_posture_counts"].values()), 14)
        self.assertEqual(summary["evidence_type"], "proxy_replay_benchmark")

    def test_report_is_explicit_about_proxy_limits(self):
        records = evaluate_scenarios(load_scenarios(SCENARIOS))
        report = markdown_report(records, summarize(records))

        self.assertIn("proxy evidence only", report)
        self.assertIn("does not prove production incident reduction", report)
        self.assertIn("NEW_VENDOR_PAYMENT_INCOMPLETE_MATCH", report)
        self.assertIn("Traditional Policy", report)

    def test_output_writers_create_json_and_markdown(self):
        records = evaluate_scenarios(load_scenarios(SCENARIOS))
        summary = summarize(records)

        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "benchmark.json"
            markdown_path = Path(directory) / "benchmark.md"
            write_outputs(records, summary, json_path, markdown_path)

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["total_scenarios"], 14)
            self.assertIn("# SMERC Proxy Incident Replay Benchmark", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

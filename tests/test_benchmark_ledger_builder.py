import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.benchmark_ledger_builder import (
    BENCHMARK_LEDGER_BUNDLE_VERSION,
    build_benchmark_ledger_bundle,
    build_decision_time_ledger,
    load_benchmark,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "reports" / "runtime_governance_benchmark.json"


class BenchmarkLedgerBuilderTests(unittest.TestCase):
    def test_builds_valid_decision_time_ledger_without_fabricating_outcome(self):
        payload = load_benchmark(BENCHMARK)
        ledger = build_decision_time_ledger(payload["records"][0])
        data = ledger.to_dict()
        self.assertTrue(data["verification"]["valid"])
        self.assertEqual(data["record_count"], 3)
        self.assertEqual(data["summary"]["event_counts"]["REQUEST"], 1)
        self.assertEqual(data["summary"]["event_counts"]["EVIDENCE"], 1)
        self.assertEqual(data["summary"]["event_counts"]["EVALUATION"], 1)
        self.assertEqual(data["summary"]["event_counts"]["EXECUTION"], 0)
        self.assertEqual(data["summary"]["event_counts"]["OUTCOME"], 0)

    def test_bundle_matches_runtime_benchmark_count_and_marks_limits(self):
        payload = load_benchmark(BENCHMARK)
        bundle = build_benchmark_ledger_bundle(payload)
        self.assertEqual(bundle["version"], BENCHMARK_LEDGER_BUNDLE_VERSION)
        self.assertEqual(bundle["summary"]["ledger_count"], payload["summary"]["total_scenarios"])
        self.assertEqual(bundle["summary"]["valid_ledger_count"], payload["summary"]["total_scenarios"])
        self.assertEqual(bundle["summary"]["invalid_ledger_count"], 0)
        self.assertEqual(bundle["summary"]["decision_time_only_count"], payload["summary"]["total_scenarios"])
        self.assertIn("intentionally absent", bundle["summary"]["evidence_boundary"])

    def test_markdown_states_evidence_boundary_and_hash_chain_value(self):
        markdown = render_markdown(build_benchmark_ledger_bundle(load_benchmark(BENCHMARK)))
        self.assertIn("hash-chained Decision Lifecycle Ledger", markdown)
        self.assertIn("do not claim live execution", markdown)
        self.assertIn("What This Does Not Prove", markdown)

    def test_output_writers_create_json_and_markdown(self):
        bundle = build_benchmark_ledger_bundle(load_benchmark(BENCHMARK))
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "bundle.json"
            markdown_path = Path(directory) / "bundle.md"
            write_outputs(bundle, json_path, markdown_path)
            parsed = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["summary"]["ledger_count"], 84)
            self.assertIn("# SMERC Benchmark Decision-Time Ledger Bundle", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

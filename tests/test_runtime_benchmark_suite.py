import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.runtime_benchmark_suite import (
    RUNTIME_BENCHMARK_VERSION,
    build_runtime_benchmark,
    expand_scenarios,
    load_scenarios,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "examples" / "proxy_incident_replay_scenarios.json"


class RuntimeBenchmarkSuiteTests(unittest.TestCase):
    def test_expands_seed_scenarios_deterministically(self):
        seeds = load_scenarios(SEEDS)
        expanded = expand_scenarios(seeds)
        self.assertEqual(len(seeds), 14)
        self.assertEqual(len(expanded), 84)
        self.assertEqual(len({item["scenario_id"] for item in expanded}), 84)
        self.assertTrue(all("benchmark_variant" in item["action"]["context"] for item in expanded))

    def test_builds_benchmark_summary(self):
        payload = build_runtime_benchmark(SEEDS)
        summary = payload["summary"]
        self.assertEqual(summary["version"], RUNTIME_BENCHMARK_VERSION)
        self.assertEqual(summary["total_scenarios"], 84)
        self.assertGreater(summary["decision_difference_count"], 0)
        self.assertGreater(summary["constrained_instead_of_allowed_count"], 0)
        self.assertGreater(summary["traditional_denies_with_non_deny_smerc_count"], 0)
        self.assertEqual(sum(summary["smerc_posture_counts"].values()), 84)

    def test_markdown_states_proxy_limits_and_demo_examples(self):
        markdown = render_markdown(build_runtime_benchmark(SEEDS))
        self.assertIn("expanded proxy evidence", markdown)
        self.assertIn("does not prove incident reduction", markdown)
        self.assertIn("Demo-Ready Decision Differences", markdown)
        self.assertIn("Category Posture Counts", markdown)

    def test_output_writers_create_files(self):
        payload = build_runtime_benchmark(SEEDS)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "runtime.json"
            markdown_path = Path(directory) / "runtime.md"
            write_outputs(payload, json_path, markdown_path)
            parsed = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["summary"]["total_scenarios"], 84)
            self.assertIn("# SMERC Runtime Governance Benchmark Suite", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

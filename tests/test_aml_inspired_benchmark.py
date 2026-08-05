import tempfile
import unittest
from pathlib import Path

from reference_engine.aml_inspired_benchmark import (
    build_benchmark,
    classify_delta,
    load_scenarios,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "aml_inspired_financial_governance_scenarios.json"


class AMLInspiredBenchmarkTests(unittest.TestCase):
    def test_delta_classifier_separates_suspiciousness_from_recoverability(self):
        self.assertEqual(classify_delta("CLEAR", "THROTTLE"), "AML_CLEAR_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("ALERT", "ALLOW"), "AML_ALERT_SMERC_ALLOW")
        self.assertEqual(classify_delta("ALERT", "FREEZE"), "AML_ALERT_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("CLEAR", "ALLOW"), "AML_CLEAR_SMERC_ALLOW")

    def test_benchmark_reports_recoverability_deltas(self):
        report = build_benchmark(load_scenarios(SCENARIOS))

        self.assertEqual(report["version"], "smerc.aml-inspired-financial-governance-benchmark.v1")
        self.assertEqual(report["scenario_count"], 8)
        self.assertGreaterEqual(report["recoverability_delta_count"], 1)
        self.assertIn("AML_CLEAR_SMERC_RESTRAINT", report["delta_counts"])
        self.assertIn("not AML software", report["evidence_boundary"])

    def test_markdown_explains_boundary_and_commercial_interpretation(self):
        markdown = render_markdown(build_benchmark(load_scenarios(SCENARIOS)))

        self.assertIn("It does not test whether SMERC-F can detect money laundering", markdown)
        self.assertIn("Commercial Interpretation", markdown)
        self.assertIn("AML_CLEAR_SMERC_RESTRAINT", markdown)

    def test_writes_outputs(self):
        report = build_benchmark(load_scenarios(SCENARIOS))
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "aml.json"
            markdown_output = Path(tmp) / "aml.md"
            write_outputs(report, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_readme_links_aml_spur(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/SMERC_F_AML_Inspired_Spur.md", readme)


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from reference_engine.model_risk_benchmark import (
    build_benchmark,
    classify_delta,
    load_scenarios,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "model_risk_governance_scenarios.json"


class ModelRiskBenchmarkTests(unittest.TestCase):
    def test_delta_classifier_separates_model_approval_from_runtime_permission(self):
        self.assertEqual(classify_delta("APPROVE_FOR_USE", "THROTTLE"), "MODEL_APPROVED_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("APPROVE_WITH_MONITORING", "DENY"), "MODEL_APPROVED_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("REQUIRE_VALIDATION", "ALLOW"), "MODEL_VALIDATION_SMERC_ALLOW")
        self.assertEqual(classify_delta("PROHIBIT_USE", "THROTTLE"), "MODEL_PROHIBITED_SMERC_BOUNDED_PATH")
        self.assertEqual(classify_delta("APPROVE_FOR_USE", "ALLOW"), "BOTH_ALLOW")

    def test_benchmark_reports_runtime_deltas(self):
        report = build_benchmark(load_scenarios(SCENARIOS))

        self.assertEqual(report["version"], "smerc.model-risk-governance-benchmark.v1")
        self.assertEqual(report["scenario_count"], 8)
        self.assertGreaterEqual(report["runtime_delta_count"], 1)
        self.assertIn("MODEL_APPROVED_SMERC_RESTRAINT", report["delta_counts"])
        self.assertIn("not regulatory model-risk management", report["evidence_boundary"])

    def test_markdown_explains_boundary_and_commercial_interpretation(self):
        markdown = render_markdown(build_benchmark(load_scenarios(SCENARIOS)))

        self.assertIn("It does not test whether SMERC validates models", markdown)
        self.assertIn("Commercial Interpretation", markdown)
        self.assertIn("MODEL_APPROVED_SMERC_RESTRAINT", markdown)

    def test_writes_outputs(self):
        report = build_benchmark(load_scenarios(SCENARIOS))
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "model_risk.json"
            markdown_output = Path(tmp) / "model_risk.md"
            write_outputs(report, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_readme_links_model_risk_spur(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Model_Risk_Inspired_Governance.md", readme)


if __name__ == "__main__":
    unittest.main()

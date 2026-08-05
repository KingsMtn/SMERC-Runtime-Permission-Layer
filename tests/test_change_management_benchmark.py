import tempfile
import unittest
from pathlib import Path

from reference_engine.change_management_benchmark import (
    build_benchmark,
    classify_delta,
    load_scenarios,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "change_management_governance_scenarios.json"


class ChangeManagementBenchmarkTests(unittest.TestCase):
    def test_delta_classifier_separates_approval_from_runtime_recoverability(self):
        self.assertEqual(classify_delta("APPROVE", "THROTTLE"), "CHANGE_APPROVED_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("EMERGENCY_APPROVE", "FREEZE"), "CHANGE_APPROVED_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("REJECT", "THROTTLE"), "CHANGE_REJECTED_SMERC_NON_DENY")
        self.assertEqual(classify_delta("APPROVE_WITH_CAB", "ALLOW"), "BOTH_APPROVE")
        self.assertEqual(classify_delta("REJECT", "DENY"), "BOTH_RESTRAIN")

    def test_benchmark_reports_recoverability_deltas(self):
        report = build_benchmark(load_scenarios(SCENARIOS))

        self.assertEqual(report["version"], "smerc.change-management-governance-benchmark.v1")
        self.assertEqual(report["scenario_count"], 8)
        self.assertGreaterEqual(report["recoverability_delta_count"], 1)
        self.assertIn("CHANGE_APPROVED_SMERC_RESTRAINT", report["delta_counts"])
        self.assertIn("not ITIL certification", report["evidence_boundary"])

    def test_markdown_explains_boundary_and_commercial_interpretation(self):
        markdown = render_markdown(build_benchmark(load_scenarios(SCENARIOS)))

        self.assertIn("It does not test whether SMERC replaces change management", markdown)
        self.assertIn("Commercial Interpretation", markdown)
        self.assertIn("CHANGE_APPROVED_SMERC_RESTRAINT", markdown)

    def test_writes_outputs(self):
        report = build_benchmark(load_scenarios(SCENARIOS))
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "change.json"
            markdown_output = Path(tmp) / "change.md"
            write_outputs(report, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_readme_links_change_management_spur(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Change_Management_Inspired_Governance.md", readme)


if __name__ == "__main__":
    unittest.main()

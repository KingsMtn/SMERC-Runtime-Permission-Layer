import tempfile
import unittest
from pathlib import Path

from reference_engine.sre_incident_benchmark import (
    build_benchmark,
    classify_delta,
    load_scenarios,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "sre_incident_governance_scenarios.json"


class SREIncidentBenchmarkTests(unittest.TestCase):
    def test_delta_classifier_separates_runbook_action_from_recoverability(self):
        self.assertEqual(classify_delta("AUTO_MITIGATE", "THROTTLE"), "SRE_AUTO_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("MANUAL_APPROVAL", "ALLOW"), "SRE_REVIEW_SMERC_ALLOW")
        self.assertEqual(classify_delta("HOLD", "THROTTLE"), "SRE_HOLD_SMERC_BOUNDED_PATH")
        self.assertEqual(classify_delta("AUTO_MITIGATE", "ALLOW"), "BOTH_AUTO_ALLOW")
        self.assertEqual(classify_delta("INCIDENT_COMMAND", "DENY"), "BOTH_RESTRAIN")

    def test_benchmark_reports_recoverability_deltas(self):
        report = build_benchmark(load_scenarios(SCENARIOS))

        self.assertEqual(report["version"], "smerc.sre-incident-governance-benchmark.v1")
        self.assertEqual(report["scenario_count"], 8)
        self.assertGreaterEqual(report["recoverability_delta_count"], 1)
        self.assertIn("SRE_AUTO_SMERC_RESTRAINT", report["delta_counts"])
        self.assertIn("not an observability platform", report["evidence_boundary"])

    def test_markdown_explains_boundary_and_commercial_interpretation(self):
        markdown = render_markdown(build_benchmark(load_scenarios(SCENARIOS)))

        self.assertIn("It does not test whether SMERC replaces observability", markdown)
        self.assertIn("Commercial Interpretation", markdown)
        self.assertIn("SRE_AUTO_SMERC_RESTRAINT", markdown)

    def test_writes_outputs(self):
        report = build_benchmark(load_scenarios(SCENARIOS))
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "sre.json"
            markdown_output = Path(tmp) / "sre.md"
            write_outputs(report, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_readme_links_sre_spur(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/SRE_Incident_Inspired_Governance.md", readme)


if __name__ == "__main__":
    unittest.main()

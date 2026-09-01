import tempfile
import unittest
from pathlib import Path

from reference_engine.gitlab_agent_action_benchmark import (
    VERSION,
    build_benchmark,
    classify_delta,
    load_scenarios,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "examples" / "gitlab_agent_action_recoverability_scenarios.json"


class GitLabAgentActionBenchmarkTests(unittest.TestCase):
    def test_delta_classifier_identifies_recoverability_gap(self):
        self.assertEqual(classify_delta("ALLOW", "THROTTLE"), "GITLAB_ALLOW_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("ASK", "FREEZE"), "GITLAB_ASK_SMERC_STRUCTURED_ROUTE")
        self.assertEqual(classify_delta("ASK", "ALLOW"), "GITLAB_ASK_SMERC_ALLOW")
        self.assertEqual(classify_delta("DENY", "ESCALATE"), "GITLAB_DENY_SMERC_NON_DENY")
        self.assertEqual(classify_delta("DENY", "DENY"), "BOTH_DENY")

    def test_benchmark_reports_gitlab_shaped_deltas(self):
        report = build_benchmark(load_scenarios(SCENARIOS))

        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["scenario_count"], 8)
        self.assertGreaterEqual(report["decision_difference_count"], 3)
        self.assertIn("GITLAB_ALLOW_SMERC_RESTRAINT", report["delta_counts"])
        self.assertIn("not a GitLab integration", report["evidence_boundary"])

    def test_markdown_explains_no_endorsement_and_impact(self):
        markdown = render_markdown(build_benchmark(load_scenarios(SCENARIOS)))

        self.assertIn("not to claim SMERC replaces GitLab permissions", markdown)
        self.assertIn("Commercial Interpretation", markdown)
        self.assertIn("authorized action can still be unrecoverable", markdown)

    def test_writes_outputs(self):
        report = build_benchmark(load_scenarios(SCENARIOS))
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "gitlab.json"
            markdown_output = Path(tmp) / "gitlab.md"
            write_outputs(report, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_readme_links_gitlab_benchmark(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/GitLab_Agent_Action_Recoverability_Benchmark.md", readme)


if __name__ == "__main__":
    unittest.main()

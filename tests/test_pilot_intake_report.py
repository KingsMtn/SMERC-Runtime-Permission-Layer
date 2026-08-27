import copy
import unittest
from pathlib import Path

from reference_engine.pilot_intake_report import (
    PILOT_INTAKE_VERSION,
    build_pilot_intake_report,
    compile_customer_evaluation_payload,
    load_payload,
    render_markdown,
    validate_payload,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "pilot_intake_template.json"
TEST_OUTPUTS = ROOT / "test_outputs" / "pilot_intake"
TEST_OUTPUTS.mkdir(parents=True, exist_ok=True)


class PilotIntakeReportTests(unittest.TestCase):
    def test_template_builds_report_with_comparison_metrics(self):
        report = build_pilot_intake_report(load_payload(SAMPLE))

        self.assertEqual(report["version"], PILOT_INTAKE_VERSION)
        self.assertEqual(report["summary"]["actions_evaluated"], 5)
        self.assertGreaterEqual(report["summary"]["decision_difference_count"], 1)
        self.assertIn(report["summary"]["pilot_fit"]["fit"], {"moderate", "strong"})
        self.assertEqual(len(report["comparisons"]), 5)
        self.assertIn("customer_evaluation", report)

    def test_compiles_to_existing_customer_evaluation_contract(self):
        compiled = compile_customer_evaluation_payload(validate_payload(load_payload(SAMPLE)))

        self.assertEqual(compiled["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(len(compiled["actions"]), 5)
        self.assertEqual(compiled["actions"][0]["tool"], "github_actions.test")
        self.assertIn("current_control_outcome", compiled["actions"][0]["context"])

    def test_markdown_is_external_reviewer_readable_and_bounded(self):
        report = build_pilot_intake_report(load_payload(SAMPLE))
        markdown = render_markdown(report)

        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("Current Controls vs SMERC", markdown)
        self.assertIn("does not prove production validation", markdown)
        self.assertIn("Constrained rather than blocked", markdown)
        self.assertIn("Recommended Next Action", markdown)

    def test_rejects_sensitive_keys_and_unknown_current_outcomes(self):
        payload = load_payload(SAMPLE)
        bad = copy.deepcopy(payload)
        bad["actions"][0]["current_control_outcome"] = "AUTO_SHIP"
        with self.assertRaises(ValueError):
            validate_payload(bad)

        bad = copy.deepcopy(payload)
        bad["actions"][0]["properties"]["api_key"] = "do-not-accept"
        with self.assertRaises(ValueError):
            validate_payload(bad)

    def test_writes_outputs(self):
        report = build_pilot_intake_report(load_payload(SAMPLE))
        json_output = TEST_OUTPUTS / "pilot_intake_report.json"
        markdown_output = TEST_OUTPUTS / "Pilot_Intake_Report.md"
        write_outputs(report, json_output, markdown_output)

        self.assertTrue(json_output.exists())
        self.assertTrue(markdown_output.exists())

    def test_docs_and_readme_link_intake_path(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        doc = (ROOT / "docs" / "Pilot_Intake_Template.md").read_text(encoding="utf-8")

        self.assertIn("docs/Pilot_Intake_Template.md", readme)
        self.assertIn("reference_engine.pilot_intake_report", doc)


if __name__ == "__main__":
    unittest.main()

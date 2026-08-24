import unittest
from pathlib import Path

from reference_engine.customer_action_intake import (
    evaluate_customer_intake,
    load_payload,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "customer_action_intake_sample.json"
TEST_OUTPUTS = ROOT / "test_outputs" / "customer_action_intake"
TEST_OUTPUTS.mkdir(parents=True, exist_ok=True)


class CustomerActionIntakeTests(unittest.TestCase):
    def test_sample_intake_scores_actions_and_pilot_fit(self):
        report = evaluate_customer_intake(load_payload(SAMPLE))

        self.assertEqual(report["schema"], "smerc.customer-action-intake.v1")
        self.assertEqual(report["organization"], "ExampleCo")
        self.assertEqual(report["summary"]["total_actions"], 6)
        self.assertGreaterEqual(report["summary"]["posture_counts"]["THROTTLE"], 1)
        self.assertGreaterEqual(
            report["summary"]["posture_counts"]["FREEZE"]
            + report["summary"]["posture_counts"]["DENY"]
            + report["summary"]["posture_counts"]["ESCALATE"],
            1,
        )
        self.assertIn(report["pilot_fit"]["fit"], {"moderate", "strong"})
        self.assertIn("metadata-only", report["evidence_boundary"])

    def test_markdown_includes_highest_exposure_and_boundary(self):
        report = evaluate_customer_intake(load_payload(SAMPLE))
        markdown = render_markdown(report)

        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("Highest Exposure Actions", markdown)
        self.assertIn("Recommended Next Action", markdown)
        self.assertIn("EXAMPLECO_SUPPORT_EMAIL_BLAST", markdown)

    def test_writes_json_and_markdown_outputs(self):
        report = evaluate_customer_intake(load_payload(SAMPLE))
        json_output = TEST_OUTPUTS / "intake.json"
        markdown_output = TEST_OUTPUTS / "intake.md"
        write_outputs(report, json_output, markdown_output)
        self.assertTrue(json_output.exists())
        self.assertTrue(markdown_output.exists())

    def test_readme_links_customer_action_intake(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Customer_Action_Intake.md", readme)


if __name__ == "__main__":
    unittest.main()

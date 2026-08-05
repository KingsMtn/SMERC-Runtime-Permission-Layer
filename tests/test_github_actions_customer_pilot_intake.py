import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.github_actions_customer_pilot_intake import assess, markdown, write_outputs


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "examples" / "github_actions_customer_pilot_intake_packet.json"
DOC = ROOT / "pilot_package" / "GitHub_Actions_Customer_Pilot_Intake.md"
README = ROOT / "README.md"


class GitHubActionsCustomerPilotIntakeTests(unittest.TestCase):
    def test_example_packet_is_ready_for_review_but_warns_on_missing_sponsor(self):
        report = assess(json.loads(PACKET.read_text(encoding="utf-8")))
        self.assertEqual(report["schema"], "smerc.github-actions-customer-pilot-intake-report.v1")
        self.assertTrue(report["ready_for_review_call"])
        self.assertFalse(report["ready_for_week_zero"])
        self.assertEqual(report["sample_action_count"], 10)
        self.assertEqual(report["blockers"], [])
        self.assertIn("Business sponsor is not confirmed", " ".join(report["warnings"]))
        self.assertIn("observe mode", report["customer_question"])
        self.assertIn("does not prove buyer demand", report["evidence_boundary"])

    def test_enforcement_request_blocks_first_pilot(self):
        payload = json.loads(PACKET.read_text(encoding="utf-8"))
        payload["pilot_controls"]["enforcement_requested"] = True
        report = assess(payload)
        self.assertFalse(report["ready_for_review_call"])
        self.assertIn("Enforcement is requested before shadow-mode calibration.", report["blockers"])

    def test_too_few_sample_actions_blocks(self):
        payload = json.loads(PACKET.read_text(encoding="utf-8"))
        payload["sample_actions"] = payload["sample_actions"][:3]
        report = assess(payload)
        self.assertFalse(report["ready_for_review_call"])
        self.assertIn("At least 10 sample action descriptions are required for pilot discussion.", report["blockers"])

    def test_markdown_and_outputs_include_decision_boundary_and_next_action(self):
        report = assess(json.loads(PACKET.read_text(encoding="utf-8")))
        text = markdown(report)
        self.assertIn("Ready for review call", text)
        self.assertIn("Customer Question", text)
        self.assertIn("Recommended Next Action", text)
        self.assertIn("Evidence Boundary", text)
        with tempfile.TemporaryDirectory() as directory:
            json_output = Path(directory) / "report.json"
            markdown_output = Path(directory) / "report.md"
            write_outputs(report, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_doc_and_readme_reference_intake_path(self):
        doc = DOC.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        self.assertIn("examples/github_actions_customer_pilot_intake_packet.json", doc)
        self.assertIn("reference_engine.github_actions_customer_pilot_intake", doc)
        self.assertIn("pilot_package/GitHub_Actions_Customer_Pilot_Intake.md", readme)


if __name__ == "__main__":
    unittest.main()

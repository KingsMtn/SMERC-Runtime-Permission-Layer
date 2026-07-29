import tempfile
import unittest
from pathlib import Path

from reference_engine.pilot_evidence_summary import build_summary, load_json, render_markdown, write_outputs


ROOT = Path(__file__).resolve().parents[1]


class PilotEvidenceSummaryTests(unittest.TestCase):
    def test_summary_recommends_observe_without_metrics(self):
        summary = build_summary(
            load_json(ROOT / "reports" / "core_prospect_route_report.json"),
            load_json(ROOT / "reports" / "customer_action_intake_report.json"),
            load_json(ROOT / "examples" / "pilot_handoff_checklist.json"),
        )

        self.assertEqual(summary["schema"], "smerc.pilot-evidence-summary.v1")
        self.assertEqual(summary["pilot_decision"], "start_observe")
        self.assertTrue(summary["handoff_gate"]["complete"])
        self.assertEqual(summary["pilot_metrics_summary"]["status"], "not_supplied")
        self.assertIn("not production certification", summary["evidence_boundary"])

    def test_summary_can_recommend_move_to_recommend_with_metrics(self):
        summary = build_summary(
            load_json(ROOT / "reports" / "core_prospect_route_report.json"),
            load_json(ROOT / "reports" / "customer_action_intake_report.json"),
            load_json(ROOT / "examples" / "pilot_handoff_checklist.json"),
            pilot_metrics=load_json(ROOT / "examples" / "pilot_metrics_summary_sample.json"),
        )

        self.assertEqual(summary["pilot_decision"], "move_to_recommend")
        self.assertEqual(summary["pilot_metrics_summary"]["reviewer_agreement_rate"], 0.8333)

    def test_markdown_contains_go_no_go_and_boundary(self):
        summary = build_summary(
            load_json(ROOT / "reports" / "core_prospect_route_report.json"),
            load_json(ROOT / "reports" / "customer_action_intake_report.json"),
            load_json(ROOT / "examples" / "pilot_handoff_checklist.json"),
            pilot_metrics=load_json(ROOT / "examples" / "pilot_metrics_summary_sample.json"),
        )
        markdown = render_markdown(summary)

        self.assertIn("Pilot decision", markdown)
        self.assertIn("Highest Exposure Actions", markdown)
        self.assertIn("Evidence Boundary", markdown)

    def test_writes_outputs(self):
        summary = build_summary(
            load_json(ROOT / "reports" / "core_prospect_route_report.json"),
            load_json(ROOT / "reports" / "customer_action_intake_report.json"),
            load_json(ROOT / "examples" / "pilot_handoff_checklist.json"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "summary.json"
            markdown_output = Path(tmp) / "summary.md"
            write_outputs(summary, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_readme_links_pilot_evidence_summary(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Pilot_Evidence_Summary.md", readme)


if __name__ == "__main__":
    unittest.main()

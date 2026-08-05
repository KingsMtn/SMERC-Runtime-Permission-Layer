import tempfile
import unittest
from pathlib import Path

from reference_engine.microsoft_security_replay import (
    DATASET_VERSION,
    REPORT_VERSION,
    action_from_event,
    build_replay_report,
    classify_delta,
    load_dataset,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "examples" / "microsoft_security_replay_events.json"
DOC = ROOT / "docs" / "Microsoft_Security_Replay_Adapter.md"
README = ROOT / "README.md"


class MicrosoftSecurityReplayTests(unittest.TestCase):
    def test_dataset_loads_and_generates_report(self):
        dataset = load_dataset(DATASET)
        report = build_replay_report(dataset)

        self.assertEqual(dataset["schema"], DATASET_VERSION)
        self.assertEqual(report["version"], REPORT_VERSION)
        self.assertEqual(report["event_count"], 6)
        self.assertGreaterEqual(report["decision_difference_count"], 1)
        self.assertIn("microsoft_defender_alert", report["event_source_counts"])
        self.assertIn("not Microsoft telemetry", report["evidence_boundary"])
        self.assertIn("MICROSOFT_AUTO_SMERC_RESTRAINT", report["delta_counts"])

    def test_delta_classifier_separates_recoverability_from_workflow(self):
        self.assertEqual(classify_delta("AUTO_RESPONSE", "THROTTLE"), "MICROSOFT_AUTO_SMERC_RESTRAINT")
        self.assertEqual(classify_delta("ANALYST_REVIEW", "ALLOW"), "MICROSOFT_REVIEW_SMERC_BOUNDED")
        self.assertEqual(classify_delta("ALERT_ONLY", "THROTTLE"), "MICROSOFT_HOLD_SMERC_BOUNDED")
        self.assertEqual(classify_delta("AUTO_RESPONSE", "ALLOW"), "BOTH_ALLOW")
        self.assertEqual(classify_delta("ESCALATE_INCIDENT", "FREEZE"), "BOTH_RESTRAIN")

    def test_action_mapping_preserves_microsoft_context(self):
        event = load_dataset(DATASET)["events"][0]
        action = action_from_event(event)

        self.assertEqual(action["context"]["microsoft_style_event_source"], "microsoft_defender_alert")
        self.assertEqual(action["context"]["domain_profile"], "security_ops")
        self.assertTrue(action["external_side_effect"])
        self.assertTrue(action["sensitive_data"])

    def test_strict_dataset_rejects_unknown_fields(self):
        dataset = load_dataset(DATASET)
        dataset["events"][0]["unexpected"] = True

        with self.assertRaisesRegex(ValueError, "unknown field"):
            build_replay_report(dataset)

    def test_markdown_and_outputs_are_reviewable(self):
        report = build_replay_report(load_dataset(DATASET))
        markdown = render_markdown(report)

        self.assertIn("SMERC Microsoft-Style Security Replay Report", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("Commercial Interpretation", markdown)
        self.assertIn("Microsoft-style workflow", markdown)
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "microsoft_replay.json"
            markdown_output = Path(tmp) / "microsoft_replay.md"
            write_outputs(report, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_docs_and_readme_link_adapter(self):
        self.assertIn("python -m reference_engine.microsoft_security_replay", DOC.read_text(encoding="utf-8"))
        self.assertIn("docs/Microsoft_Security_Replay_Adapter.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

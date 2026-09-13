import unittest
from pathlib import Path

from reference_engine.local_shadow_intake import build_intake_report, load_payload, render_markdown


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "local_shadow_intake_examples.json"


class LocalShadowIntakeTests(unittest.TestCase):
    def test_builds_reject_first_shadow_intake_report(self):
        report = build_intake_report(load_payload(INPUTS))

        self.assertEqual(report["version"], "smerc.local-shadow-intake.v1")
        self.assertEqual(report["input_action_count"], 7)
        self.assertEqual(report["accepted_action_count"], 5)
        self.assertEqual(report["classification_counts"]["ACCEPTED_METADATA_ONLY"], 5)
        self.assertEqual(report["classification_counts"]["SKIPPED_PROHIBITED_FIELD"], 1)
        self.assertEqual(report["classification_counts"]["REJECTED_RAW_LOG"], 1)
        self.assertEqual(report["share_status"], "HUMAN_REVIEW_REQUIRED")

    def test_sanitized_draft_contains_only_accepted_metadata(self):
        report = build_intake_report(load_payload(INPUTS))
        draft = report["sanitized_metadata_draft"]

        self.assertEqual(draft["schema_version"], "smerc.local-shadow-metadata-draft.v1")
        self.assertEqual(len(draft["actions"]), 5)
        first = draft["actions"][0]
        self.assertIn("tool_system_class", first)
        self.assertIn("intake_posture_hint", first)
        self.assertNotIn("account_id", first)

    def test_posture_hints_preserve_useful_shadow_signal(self):
        report = build_intake_report(load_payload(INPUTS))
        by_id = {row["action_id"]: row for row in report["sanitized_metadata_draft"]["actions"]}

        self.assertEqual(by_id["ACT-001"]["intake_posture_hint"], "THROTTLE")
        self.assertEqual(by_id["ACT-002"]["intake_posture_hint"], "FREEZE")
        self.assertEqual(by_id["ACT-003"]["intake_posture_hint"], "DENY")
        self.assertEqual(by_id["ACT-004"]["intake_posture_hint"], "FREEZE")
        self.assertEqual(by_id["ACT-005"]["intake_posture_hint"], "THROTTLE")

    def test_markdown_and_docs_are_reviewer_readable(self):
        markdown = render_markdown(build_intake_report(load_payload(INPUTS)))
        doc = (ROOT / "docs" / "Local_Shadow_Intake.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("SMERC Local Shadow Intake Report", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("python -m reference_engine.local_shadow_intake", doc)
        self.assertIn("docs/Local_Shadow_Intake.md", readme)


if __name__ == "__main__":
    unittest.main()

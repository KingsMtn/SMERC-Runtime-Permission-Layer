import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PilotHandoffChecklistTests(unittest.TestCase):
    def test_handoff_doc_defines_required_customer_gate(self):
        text = (ROOT / "pilot_package" / "Pilot_Handoff_Checklist.md").read_text()

        self.assertIn("Proceed only when the answer is yes", text)
        self.assertIn("metadata-only", text)
        self.assertIn("reviewer agreement", text)
        self.assertIn("Do not move to enforcement", text)
        self.assertIn("return to quickstart and action intake", text)

    def test_handoff_example_is_observe_mode_and_bounded(self):
        payload = json.loads((ROOT / "examples" / "pilot_handoff_checklist.json").read_text())

        self.assertEqual(payload["schema"], "smerc.pilot-handoff-checklist.v1")
        statuses = {item["item"]: item["status"] for item in payload["required_items"]}
        self.assertEqual(statuses["observe_mode_only"], "yes")
        self.assertEqual(statuses["metadata_only_boundary"], "yes")
        self.assertIn("move_to_recommend", payload["go_no_go_options"])
        self.assertIn("does not prove customer demand", payload["evidence_boundary"])

    def test_readme_links_pilot_handoff(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("pilot_package/Pilot_Handoff_Checklist.md", readme)


if __name__ == "__main__":
    unittest.main()

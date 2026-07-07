import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "examples" / "pilot_evaluation_checklist.json"


class PilotEvaluationChecklistTests(unittest.TestCase):
    def test_checklist_is_structured_and_references_existing_files(self):
        data = json.loads(CHECKLIST.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "smerc.pilot-evaluation-checklist.v1")
        self.assertGreaterEqual(data["minimum_fit"]["required_true_count"], 1)
        self.assertGreaterEqual(len(data["minimum_fit"]["criteria"]), 5)

        area_ids = [area["id"] for area in data["review_areas"]]
        self.assertEqual(len(area_ids), len(set(area_ids)))
        self.assertIn("github_deployment_adapter", area_ids)

        for area in data["review_areas"]:
            self.assertGreaterEqual(len(area["checks"]), 3, area["id"])
            for rel_path in area["evidence_files"]:
                path = ROOT / rel_path
                self.assertTrue(path.exists(), f"{rel_path} must exist")

    def test_metrics_and_stop_conditions_are_not_empty(self):
        data = json.loads(CHECKLIST.read_text(encoding="utf-8"))

        self.assertIn("reviewer_agreement_rate", data["shadow_mode_metrics"])
        self.assertIn("false_release_rate", data["shadow_mode_metrics"])
        self.assertIn("false_constraint_rate", data["shadow_mode_metrics"])
        self.assertGreaterEqual(len(data["stop_conditions"]), 5)


if __name__ == "__main__":
    unittest.main()


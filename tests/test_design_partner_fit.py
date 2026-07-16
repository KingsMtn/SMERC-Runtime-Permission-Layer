import copy
import json
import unittest
from pathlib import Path

from reference_engine.design_partner_fit import assess, markdown, validate_payload


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "examples" / "design_partner_fit_example.json").read_text(encoding="utf-8"))


class DesignPartnerFitTests(unittest.TestCase):
    def test_example_scores_moderate_fit_and_recommends_paid_shadow_pilot(self):
        report = assess(EXAMPLE)

        self.assertEqual(report["total_score"], 19)
        self.assertEqual(report["fit"], "moderate")
        self.assertIn("30-Day Shadow-Mode Pilot", report["recommendation"])
        self.assertEqual(report["blockers"], [])
        self.assertIn("not proof of buyer intent", report["evidence_boundary"])

    def test_strong_fit_recommends_design_partner_pilot(self):
        payload = copy.deepcopy(EXAMPLE)
        for key in payload["scores"]:
            payload["scores"][key] = 3
        report = assess(payload)

        self.assertEqual(report["total_score"], 24)
        self.assertEqual(report["fit"], "strong")
        self.assertIn("$25,000-$50,000", report["recommendation"])

    def test_blockers_override_interpretation_for_bad_fit_signals(self):
        payload = copy.deepcopy(EXAMPLE)
        payload["scores"]["reviewer_capacity"] = 0
        payload["scores"]["data_boundary"] = 1
        report = assess(payload)

        self.assertIn("No reviewer capacity", " ".join(report["blockers"]))
        self.assertIn("Data boundary", " ".join(report["blockers"]))

    def test_validation_is_strict(self):
        payload = copy.deepcopy(EXAMPLE)
        payload["extra"] = True
        with self.assertRaisesRegex(ValueError, "unknown field"):
            validate_payload(payload)

        payload = copy.deepcopy(EXAMPLE)
        payload["scores"]["workflow_fit"] = 4
        with self.assertRaisesRegex(ValueError, "between 0 and 3"):
            validate_payload(payload)

        payload = copy.deepcopy(EXAMPLE)
        del payload["evidence"]["workflow_fit"]
        with self.assertRaisesRegex(ValueError, "include every declared"):
            validate_payload(payload)

    def test_markdown_contains_fit_band_offer_and_boundary(self):
        report = markdown(assess(EXAMPLE))

        self.assertIn("Fit band: `moderate`", report)
        self.assertIn("30-Day Shadow-Mode Pilot", report)
        self.assertIn("Qualification screen only", report)


if __name__ == "__main__":
    unittest.main()


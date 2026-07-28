import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class YCNextCyclePlanTests(unittest.TestCase):
    def test_yc_plan_is_evidence_first_and_bounded(self):
        text = (ROOT / "docs" / "YC_Next_Cycle_Readiness_Plan.md").read_text(encoding="utf-8")
        self.assertIn("customer-context pilot records", text)
        self.assertIn("Reviewer agreement", text)
        self.assertIn("What Not To Say", text)
        self.assertIn("Do not claim", text)
        self.assertIn("not too late if the time is used to create evidence", text)

    def test_yc_application_draft_has_empty_evidence_slots(self):
        text = (ROOT / "docs" / "YC_Application_Evidence_Draft.md").read_text(encoding="utf-8")
        self.assertIn("Evidence Slots To Fill Before Submission", text)
        self.assertIn("Do not invent these", text)
        self.assertIn("pending", text)
        self.assertIn("SMERC does not replace existing security tools", text)

    def test_readme_links_yc_next_cycle_materials(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/YC_Next_Cycle_Readiness_Plan.md", readme)
        self.assertIn("docs/YC_Application_Evidence_Draft.md", readme)


if __name__ == "__main__":
    unittest.main()

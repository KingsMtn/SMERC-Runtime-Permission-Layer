import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PILOT_PACKAGE = ROOT / "pilot_package"


REQUIRED_FILES = [
    "Pilot_Kickoff_Packet.md",
    "Customer_Integration_Questionnaire.md",
    "Pilot_Data_Handling_and_Security_Boundary.md",
    "Weekly_Review_Template.md",
    "30_60_90_Day_Pilot_Plan.md",
    "Sample_Pilot_Report.md",
    "Customer_Responsibilities_Checklist.md",
    "Go_No_Go_Criteria.md",
    "Design_Partner_Qualification_Checklist.md",
    "Pricing_And_Pilot_Evidence_Position.md",
    "First_Pilot_Path.md",
]


class PilotOperatingKitTests(unittest.TestCase):
    def test_required_operating_files_exist_and_are_not_empty(self):
        for name in REQUIRED_FILES:
            path = PILOT_PACKAGE / name
            self.assertTrue(path.exists(), name)
            self.assertGreater(len(path.read_text(encoding="utf-8")), 500, name)

    def test_documents_preserve_pilot_boundary(self):
        combined = "\n".join((PILOT_PACKAGE / name).read_text(encoding="utf-8") for name in REQUIRED_FILES)
        lowered = combined.lower()
        self.assertIn("not production-certified", lowered)
        self.assertIn("observe", lowered)
        self.assertIn("metadata", lowered)
        self.assertIn("go/no-go", lowered)
        self.assertIn("false release", lowered)
        self.assertIn("false constraint", lowered)

    def test_documents_define_customer_and_smerc_responsibilities(self):
        responsibilities = (PILOT_PACKAGE / "Customer_Responsibilities_Checklist.md").read_text(encoding="utf-8")
        self.assertIn("Customer should", responsibilities)
        self.assertIn("SMERC provides", responsibilities)
        self.assertIn("SMERC does not provide", responsibilities)

    def test_sample_report_marks_values_as_illustrative(self):
        report = (PILOT_PACKAGE / "Sample_Pilot_Report.md").read_text(encoding="utf-8")
        self.assertIn("illustrative", report.lower())
        self.assertIn("must be replaced with customer pilot data", report.lower())

    def test_pricing_positions_ledger_as_evidence_support_not_compliance_claim(self):
        one_pager = (PILOT_PACKAGE / "SMERC_Shadow_Mode_Pilot_One_Pager.md").read_text(encoding="utf-8")
        pricing = (PILOT_PACKAGE / "Pricing_And_Pilot_Evidence_Position.md").read_text(encoding="utf-8")
        combined = f"{one_pager}\n{pricing}"
        self.assertIn("$7,500-$15,000", combined)
        self.assertIn("$25,000-$50,000", combined)
        self.assertIn("The ledger is the evidence engine underneath that promise", combined)
        self.assertIn("not be sold as a standalone compliance guarantee", combined)
        self.assertIn("30-day GitHub Actions shadow-mode pilot", combined)

    def test_design_partner_checklist_screens_for_fit_before_pilot(self):
        checklist = (PILOT_PACKAGE / "Design_Partner_Qualification_Checklist.md").read_text(encoding="utf-8")
        self.assertIn("Weak fit", checklist)
        self.assertIn("Exploratory fit", checklist)
        self.assertIn("Moderate fit", checklist)
        self.assertIn("Strong fit", checklist)
        self.assertIn("reviewer agreement", checklist.lower())
        self.assertIn("metadata-only", checklist)
        self.assertIn("Do not pursue a paid pilot", checklist)

    def test_first_pilot_path_is_specific_and_bounded(self):
        path = (PILOT_PACKAGE / "First_Pilot_Path.md").read_text(encoding="utf-8")
        self.assertIn("Week Zero: Qualification", path)
        self.assertIn("Week One: Observe", path)
        self.assertIn("30-Day Decision", path)
        self.assertIn("GitHub Actions", path)
        self.assertIn("metadata-only", path)
        self.assertIn("not require production secrets", path)
        self.assertIn("reviewer agreement rate", path)
        self.assertIn("$7,500-$15,000", path)
        self.assertIn("not about proving that SMERC is universally correct", path)


if __name__ == "__main__":
    unittest.main()

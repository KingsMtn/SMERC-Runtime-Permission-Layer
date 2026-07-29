import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SMERCFStablecoinPilotFitTests(unittest.TestCase):
    def test_stablecoin_fit_doc_keeps_core_wedge_and_financial_spur_separate(self):
        text = (ROOT / "docs" / "SMERC_F_Stablecoin_Blockchain_Pilot_Fit.md").read_text()

        self.assertIn("second wedge", text)
        self.assertIn("GitHub Actions pilot", text)
        self.assertIn("stablecoin", text)
        self.assertIn("AML_CLEAR_SMERC_RESTRAINT", text)
        self.assertIn("does not provide regulatory AML compliance", text)

    def test_financial_pilot_path_is_shadow_mode_only(self):
        text = (ROOT / "pilot_package" / "SMERC_F_Financial_Shadow_Mode_Pilot_Path.md").read_text()

        self.assertIn("shadow mode", text)
        self.assertIn("Do not start with live movement of funds", text)
        self.assertIn("Do not move to production enforcement", text)
        self.assertIn("recoverability delta count", text)

    def test_readme_links_financial_stablecoin_path(self):
        readme = (ROOT / "README.md").read_text()

        self.assertIn("docs/SMERC_F_Stablecoin_Blockchain_Pilot_Fit.md", readme)
        self.assertIn("pilot_package/SMERC_F_Financial_Shadow_Mode_Pilot_Path.md", readme)


if __name__ == "__main__":
    unittest.main()

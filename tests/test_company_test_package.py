import unittest
from pathlib import Path

from reference_engine.customer_evaluation import build_customer_evaluation, load_payload


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "examples" / "customer_metadata_template.json"
GUIDE = ROOT / "docs" / "Company_Test_Package.md"
README = ROOT / "README.md"


class CompanyTestPackageTests(unittest.TestCase):
    def test_template_runs_through_customer_evaluation(self):
        report = build_customer_evaluation(load_payload(TEMPLATE))

        self.assertEqual(report["summary"]["total_actions"], 5)
        self.assertIn(report["pilot_fit"]["fit"], {"moderate", "strong"})
        self.assertGreaterEqual(report["summary"]["valid_ledgers"], 5)
        self.assertGreaterEqual(report["summary"]["non_executable_routes"], 1)

    def test_guide_sets_data_boundary_and_success_criteria(self):
        text = GUIDE.read_text(encoding="utf-8")

        self.assertIn("without giving SMERC production access", text)
        self.assertIn("examples/customer_metadata_template.json", text)
        self.assertIn("Pass/Fail Criteria", text)
        self.assertIn("30-day shadow-mode pilot", text)
        self.assertIn("does not prove incident reduction", text)

    def test_readme_points_to_company_test_package(self):
        text = README.read_text(encoding="utf-8")

        self.assertIn("docs/Company_Test_Package.md", text)
        self.assertIn("examples/customer_metadata_template.json", text)


if __name__ == "__main__":
    unittest.main()

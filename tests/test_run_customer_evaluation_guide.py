import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "Run_Customer_Evaluation_From_GitHub.md"
README = ROOT / "README.md"


class RunCustomerEvaluationGuideTests(unittest.TestCase):
    def test_guide_names_click_path_artifact_and_boundaries(self):
        text = GUIDE.read_text(encoding="utf-8")

        self.assertIn("actions/workflows/customer-evaluations.yml", text)
        self.assertIn("evaluation_set", text)
        self.assertIn("both", text)
        self.assertIn("company-template", text)
        self.assertIn("smerc-customer-evaluations", text)
        self.assertIn("financial runtime customer-evaluation", text)
        self.assertIn("What This Does Not Prove", text)
        self.assertIn("production safety", text)
        self.assertIn("shadow-mode pilot", text)

    def test_readme_links_guide_and_workflow(self):
        text = README.read_text(encoding="utf-8")

        self.assertIn("docs/Run_Customer_Evaluation_From_GitHub.md", text)
        self.assertIn(".github/workflows/customer-evaluations.yml", text)


if __name__ == "__main__":
    unittest.main()

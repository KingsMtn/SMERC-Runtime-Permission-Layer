import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "customer-evaluations.yml"


class CustomerEvaluationsWorkflowTests(unittest.TestCase):
    def test_repository_workflow_runs_general_and_smerc_f_packs(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch", text)
        self.assertIn("evaluation_set", text)
        self.assertIn("examples/customer_eval_actions.json", text)
        self.assertIn("examples/smerc_f_customer_eval_actions.json", text)
        self.assertIn("python -m reference_engine.customer_evaluation", text)
        self.assertIn("smerc-customer-evaluations", text)
        self.assertIn("SUMMARY.md", text)
        self.assertIn("contents: read", text)
        self.assertNotIn("secrets.", text)
        self.assertNotIn("id-token: write", text)

    def test_docs_reference_repository_actions_workflow(self):
        general_doc = (ROOT / "docs" / "Customer_Evaluation.md").read_text(encoding="utf-8")
        finance_doc = (ROOT / "docs" / "SMERC_F_Customer_Evaluation.md").read_text(encoding="utf-8")

        self.assertIn(".github/workflows/customer-evaluations.yml", general_doc)
        self.assertIn("evaluation_set", general_doc)
        self.assertIn(".github/workflows/customer-evaluations.yml", finance_doc)
        self.assertIn("evaluation_set = smerc-f", finance_doc)


if __name__ == "__main__":
    unittest.main()

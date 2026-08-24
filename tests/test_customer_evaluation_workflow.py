import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "integrations" / "github_actions" / "customer_evaluation_workflow.yml"


class CustomerEvaluationWorkflowTests(unittest.TestCase):
    def test_workflow_is_copyable_and_metadata_only(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch", text)
        self.assertIn("examples/customer_eval_actions.json", text)
        self.assertIn("python -m reference_engine.customer_evaluation", text)
        self.assertIn("smerc-customer-evaluation-report", text)
        self.assertIn("contents: read", text)
        self.assertNotIn("secrets.", text)
        self.assertNotIn("id-token: write", text)

    def test_docs_link_customer_evaluation_workflow(self):
        doc = (ROOT / "docs" / "Customer_Evaluation.md").read_text(encoding="utf-8")
        readme = (ROOT / "integrations" / "github_actions" / "README.md").read_text(encoding="utf-8")

        self.assertIn("integrations/github_actions/customer_evaluation_workflow.yml", doc)
        self.assertIn("customer_evaluation_workflow.yml", readme)
        self.assertIn("metadata-only customer actions", readme)


if __name__ == "__main__":
    unittest.main()

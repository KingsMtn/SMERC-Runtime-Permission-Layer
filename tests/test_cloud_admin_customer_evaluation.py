import unittest
from pathlib import Path

from reference_engine.customer_evaluation import build_customer_evaluation, load_payload, render_markdown


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "cloud_admin_customer_eval_actions.json"
DOC = ROOT / "docs" / "Cloud_Admin_Customer_Evaluation.md"


class CloudAdminCustomerEvaluationTests(unittest.TestCase):
    def test_cloud_admin_pack_runs_complete_runtime_path(self):
        report = build_customer_evaluation(load_payload(SAMPLE))

        self.assertEqual(report["summary"]["total_actions"], 8)
        self.assertEqual(report["summary"]["valid_ledgers"], 8)
        self.assertGreaterEqual(report["summary"]["ref_gate_counts"]["fail"], 2)
        self.assertGreaterEqual(report["summary"]["non_executable_routes"], 2)
        self.assertIn(report["pilot_fit"]["fit"], {"moderate", "strong"})

    def test_cloud_admin_pack_has_cloud_specific_high_exposure_actions(self):
        report = build_customer_evaluation(load_payload(SAMPLE))
        highest = {item["action_id"] for item in report["summary"]["highest_exposure_actions"]}

        self.assertIn("CLOUDCO_DATABASE_DELETE_003", highest)
        self.assertTrue(
            highest.intersection({"CLOUDCO_IAM_EXPANSION_001", "CLOUDCO_BACKUP_RETENTION_008"})
        )

    def test_cloud_admin_markdown_explains_evidence_boundary(self):
        markdown = render_markdown(build_customer_evaluation(load_payload(SAMPLE)))

        self.assertIn("CloudCo SMERC Customer Evaluation Report", markdown)
        self.assertIn("does not prove production safety", markdown)
        self.assertIn("CLOUDCO_SECURITY_GROUP_002", markdown)

    def test_cloud_admin_doc_links_workflow_and_sample(self):
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("examples/cloud_admin_customer_eval_actions.json", text)
        self.assertIn("customer-evaluations.yml", text)
        self.assertIn("evaluation_set = cloud-admin", text)
        self.assertIn("does not prove production safety", text)


if __name__ == "__main__":
    unittest.main()

import copy
import unittest
from pathlib import Path

from reference_engine.customer_evaluation import (
    CUSTOMER_EVALUATION_VERSION,
    build_customer_evaluation,
    load_payload,
    render_markdown,
    validate_payload,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "customer_eval_actions.json"
TEST_OUTPUTS = ROOT / "test_outputs" / "customer_evaluation"
TEST_OUTPUTS.mkdir(parents=True, exist_ok=True)


class CustomerEvaluationTests(unittest.TestCase):
    def test_sample_runs_complete_runtime_path(self):
        report = build_customer_evaluation(load_payload(SAMPLE))

        self.assertEqual(report["version"], CUSTOMER_EVALUATION_VERSION)
        self.assertEqual(report["summary"]["total_actions"], 5)
        self.assertGreaterEqual(report["summary"]["ref_gate_counts"]["fail"], 1)
        self.assertGreaterEqual(report["summary"]["non_executable_routes"], 1)
        self.assertEqual(report["summary"]["valid_ledgers"], 5)
        self.assertIn(report["pilot_fit"]["fit"], {"moderate", "strong"})
        self.assertIn(report["summary"]["autonomy_state"], {"WATCH", "DEGRADE", "SUSPEND_AUTONOMY"})

    def test_ref_gate_failure_caps_scoring_and_blocks_route(self):
        report = build_customer_evaluation(load_payload(SAMPLE))
        failed = [record for record in report["records"] if record["ref_gate"]["status"] == "fail"]

        self.assertTrue(failed)
        self.assertEqual(failed[0]["scoring_admission"], "capped_by_ref_gate")
        self.assertEqual(failed[0]["decision"]["posture"], "DENY")
        self.assertFalse(failed[0]["sparta_route"]["executable"])
        self.assertTrue(failed[0]["decision_lifecycle_ledger"]["verification"]["valid"])

    def test_sensitive_customer_material_is_rejected(self):
        payload = load_payload(SAMPLE)
        payload = copy.deepcopy(payload)
        payload["actions"][0]["context"]["api_token"] = "do-not-accept"

        with self.assertRaises(ValueError) as error:
            validate_payload(payload)

        self.assertIn("prohibited sensitive material", str(error.exception))

    def test_markdown_is_customer_readable_and_bounded(self):
        report = build_customer_evaluation(load_payload(SAMPLE))
        markdown = render_markdown(report)

        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("Decision Path", markdown)
        self.assertIn("Autonomy Budget", markdown)
        self.assertIn("does not prove production safety", markdown)
        self.assertIn("EXAMPLECO_FINANCE_TRANSFER_005", markdown)

    def test_writes_outputs(self):
        report = build_customer_evaluation(load_payload(SAMPLE))
        json_output = TEST_OUTPUTS / "customer_evaluation_report.json"
        markdown_output = TEST_OUTPUTS / "Customer_Evaluation_Report.md"
        write_outputs(report, json_output, markdown_output)

        self.assertTrue(json_output.exists())
        self.assertTrue(markdown_output.exists())

    def test_docs_and_readme_link_customer_evaluation(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        doc = (ROOT / "docs" / "Customer_Evaluation.md").read_text(encoding="utf-8")

        self.assertIn("docs/Customer_Evaluation.md", readme)
        self.assertIn("reference_engine.customer_evaluation", doc)


if __name__ == "__main__":
    unittest.main()

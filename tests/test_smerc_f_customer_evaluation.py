import json
import unittest
from pathlib import Path

from reference_engine.customer_evaluation import build_customer_evaluation, load_payload, render_markdown


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "smerc_f_customer_eval_actions.json"
DOC = ROOT / "docs" / "SMERC_F_Customer_Evaluation.md"


class SmercFCustomerEvaluationTests(unittest.TestCase):
    def test_financial_sample_runs_and_has_mixed_postures(self):
        report = build_customer_evaluation(load_payload(SAMPLE))
        summary = report["summary"]

        self.assertEqual(report["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(report["tenant_id"], "financialco")
        self.assertEqual(summary["total_actions"], 8)
        self.assertGreaterEqual(summary["posture_counts"].get("ALLOW", 0), 1)
        self.assertGreaterEqual(summary["posture_counts"].get("THROTTLE", 0), 1)
        self.assertGreaterEqual(summary["posture_counts"].get("DENY", 0), 1)
        self.assertGreaterEqual(summary["ref_gate_counts"].get("fail", 0), 1)
        self.assertEqual(summary["valid_ledgers"], 8)
        self.assertEqual(report["pilot_fit"]["fit"], "strong")

    def test_financial_sample_preserves_metadata_only_boundary(self):
        payload_text = SAMPLE.read_text(encoding="utf-8")
        payload = json.loads(payload_text)

        boundary = payload["data_boundary"].lower()
        self.assertIn("metadata-only", boundary)
        self.assertIn("no secrets", boundary)
        self.assertIn("wallet keys", boundary)
        self.assertIn("regulated transaction payloads", boundary)
        self.assertNotIn("private_key", payload_text)
        self.assertNotIn("api_key", payload_text)
        self.assertNotIn("password", payload_text)

    def test_report_and_docs_are_financial_reviewer_readable(self):
        report = build_customer_evaluation(load_payload(SAMPLE))
        markdown = render_markdown(report)
        doc = DOC.read_text(encoding="utf-8")

        self.assertIn("SMERC-F Customer Evaluation", doc)
        self.assertIn("examples/smerc_f_customer_eval_actions.json", doc)
        self.assertIn("action_file = examples/smerc_f_customer_eval_actions.json", doc)
        self.assertIn("It does not prove production safety", doc)
        self.assertIn("FinancialCo SMERC Customer Evaluation Report", markdown)
        self.assertIn("SMERCF_STABLECOIN_BRIDGE_003", markdown)
        self.assertIn("Autonomy Budget", markdown)


if __name__ == "__main__":
    unittest.main()

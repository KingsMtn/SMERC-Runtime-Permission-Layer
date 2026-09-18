import copy
import unittest
from pathlib import Path

from reference_engine.aws_metadata_adapter import build_adapter_report, load_source_exports, normalize_source_exports
from reference_engine.customer_evaluation import build_customer_evaluation


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "examples" / "aws_open_source_validation_corpus.json"


class AWSOpenSourceValidationCorpusTests(unittest.TestCase):
    def test_corpus_is_external_provenance_with_inference_disclosure(self):
        rows = load_source_exports(CORPUS)

        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row["record_id"] for row in rows}), 8)
        for row in rows:
            self.assertTrue(row["source_url"].startswith("https://github.com/aws"))
            self.assertTrue(row["source_observation"])
            self.assertIn("SMERC analyst inference", row["label_basis"])
            self.assertIn(row["label_confidence"], {"medium", "high"})

    def test_corpus_runs_without_unsafe_or_rejected_rows(self):
        report = build_adapter_report(load_source_exports(CORPUS))

        self.assertEqual(report["accepted_rows"], 8)
        self.assertEqual(report["skipped_rows"], 0)
        self.assertEqual(report["customer_evaluation"]["summary"]["total_actions"], 8)
        self.assertEqual(report["customer_evaluation"]["summary"]["valid_ledgers"], 8)
        self.assertGreaterEqual(len(report["customer_evaluation"]["summary"]["posture_counts"]), 2)
        for action in report["normalized_customer_evaluation"]["actions"]:
            metadata = action["tool_plan"]["metadata"]
            self.assertTrue(metadata["source_observation"])
            self.assertIn("SMERC analyst inference", metadata["label_basis"])
            self.assertIn(metadata["label_confidence"], {"medium", "high"})

    def test_missing_rollback_evidence_on_high_impact_action_never_allows(self):
        payload = normalize_source_exports(load_source_exports(CORPUS))
        high_impact = next(
            action for action in payload["actions"] if action["tool_plan"]["metadata"]["source_record_id"] == "aws-open-iam-policy-change-003"
        )
        mutated = copy.deepcopy(payload)
        mutated.pop("adapter_summary")
        target = next(action for action in mutated["actions"] if action["action_id"] == high_impact["action_id"])
        target.pop("rollback_latency")

        report = build_customer_evaluation(mutated)
        record = next(item for item in report["records"] if item["action_id"] == target["action_id"])
        decision = record["decision"]

        self.assertNotEqual(decision["posture"], "ALLOW")
        self.assertIn("ROLLBACK_LATENCY_UNAVAILABLE", decision["reason_codes"])


if __name__ == "__main__":
    unittest.main()

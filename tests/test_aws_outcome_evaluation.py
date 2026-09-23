import copy
import unittest

from reference_engine.aws_mcp_enforced_live_proof import run_proof
from reference_engine.aws_outcome_evaluation import evaluate_record, evaluate_records
from reference_engine.aws_reversible_mutation_proof import run_mutation_proof


def mutation_result():
    return {
        "content": [],
        "structuredContent": {
            "return_value": {
                "resource_created": True,
                "resource_deleted": True,
                "rollback_latency_seconds": 0.4,
                "total_exposure_seconds": 1.0,
                "residual_count": 0,
            }
        },
        "isError": False,
    }


class AWSOutcomeEvaluationTests(unittest.TestCase):
    def test_read_only_success_is_coherent_without_self_awarded_accuracy(self):
        proof = run_proof(lambda *_args: {"content": [], "isError": False}, observed_at="2026-09-23T00:00:00Z")
        result = evaluate_record(proof["portable_evidence"])
        self.assertEqual(result["decision_execution_coherence"], "COHERENT")
        self.assertEqual(result["recovery_evidence"], "NOT_APPLICABLE")
        self.assertEqual(result["judgment_correctness"], "UNDETERMINED")
        self.assertEqual(result["learning_eligibility"], "READY_FOR_EXTERNAL_LABEL")

    def test_reversible_mutation_requires_and_recognizes_verified_recovery(self):
        proof = run_mutation_proof(lambda *_args: mutation_result(), observed_at="2026-09-23T00:00:00Z")
        result = evaluate_record(proof["portable_evidence"])
        self.assertEqual(result["posture"], "THROTTLE")
        self.assertEqual(result["decision_execution_coherence"], "COHERENT")
        self.assertEqual(result["recovery_evidence"], "VERIFIED")

    def test_tampered_record_is_rejected_before_evaluation(self):
        proof = run_proof(lambda *_args: {"content": [], "isError": False}, observed_at="2026-09-23T00:00:00Z")
        tampered = copy.deepcopy(proof["portable_evidence"])
        tampered["decision"]["posture"] = "DENY"
        with self.assertRaisesRegex(ValueError, "does not match"):
            evaluate_record(tampered)

    def test_report_discloses_missing_external_labels(self):
        read_only = run_proof(lambda *_args: {"content": [], "isError": False})["portable_evidence"]
        mutation = run_mutation_proof(lambda *_args: mutation_result())["portable_evidence"]
        report = evaluate_records([read_only, mutation], observed_at="2026-09-23T00:00:00Z")
        self.assertEqual(report["summary"]["record_count"], 2)
        self.assertEqual(report["summary"]["coherence_counts"], {"COHERENT": 2})
        self.assertEqual(report["summary"]["recovery_counts"], {"NOT_APPLICABLE": 1, "VERIFIED": 1})
        self.assertEqual(report["summary"]["ready_for_external_label_count"], 2)
        self.assertIsNone(report["summary"]["judgment_correctness_rate"])
        self.assertIn("independent", report["evidence_boundary"][1])


if __name__ == "__main__":
    unittest.main()

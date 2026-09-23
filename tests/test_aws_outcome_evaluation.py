import copy
import unittest

from reference_engine.aws_mcp_enforced_live_proof import run_proof
from reference_engine.aws_external_outcome_label import build_external_outcome_label
from reference_engine.aws_outcome_evaluation import evaluate_record, evaluate_records, load_external_labels
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
    KEY = b"independent-reviewer-test-key-32-bytes-minimum"

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

    def test_authenticated_external_label_enables_correctness_metric(self):
        record = run_proof(lambda *_args: {"content": [], "isError": False})["portable_evidence"]
        label = build_external_outcome_label(
            record,
            label_id="review-001",
            source_type="HUMAN_REVIEW",
            reviewer_id="external-reviewer-1",
            observed_at="2026-09-23T01:00:00Z",
            judged_correct=True,
            unexpected_consequences=False,
            controls_sufficient=True,
            rationale="Read-only action completed with no unexpected consequence.",
            key_id="reviewer-key-1",
            signing_key=self.KEY,
        )
        report = evaluate_records(
            [record], external_labels={record["record_id"]: label}, label_verification_key=self.KEY
        )
        self.assertEqual(report["summary"]["external_label_count"], 1)
        self.assertEqual(report["summary"]["judgment_correctness_rate"], 1.0)
        self.assertEqual(report["evaluations"][0]["judgment_correctness"], "CORRECT")

    def test_label_for_different_record_is_rejected(self):
        first = run_proof(lambda *_args: {"value": 1, "isError": False})["portable_evidence"]
        second = run_proof(lambda *_args: {"value": 2, "isError": False})["portable_evidence"]
        label = build_external_outcome_label(
            first,
            label_id="review-002",
            source_type="INCIDENT_OUTCOME",
            reviewer_id="incident-reviewer",
            observed_at="2026-09-23T02:00:00Z",
            judged_correct=False,
            unexpected_consequences=True,
            controls_sufficient=False,
            rationale="Independent incident review found an unexpected consequence.",
            key_id="reviewer-key-1",
            signing_key=self.KEY,
        )
        with self.assertRaisesRegex(ValueError, "not bound"):
            evaluate_record(second, external_label=label, label_verification_key=self.KEY)

    def test_duplicate_label_files_are_rejected(self):
        import json
        from pathlib import Path

        scratch = Path("tests/_tmp/aws-outcome-labels")
        scratch.mkdir(parents=True, exist_ok=True)
        first = scratch / "first.json"
        second = scratch / "second.json"
        payload = {"record_id": "same-record"}
        first.write_text(json.dumps(payload), encoding="utf-8")
        second.write_text(json.dumps(payload), encoding="utf-8")
        try:
            with self.assertRaisesRegex(ValueError, "duplicate external label"):
                load_external_labels([first, second])
        finally:
            first.unlink(missing_ok=True)
            second.unlink(missing_ok=True)
            scratch.rmdir()


if __name__ == "__main__":
    unittest.main()

import copy
import unittest

from reference_engine.aws_external_outcome_label import build_external_outcome_label
from reference_engine.aws_final_proof_package import build_final_proof_package
from reference_engine.aws_mcp_denied_write_proof import run_denied_write_proof
from reference_engine.aws_mcp_enforced_live_proof import run_proof
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


class AWSFinalProofPackageTests(unittest.TestCase):
    KEY = b"independent-reviewer-test-key-32-bytes-minimum"

    def setUp(self):
        self.read = run_proof(lambda *_args: {"content": [], "isError": False})
        self.denied = run_denied_write_proof()
        self.mutation = run_mutation_proof(lambda *_args: mutation_result())

    def test_builds_technical_package_without_claiming_accuracy(self):
        package = build_final_proof_package(self.read, self.denied, self.mutation, cost_cap_usd=1.0)
        self.assertEqual(package["status"], "TECHNICALLY_COMPLETE_AWAITING_EXTERNAL_LABELS")
        self.assertEqual(package["proofs"]["denied_write"]["status"], "VERIFIED_BEFORE_EXECUTION")
        self.assertEqual(package["proofs"]["reversible_mutation"]["residual_count"], 0)
        self.assertEqual(package["cost_control"]["estimated_total_usd"], 0.0)
        self.assertIsNone(package["outcome_evaluation"]["summary"]["judgment_correctness_rate"])

    def test_authenticated_labels_complete_independent_validation(self):
        labels = {}
        for index, record in enumerate((self.read["portable_evidence"], self.mutation["portable_evidence"]), 1):
            label = build_external_outcome_label(
                record,
                label_id=f"review-{index}",
                source_type="HUMAN_REVIEW",
                reviewer_id="external-reviewer",
                observed_at="2026-09-23T00:00:00Z",
                judged_correct=True,
                unexpected_consequences=False,
                controls_sufficient=True,
                rationale="Independent review confirmed the observed outcome and controls.",
                key_id="reviewer-key-1",
                signing_key=self.KEY,
            )
            labels[record["record_id"]] = label
        package = build_final_proof_package(
            self.read,
            self.denied,
            self.mutation,
            cost_cap_usd=1.0,
            external_labels=labels,
            label_verification_key=self.KEY,
        )
        self.assertEqual(package["status"], "INDEPENDENTLY_VALIDATED")
        self.assertEqual(package["external_validation"]["coverage"], 1.0)
        self.assertEqual(package["outcome_evaluation"]["summary"]["judgment_correctness_rate"], 1.0)

    def test_rejects_denial_that_reached_executor(self):
        denied = copy.deepcopy(self.denied)
        denied["aws_executor_called"] = True
        with self.assertRaisesRegex(ValueError, "reached"):
            build_final_proof_package(self.read, denied, self.mutation, cost_cap_usd=1.0)

    def test_rejects_mutation_with_residual_state(self):
        mutation = copy.deepcopy(self.mutation)
        mutation["aws_observation"]["residual_count"] = 1
        with self.assertRaisesRegex(ValueError, "zero residual"):
            build_final_proof_package(self.read, self.denied, mutation, cost_cap_usd=1.0)

    def test_rejects_cost_above_cap(self):
        read = copy.deepcopy(self.read)
        read["action"]["estimated_incremental_cost_usd"] = 1.01
        with self.assertRaisesRegex(ValueError, "exceeds"):
            build_final_proof_package(read, self.denied, self.mutation, cost_cap_usd=1.0)


if __name__ == "__main__":
    unittest.main()

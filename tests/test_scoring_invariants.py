import unittest

from reference_engine.scoring_invariants import evaluate_invariants


class ScoringInvariantTests(unittest.TestCase):
    def setUp(self):
        self.result = evaluate_invariants()

    def test_all_declared_invariants_pass(self):
        self.assertEqual(self.result["summary"]["status"], "PASS")
        self.assertEqual(self.result["summary"]["failed"], 0)
        self.assertGreaterEqual(self.result["summary"]["total"], 10)

    def test_recoverability_invariants_are_present(self):
        ids = {item["invariant_id"] for item in self.result["results"]}
        self.assertIn("RECOVERY_REVERSIBILITY_MONOTONIC", ids)
        self.assertIn("RECOVERY_ROLLBACK_LATENCY_MONOTONIC", ids)
        self.assertIn("RECOVERY_EVIDENCE_VALIDITY_MONOTONIC", ids)
        self.assertIn("RECOVERY_ANOMALY_PRESSURE_MONOTONIC", ids)

    def test_model_fitness_fail_closed_invariants_are_present(self):
        ids = {item["invariant_id"] for item in self.result["results"]}
        self.assertIn("FITNESS_DATA_BOUNDARY_FAIL_CLOSED", ids)
        self.assertIn("FITNESS_TOOL_AUTHORITY_FAIL_CLOSED", ids)
        self.assertIn("FITNESS_CAPABILITY_GAP_FAIL_CLOSED", ids)

    def test_claim_boundary_disclaims_production_accuracy(self):
        boundary = self.result["summary"]["claim_boundary"].lower()
        self.assertIn("do not prove production incident reduction", boundary)
        self.assertIn("customer-calibrated thresholds", boundary)


if __name__ == "__main__":
    unittest.main()

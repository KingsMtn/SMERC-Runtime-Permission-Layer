import unittest

from reference_engine.aws_mcp_recovery_proof import VERSION, run_proof


class AWSMCPRecoveryProofTests(unittest.TestCase):
    def test_three_case_proof_preserves_gate_ordering(self):
        proof = run_proof()
        self.assertEqual(proof["version"], VERSION)
        self.assertTrue(proof["result"]["missing_stopped_before_governance"])
        self.assertTrue(proof["result"]["stale_stopped_before_governance"])
        self.assertTrue(proof["result"]["verified_reached_normal_governance"])
        self.assertTrue(proof["result"]["verified_did_not_gain_authority"])

    def test_missing_and_stale_cases_are_distinct(self):
        proof = run_proof()
        self.assertEqual(proof["cases"]["missing"]["recovery_boundary"]["max_recommended_posture"], "DENY")
        self.assertEqual(proof["cases"]["stale"]["recovery_boundary"]["max_recommended_posture"], "FREEZE")
        self.assertEqual(proof["cases"]["verified"]["recovery_boundary"]["boundary_state"], "ADMIT_TO_GOVERNANCE")

    def test_proof_is_zero_spend_and_does_not_claim_live_aws(self):
        proof = run_proof()
        self.assertFalse(proof["aws_resources_created_or_modified"])
        self.assertEqual(proof["incremental_aws_cost_usd"], 0.0)
        self.assertIn("not a live AWS call", proof["boundary"])


if __name__ == "__main__":
    unittest.main()

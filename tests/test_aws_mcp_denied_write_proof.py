import unittest

from reference_engine.aws_mcp_denied_write_proof import (
    PROOF_BUCKET,
    SCHEMA,
    build_denied_write_request,
    run_denied_write_proof,
)


class AWSMCPDeniedWriteProofTests(unittest.TestCase):
    def test_destructive_write_is_denied_before_executor(self):
        proof = run_denied_write_proof(observed_at="2026-09-21T00:00:00+00:00")

        self.assertEqual(proof["schema"], SCHEMA)
        self.assertFalse(proof["aws_executor_called"])
        self.assertFalse(proof["aws_resource_changed"])
        self.assertEqual(proof["smerc"]["admission_decision"], "ADMIT")
        self.assertEqual(proof["smerc"]["posture"], "DENY")
        self.assertEqual(proof["smerc"]["route_state"], "BLOCK")
        self.assertIn("IRREVERSIBLE_EXPOSURE_HIGH", proof["smerc"]["reason_codes"])
        self.assertIn("block_execution", proof["smerc"]["required_controls"])
        self.assertNotIn("execution_result", proof["smerc"])

    def test_request_binds_concrete_write_target(self):
        request = build_denied_write_request()
        arguments = request["params"]["arguments"]

        self.assertEqual(arguments["aws_call"]["tool_name"], "delete_bucket")
        self.assertEqual(arguments["aws_call"]["arguments"], {"bucket": PROOF_BUCKET})
        self.assertTrue(arguments["governance_request"]["tool_call"]["external_side_effect"])
        self.assertFalse(arguments["governance_request"]["tool_call"]["supports_rollback"])


if __name__ == "__main__":
    unittest.main()

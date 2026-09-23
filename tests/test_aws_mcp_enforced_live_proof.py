import unittest

from reference_engine.aws_mcp_enforced_live_proof import SCHEMA, build_request, run_proof
from reference_engine.mcp_aws_enforcement_adapter import AWSMCPEnforcementAdapter
from reference_engine.portable_evidence import verify_portable_evidence


class AWSMCPEnforcedLiveProofTests(unittest.TestCase):
    def test_success_proof_contains_only_bounded_result_evidence(self):
        calls = []

        def executor(server, tool, arguments):
            calls.append((server, tool, arguments))
            return {"content": [{"type": "text", "text": "37 regions"}], "isError": False}

        proof = run_proof(executor, observed_at="2026-09-20T00:00:00+00:00")

        self.assertEqual(proof["schema"], SCHEMA)
        self.assertTrue(proof["transport_enforced_for_observed_call"])
        self.assertFalse(proof["production_evidence"])
        self.assertEqual(calls, [("aws-mcp", "list_regions", {})])
        self.assertEqual(proof["smerc"]["admission_decision"], "ADMIT")
        self.assertEqual(proof["smerc"]["posture"], "ALLOW")
        self.assertEqual(proof["smerc"]["execution_result"]["status"], "succeeded")
        self.assertRegex(proof["smerc"]["execution_result"]["result_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("aws_result", proof)
        self.assertFalse(proof["sanitation"]["raw_aws_response_stored"])
        portable = proof["portable_evidence"]
        self.assertEqual(verify_portable_evidence(portable)["status"], "HASH_VERIFIED")
        self.assertEqual(portable["decision"]["posture"], "ALLOW")
        self.assertEqual(portable["containment"]["cleanup_status"], "NOT_REQUIRED")
        self.assertFalse(portable["containment"]["cleanup_verified"])

    def test_failed_admission_never_reaches_executor(self):
        request = build_request()
        request["params"]["arguments"]["runtime_admission"]["checks"]["least_privilege_confirmed"] = False
        calls = []

        response = AWSMCPEnforcementAdapter(lambda *args: calls.append(args)).handle(request)

        self.assertTrue(response["result"]["isError"])
        self.assertEqual(response["result"]["structuredContent"]["smerc"]["admission_decision"], "REJECT")
        self.assertEqual(calls, [])

    def test_executor_failure_cannot_create_success_proof(self):
        def failed_executor(*_args):
            raise RuntimeError("authentication unavailable")

        with self.assertRaisesRegex(RuntimeError, "no success proof"):
            run_proof(failed_executor)


if __name__ == "__main__":
    unittest.main()

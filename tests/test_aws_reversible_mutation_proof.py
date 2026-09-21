import unittest

from reference_engine.aws_reversible_mutation_proof import AWS_MUTATION_SCRIPT, SCHEMA, TOOL_NAME, build_mutation_approval, build_mutation_request, run_mutation_proof
from reference_engine.mcp_aws_enforcement_adapter import AWSMCPEnforcementAdapter


def result_payload(*, residual_count=0, deleted=True):
    return {
        "content": [],
        "structuredContent": {"return_value": {"resource_created": True, "resource_deleted": deleted, "rollback_latency_seconds": 0.597, "total_exposure_seconds": 1.416, "residual_count": residual_count}},
        "isError": False,
    }


class AWSReversibleMutationProofTests(unittest.TestCase):
    def test_success_requires_cleanup_and_zero_residual_state(self):
        calls = []

        def executor(server, tool, arguments):
            calls.append((server, tool, arguments))
            return result_payload()

        proof = run_mutation_proof(executor, observed_at="2026-09-21T00:00:00+00:00")
        self.assertEqual(proof["schema"], SCHEMA)
        self.assertEqual(calls, [("aws-mcp", TOOL_NAME, {"code": AWS_MUTATION_SCRIPT})])
        self.assertEqual(proof["smerc"]["posture"], "THROTTLE")
        self.assertEqual(
            proof["smerc"]["approval_transition"]["executed_posture"],
            "ALLOW_WITH_OWNER_APPROVAL",
        )
        self.assertEqual(proof["aws_observation"]["rollback_latency_seconds"], 0.597)
        self.assertEqual(proof["aws_observation"]["residual_count"], 0)

    def test_residual_state_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "rollback or residual-state"):
            run_mutation_proof(lambda *_args: result_payload(residual_count=1, deleted=False))

    def test_request_is_fixed_to_bounded_create_delete_sequence(self):
        request = build_mutation_request()
        arguments = request["params"]["arguments"]
        self.assertEqual(arguments["aws_call"]["arguments"], {"code": AWS_MUTATION_SCRIPT})
        self.assertIn("CreateSecurityGroup", AWS_MUTATION_SCRIPT)
        self.assertIn("DeleteSecurityGroup", AWS_MUTATION_SCRIPT)
        self.assertIn("DescribeSecurityGroups", AWS_MUTATION_SCRIPT)
        self.assertEqual(arguments["governance_request"]["agent_identity"]["credential_scope"], "production_write")
        self.assertNotIn("operator_approval", arguments)

    def test_tampered_target_approval_fails_before_execution(self):
        request = build_mutation_request()
        request["params"]["arguments"]["aws_call"]["arguments"]["code"] += "\n# tampered"
        approval = build_mutation_approval()
        calls = []

        response = AWSMCPEnforcementAdapter(
            lambda *args: calls.append(args),
            approved_target_sha256=approval["approved_target_sha256"],
            approver_id=approval["approver_id"],
        ).handle(request)

        self.assertTrue(response["result"]["isError"])
        self.assertEqual(calls, [])

    def test_throttle_without_trusted_adapter_approval_does_not_execute(self):
        calls = []

        response = AWSMCPEnforcementAdapter(lambda *args: calls.append(args)).handle(build_mutation_request())

        evidence = response["result"]["structuredContent"]["smerc"]
        self.assertTrue(response["result"]["isError"])
        self.assertEqual(evidence["posture"], "THROTTLE")
        self.assertNotIn("approval_transition", evidence)
        self.assertEqual(calls, [])

    def test_owner_approval_cannot_override_deny(self):
        request = build_mutation_request()
        request["params"]["arguments"]["governance_request"]["risk_signals"].update(
            {
                "base_action_risk": 1.0,
                "reversibility": 0.0,
                "containment_strength": 0.0,
                "rollback_latency": 1.0,
                "evidence_validity": 0.4,
                "anomaly_pressure": 0.8,
                "impact_scope": 1.0,
                "cancel_reliability": 0.0,
                "authorization_confidence": 0.4,
            }
        )
        approval = build_mutation_approval()
        calls = []

        response = AWSMCPEnforcementAdapter(
            lambda *args: calls.append(args),
            approved_target_sha256=approval["approved_target_sha256"],
            approver_id=approval["approver_id"],
        ).handle(request)

        evidence = response["result"]["structuredContent"]["smerc"]
        self.assertEqual(evidence["posture"], "DENY")
        self.assertNotIn("approval_transition", evidence)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()

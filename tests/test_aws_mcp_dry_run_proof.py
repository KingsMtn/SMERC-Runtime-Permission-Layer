import unittest

from reference_engine.aws_mcp_dry_run_proof import (
    AWS_DRY_RUN_SCRIPT,
    SCHEMA,
    SENTINEL_GROUP,
    TOOL_NAME,
    build_dry_run_request,
    run_dry_run_proof,
)


class AWSMCPDryRunProofTests(unittest.TestCase):
    @staticmethod
    def successful_executor(_server, _tool, _arguments):
        return {
            "content": [{"type": "text", "text": "dry run complete"}],
            "structuredContent": {
                "return_value": {
                    "error_code": "DryRunOperation",
                    "authorized": True,
                    "matching_group_count": 0,
                    "resource_created": False,
                }
            },
            "isError": False,
        }

    def test_success_requires_authorized_dry_run_and_zero_read_back(self):
        calls = []

        def executor(server, tool, arguments):
            calls.append((server, tool, arguments))
            return self.successful_executor(server, tool, arguments)

        proof = run_dry_run_proof(executor, observed_at="2026-09-21T00:00:00+00:00")

        self.assertEqual(proof["schema"], SCHEMA)
        self.assertEqual(calls, [("aws-mcp", TOOL_NAME, {"code": AWS_DRY_RUN_SCRIPT})])
        self.assertEqual(proof["smerc"]["admission_decision"], "ADMIT")
        self.assertEqual(proof["smerc"]["posture"], "ALLOW")
        self.assertTrue(proof["aws_observation"]["authorized"])
        self.assertFalse(proof["aws_observation"]["resource_created"])

    def test_resource_read_back_fails_closed(self):
        def executor(*_args):
            result = dict(self.successful_executor(None, None, None))
            result["structuredContent"] = {
                "return_value": {
                    "error_code": "DryRunOperation",
                    "authorized": True,
                    "matching_group_count": 1,
                    "resource_created": True,
                }
            }
            return result

        with self.assertRaisesRegex(RuntimeError, "authorized non-mutation"):
            run_dry_run_proof(executor)

    def test_fixed_script_contains_dry_run_and_read_back(self):
        request = build_dry_run_request()
        call = request["params"]["arguments"]["aws_call"]

        self.assertEqual(call["tool_name"], TOOL_NAME)
        self.assertEqual(call["arguments"], {"code": AWS_DRY_RUN_SCRIPT})
        self.assertEqual(
            request["params"]["arguments"]["governance_request"]["agent_identity"]["credential_scope"],
            "production_write",
        )
        self.assertIn('"DryRun": True', AWS_DRY_RUN_SCRIPT)
        self.assertIn("DescribeSecurityGroups", AWS_DRY_RUN_SCRIPT)
        self.assertIn(SENTINEL_GROUP, AWS_DRY_RUN_SCRIPT)


if __name__ == "__main__":
    unittest.main()

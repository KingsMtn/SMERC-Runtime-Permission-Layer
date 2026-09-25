import copy
import hashlib
import json
import unittest

from reference_engine.recovery_capability_contract import evaluate_recovery_capability


def _sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def capability(test_status="VERIFIED", mechanism="SNAPSHOT_RESTORE"):
    value = {
        "version": "smerc.recovery-capability.v1", "provider_id": "aws-adapter",
        "tool_family": "aws.ec2", "operation": "update_launch_template",
        "scope": {"resource_patterns": ["arn:aws:ec2:us-east-1:123:launch-template/*"], "environment": "pilot"},
        "mechanism": {"type": mechanism, "isolation": "RESOURCE", "trigger": "EXTERNAL_AUTHORITY",
            "max_rollback_latency_seconds": 90, "validity_window_seconds": 3600},
        "evidence": {"plan_ref": "evidence://rollback-test/42", "test_status": test_status,
            "tested_at_ms": 1_000, "evidence_sha256": "a" * 64},
        "limits": {"max_scope_units": 5, "max_mutations": 2, "irreversible_side_effects": False},
        "authority_effect": "NONE", "advisory_only": True,
        "issued_at_ms": 1_000, "expires_at_ms": 2_000,
    }
    value["capability_sha256"] = _sha(value)
    value["capability_id"] = f"recovery_{value['capability_sha256'][:24]}"
    return value


def evaluate(value, **overrides):
    args = {"now_ms": 1_500, "expected_tool_family": "aws.ec2",
        "expected_operation": "update_launch_template", "expected_environment": "pilot",
        "requested_scope_units": 2, "requested_mutations": 1,
        "max_acceptable_rollback_latency_seconds": 120}
    args.update(overrides)
    return evaluate_recovery_capability(value, **args)


class RecoveryCapabilityContractTests(unittest.TestCase):
    def test_verified_capability_adds_no_permission(self):
        result = evaluate(capability())
        self.assertEqual(result["decision"], "ACCEPT_EVIDENCE")
        self.assertIsNone(result["max_recommended_posture"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_unverified_or_stale_capability_freezes(self):
        for state in ("UNVERIFIED", "STALE"):
            with self.subTest(state=state):
                result = evaluate(capability(state))
                self.assertEqual(result["decision"], "CONSTRAIN")
                self.assertEqual(result["max_recommended_posture"], "FREEZE")

    def test_failed_or_absent_recovery_denies(self):
        self.assertEqual(evaluate(capability("FAILED"))["max_recommended_posture"], "DENY")
        self.assertEqual(evaluate(capability(mechanism="NONE"))["max_recommended_posture"], "DENY")

    def test_scope_and_latency_limits_freeze(self):
        self.assertEqual(evaluate(capability(), requested_scope_units=6)["max_recommended_posture"], "FREEZE")
        self.assertEqual(evaluate(capability(), max_acceptable_rollback_latency_seconds=30)["max_recommended_posture"], "FREEZE")

    def test_tampering_expiry_and_authority_claim_fail_closed(self):
        tampered = capability(); tampered["limits"]["max_scope_units"] = 999
        self.assertEqual(evaluate(tampered)["max_recommended_posture"], "DENY")
        self.assertEqual(evaluate(capability(), now_ms=2_000)["max_recommended_posture"], "DENY")
        authority = copy.deepcopy(capability()); authority["authority_effect"] = "ALLOW"
        unsigned = {k: v for k, v in authority.items() if k not in {"capability_id", "capability_sha256"}}
        authority["capability_sha256"] = _sha(unsigned)
        authority["capability_id"] = f"recovery_{authority['capability_sha256'][:24]}"
        result = evaluate(authority)
        self.assertEqual(result["max_recommended_posture"], "DENY")
        self.assertIn("cannot grant authority", result["plain_english_summary"])

    def test_runtime_scope_mismatch_denies(self):
        result = evaluate(capability(), expected_environment="production")
        self.assertEqual(result["max_recommended_posture"], "DENY")
        self.assertIn("environment", result["plain_english_summary"])


if __name__ == "__main__":
    unittest.main()

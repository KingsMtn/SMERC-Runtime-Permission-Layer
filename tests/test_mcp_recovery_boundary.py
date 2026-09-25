import copy
import hashlib
import json
import unittest

from reference_engine.mcp_recovery_boundary import evaluate_mcp_recovery_boundary


def _sha(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode()).hexdigest()


def capability(status="VERIFIED"):
    value = {
        "version": "smerc.recovery-capability.v1", "provider_id": "mcp-adapter",
        "tool_family": "mcp.aws_ops", "operation": "update_stack",
        "scope": {"resource_patterns": ["arn:aws:cloudformation:us-east-1:123:stack/pilot/*"], "environment": "pilot"},
        "mechanism": {"type": "RECREATE_FROM_DECLARATION", "isolation": "RESOURCE",
            "trigger": "EXTERNAL_AUTHORITY", "max_rollback_latency_seconds": 90,
            "validity_window_seconds": 3600},
        "evidence": {"plan_ref": "evidence://mcp/recovery/1", "test_status": status,
            "tested_at_ms": 1_000, "evidence_sha256": "a" * 64},
        "limits": {"max_scope_units": 5, "max_mutations": 2, "irreversible_side_effects": False},
        "authority_effect": "NONE", "advisory_only": True, "issued_at_ms": 1_000, "expires_at_ms": 2_000,
    }
    value["capability_sha256"] = _sha(value)
    value["capability_id"] = f"recovery_{value['capability_sha256'][:24]}"
    return value


def envelope(operation="write", include_capability=True):
    value = {"version": "smerc.mcp-recovery-boundary.v1", "request_id": "mcp-1",
        "server_name": "aws_ops", "tool_name": "update_stack", "operation": operation,
        "environment": "pilot", "requested_scope_units": 2, "requested_mutations": 1,
        "max_acceptable_rollback_latency_seconds": 120}
    if include_capability:
        value["recovery_capability"] = capability()
    return value


class MCPRecoveryBoundaryTests(unittest.TestCase):
    def test_verified_capability_only_admits_to_downstream_governance(self):
        result = evaluate_mcp_recovery_boundary(envelope(), now_ms=1_500)
        self.assertEqual(result["boundary_state"], "ADMIT_TO_GOVERNANCE")
        self.assertTrue(result["eligible_for_downstream_governance"])
        self.assertFalse(result["should_execute_tool"])
        self.assertEqual(result["authority_effect"], "NONE")

    def test_mutation_without_capability_denies(self):
        result = evaluate_mcp_recovery_boundary(envelope(include_capability=False), now_ms=1_500)
        self.assertEqual(result["boundary_state"], "REJECT")
        self.assertEqual(result["max_recommended_posture"], "DENY")

    def test_read_only_call_can_continue_without_recovery_evidence(self):
        result = evaluate_mcp_recovery_boundary(envelope("read", False), now_ms=1_500)
        self.assertEqual(result["boundary_state"], "ADMIT_READ_ONLY")
        self.assertTrue(result["eligible_for_downstream_governance"])
        self.assertFalse(result["should_execute_tool"])

    def test_stale_capability_holds(self):
        value = envelope(); value["recovery_capability"] = capability("STALE")
        result = evaluate_mcp_recovery_boundary(value, now_ms=1_500)
        self.assertEqual(result["boundary_state"], "HOLD")
        self.assertEqual(result["max_recommended_posture"], "FREEZE")

    def test_tampered_mismatched_and_expired_capabilities_deny(self):
        tampered = envelope(); tampered["recovery_capability"]["limits"]["max_mutations"] = 99
        mismatch = envelope(); mismatch["server_name"] = "different_server"
        for value, now in ((tampered, 1_500), (mismatch, 1_500), (envelope(), 2_000)):
            with self.subTest(value=value, now=now):
                result = evaluate_mcp_recovery_boundary(value, now_ms=now)
                self.assertEqual(result["boundary_state"], "REJECT")
                self.assertEqual(result["max_recommended_posture"], "DENY")

    def test_recovery_evidence_cannot_claim_authority(self):
        value = envelope(); value["recovery_capability"]["authority_effect"] = "ALLOW"
        unsigned = {k: v for k, v in value["recovery_capability"].items()
            if k not in {"capability_id", "capability_sha256"}}
        value["recovery_capability"]["capability_sha256"] = _sha(unsigned)
        value["recovery_capability"]["capability_id"] = f"recovery_{value['recovery_capability']['capability_sha256'][:24]}"
        result = evaluate_mcp_recovery_boundary(value, now_ms=1_500)
        self.assertEqual(result["boundary_state"], "REJECT")
        self.assertIn("cannot grant authority", result["plain_english_summary"])


if __name__ == "__main__":
    unittest.main()

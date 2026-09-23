import copy
import hashlib
import unittest

from reference_engine.portable_evidence import build_portable_evidence, verify_portable_evidence


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def payload():
    return {
        "record_id": "aws-proof-001",
        "observed_at": "2026-09-23T00:00:00Z",
        "workload": {"workload_id": "smerc-aws-mcp", "model_id": "not-observed", "model_digest": sha("not-observed")},
        "source_control": {"repository": "KingsMtn/SMERC-Runtime-Permission-Layer", "commit_sha": "a" * 40, "workflow": "aws-live-proof", "ephemeral_ref": "refs/heads/codex/proof-001"},
        "runtime": {"platform": "aws", "account": "redacted", "region": "us-east-1", "principal": "SMERC-MCP-Pilot", "execution_boundary": "managed-aws-mcp"},
        "policy": {"policy_id": "pilot-read-only", "policy_revision": "1", "policy_bundle_sha256": sha("policy"), "enforcement_mode": "ENFORCE"},
        "decision": {"admission": "ADMIT", "posture": "ALLOW", "explanation_code": "READ_ONLY_ZERO_COST", "decision_id": "decision-001"},
        "tool_activity": {"transcript_sha256": sha("list-regions"), "call_count": 1, "tools": ["aws.list_regions"]},
        "containment": {"isolation": "ephemeral-worktree", "network_scope": "aws-mcp-only", "failure_contained": True, "cleanup_status": "SUCCEEDED", "cleanup_verified": True},
        "data_handling": {"data_classes": ["cloud-metadata"], "redacted_fields": ["account", "authorization"], "secrets_persisted": False},
        "claim_boundary": "This record proves record integrity and issuer authentication only; it is not TRACE conformance, hardware attestation, or production certification.",
    }


class PortableEvidenceTests(unittest.TestCase):
    def test_hash_record_is_deterministic_and_tamper_evident(self):
        record = build_portable_evidence(payload(), issuer="smerc-reference-engine")
        self.assertEqual(record, build_portable_evidence(payload(), issuer="smerc-reference-engine"))
        self.assertEqual(verify_portable_evidence(record)["status"], "HASH_VERIFIED")
        tampered = copy.deepcopy(record)
        tampered["decision"]["posture"] = "DENY"
        with self.assertRaisesRegex(ValueError, "does not match"):
            verify_portable_evidence(tampered)

    def test_authenticated_record_requires_correct_key(self):
        key = b"portable-evidence-test-key-32-bytes-minimum"
        record = build_portable_evidence(payload(), issuer="smerc-reference-engine", key_id="pilot-key-1", signing_key=key)
        with self.assertRaisesRegex(ValueError, "verification_key is required"):
            verify_portable_evidence(record)
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            verify_portable_evidence(record, verification_key=b"wrong-key-that-is-at-least-32-bytes")
        self.assertEqual(verify_portable_evidence(record, verification_key=key)["status"], "AUTHENTICATED")

    def test_cleanup_claim_must_be_consistent(self):
        value = payload()
        value["containment"]["cleanup_status"] = "UNVERIFIED"
        with self.assertRaisesRegex(ValueError, "verified cleanup"):
            build_portable_evidence(value, issuer="smerc-reference-engine")

    def test_secrets_cannot_be_declared_persisted(self):
        value = payload()
        value["data_handling"]["secrets_persisted"] = True
        with self.assertRaisesRegex(ValueError, "never claim"):
            build_portable_evidence(value, issuer="smerc-reference-engine")

    def test_unknown_fields_fail_closed(self):
        value = payload()
        value["runtime"]["surprise"] = "field"
        with self.assertRaisesRegex(ValueError, "runtime fields are invalid"):
            build_portable_evidence(value, issuer="smerc-reference-engine")


if __name__ == "__main__":
    unittest.main()

import copy
import unittest

from reference_engine.ephemeral_execution_envelope import (
    canonical_digest, create_envelope, envelope_digest, transition_envelope, verify_envelope,
)
from reference_engine.trace_evidence_export import TRACE_PROFILE, export_trace_candidate


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def envelope():
    return create_envelope(
        namespace="codex", run_id="run-001", base_ref="refs/heads/main",
        base_commit_sha=SHA_A, policy_bundle_sha256=SHA_B,
        execution_target_sha256=SHA_C, permit_id="permit-001",
        replay_id="replay-001", now=1_000, ttl_seconds=600,
    )


def promotion_evidence(**changes):
    value = {
        "tests_passed": True, "review_approved": True, "policy_rechecked": True,
        "isolation_verified": True, "approved_target_sha256": SHA_C,
        "sealed_commit_sha": SHA_A, "durable_ref": "refs/heads/reviewed/run-001",
    }
    value.update(changes)
    return value


class EphemeralExecutionEnvelopeTests(unittest.TestCase):
    def test_happy_path_promotes_only_after_seal_and_evidence(self):
        active = transition_envelope(envelope(), "ACTIVE", now=1_010)
        sealed = transition_envelope(active, "SEALED", now=1_020, evidence={"sealed_commit_sha": SHA_A})
        promoted = transition_envelope(sealed, "PROMOTED", now=1_030, evidence=promotion_evidence())
        self.assertEqual(promoted["state"], "PROMOTED")
        self.assertEqual(promoted["ephemeral_ref"], "refs/ephemeral/codex/run-001")
        self.assertFalse(promoted["containment"]["direct_durable_writes"])
        self.assertEqual(len(promoted["events"]), 4)
        self.assertEqual(verify_envelope(promoted, now=1_040)["state"], "PROMOTED")

    def test_promotion_requires_every_gate_and_exact_target(self):
        sealed = transition_envelope(
            transition_envelope(envelope(), "ACTIVE", now=1_010), "SEALED", now=1_020,
            evidence={"sealed_commit_sha": SHA_A},
        )
        with self.assertRaisesRegex(ValueError, "review_approved"):
            transition_envelope(sealed, "PROMOTED", now=1_030, evidence=promotion_evidence(review_approved=False))
        with self.assertRaisesRegex(ValueError, "target"):
            transition_envelope(sealed, "PROMOTED", now=1_030, evidence=promotion_evidence(approved_target_sha256=SHA_A))

    def test_expired_envelope_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "expired"):
            verify_envelope(envelope(), now=1_600)
        expired = transition_envelope(envelope(), "EXPIRED", now=1_600, reason="TTL elapsed")
        self.assertEqual(expired["state"], "EXPIRED")

    def test_invalid_transition_and_tampering_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "invalid envelope transition"):
            transition_envelope(envelope(), "PROMOTED", now=1_010, evidence=promotion_evidence())
        tampered = copy.deepcopy(envelope())
        tampered["execution_target_sha256"] = SHA_A
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_envelope(tampered, now=1_010)

    def test_rehashed_invalid_event_chain_still_fails_closed(self):
        forged = copy.deepcopy(envelope())
        event = forged["events"][0]
        event["to_state"] = "SEALED"
        event["event_sha256"] = canonical_digest(
            {key: value for key, value in event.items() if key != "event_sha256"}
        )
        forged["state"] = "SEALED"
        forged["envelope_sha256"] = envelope_digest(forged)
        with self.assertRaisesRegex(ValueError, "begin with envelope creation"):
            verify_envelope(forged, now=1_010)

    def test_rehashed_wrong_ephemeral_ref_still_fails_closed(self):
        forged = copy.deepcopy(envelope())
        forged["ephemeral_ref"] = "refs/ephemeral/other/run-001"
        forged["envelope_sha256"] = envelope_digest(forged)
        with self.assertRaisesRegex(ValueError, "ephemeral_ref"):
            verify_envelope(forged, now=1_010)

    def test_discard_requires_reason_and_is_terminal(self):
        with self.assertRaisesRegex(ValueError, "terminal reason"):
            transition_envelope(envelope(), "DISCARDED", now=1_010)
        discarded = transition_envelope(envelope(), "DISCARDED", now=1_010, reason="review rejected")
        with self.assertRaisesRegex(ValueError, "invalid envelope transition"):
            transition_envelope(discarded, "ACTIVE", now=1_020)

    def test_trace_export_is_explicitly_unsigned_and_unverified(self):
        candidate = export_trace_candidate(
            envelope(), issued_at=1_010, subject="spiffe://smerc.example/agent/codex",
            model_provider="example", model_id="model-1", runtime_platform="software-only",
            runtime_measurement="sha256:" + SHA_A, data_class="internal",
            tool_transcript_sha256=SHA_B, tool_call_count=2,
        )
        self.assertEqual(candidate["claim"]["eat_profile"], TRACE_PROFILE)
        self.assertEqual(candidate["conformance_status"], "unverified")
        self.assertFalse(candidate["signed"])
        self.assertFalse(candidate["hardware_attested"])
        self.assertIn("not a conformant TRACE Trust Record", candidate["boundary"])
        with self.assertRaisesRegex(ValueError, "tool_transcript_sha256"):
            export_trace_candidate(
                envelope(), issued_at=1_010, subject="spiffe://smerc.example/agent/codex",
                model_provider="example", model_id="model-1", runtime_platform="software-only",
                runtime_measurement="sha256:" + SHA_A, data_class="internal",
                tool_transcript_sha256="not-a-digest", tool_call_count=2,
            )


if __name__ == "__main__":
    unittest.main()

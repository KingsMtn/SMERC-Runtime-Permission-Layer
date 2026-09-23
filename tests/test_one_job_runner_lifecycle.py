import hashlib
import unittest

from reference_engine.ephemeral_execution_envelope import create_envelope, transition_envelope
from reference_engine.one_job_runner_lifecycle import (
    OneJobLifecycleError, build_one_job_portable_evidence, run_one_job,
)
from reference_engine.portable_evidence import verify_portable_evidence


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def active_envelope():
    envelope = create_envelope(
        namespace="aws", run_id="job-001", base_ref="refs/heads/main",
        base_commit_sha=SHA_A, policy_bundle_sha256=SHA_B,
        execution_target_sha256=SHA_C, permit_id="permit-001",
        replay_id="replay-001", now=1000, ttl_seconds=600,
    )
    return transition_envelope(envelope, "ACTIVE", now=1010)


def execution(tool="aws.list_regions"):
    return {"status": "SUCCEEDED", "tool": tool, "transcript_sha256": SHA_A, "failure_contained": True}


def cleanup(**changes):
    value = {"status": "SUCCEEDED", "runner_destroyed": True, "credentials_revoked": True, "ephemeral_ref_deleted": True}
    value.update(changes)
    return value


def portable_payload():
    digest = lambda text: hashlib.sha256(text.encode()).hexdigest()
    return {
        "record_id": "one-job-001", "observed_at": "2026-09-23T00:00:00Z",
        "workload": {"workload_id": "smerc-aws-mcp", "model_id": "not-observed", "model_digest": digest("not-observed")},
        "source_control": {"repository": "KingsMtn/SMERC-Runtime-Permission-Layer", "commit_sha": "a" * 40, "workflow": "one-job-runner", "ephemeral_ref": "refs/ephemeral/aws/job-001"},
        "runtime": {"platform": "aws", "account": "redacted", "region": "us-east-1", "principal": "SMERC-MCP-Pilot", "execution_boundary": "ephemeral-runner"},
        "policy": {"policy_id": "pilot-read-only", "policy_revision": "1", "policy_bundle_sha256": digest("policy"), "enforcement_mode": "ENFORCE"},
        "decision": {"admission": "ADMIT", "posture": "ALLOW", "explanation_code": "ONE_JOB_ONLY", "decision_id": "decision-001"},
        "tool_activity": {}, "containment": {},
        "data_handling": {"data_classes": ["cloud-metadata"], "redacted_fields": ["account", "authorization"], "secrets_persisted": False},
        "claim_boundary": "Software lifecycle evidence only; not hardware attestation or production certification.",
    }


class OneJobRunnerLifecycleTests(unittest.TestCase):
    def test_success_runs_once_and_requires_complete_cleanup(self):
        calls = []
        receipt = run_one_job(
            active_envelope(), now=1020, job_id="job-001", tool="aws.list_regions",
            execute=lambda: calls.append("execute") or execution(),
            cleanup=lambda: calls.append("cleanup") or cleanup(),
        )
        self.assertEqual(calls, ["execute", "cleanup"])
        self.assertEqual(receipt["operation_count"], 1)
        self.assertTrue(receipt["cleanup_verified"])

    def test_executor_failure_still_cleans_up_and_fails_closed(self):
        calls = []
        def fail():
            calls.append("execute")
            raise RuntimeError("transport failed")
        with self.assertRaises(OneJobLifecycleError) as caught:
            run_one_job(
                active_envelope(), now=1020, job_id="job-001", tool="aws.list_regions",
                execute=fail, cleanup=lambda: calls.append("cleanup") or cleanup(),
            )
        self.assertEqual(caught.exception.code, "execution_failed")
        self.assertTrue(caught.exception.receipt["cleanup_verified"])
        self.assertEqual(calls, ["execute", "cleanup"])

    def test_incomplete_cleanup_is_not_treated_as_success(self):
        with self.assertRaises(OneJobLifecycleError) as caught:
            run_one_job(
                active_envelope(), now=1020, job_id="job-001", tool="aws.list_regions",
                execute=lambda: execution(), cleanup=lambda: cleanup(credentials_revoked=False),
            )
        self.assertEqual(caught.exception.code, "cleanup_unverified")
        self.assertFalse(caught.exception.receipt["cleanup_verified"])

    def test_wrong_tool_and_inactive_envelope_fail_closed(self):
        with self.assertRaisesRegex(OneJobLifecycleError, "different tool"):
            run_one_job(
                active_envelope(), now=1020, job_id="job-001", tool="aws.list_regions",
                execute=lambda: execution("aws.delete_bucket"), cleanup=lambda: cleanup(),
            )
        with self.assertRaisesRegex(OneJobLifecycleError, "ACTIVE"):
            run_one_job(
                create_envelope(namespace="aws", run_id="job-002", base_ref="refs/heads/main", base_commit_sha=SHA_A, policy_bundle_sha256=SHA_B, execution_target_sha256=SHA_C, permit_id="permit-002", replay_id="replay-002", now=1000),
                now=1020, job_id="job-002", tool="aws.list_regions",
                execute=lambda: execution(), cleanup=lambda: cleanup(),
            )

    def test_receipt_populates_portable_evidence(self):
        receipt = run_one_job(
            active_envelope(), now=1020, job_id="job-001", tool="aws.list_regions",
            execute=lambda: execution(), cleanup=lambda: cleanup(),
        )
        record = build_one_job_portable_evidence(receipt, portable_payload(), issuer="smerc-reference-engine")
        verified = verify_portable_evidence(record)
        self.assertEqual(verified["status"], "HASH_VERIFIED")
        self.assertTrue(verified["cleanup_verified"])
        self.assertEqual(record["tool_activity"]["call_count"], 1)


if __name__ == "__main__":
    unittest.main()

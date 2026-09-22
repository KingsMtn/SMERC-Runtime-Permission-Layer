import os
import shutil
import subprocess
import unittest
from pathlib import Path
from uuid import uuid4

from integrations.ephemeral_git.ephemeral_git_adapter import (
    EphemeralGitAdapter,
    EphemeralGitAdapterError,
)
from reference_engine.ephemeral_execution_envelope import create_envelope


TARGET_SHA = "c" * 64


class EphemeralGitAdapterTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2] / ".runtime" / "ephemeral-git-tests" / uuid4().hex
        self.repo = self.root / "repo"
        self.manifests = self.root / "manifests"
        self.repo.mkdir(parents=True)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "SMERC Test")
        self.git("config", "user.email", "smerc-test@example.invalid")
        (self.repo / "README.md").write_text("base\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "base")
        self.base_oid = self.git("rev-parse", "HEAD")
        self.adapter = EphemeralGitAdapter(self.repo, self.manifests)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args], text=True, capture_output=True,
            check=False, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        if result.returncode:
            self.fail(result.stderr)
        return result.stdout.strip()

    def envelope(self, *, run_id="run-001", now=1_000):
        return create_envelope(
            namespace="codex", run_id=run_id, base_ref="refs/heads/main",
            base_commit_sha=self.base_oid, policy_bundle_sha256="b" * 64,
            execution_target_sha256=TARGET_SHA, permit_id="permit-001",
            replay_id="replay-001", now=now, ttl_seconds=600,
        )

    def advance_ephemeral_ref(self, ref):
        tree = self.git("rev-parse", f"{self.base_oid}^{{tree}}")
        commit = self.git("commit-tree", tree, "-p", self.base_oid, "-m", "agent result")
        self.git("update-ref", ref, commit, self.base_oid)
        return commit

    def test_create_seal_and_atomic_promote(self):
        active = self.adapter.create(self.envelope(), now=1_010)
        self.assertEqual(active["state"], "ACTIVE")
        self.assertEqual(self.git("rev-parse", active["ephemeral_ref"]), self.base_oid)
        sealed_oid = self.advance_ephemeral_ref(active["ephemeral_ref"])
        sealed = self.adapter.seal(active, now=1_020)
        result = self.adapter.promote(
            sealed, now=1_030, expected_durable_oid=None,
            evidence={
                "tests_passed": True,
                "review_approved": True,
                "policy_rechecked": True,
                "isolation_verified": True,
                "approved_target_sha256": TARGET_SHA,
                "sealed_commit_sha": sealed_oid,
                "durable_ref": "refs/heads/reviewed/run-001",
            },
        )
        self.assertEqual(result["state"], "PROMOTED")
        self.assertEqual(self.git("rev-parse", "refs/heads/reviewed/run-001"), sealed_oid)
        missing = subprocess.run(
            ["git", "-C", str(self.repo), "show-ref", "--verify", active["ephemeral_ref"]],
            capture_output=True, check=False,
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertTrue(Path(result["manifest_path"]).is_file())

    def test_create_fails_if_base_ref_drifted(self):
        (self.repo / "README.md").write_text("drift\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "drift")
        with self.assertRaisesRegex(EphemeralGitAdapterError, "base ref no longer resolves"):
            self.adapter.create(self.envelope(), now=1_010)

    def test_promote_fails_if_ephemeral_ref_changed_after_seal(self):
        active = self.adapter.create(self.envelope(), now=1_010)
        sealed_oid = self.advance_ephemeral_ref(active["ephemeral_ref"])
        sealed = self.adapter.seal(active, now=1_020)
        tree = self.git("rev-parse", f"{sealed_oid}^{{tree}}")
        changed_oid = self.git("commit-tree", tree, "-p", sealed_oid, "-m", "changed")
        self.git("update-ref", active["ephemeral_ref"], changed_oid, sealed_oid)
        with self.assertRaisesRegex(EphemeralGitAdapterError, "changed after sealing"):
            self.adapter.promote(
                sealed, now=1_030, expected_durable_oid=None,
                evidence={
                    "tests_passed": True, "review_approved": True,
                    "policy_rechecked": True, "isolation_verified": True,
                    "approved_target_sha256": TARGET_SHA, "sealed_commit_sha": sealed_oid,
                    "durable_ref": "refs/heads/reviewed/run-001",
                },
            )
        self.assertFalse(self.manifests.exists())

    def test_promotion_cannot_target_main_outside_allowlist(self):
        active = self.adapter.create(self.envelope(), now=1_010)
        sealed_oid = self.advance_ephemeral_ref(active["ephemeral_ref"])
        sealed = self.adapter.seal(active, now=1_020)
        with self.assertRaisesRegex(EphemeralGitAdapterError, "outside the configured allowlist"):
            self.adapter.promote(
                sealed, now=1_030, expected_durable_oid=self.base_oid,
                evidence={
                    "tests_passed": True, "review_approved": True,
                    "policy_rechecked": True, "isolation_verified": True,
                    "approved_target_sha256": TARGET_SHA, "sealed_commit_sha": sealed_oid,
                    "durable_ref": "refs/heads/main",
                },
            )
        self.assertEqual(self.git("rev-parse", "refs/heads/main"), self.base_oid)
        self.assertEqual(self.git("rev-parse", active["ephemeral_ref"]), sealed_oid)

    def test_discard_deletes_ref_and_retains_terminal_manifest(self):
        active = self.adapter.create(self.envelope(), now=1_010)
        result = self.adapter.discard(active, now=1_020, reason="review rejected")
        self.assertEqual(result["state"], "DISCARDED")
        self.assertEqual(result["envelope"]["terminal_reason"], "review rejected")
        self.assertTrue(Path(result["manifest_path"]).is_file())

    def test_promotion_compare_and_swap_preserves_both_refs_on_conflict(self):
        active = self.adapter.create(self.envelope(), now=1_010)
        sealed_oid = self.advance_ephemeral_ref(active["ephemeral_ref"])
        sealed = self.adapter.seal(active, now=1_020)
        self.git("branch", "reviewed/run-001", self.base_oid)
        with self.assertRaises(EphemeralGitAdapterError):
            self.adapter.promote(
                sealed, now=1_030, expected_durable_oid="d" * len(self.base_oid),
                evidence={
                    "tests_passed": True, "review_approved": True,
                    "policy_rechecked": True, "isolation_verified": True,
                    "approved_target_sha256": TARGET_SHA, "sealed_commit_sha": sealed_oid,
                    "durable_ref": "refs/heads/reviewed/run-001",
                },
            )
        self.assertEqual(self.git("rev-parse", active["ephemeral_ref"]), sealed_oid)
        self.assertEqual(self.git("rev-parse", "refs/heads/reviewed/run-001"), self.base_oid)


if __name__ == "__main__":
    unittest.main()

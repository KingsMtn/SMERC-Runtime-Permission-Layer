import os
import shutil
import subprocess
import unittest
from pathlib import Path
from uuid import uuid4

from integrations.github_ephemeral.github_remote_adapter import (
    GitHubRemoteEvidenceError, GitHubRemoteTransport, build_github_admission_evidence,
)
from reference_engine.ephemeral_execution_envelope import create_envelope, transition_envelope


class GitHubRemoteEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2] / ".runtime" / "github-remote-tests" / uuid4().hex
        self.repo = self.root / "repo"
        self.remote = self.root / "remote.git"
        self.repo.mkdir(parents=True)
        self.run_cmd("git", "init", "--bare", str(self.remote))
        self.git("init", "-b", "main")
        self.git("config", "user.name", "SMERC Test")
        self.git("config", "user.email", "smerc-test@example.invalid")
        self.git("remote", "add", "origin", str(self.remote))
        (self.repo / "a.txt").write_text("base\n", encoding="utf-8")
        self.git("add", "a.txt")
        self.git("commit", "-m", "base")
        self.base = self.git("rev-parse", "HEAD")
        self.envelope = create_envelope(
            namespace="codex", run_id="remote-001", base_ref="refs/heads/main",
            base_commit_sha=self.base, policy_bundle_sha256="b" * 64,
            execution_target_sha256="c" * 64, permit_id="permit-001",
            replay_id="replay-001", now=1000, ttl_seconds=600,
        )
        self.git("update-ref", self.envelope["ephemeral_ref"], self.base)
        active = transition_envelope(self.envelope, "ACTIVE", now=1010)
        self.sealed = transition_envelope(active, "SEALED", now=1020, evidence={"sealed_commit_sha": self.base})
        self.transport = GitHubRemoteTransport(self.repo)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_cmd(self, *args):
        result = subprocess.run(args, text=True, capture_output=True, check=False, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
        if result.returncode:
            self.fail(result.stderr)
        return result.stdout.strip()

    def git(self, *args):
        return self.run_cmd("git", "-C", str(self.repo), *args)

    def test_publish_reads_back_exact_commit_and_cleanup_is_leased(self):
        evidence = self.transport.publish(self.sealed)
        self.assertEqual(evidence["sealed_commit_sha"], self.base)
        self.assertTrue(evidence["transport_verified"])
        self.transport.cleanup(evidence)
        self.assertEqual(self.git("ls-remote", "--refs", "origin", evidence["remote_ref"]), "")

    def test_post_seal_local_ref_change_cannot_publish(self):
        self.transport.publish(self.sealed)
        tree = self.git("rev-parse", f"{self.base}^{{tree}}")
        changed = self.git("commit-tree", tree, "-p", self.base, "-m", "changed after seal")
        self.git("update-ref", self.envelope["ephemeral_ref"], changed, self.base)
        with self.assertRaisesRegex(GitHubRemoteEvidenceError, "changed after sealing"):
            self.transport.publish(self.sealed)

    def test_admission_requires_bound_transport_active_ruleset_and_green_checks(self):
        transport = self.transport.publish(self.sealed)
        admitted = build_github_admission_evidence(
            self.sealed, transport, repository="KingsMtn/SMERC-Runtime-Permission-Layer",
            rulesets=[{"id": 7, "target": "branch", "enforcement": "active", "applies_to_ref": True}],
            check_runs=[{"name": "unittest", "status": "completed", "conclusion": "success"}],
            required_checks=["unittest"],
        )
        self.assertTrue(admitted["admitted"])
        self.assertIn("not a GitHub-signed attestation", admitted["authenticity_boundary"])

    def test_admission_fails_closed_without_ruleset_or_successful_check(self):
        transport = self.transport.publish(self.sealed)
        with self.assertRaisesRegex(GitHubRemoteEvidenceError, "no active branch ruleset"):
            build_github_admission_evidence(
                self.sealed, transport, repository="KingsMtn/repo", rulesets=[],
                check_runs=[], required_checks=["unittest"],
            )
        with self.assertRaisesRegex(GitHubRemoteEvidenceError, "required checks"):
            build_github_admission_evidence(
                self.sealed, transport, repository="KingsMtn/repo",
                rulesets=[{"id": 7, "target": "branch", "enforcement": "active", "applies_to_ref": True}],
                check_runs=[{"name": "unittest", "status": "completed", "conclusion": "failure"}],
                required_checks=["unittest"],
            )


if __name__ == "__main__":
    unittest.main()

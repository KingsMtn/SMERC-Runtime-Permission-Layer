from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

from reference_engine.ephemeral_execution_envelope import canonical_digest, verify_envelope


VERSION = "smerc.github-remote-evidence.v1"
REMOTE_PREFIX = "refs/heads/smerc-ephemeral/"


class GitHubRemoteEvidenceError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _oid(value: Any, path: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
        raise GitHubRemoteEvidenceError("invalid_oid", f"{path} must be a Git object ID")
    return value


def remote_ref_for(envelope: Mapping[str, Any]) -> str:
    verified = verify_envelope(envelope, allow_expired=True)
    return f"{REMOTE_PREFIX}{verified['namespace']}/{verified['run_id']}"


class GitHubRemoteTransport:
    def __init__(self, repository: Path | str, *, remote: str = "origin") -> None:
        self.repository = Path(repository).resolve()
        if not self.repository.is_dir() or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", remote):
            raise GitHubRemoteEvidenceError("invalid_transport", "repository or remote is invalid")
        self.remote = remote
        self._git("rev-parse", "--git-dir")

    def publish(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        verified = verify_envelope(envelope)
        if verified["state"] != "SEALED":
            raise GitHubRemoteEvidenceError("invalid_state", "remote publication requires a SEALED envelope")
        # The sealed transition binds its evidence digest; the adapter also reads the exact commit from the ref.
        local_oid = self._git("rev-parse", "--verify", "--end-of-options", f"{verified['ephemeral_ref']}^{{commit}}")
        _oid(local_oid, "local ephemeral ref")
        if local_oid != verified["sealed_commit_sha"]:
            raise GitHubRemoteEvidenceError("sealed_ref_mismatch", "local ephemeral ref changed after sealing")
        remote_ref = remote_ref_for(verified)
        zero = "0" * len(local_oid)
        self._git(
            "push", "--porcelain", f"--force-with-lease={remote_ref}:{zero}",
            self.remote, f"{local_oid}:{remote_ref}",
        )
        observed = self._remote_oid(remote_ref)
        if observed != local_oid:
            raise GitHubRemoteEvidenceError("remote_ref_mismatch", "remote did not retain the exact sealed commit")
        material = {
            "version": VERSION,
            "envelope_id": verified["envelope_id"],
            "envelope_sha256": verified["envelope_sha256"],
            "remote": self.remote,
            "remote_ref": remote_ref,
            "sealed_commit_sha": local_oid,
            "observed_remote_sha": observed,
            "transport_verified": True,
        }
        return {**material, "evidence_sha256": canonical_digest(material)}

    def cleanup(self, evidence: Mapping[str, Any]) -> None:
        verified = verify_remote_transport_evidence(evidence)
        remote_ref = verified["remote_ref"]
        expected = verified["observed_remote_sha"]
        self._git(
            "push", "--porcelain", f"--force-with-lease={remote_ref}:{expected}",
            self.remote, f":{remote_ref}",
        )
        if self._remote_oid(remote_ref, missing_ok=True) is not None:
            raise GitHubRemoteEvidenceError("remote_cleanup_failed", "remote ephemeral ref still exists")

    def _remote_oid(self, ref: str, *, missing_ok: bool = False) -> str | None:
        output = self._git("ls-remote", "--refs", self.remote, ref)
        if not output:
            if missing_ok:
                return None
            raise GitHubRemoteEvidenceError("remote_ref_missing", "remote ephemeral ref was not found")
        lines = output.splitlines()
        if len(lines) != 1:
            raise GitHubRemoteEvidenceError("ambiguous_remote_ref", "remote ref lookup was ambiguous")
        oid, observed_ref = lines[0].split("\t", 1)
        if observed_ref != ref:
            raise GitHubRemoteEvidenceError("remote_ref_mismatch", "remote returned an unexpected ref")
        return _oid(oid, "remote object ID")

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repository), *args], text=True, capture_output=True,
            check=False, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}, timeout=60,
        )
        if result.returncode:
            raise GitHubRemoteEvidenceError("git_command_failed", result.stderr.strip()[:512])
        return result.stdout.strip()


def verify_remote_transport_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    fields = {
        "version", "envelope_id", "envelope_sha256", "remote", "remote_ref",
        "sealed_commit_sha", "observed_remote_sha", "transport_verified", "evidence_sha256",
    }
    if not isinstance(evidence, Mapping) or set(evidence) != fields or evidence.get("version") != VERSION:
        raise GitHubRemoteEvidenceError("invalid_evidence", "remote evidence fields are invalid")
    candidate = dict(evidence)
    digest = candidate.pop("evidence_sha256")
    if digest != canonical_digest(candidate):
        raise GitHubRemoteEvidenceError("invalid_evidence", "remote evidence digest mismatch")
    if not str(candidate["remote_ref"]).startswith(REMOTE_PREFIX):
        raise GitHubRemoteEvidenceError("invalid_evidence", "remote ref is outside the ephemeral namespace")
    if candidate["transport_verified"] is not True:
        raise GitHubRemoteEvidenceError("invalid_evidence", "transport is not verified")
    if _oid(candidate["sealed_commit_sha"], "sealed_commit_sha") != _oid(
        candidate["observed_remote_sha"], "observed_remote_sha"
    ):
        raise GitHubRemoteEvidenceError("invalid_evidence", "sealed and observed commits differ")
    return dict(evidence)


def build_github_admission_evidence(
    envelope: Mapping[str, Any], transport_evidence: Mapping[str, Any], *,
    repository: str, rulesets: Sequence[Mapping[str, Any]],
    check_runs: Sequence[Mapping[str, Any]], required_checks: Sequence[str],
) -> dict[str, Any]:
    verified = verify_envelope(envelope, allow_expired=True)
    if verified["state"] != "SEALED":
        raise GitHubRemoteEvidenceError("invalid_state", "GitHub admission evidence requires SEALED state")
    transport = verify_remote_transport_evidence(transport_evidence)
    if transport["envelope_id"] != verified["envelope_id"] or transport["envelope_sha256"] != verified["envelope_sha256"]:
        raise GitHubRemoteEvidenceError("binding_mismatch", "transport evidence is not bound to the envelope")
    active_rules = [
        item for item in rulesets
        if item.get("enforcement") == "active" and item.get("target") == "branch"
        and item.get("applies_to_ref") is True
    ]
    if not active_rules:
        raise GitHubRemoteEvidenceError("ruleset_unverified", "no active branch ruleset was proven for the remote ref")
    observed = {
        item.get("name"): item.get("conclusion")
        for item in check_runs if item.get("status") == "completed"
    }
    missing = sorted(name for name in required_checks if observed.get(name) != "success")
    if missing:
        raise GitHubRemoteEvidenceError("checks_incomplete", f"required checks are not successful: {missing}")
    material = {
        "version": "smerc.github-admission-evidence.v1",
        "repository": repository,
        "envelope_id": verified["envelope_id"],
        "envelope_sha256": verified["envelope_sha256"],
        "remote_ref": transport["remote_ref"],
        "sealed_commit_sha": transport["sealed_commit_sha"],
        "active_ruleset_ids": sorted(str(item["id"]) for item in active_rules),
        "required_checks": sorted(set(required_checks)),
        "check_conclusions": {name: observed[name] for name in sorted(set(required_checks))},
        "admitted": True,
        "authenticity_boundary": (
            "This evidence records authenticated GitHub API observations but is not a GitHub-signed attestation."
        ),
    }
    return {**material, "evidence_sha256": canonical_digest(material)}


def verify_github_admission_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    fields = {
        "version", "repository", "envelope_id", "envelope_sha256", "remote_ref",
        "sealed_commit_sha", "active_ruleset_ids", "required_checks", "check_conclusions",
        "admitted", "authenticity_boundary", "evidence_sha256",
    }
    if not isinstance(evidence, Mapping) or set(evidence) != fields:
        raise GitHubRemoteEvidenceError("invalid_admission_evidence", "GitHub admission evidence fields are invalid")
    candidate = dict(evidence)
    digest = candidate.pop("evidence_sha256")
    if candidate.get("version") != "smerc.github-admission-evidence.v1" or digest != canonical_digest(candidate):
        raise GitHubRemoteEvidenceError("invalid_admission_evidence", "GitHub admission evidence digest is invalid")
    if candidate.get("admitted") is not True or not candidate.get("active_ruleset_ids"):
        raise GitHubRemoteEvidenceError("invalid_admission_evidence", "GitHub admission was not established")
    required = candidate.get("required_checks")
    conclusions = candidate.get("check_conclusions")
    if not isinstance(required, list) or not isinstance(conclusions, Mapping):
        raise GitHubRemoteEvidenceError("invalid_admission_evidence", "GitHub check evidence is invalid")
    if any(conclusions.get(name) != "success" for name in required):
        raise GitHubRemoteEvidenceError("invalid_admission_evidence", "GitHub required checks are not successful")
    _oid(candidate.get("sealed_commit_sha"), "sealed_commit_sha")
    if not str(candidate.get("remote_ref", "")).startswith(REMOTE_PREFIX):
        raise GitHubRemoteEvidenceError("invalid_admission_evidence", "GitHub remote ref is outside the ephemeral namespace")
    return dict(evidence)

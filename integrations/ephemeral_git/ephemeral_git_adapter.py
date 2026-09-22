from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

from reference_engine.ephemeral_execution_envelope import transition_envelope, verify_envelope


MANIFEST_VERSION = "smerc.ephemeral-git-terminal-manifest.v1"
ZERO_OIDS = {"sha1": "0" * 40, "sha256": "0" * 64}


class EphemeralGitAdapterError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _ref(value: Any, path: str, *, ephemeral: bool | None = None) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"refs/(?:heads|ephemeral)/[A-Za-z0-9][A-Za-z0-9._/-]{0,240}", value
    ):
        raise EphemeralGitAdapterError("invalid_ref", f"{path} is not an allowed full Git ref")
    if any(part in {"", ".", ".."} or part.endswith(".lock") for part in value.split("/")):
        raise EphemeralGitAdapterError("invalid_ref", f"{path} contains an unsafe ref segment")
    is_ephemeral = value.startswith("refs/ephemeral/")
    if ephemeral is not None and is_ephemeral is not ephemeral:
        kind = "ephemeral" if ephemeral else "durable"
        raise EphemeralGitAdapterError("invalid_ref", f"{path} must be a {kind} ref")
    return value


class EphemeralGitAdapter:
    def __init__(
        self, repository: Path | str, manifest_directory: Path | str,
        *, durable_ref_prefixes: tuple[str, ...] = ("refs/heads/reviewed/",),
    ) -> None:
        self.repository = Path(repository).resolve()
        self.manifest_directory = Path(manifest_directory).resolve()
        if not durable_ref_prefixes:
            raise EphemeralGitAdapterError("invalid_ref_policy", "at least one durable ref prefix is required")
        for prefix in durable_ref_prefixes:
            if not isinstance(prefix, str) or not prefix.startswith("refs/heads/") or not prefix.endswith("/"):
                raise EphemeralGitAdapterError(
                    "invalid_ref_policy", "durable ref prefixes must be full refs/heads/.../ prefixes"
                )
        self.durable_ref_prefixes = durable_ref_prefixes
        if not self.repository.is_dir():
            raise EphemeralGitAdapterError("invalid_repository", "repository must be an existing directory")
        self._git("rev-parse", "--git-dir")

    def create(self, envelope: Mapping[str, Any], *, now: int) -> dict[str, Any]:
        verified = verify_envelope(envelope, now=now)
        if verified["state"] != "CREATED":
            raise EphemeralGitAdapterError("invalid_state", "create requires a CREATED envelope")
        ephemeral_ref = _ref(verified["ephemeral_ref"], "ephemeral_ref", ephemeral=True)
        base_ref = _ref(verified["base_ref"], "base_ref", ephemeral=False)
        base_oid = self._resolve(base_ref)
        if base_oid != verified["base_commit_sha"]:
            raise EphemeralGitAdapterError("base_mismatch", "base ref no longer resolves to the approved commit")
        zero = self._zero_oid()
        self._git("update-ref", "--create-reflog", ephemeral_ref, base_oid, zero)
        return transition_envelope(
            verified, "ACTIVE", now=now,
            evidence={"ephemeral_ref": ephemeral_ref, "base_commit_sha": base_oid},
        )

    def seal(self, envelope: Mapping[str, Any], *, now: int) -> dict[str, Any]:
        verified = verify_envelope(envelope, now=now)
        if verified["state"] != "ACTIVE":
            raise EphemeralGitAdapterError("invalid_state", "seal requires an ACTIVE envelope")
        ephemeral_ref = _ref(verified["ephemeral_ref"], "ephemeral_ref", ephemeral=True)
        sealed_oid = self._resolve(ephemeral_ref)
        ancestor = self._git_result("merge-base", "--is-ancestor", verified["base_commit_sha"], sealed_oid)
        if ancestor.returncode != 0:
            raise EphemeralGitAdapterError("history_escape", "sealed commit is not descended from the approved base")
        return transition_envelope(
            verified, "SEALED", now=now,
            evidence={"sealed_commit_sha": sealed_oid},
        )

    def promote(
        self, envelope: Mapping[str, Any], *, now: int,
        evidence: Mapping[str, Any], expected_durable_oid: str | None,
    ) -> dict[str, Any]:
        verified = verify_envelope(envelope, now=now)
        if verified["state"] != "SEALED":
            raise EphemeralGitAdapterError("invalid_state", "promote requires a SEALED envelope")
        promoted = transition_envelope(verified, "PROMOTED", now=now, evidence=evidence)
        ephemeral_ref = _ref(verified["ephemeral_ref"], "ephemeral_ref", ephemeral=True)
        durable_ref = _ref(evidence.get("durable_ref"), "promotion.durable_ref", ephemeral=False)
        if not any(durable_ref.startswith(prefix) for prefix in self.durable_ref_prefixes):
            raise EphemeralGitAdapterError(
                "durable_ref_not_allowed", "promotion durable ref is outside the configured allowlist"
            )
        sealed_oid = evidence["sealed_commit_sha"]
        if self._resolve(ephemeral_ref) != sealed_oid:
            raise EphemeralGitAdapterError("sealed_ref_mismatch", "ephemeral ref changed after sealing")
        expected = expected_durable_oid or self._zero_oid()
        self._validate_oid(expected, "expected_durable_oid", allow_zero=True)
        transaction = (
            f"update {durable_ref}\0{sealed_oid}\0{expected}\0"
            f"delete {ephemeral_ref}\0{sealed_oid}\0"
        )
        pending = self._write_pending_manifest(promoted)
        try:
            self._git("update-ref", "--stdin", "-z", input_text=transaction)
        except Exception:
            pending.unlink(missing_ok=True)
            raise
        return self._commit_manifest(pending, promoted)

    def discard(self, envelope: Mapping[str, Any], *, now: int, reason: str) -> dict[str, Any]:
        verified = verify_envelope(envelope, now=now, allow_expired=True)
        if verified["state"] not in {"CREATED", "ACTIVE", "SEALED"}:
            raise EphemeralGitAdapterError("invalid_state", "discard requires a non-terminal envelope")
        discarded = transition_envelope(verified, "DISCARDED", now=now, reason=reason)
        ephemeral_ref = _ref(verified["ephemeral_ref"], "ephemeral_ref", ephemeral=True)
        result = self._git_result("rev-parse", "--verify", "--end-of-options", f"{ephemeral_ref}^{{commit}}")
        pending = self._write_pending_manifest(discarded)
        try:
            if result.returncode == 0:
                self._git("update-ref", "-d", ephemeral_ref, result.stdout.strip())
        except Exception:
            pending.unlink(missing_ok=True)
            raise
        return self._commit_manifest(pending, discarded)

    def _write_pending_manifest(self, envelope: Mapping[str, Any]) -> Path:
        self.manifest_directory.mkdir(parents=True, exist_ok=True)
        pending = self.manifest_directory / f".{envelope['envelope_id']}.pending"
        payload = {
            "version": MANIFEST_VERSION,
            "envelope_id": envelope["envelope_id"],
            "terminal_state": envelope["state"],
            "envelope_sha256": envelope["envelope_sha256"],
            "envelope": dict(envelope),
        }
        pending.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return pending

    def _commit_manifest(self, pending: Path, envelope: Mapping[str, Any]) -> dict[str, Any]:
        destination = self.manifest_directory / f"{envelope['envelope_id']}.json"
        os.replace(pending, destination)
        return {
            "version": MANIFEST_VERSION,
            "state": envelope["state"],
            "envelope": dict(envelope),
            "manifest_path": str(destination),
        }

    def _resolve(self, ref: str) -> str:
        return self._git("rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")

    def _zero_oid(self) -> str:
        object_format = self._git("rev-parse", "--show-object-format")
        if object_format not in ZERO_OIDS:
            raise EphemeralGitAdapterError("unsupported_object_format", "unsupported Git object format")
        return ZERO_OIDS[object_format]

    @staticmethod
    def _validate_oid(value: Any, path: str, *, allow_zero: bool = False) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
            raise EphemeralGitAdapterError("invalid_oid", f"{path} must be a Git object ID")
        if not allow_zero and not int(value, 16):
            raise EphemeralGitAdapterError("invalid_oid", f"{path} cannot be the zero object ID")
        return value

    def _git(self, *args: str, input_text: str | None = None) -> str:
        result = self._git_result(*args, input_text=input_text)
        if result.returncode != 0:
            detail = (result.stderr or "Git command failed").strip()[:512]
            raise EphemeralGitAdapterError("git_command_failed", detail)
        return result.stdout.strip()

    def _git_result(self, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.repository), *args],
            input=input_text, text=True, capture_output=True, check=False,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}, timeout=30,
        )

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from reference_engine.control_evidence import (  # noqa: E402
    ControlEvidenceError,
    ControlEvidenceSigner,
    parse_control_evidence_signers,
)
from reference_engine.action_language import action_hash  # noqa: E402


EXECUTION_PLAN_VERSION = "smerc.execution-plan.v1"
EXECUTION_REPORT_VERSION = "smerc.execution-report.v1"
SPARTA_EXECUTION_EVIDENCE_VERSION = "smerc.sparta-execution-evidence.v1"
MAX_PLAN_BYTES = 128 * 1024
MAX_API_RESPONSE_BYTES = 1024 * 1024
MAX_ARGUMENTS = 128
MAX_ARGUMENT_LENGTH = 4096
MAX_CONTROLS = 64
DEFAULT_COMMAND_TIMEOUT = 900
INTERNAL_CONTROLS = frozenset({"retain_cancel_handle"})
EMPTY_OUTPUT_SHA256 = hashlib.sha256(b"").hexdigest()


class DeploymentAdapterError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class SameOriginRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        original = urlsplit(req.full_url)
        redirected = urlsplit(newurl)
        if (
            original.scheme.lower(), original.hostname, original.port
        ) != (
            redirected.scheme.lower(), redirected.hostname, redirected.port
        ):
            raise HTTPError(newurl, code, "Cross-origin API redirect refused.", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _identifier(value: Any, path: str, maximum: int = 128) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        rf"[A-Za-z0-9][A-Za-z0-9._:-]{{0,{maximum - 1}}}", value
    ):
        raise DeploymentAdapterError(
            "invalid_execution_plan", f"{path} must be a safe identifier of 1 to {maximum} characters."
        )
    return value


def _bounded_text(value: Any, path: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum or any(
        ord(character) < 32 for character in value
    ):
        raise DeploymentAdapterError(
            "invalid_execution_plan", f"{path} must be bounded printable text."
        )
    return value


def _positive_int(value: Any, path: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise DeploymentAdapterError(
            "invalid_execution_plan", f"{path} must be an integer from 1 through {maximum}."
        )
    return value


def _argv(value: Any, path: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or len(value) > MAX_ARGUMENTS:
        raise DeploymentAdapterError(
            "invalid_execution_plan", f"{path} must be a non-empty argument array."
        )
    if any(
        not isinstance(item, str)
        or not item
        or len(item) > MAX_ARGUMENT_LENGTH
        or "\x00" in item
        for item in value
    ):
        raise DeploymentAdapterError(
            "invalid_execution_plan", f"{path} contains an invalid argument."
        )
    return tuple(value)


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _route_report_digest(route_report: Mapping[str, Any]) -> str:
    material = {key: value for key, value in dict(route_report).items() if key != "signature"}
    return _canonical_digest(material)


def _sparta_execution_evidence(
    route_report: Mapping[str, Any],
    *,
    permit: Mapping[str, Any],
) -> Dict[str, Any]:
    if route_report.get("version") != "smerc.sparta-route.v1":
        raise DeploymentAdapterError("invalid_sparta_route", "SPARTa route report version is unsupported.")
    route_id = _identifier(route_report.get("route_id"), "sparta.route_id", 192)
    decision_replay_id = _identifier(route_report.get("decision_replay_id"), "sparta.decision_replay_id", 192)
    source_posture = _bounded_text(route_report.get("source_posture"), "sparta.source_posture", 32)
    route_state = _bounded_text(route_report.get("route_state"), "sparta.route_state", 64)
    executable = route_report.get("executable")
    if not isinstance(executable, bool):
        raise DeploymentAdapterError("invalid_sparta_route", "SPARTa route executable flag is invalid.")
    applied_controls = route_report.get("applied_controls")
    if not isinstance(applied_controls, list) or any(not isinstance(item, str) for item in applied_controls):
        raise DeploymentAdapterError("invalid_sparta_route", "SPARTa route controls are invalid.")
    required_controls = set(permit["required_controls"]) - INTERNAL_CONTROLS
    missing_controls = sorted(required_controls - set(applied_controls))
    checks = {
        "replay_id_matches": decision_replay_id == permit["replay_id"],
        "posture_matches": source_posture == permit["posture"],
        "route_is_executable": executable is True,
        "required_controls_declared_by_route": not missing_controls,
    }
    if not all(checks.values()):
        raise DeploymentAdapterError(
            "sparta_binding_mismatch",
            "SPARTa route does not bind to the permit replay, posture, executable state, or required controls.",
        )
    return {
        "version": SPARTA_EXECUTION_EVIDENCE_VERSION,
        "route_id": route_id,
        "route_report_digest": _route_report_digest(route_report),
        "decision_replay_id": decision_replay_id,
        "source_posture": source_posture,
        "route_state": route_state,
        "binding": {
            "valid": True,
            "checks": checks,
            "missing_required_controls": missing_controls,
        },
        "adapter_boundary": (
            "The GitHub deployment adapter verifies route-to-permit binding before execution; "
            "live GitHub environment protections and target-platform restoration remain external evidence."
        ),
    }


@dataclass(frozen=True)
class CommandSpec:
    argv: tuple[str, ...]
    timeout_seconds: int
    mechanism: str


@dataclass(frozen=True)
class RollbackSpec:
    command: CommandSpec
    on_failure: bool
    on_timeout: bool
    on_cancel: bool


@dataclass(frozen=True)
class ExecutionPlan:
    execution_id: str
    audience: str
    working_directory: str
    command: CommandSpec
    cancel_grace_seconds: int
    environment_allowlist: tuple[str, ...]
    controls: Mapping[str, CommandSpec]
    rollback: Optional[RollbackSpec]
    source: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, value: Any) -> "ExecutionPlan":
        fields = {
            "version", "execution_id", "audience", "working_directory", "command",
            "timeout_seconds", "cancel_grace_seconds", "environment_allowlist",
            "controls", "rollback",
        }
        if not isinstance(value, dict) or set(value) != fields:
            raise DeploymentAdapterError(
                "invalid_execution_plan", "Execution-plan fields are incomplete or unknown."
            )
        if value["version"] != EXECUTION_PLAN_VERSION:
            raise DeploymentAdapterError("invalid_execution_plan", "Execution-plan version is unsupported.")
        working_directory = value["working_directory"]
        if (
            not isinstance(working_directory, str)
            or not working_directory
            or len(working_directory) > 512
            or Path(working_directory).is_absolute()
            or ".." in Path(working_directory).parts
        ):
            raise DeploymentAdapterError(
                "invalid_execution_plan", "working_directory must be a bounded relative path."
            )
        environment_allowlist = value["environment_allowlist"]
        if (
            not isinstance(environment_allowlist, list)
            or len(environment_allowlist) > 64
            or len(environment_allowlist) != len(set(environment_allowlist))
            or any(not isinstance(item, str) or not re.fullmatch(r"[A-Z_][A-Z0-9_]{0,127}", item) for item in environment_allowlist)
        ):
            raise DeploymentAdapterError(
                "invalid_execution_plan", "environment_allowlist must contain unique environment names."
            )
        controls = value["controls"]
        if not isinstance(controls, dict) or len(controls) > MAX_CONTROLS:
            raise DeploymentAdapterError("invalid_execution_plan", "controls must be a bounded object.")
        parsed_controls: Dict[str, CommandSpec] = {}
        for control_id, item in controls.items():
            control_id = _identifier(control_id, "control ID")
            if control_id in INTERNAL_CONTROLS:
                raise DeploymentAdapterError(
                    "invalid_execution_plan",
                    f"Control {control_id} is implemented internally and cannot declare a command.",
                )
            parsed_controls[control_id] = cls._command_spec(item, f"controls.{control_id}", 300)
        rollback = value["rollback"]
        parsed_rollback = None
        if rollback is not None:
            rollback_fields = {"command", "timeout_seconds", "mechanism", "on_failure", "on_timeout", "on_cancel"}
            if not isinstance(rollback, dict) or set(rollback) != rollback_fields:
                raise DeploymentAdapterError("invalid_execution_plan", "rollback fields are incomplete or unknown.")
            for flag in ("on_failure", "on_timeout", "on_cancel"):
                if not isinstance(rollback[flag], bool):
                    raise DeploymentAdapterError("invalid_execution_plan", f"rollback.{flag} must be boolean.")
            parsed_rollback = RollbackSpec(
                command=cls._command_spec(
                    {key: rollback[key] for key in ("command", "timeout_seconds", "mechanism")},
                    "rollback",
                    900,
                ),
                on_failure=rollback["on_failure"],
                on_timeout=rollback["on_timeout"],
                on_cancel=rollback["on_cancel"],
            )
        return cls(
            execution_id=_identifier(value["execution_id"], "execution_id", 192),
            audience=_identifier(value["audience"], "audience"),
            working_directory=working_directory,
            command=CommandSpec(
                argv=_argv(value["command"], "command"),
                timeout_seconds=_positive_int(value["timeout_seconds"], "timeout_seconds", 3600),
                mechanism="managed_subprocess",
            ),
            cancel_grace_seconds=_positive_int(value["cancel_grace_seconds"], "cancel_grace_seconds", 60),
            environment_allowlist=tuple(sorted(environment_allowlist)),
            controls=parsed_controls,
            rollback=parsed_rollback,
            source=dict(value),
        )

    @staticmethod
    def _command_spec(value: Any, path: str, maximum_timeout: int) -> CommandSpec:
        fields = {"command", "timeout_seconds", "mechanism"}
        if not isinstance(value, dict) or set(value) != fields:
            raise DeploymentAdapterError("invalid_execution_plan", f"{path} fields are incomplete or unknown.")
        return CommandSpec(
            argv=_argv(value["command"], f"{path}.command"),
            timeout_seconds=_positive_int(value["timeout_seconds"], f"{path}.timeout_seconds", maximum_timeout),
            mechanism=_bounded_text(value["mechanism"], f"{path}.mechanism", 128),
        )

    def resolve_working_directory(self, workspace: Path) -> Path:
        root = workspace.resolve()
        candidate = (root / self.working_directory).resolve()
        if candidate != root and root not in candidate.parents:
            raise DeploymentAdapterError("working_directory_escape", "working_directory escapes the workspace.")
        if not candidate.is_dir():
            raise DeploymentAdapterError("working_directory_missing", "working_directory does not exist.")
        return candidate


@dataclass
class CommandResult:
    status: str
    exit_code: Optional[int]
    started_at: str
    finished_at: str
    duration_ms: int
    output_sha256: str
    output_bytes: int

    def public(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "output_sha256": self.output_sha256,
            "output_bytes": self.output_bytes,
        }


class _OutputDigest:
    def __init__(self, stream: Any) -> None:
        self.stream = stream
        self.digest = hashlib.sha256()
        self.count = 0

    def read(self) -> None:
        while True:
            chunk = self.stream.read(64 * 1024)
            if not chunk:
                return
            self.digest.update(chunk)
            self.count += len(chunk)


class ProcessSupervisor:
    def __init__(self, cancel_event: Optional[threading.Event] = None) -> None:
        self.cancel_event = cancel_event or threading.Event()

    def run(
        self,
        command: CommandSpec,
        *,
        cwd: Path,
        environment: Mapping[str, str],
        grace_seconds: int,
        honor_cancel: bool = True,
    ) -> CommandResult:
        started_wall = datetime.now(timezone.utc)
        started = time.monotonic()
        creationflags = 0
        kwargs: Dict[str, Any] = {}
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            kwargs["start_new_session"] = True
        try:
            process = subprocess.Popen(
                list(command.argv),
                cwd=str(cwd),
                env=dict(environment),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False,
                creationflags=creationflags,
                **kwargs,
            )
        except OSError:
            finished_wall = datetime.now(timezone.utc)
            return CommandResult(
                status="start_failed",
                exit_code=None,
                started_at=started_wall.isoformat(),
                finished_at=finished_wall.isoformat(),
                duration_ms=max(0, round((time.monotonic() - started) * 1000)),
                output_sha256=EMPTY_OUTPUT_SHA256,
                output_bytes=0,
            )
        assert process.stdout is not None
        output = _OutputDigest(process.stdout)
        reader = threading.Thread(target=output.read, daemon=True)
        reader.start()
        deadline = started + command.timeout_seconds
        status = "running"
        while process.poll() is None:
            if honor_cancel and self.cancel_event.is_set():
                status = "cancelled"
                self._stop(process, grace_seconds)
                break
            if time.monotonic() >= deadline:
                status = "timed_out"
                self._stop(process, grace_seconds)
                break
            time.sleep(0.05)
        exit_code = process.wait()
        reader.join(timeout=5)
        if reader.is_alive():
            process.stdout.close()
            reader.join(timeout=1)
        else:
            process.stdout.close()
        if status == "running":
            status = "succeeded" if exit_code == 0 else "failed"
        finished_wall = datetime.now(timezone.utc)
        return CommandResult(
            status=status,
            exit_code=exit_code,
            started_at=started_wall.isoformat(),
            finished_at=finished_wall.isoformat(),
            duration_ms=max(0, round((time.monotonic() - started) * 1000)),
            output_sha256=output.digest.hexdigest(),
            output_bytes=output.count,
        )

    @staticmethod
    def _stop(process: subprocess.Popen[Any], grace_seconds: int) -> None:
        if process.poll() is not None:
            return
        try:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            process.wait(timeout=grace_seconds)
        except (OSError, subprocess.TimeoutExpired):
            if process.poll() is None:
                try:
                    if os.name != "nt":
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                except OSError:
                    pass


def _load_json(path: Path, *, maximum: int, label: str) -> Dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise DeploymentAdapterError(f"{label}_unavailable", f"{label} could not be read.") from exc
    if not raw or len(raw) > maximum:
        raise DeploymentAdapterError(f"invalid_{label}", f"{label} is empty or too large.")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeploymentAdapterError(f"invalid_{label}", f"{label} must be valid JSON.") from exc
    if not isinstance(value, dict):
        raise DeploymentAdapterError(f"invalid_{label}", f"{label} must be a JSON object.")
    return value


def _decode_unverified_permit(token: str) -> Dict[str, Any]:
    if not isinstance(token, str) or len(token) > 16_384:
        raise DeploymentAdapterError("invalid_permit_file", "Permit token is missing or too large.")
    parts = token.split(".")
    if len(parts) != 3 or not re.fullmatch(r"[A-Za-z0-9_-]+", parts[1]):
        raise DeploymentAdapterError("invalid_permit_file", "Permit token is malformed.")
    try:
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeploymentAdapterError("invalid_permit_file", "Permit claims are malformed.") from exc
    return _validate_permit_payload(payload)


def _validate_permit_payload(payload: Any) -> Dict[str, Any]:
    required = {
        "version", "permit_id", "tenant_id", "audience", "action_hash", "replay_id",
        "posture", "authorization", "required_controls", "policy", "issued_at",
        "not_before", "expires_at", "max_uses",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        raise DeploymentAdapterError("invalid_permit_file", "Permit claims are incomplete or unknown.")
    if payload["version"] != "smerc.permit.v1" or payload["max_uses"] != 1:
        raise DeploymentAdapterError("invalid_permit_file", "Permit contract is unsupported.")
    if not isinstance(payload["required_controls"], list) or len(payload["required_controls"]) > MAX_CONTROLS:
        raise DeploymentAdapterError("invalid_permit_file", "Permit controls are invalid.")
    for field in ("permit_id", "tenant_id", "audience", "replay_id"):
        _identifier(payload[field], f"permit.{field}", 192 if field in {"permit_id", "replay_id"} else 128)
    if not isinstance(payload["action_hash"], str) or not re.fullmatch(r"[0-9a-f]{64}", payload["action_hash"]):
        raise DeploymentAdapterError("invalid_permit_file", "Permit action hash is invalid.")
    controls = [_identifier(item, "permit.required_controls") for item in payload["required_controls"]]
    if len(controls) != len(set(controls)):
        raise DeploymentAdapterError("invalid_permit_file", "Permit controls cannot repeat.")
    payload["required_controls"] = sorted(controls)
    return payload


def _read_and_remove_permit(path: Path) -> str:
    try:
        token = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise DeploymentAdapterError("permit_file_unavailable", "Permit token file could not be read.") from exc
    cleanup_error: Optional[OSError] = None
    for attempt in range(6):
        try:
            path.unlink()
            cleanup_error = None
            break
        except FileNotFoundError:
            cleanup_error = None
            break
        except OSError as exc:
            cleanup_error = exc
            time.sleep(0.05 * (attempt + 1))
    if cleanup_error is not None or path.exists():
        raise DeploymentAdapterError("permit_file_cleanup_failed", "Permit token file could not be removed.")
    return token


def _api_endpoint(api_url: str, operation: str) -> str:
    parsed = urlsplit(api_url.strip())
    if not parsed.scheme or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise DeploymentAdapterError("invalid_api_url", "SMERC API URL is invalid.")
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme.lower() != "https" and not (parsed.scheme.lower() == "http" and loopback):
        raise DeploymentAdapterError("insecure_api_url", "SMERC execution API requires HTTPS outside loopback.")
    path = parsed.path.rstrip("/")
    for suffix in ("/v1/permits/prepare", "/v1/permits/consume"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
    return urlunsplit((parsed.scheme.lower(), parsed.netloc, f"{path}/v1/permits/{operation}", "", ""))


def _prepare_permit(
    *,
    api_url: str,
    executor_token: str,
    permit_token: str,
    action: Mapping[str, Any],
    audience: str,
    execution_id: str,
    timeout_seconds: int = 10,
) -> Dict[str, Any]:
    if not executor_token or "\n" in executor_token or "\r" in executor_token:
        raise DeploymentAdapterError("missing_executor_token", "SMERC_EXECUTOR_TOKEN is missing or invalid.")
    request = Request(
        _api_endpoint(api_url, "prepare"),
        data=json.dumps(
            {
                "permit_token": permit_token,
                "action": dict(action),
                "audience": audience,
                "execution_id": execution_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {executor_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SMERC-GitHub-Deployment-Adapter/1.0",
        },
        method="POST",
    )
    try:
        with build_opener(SameOriginRedirectHandler()).open(request, timeout=timeout_seconds) as response:
            raw = response.read(MAX_API_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise DeploymentAdapterError("permit_preparation_denied", f"SMERC permit preparation returned HTTP {exc.code}.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise DeploymentAdapterError("permit_service_unavailable", "SMERC permit service could not be reached.") from exc
    if len(raw) > MAX_API_RESPONSE_BYTES:
        raise DeploymentAdapterError("invalid_permit_response", "SMERC permit response is too large.")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeploymentAdapterError("invalid_permit_response", "SMERC permit response is invalid JSON.") from exc
    if not isinstance(result, dict) or result.get("valid") is not True:
        raise DeploymentAdapterError("invalid_permit_response", "SMERC did not authenticate the permit.")
    permit = _validate_permit_payload(result.get("permit"))
    preparation = result.get("preparation")
    if not isinstance(preparation, dict) or not isinstance(preparation.get("preparation_id"), str):
        raise DeploymentAdapterError("invalid_permit_response", "SMERC omitted the execution reservation.")
    preparation_id = preparation["preparation_id"]
    if not re.fullmatch(r"preparation_[0-9a-f]{32}", preparation_id):
        raise DeploymentAdapterError("invalid_permit_response", "SMERC returned an invalid execution reservation.")
    return {"permit": permit, "preparation_id": preparation_id}


def _consume_permit(
    *,
    api_url: str,
    executor_token: str,
    tenant_id: str,
    permit_token: str,
    action: Mapping[str, Any],
    audience: str,
    control_evidence_token: str,
    preparation_id: str,
    timeout_seconds: int = 10,
) -> Dict[str, Any]:
    if not executor_token or "\n" in executor_token or "\r" in executor_token:
        raise DeploymentAdapterError("missing_executor_token", "SMERC_EXECUTOR_TOKEN is missing or invalid.")
    payload = {
        "permit_token": permit_token,
        "action": dict(action),
        "audience": audience,
        "control_evidence_token": control_evidence_token,
        "preparation_id": preparation_id,
    }
    request = Request(
        _api_endpoint(api_url, "consume"),
        data=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {executor_token}",
            "X-SMERC-Tenant": tenant_id,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SMERC-GitHub-Deployment-Adapter/1.0",
        },
        method="POST",
    )
    try:
        with build_opener(SameOriginRedirectHandler()).open(request, timeout=timeout_seconds) as response:
            raw = response.read(MAX_API_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise DeploymentAdapterError("permit_consumption_denied", f"SMERC permit consumption returned HTTP {exc.code}.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise DeploymentAdapterError("permit_service_unavailable", "SMERC permit service could not be reached.") from exc
    if len(raw) > MAX_API_RESPONSE_BYTES:
        raise DeploymentAdapterError("invalid_permit_response", "SMERC permit response is too large.")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeploymentAdapterError("invalid_permit_response", "SMERC permit response is invalid JSON.") from exc
    if not isinstance(result, dict) or result.get("valid") is not True:
        raise DeploymentAdapterError("invalid_permit_response", "SMERC did not confirm permit consumption.")
    consumption = result.get("consumption")
    if not isinstance(consumption, dict) or not isinstance(consumption.get("consumed_at"), str):
        raise DeploymentAdapterError("invalid_permit_response", "SMERC omitted permit consumption attribution.")
    return result


def _execution_environment(allowlist: Iterable[str]) -> Dict[str, str]:
    always = {"PATH", "SYSTEMROOT", "WINDIR", "PATHEXT", "HOME", "TMP", "TEMP", "LANG", "LC_ALL"}
    selected = set(allowlist) | always
    return {key: value for key, value in os.environ.items() if key in selected}


def _control_result(control_id: str, command: CommandSpec, result: CommandResult, execution_id: str) -> Dict[str, Any]:
    run_id = re.sub(r"[^A-Za-z0-9._:-]", "-", os.environ.get("GITHUB_RUN_ID", "local"))[:64]
    reference = f"run:{run_id}:execution:{execution_id}:control:{control_id}:sha256:{result.output_sha256}"
    return {
        "control_id": control_id,
        "outcome": "applied",
        "mechanism": command.mechanism,
        "evidence_ref": reference[:256],
        "observed_at": int(time.time()),
    }


def _internal_cancel_result(execution_id: str) -> Dict[str, Any]:
    run_id = re.sub(r"[^A-Za-z0-9._:-]", "-", os.environ.get("GITHUB_RUN_ID", "local"))[:64]
    return {
        "control_id": "retain_cancel_handle",
        "outcome": "applied",
        "mechanism": "managed subprocess with terminate and kill escalation",
        "evidence_ref": f"run:{run_id}:execution:{execution_id}:cancel-handle"[:256],
        "observed_at": int(time.time()),
    }


def _should_rollback(status: str, rollback: RollbackSpec) -> bool:
    return (
        (status in {"failed", "start_failed"} and rollback.on_failure)
        or (status == "timed_out" and rollback.on_timeout)
        or (status == "cancelled" and rollback.on_cancel)
    )


def execute(
    *,
    action: Dict[str, Any],
    plan: ExecutionPlan,
    permit_token: str,
    api_url: str,
    executor_token: str,
    evidence_signer: ControlEvidenceSigner,
    workspace: Path,
    sparta_route_report: Optional[Mapping[str, Any]] = None,
    cancel_event: Optional[threading.Event] = None,
) -> Dict[str, Any]:
    prepared = _prepare_permit(
        api_url=api_url,
        executor_token=executor_token,
        permit_token=permit_token,
        action=action,
        audience=plan.audience,
        execution_id=plan.execution_id,
    )
    permit = prepared["permit"]
    if permit["tenant_id"] != evidence_signer.tenant_id or permit["audience"] != evidence_signer.audience:
        raise DeploymentAdapterError("adapter_binding_mismatch", "Permit is not assigned to this evidence adapter.")
    if permit["audience"] != plan.audience:
        raise DeploymentAdapterError("audience_mismatch", "Execution plan and permit audience differ.")
    if permit["action_hash"] != action_hash(action):
        raise DeploymentAdapterError("action_mismatch", "Execution action does not match the permit action hash.")
    sparta_evidence = None
    if sparta_route_report is not None:
        sparta_evidence = _sparta_execution_evidence(sparta_route_report, permit=permit)
    cwd = plan.resolve_working_directory(workspace)
    environment = _execution_environment(plan.environment_allowlist)
    supervisor = ProcessSupervisor(cancel_event)
    required_controls = permit["required_controls"]
    control_results = []
    control_report: Dict[str, Any] = {}
    for control_id in required_controls:
        if control_id == "retain_cancel_handle":
            control_results.append(_internal_cancel_result(plan.execution_id))
            control_report[control_id] = {"status": "applied", "mechanism": "managed_subprocess"}
            continue
        command = plan.controls.get(control_id)
        if command is None:
            raise DeploymentAdapterError(
                "unsupported_required_control", f"No native implementation exists for required control {control_id}."
            )
        result = supervisor.run(
            command,
            cwd=cwd,
            environment=environment,
            grace_seconds=plan.cancel_grace_seconds,
        )
        control_report[control_id] = result.public()
        if result.status != "succeeded":
            raise DeploymentAdapterError(
                "control_application_failed", f"Required control {control_id} did not complete successfully."
            )
        control_results.append(_control_result(control_id, command, result, plan.execution_id))
    try:
        evidence = evidence_signer.issue(permit, control_results, ttl_seconds=60)
    except ControlEvidenceError as exc:
        raise DeploymentAdapterError(exc.code, exc.message) from exc
    consumption = _consume_permit(
        api_url=api_url,
        executor_token=executor_token,
        tenant_id=permit["tenant_id"],
        permit_token=permit_token,
        action=action,
        audience=plan.audience,
        control_evidence_token=evidence["control_evidence_token"],
        preparation_id=prepared["preparation_id"],
    )
    execution = supervisor.run(
        plan.command,
        cwd=cwd,
        environment=environment,
        grace_seconds=plan.cancel_grace_seconds,
    )
    rollback_report: Optional[Dict[str, Any]] = None
    if plan.rollback is not None and _should_rollback(execution.status, plan.rollback):
        rollback_result = supervisor.run(
            plan.rollback.command,
            cwd=cwd,
            environment=environment,
            grace_seconds=plan.cancel_grace_seconds,
            honor_cancel=False,
        )
        rollback_report = rollback_result.public()
    outcome = "SUCCEEDED" if execution.status == "succeeded" else "FAILED"
    if execution.status == "cancelled":
        outcome = "CANCELLED"
    elif execution.status == "timed_out":
        outcome = "TIMED_OUT"
    return {
        "report_version": EXECUTION_REPORT_VERSION,
        "execution_id": plan.execution_id,
        "outcome": outcome,
        "tenant_id": permit["tenant_id"],
        "audience": plan.audience,
        "action_hash": permit["action_hash"],
        "plan_hash": _canonical_digest(plan.source),
        "permit": {
            "permit_id": permit["permit_id"],
            "replay_id": permit["replay_id"],
            "posture": permit["posture"],
            "authorization": permit["authorization"],
            "required_controls": required_controls,
            "expires_at": permit["expires_at"],
        },
        "control_evidence": {
            "evidence_id": evidence["control_evidence"]["evidence_id"],
            "adapter_id": evidence["control_evidence"]["adapter_id"],
            "controls": control_report,
        },
        "permit_consumption": {
            "valid": True,
            "preparation_id": prepared["preparation_id"],
            "consumed_at": consumption["consumption"]["consumed_at"],
            "control_evidence_mode": consumption.get("control_evidence", {}).get("mode"),
        },
        "sparta": sparta_evidence,
        "execution": execution.public(),
        "rollback": rollback_report,
        "environment_names": sorted(key for key in environment if key in plan.environment_allowlist),
    }


def _write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    path.write_text(encoded, encoding="utf-8")


def _publish_github(report: Dict[str, Any], report_path: Path) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with Path(output).open("a", encoding="utf-8") as handle:
            handle.write(f"outcome={report['outcome']}\n")
            handle.write(f"execution-id={report['execution_id']}\n")
            handle.write(f"rollback-status={(report.get('rollback') or {}).get('status', 'not_run')}\n")
            handle.write(f"report-path={report_path}\n")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        lines = [
            "# SMERC Deployment Execution",
            "",
            f"- Execution: `{report['execution_id']}`",
            f"- Outcome: `{report['outcome']}`",
        ]
        if "permit" in report:
            lines.extend(
                [
                    f"- Permit: `{report['permit']['permit_id']}`",
                    f"- Posture: `{report['permit']['posture']}`",
                    f"- Process status: `{report['execution']['status']}`",
                    f"- Rollback: `{(report.get('rollback') or {}).get('status', 'not_run')}`",
                ]
            )
        else:
            if report["outcome"] == "VALIDATED":
                lines.append("- Mode: `validate` (no action executed)")
            else:
                lines.append(f"- Error: `{report.get('error', 'adapter_error')}`")
        Path(summary).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute one SMERC-authorized deployment plan.")
    parser.add_argument("--action-file", required=True)
    parser.add_argument("--plan-file", required=True)
    parser.add_argument("--permit-token-file")
    parser.add_argument("--sparta-route-file")
    parser.add_argument("--api-url", default=os.environ.get("SMERC_API_URL", ""))
    parser.add_argument("--workspace", default=os.environ.get("GITHUB_WORKSPACE", "."))
    parser.add_argument("--report-file", default="smerc-execution-report.json")
    parser.add_argument("--mode", choices=["validate", "enforce"], default="validate")
    args = parser.parse_args()

    action = _load_json(Path(args.action_file), maximum=MAX_PLAN_BYTES, label="action")
    plan_source = _load_json(Path(args.plan_file), maximum=MAX_PLAN_BYTES, label="execution_plan")
    plan = ExecutionPlan.from_mapping(plan_source)
    sparta_route_report = None
    if args.sparta_route_file:
        sparta_route_report = _load_json(Path(args.sparta_route_file), maximum=MAX_PLAN_BYTES, label="sparta_route")
    workspace = Path(args.workspace)
    plan.resolve_working_directory(workspace)
    report_path = Path(args.report_file)
    if args.mode == "validate":
        report = {
            "report_version": EXECUTION_REPORT_VERSION,
            "execution_id": plan.execution_id,
            "outcome": "VALIDATED",
            "action_hash": action_hash(action),
            "plan_hash": _canonical_digest(plan.source),
            "sparta": None,
            "required_external_inputs": [
                "permit_token_file", "SMERC_EXECUTOR_TOKEN", "SMERC_CONTROL_EVIDENCE_KEY"
            ],
        }
        _write_report(report_path, report)
        _publish_github(report, report_path)
        print(json.dumps(report, indent=2))
        return 0
    if not args.permit_token_file:
        raise DeploymentAdapterError(
            "missing_permit_file", "--permit-token-file is required in enforce mode."
        )
    if not args.api_url:
        raise DeploymentAdapterError("missing_api_url", "SMERC API URL is required in enforce mode.")
    permit_token = _read_and_remove_permit(Path(args.permit_token_file))
    permit = _decode_unverified_permit(permit_token)
    try:
        signers = parse_control_evidence_signers(os.environ.get("SMERC_CONTROL_EVIDENCE_KEY", ""))
    except ValueError as exc:
        raise DeploymentAdapterError(
            "invalid_control_evidence_key", "SMERC_CONTROL_EVIDENCE_KEY configuration is invalid."
        ) from exc
    signer = signers.get((permit["tenant_id"], permit["audience"]))
    if signer is None:
        raise DeploymentAdapterError(
            "missing_control_evidence_key", "No control-evidence key matches the permit tenant and audience."
        )
    cancel_event = threading.Event()
    previous_handlers: Dict[int, Any] = {}

    def request_cancel(_signum: int, _frame: Any) -> None:
        cancel_event.set()

    for signum in (signal.SIGINT, signal.SIGTERM):
        previous_handlers[signum] = signal.signal(signum, request_cancel)
    try:
        try:
            report = execute(
                action=action,
                plan=plan,
                permit_token=permit_token,
                api_url=args.api_url,
                executor_token=os.environ.get("SMERC_EXECUTOR_TOKEN", ""),
                evidence_signer=signer,
                workspace=workspace,
                sparta_route_report=sparta_route_report,
                cancel_event=cancel_event,
            )
        except DeploymentAdapterError as exc:
            report = {
                "report_version": EXECUTION_REPORT_VERSION,
                "execution_id": plan.execution_id,
                "outcome": "BLOCKED",
                "error": exc.code,
                "message": exc.message,
                "action_hash": action_hash(action),
                "plan_hash": _canonical_digest(plan.source),
            }
    finally:
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
    _write_report(report_path, report)
    _publish_github(report, report_path)
    print(json.dumps(report, indent=2))
    if report["outcome"] == "BLOCKED":
        return 2
    if report["outcome"] != "SUCCEEDED":
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DeploymentAdapterError as exc:
        fallback = argparse.ArgumentParser(add_help=False)
        fallback.add_argument("--report-file", default="smerc-execution-report.json")
        known, _unknown = fallback.parse_known_args()
        report = {
            "report_version": EXECUTION_REPORT_VERSION,
            "execution_id": "unavailable",
            "outcome": "BLOCKED",
            "error": exc.code,
            "message": exc.message,
        }
        report_path = Path(known.report_file)
        try:
            _write_report(report_path, report)
            _publish_github(report, report_path)
        except OSError:
            pass
        print(json.dumps({"error": exc.code, "message": exc.message}), file=sys.stderr)
        raise SystemExit(2)

import base64
import json
import os
import shutil
import sys
import threading
import time
import unittest
from uuid import uuid4
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from integrations.github_deployment.deployment_adapter import (
    DeploymentAdapterError,
    ExecutionPlan,
    _decode_unverified_permit,
    _read_and_remove_permit,
    execute,
)
from reference_engine.action_language import action_hash
from reference_engine.control_evidence import ControlEvidenceSigner
from tests.test_authorization_permit import low_risk_action


def encode(value):
    return base64.urlsafe_b64encode(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).rstrip(b"=").decode("ascii")


def permit_token(action, controls=None):
    now = int(time.time())
    payload = {
        "version": "smerc.permit.v1",
        "permit_id": "permit_0123456789abcdef0123456789abcdef",
        "tenant_id": "alpha",
        "audience": "github-production-executor",
        "action_hash": action_hash(action),
        "replay_id": "replay_adapter_1001",
        "posture": "THROTTLE",
        "authorization": "constrain",
        "required_controls": sorted(controls or ["retain_cancel_handle"]),
        "policy": {
            "policy_id": "alpha-enforce",
            "policy_revision": "1.0.0",
            "policy_hash": "a" * 64,
            "mode": "ENFORCE",
            "evidence_ceiling": "LIMITED_ENFORCE",
        },
        "issued_at": now,
        "not_before": now,
        "expires_at": now + 300,
        "max_uses": 1,
    }
    return f"{encode({'alg': 'HS256', 'kid': 'test', 'typ': 'SMERC-PERMIT'})}.{encode(payload)}.signature"


def command(argv, timeout=10, mechanism="test mechanism"):
    return {"command": list(argv), "timeout_seconds": timeout, "mechanism": mechanism}


def plan_mapping(deploy_argv, *, controls=None, rollback=None, timeout=10, allowlist=None):
    return {
        "version": "smerc.execution-plan.v1",
        "execution_id": "deployment-1001",
        "audience": "github-production-executor",
        "working_directory": ".",
        "command": list(deploy_argv),
        "timeout_seconds": timeout,
        "cancel_grace_seconds": 1,
        "environment_allowlist": allowlist or [],
        "controls": controls or {},
        "rollback": rollback,
    }


class PermitHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        payload = json.loads(self.rfile.read(length))
        self.server.requests.append(
            {
                "path": self.path,
                "authorization": self.headers.get("authorization"),
                "tenant": self.headers.get("x-smerc-tenant"),
                "payload": payload,
            }
        )
        if self.path == "/v1/permits/prepare":
            if self.server.prepare_responses:
                status, response = self.server.prepare_responses.pop(0)
            else:
                status, response = 200, {
                    "valid": True,
                    "permit": _decode_unverified_permit(payload["permit_token"]),
                    "preparation": {
                        "preparation_id": "preparation_0123456789abcdef0123456789abcdef"
                    },
                }
        else:
            status, response = self.server.responses.pop(0)
        encoded = json.dumps(response).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        return


class PermitServer(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), PermitHandler)
        self.requests = []
        self.responses = []
        self.prepare_responses = []


class GitHubDeploymentAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = PermitServer()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        self.server.requests.clear()
        self.server.responses.clear()
        self.server.prepare_responses.clear()
        self.workspace = (
            Path(__file__).resolve().parents[2]
            / ".runtime"
            / "deployment-adapter-tests"
            / uuid4().hex
        )
        self.workspace.mkdir(parents=True)
        self.action = low_risk_action()
        self.signer = ControlEvidenceSigner(
            "alpha",
            "github-production-executor",
            "github-deployment-adapter",
            "adapter-key",
            b"e" * 32,
        )

    def tearDown(self):
        shutil.rmtree(self.workspace, ignore_errors=True)

    @property
    def api_url(self):
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    def run_execute(self, plan, token, *, cancel_event=None):
        return execute(
            action=self.action,
            plan=ExecutionPlan.from_mapping(plan),
            permit_token=token,
            api_url=self.api_url,
            executor_token="executor-secret-012345678901",
            evidence_signer=self.signer,
            workspace=self.workspace,
            cancel_event=cancel_event,
        )

    def allow_consumption(self):
        self.server.responses.append(
            (
                200,
                {
                    "valid": True,
                    "consumption": {"consumed_at": "2026-07-05T12:00:00+00:00"},
                    "control_evidence": {"mode": "signed_adapter_receipt"},
                },
            )
        )

    def test_success_applies_controls_consumes_once_and_omits_secrets_and_output(self):
        self.allow_consumption()
        secret = "deployment-secret-that-must-not-appear"
        os.environ["DEPLOYMENT_TEST_SECRET"] = secret
        controls = {
            "checkpoint_before_execution": command(
                [sys.executable, "-c", "print('checkpoint output')"],
                mechanism="git checkpoint assertion",
            )
        }
        plan = plan_mapping(
            [sys.executable, "-c", "import os; print(os.environ['DEPLOYMENT_TEST_SECRET'])"],
            controls=controls,
            allowlist=["DEPLOYMENT_TEST_SECRET"],
        )
        token = permit_token(
            self.action, ["retain_cancel_handle", "checkpoint_before_execution"]
        )
        report = self.run_execute(plan, token)
        self.assertEqual(report["outcome"], "SUCCEEDED")
        self.assertEqual(report["execution"]["status"], "succeeded")
        self.assertGreater(report["execution"]["output_bytes"], 0)
        self.assertEqual(report["rollback"], None)
        self.assertNotIn(secret, json.dumps(report))
        self.assertNotIn(token, json.dumps(report))
        self.assertEqual(len(self.server.requests), 2)
        self.assertEqual(self.server.requests[0]["path"], "/v1/permits/prepare")
        request = self.server.requests[1]
        self.assertEqual(request["path"], "/v1/permits/consume")
        self.assertEqual(request["authorization"], "Bearer executor-secret-012345678901")
        self.assertEqual(request["tenant"], "alpha")
        self.assertIn("control_evidence_token", request["payload"])

    def test_missing_or_failed_required_control_stops_before_consumption_and_deploy(self):
        marker = self.workspace / "deployed.txt"
        deploy = [
            sys.executable,
            "-c",
            "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('deployed')",
            str(marker),
        ]
        token = permit_token(self.action, ["checkpoint_before_execution"])
        with self.assertRaisesRegex(DeploymentAdapterError, "No native implementation"):
            self.run_execute(plan_mapping(deploy), token)
        self.assertFalse(marker.exists())
        self.assertEqual([item["path"] for item in self.server.requests], ["/v1/permits/prepare"])

        failing = {
            "checkpoint_before_execution": command([sys.executable, "-c", "raise SystemExit(9)"])
        }
        with self.assertRaisesRegex(DeploymentAdapterError, "did not complete"):
            self.run_execute(plan_mapping(deploy, controls=failing), token)
        self.assertFalse(marker.exists())
        self.assertEqual(
            [item["path"] for item in self.server.requests],
            ["/v1/permits/prepare", "/v1/permits/prepare"],
        )

    def test_forged_permit_cannot_trigger_control_commands(self):
        marker = self.workspace / "control-must-not-run.txt"
        self.server.prepare_responses.append((400, {"error": "invalid_permit_signature"}))
        controls = {
            "checkpoint_before_execution": command(
                [
                    sys.executable,
                    "-c",
                    "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('ran')",
                    str(marker),
                ]
            )
        }
        with self.assertRaisesRegex(DeploymentAdapterError, "preparation returned HTTP 400"):
            self.run_execute(
                plan_mapping([sys.executable, "-c", "print('deploy')"], controls=controls),
                permit_token(self.action, ["checkpoint_before_execution"]),
            )
        self.assertFalse(marker.exists())
        self.assertEqual([item["path"] for item in self.server.requests], ["/v1/permits/prepare"])

    def test_timeout_terminates_deployment_and_runs_declared_rollback(self):
        self.allow_consumption()
        rollback_marker = self.workspace / "rolled-back.txt"
        rollback = {
            **command(
                [
                    sys.executable,
                    "-c",
                    "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('rollback')",
                    str(rollback_marker),
                ],
                timeout=5,
                mechanism="restore prior release",
            ),
            "on_failure": True,
            "on_timeout": True,
            "on_cancel": True,
        }
        plan = plan_mapping(
            [sys.executable, "-c", "import time; time.sleep(10)"],
            rollback=rollback,
            timeout=1,
        )
        report = self.run_execute(plan, permit_token(self.action))
        self.assertEqual(report["outcome"], "TIMED_OUT")
        self.assertEqual(report["execution"]["status"], "timed_out")
        self.assertEqual(report["rollback"]["status"], "succeeded")
        self.assertTrue(rollback_marker.exists())

    def test_start_failure_after_consumption_runs_declared_rollback(self):
        self.allow_consumption()
        rollback_marker = self.workspace / "start-failure-rollback.txt"
        rollback = {
            **command(
                [
                    sys.executable,
                    "-c",
                    "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('rollback')",
                    str(rollback_marker),
                ],
                timeout=5,
                mechanism="restore prior release",
            ),
            "on_failure": True,
            "on_timeout": False,
            "on_cancel": False,
        }
        report = self.run_execute(
            plan_mapping(["executable-that-does-not-exist-smerc"], rollback=rollback),
            permit_token(self.action),
        )
        self.assertEqual(report["outcome"], "FAILED")
        self.assertEqual(report["execution"]["status"], "start_failed")
        self.assertEqual(report["execution"]["output_bytes"], 0)
        self.assertEqual(report["rollback"]["status"], "succeeded")
        self.assertTrue(rollback_marker.exists())

    def test_cancel_signal_terminates_deployment_and_runs_rollback(self):
        self.allow_consumption()
        cancel_event = threading.Event()
        threading.Timer(0.25, cancel_event.set).start()
        rollback_marker = self.workspace / "cancel-rollback.txt"
        rollback = {
            **command(
                [
                    sys.executable,
                    "-c",
                    "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('rollback')",
                    str(rollback_marker),
                ],
                timeout=5,
                mechanism="cancel recovery",
            ),
            "on_failure": True,
            "on_timeout": True,
            "on_cancel": True,
        }
        report = self.run_execute(
            plan_mapping(
                [sys.executable, "-c", "import time; time.sleep(10)"],
                rollback=rollback,
                timeout=5,
            ),
            permit_token(self.action),
            cancel_event=cancel_event,
        )
        self.assertEqual(report["outcome"], "CANCELLED")
        self.assertEqual(report["rollback"]["status"], "succeeded")

    def test_permit_denial_prevents_command_execution(self):
        marker = self.workspace / "must-not-exist.txt"
        self.server.responses.append((409, {"error": "permit_already_consumed"}))
        with self.assertRaisesRegex(DeploymentAdapterError, "HTTP 409"):
            self.run_execute(
                plan_mapping(
                    [
                        sys.executable,
                        "-c",
                        "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('bad')",
                        str(marker),
                    ]
                ),
                permit_token(self.action),
            )
        self.assertFalse(marker.exists())

    def test_plan_rejects_shell_strings_path_escape_unknown_fields_and_internal_override(self):
        valid = plan_mapping([sys.executable, "-c", "print('ok')"])
        invalid = dict(valid)
        invalid["command"] = "echo unsafe"
        with self.assertRaises(DeploymentAdapterError):
            ExecutionPlan.from_mapping(invalid)
        invalid = dict(valid)
        invalid["working_directory"] = "../outside"
        with self.assertRaises(DeploymentAdapterError):
            ExecutionPlan.from_mapping(invalid)
        invalid = dict(valid)
        invalid["unknown"] = True
        with self.assertRaises(DeploymentAdapterError):
            ExecutionPlan.from_mapping(invalid)
        invalid = dict(valid)
        invalid["controls"] = {
            "retain_cancel_handle": command([sys.executable, "-c", "print('fake')"])
        }
        with self.assertRaisesRegex(DeploymentAdapterError, "implemented internally"):
            ExecutionPlan.from_mapping(invalid)

    @unittest.skipIf(os.name == "nt", "Codex managed Windows workspace denies file deletion; CI verifies it on Linux.")
    def test_permit_file_is_removed_immediately_after_read(self):
        path = self.workspace / "permit.token"
        path.write_text("header.payload.signature\n", encoding="utf-8")
        self.assertEqual(_read_and_remove_permit(path), "header.payload.signature")
        self.assertFalse(path.exists())

    def test_permit_is_not_returned_until_cleanup_is_verified(self):
        class PermitPath:
            removed = False

            def read_text(self, *, encoding):
                self.asserted_encoding = encoding
                return "header.payload.signature\n"

            def unlink(self):
                self.removed = True

            def exists(self):
                return not self.removed

        path = PermitPath()
        self.assertEqual(_read_and_remove_permit(path), "header.payload.signature")
        self.assertTrue(path.removed)


if __name__ == "__main__":
    unittest.main()

import copy
import hashlib
import json
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from api_server import create_server
from reference_engine.action_language import evaluate_language_action
from reference_engine.audit_store import (
    AuditStore,
    PermitIssuanceConflictError,
    PermitNotIssuedError,
    PermitReplayError,
)
from reference_engine.authorization_permit import PermitError, PermitSigner, parse_permit_signers
from reference_engine.policy import PolicyRegistry, PolicyThresholds, RuntimePolicy
from reference_engine.recoverability_engine import RecoverabilityEngine


ROOT = Path(__file__).resolve().parents[1]
BASE_ACTION = json.loads(
    (ROOT / "examples" / "action_language" / "production_database_change.json").read_text(encoding="utf-8")
)


def low_risk_action():
    action = copy.deepcopy(BASE_ACTION)
    action["action"]["id"] = "staged-release-100"
    action["action"]["description"] = "Promote a reversible canary release to a contained staging target"
    action["action"]["target"] = {"resource": "service/canary", "environment": "staging"}
    action["action"]["authority"] = {"basis": "approved deployment ticket", "confidence": 0.96}
    action["signals"] = {
        "base_action_risk": 0.10,
        "evidence_validity": 0.96,
        "anomaly_pressure": 0.03,
        "impact_scope": 0.08,
    }
    action["recoverability"] = {
        "reversibility": 0.97,
        "containment_strength": 0.96,
        "rollback_latency": 0.03,
        "cancel_reliability": 0.99,
        "rollback_method": "Restore the prior canary image",
    }
    action["effects"] = {"external_side_effect": False, "sensitive_data": False}
    action["context"] = {"change_ticket": "CHG-100", "workflow": "staging-canary"}
    return action


def enforce_policy():
    return RuntimePolicy(
        tenant_id="alpha",
        policy_id="alpha-runtime-enforcement",
        policy_revision="1.0.0",
        mode="ENFORCE",
        evidence_program_id="alpha-pilot-evidence-v1",
        evidence_ceiling="LIMITED_ENFORCE",
        fail_behavior="fail_closed",
        approved_by_role="security-architecture",
        effective_at="2026-07-01T00:00:00Z",
        thresholds=PolicyThresholds(),
    )


def allow_decision(action=None):
    source = action or low_risk_action()
    decision = evaluate_language_action(source, RecoverabilityEngine(enforce_policy()))
    decision["tenant_id"] = "alpha"
    assert decision["posture"] == "ALLOW"
    return decision


class AuthorizationPermitTests(unittest.TestCase):
    def setUp(self):
        self.signer = PermitSigner("alpha-permit-2026-01", b"a" * 32)
        self.action = low_risk_action()
        self.decision = allow_decision(self.action)

    def issue(self, **overrides):
        values = {
            "tenant_id": "alpha",
            "audience": "github-actions-deployer",
            "ttl_seconds": 60,
            "now": 1_000,
        }
        values.update(overrides)
        return self.signer.issue(self.decision, self.action, **values)

    def test_permit_binds_action_tenant_audience_policy_and_controls(self):
        issued = self.issue()
        verified = self.signer.verify(
            issued["permit_token"],
            self.action,
            tenant_id="alpha",
            audience="github-actions-deployer",
            enforced_controls=["retain_cancel_handle"],
            now=1_030,
        )
        self.assertEqual(verified["action_hash"], self.decision["action_hash"])
        self.assertEqual(verified["policy"]["policy_hash"], enforce_policy().policy_hash)
        self.assertEqual(verified["authorization"], "release")
        self.assertEqual(verified["required_controls"], ["retain_cancel_handle"])
        self.assertEqual(verified["max_uses"], 1)

    def test_tampering_wrong_action_audience_expiry_and_missing_controls_fail(self):
        issued = self.issue()
        token = issued["permit_token"]
        corrupted = token[:-1] + ("A" if token[-1] != "A" else "B")
        with self.assertRaisesRegex(PermitError, "signature"):
            self.signer.verify(
                corrupted,
                self.action,
                tenant_id="alpha",
                audience="github-actions-deployer",
                enforced_controls=["retain_cancel_handle"],
                now=1_001,
            )
        changed = low_risk_action()
        changed["action"]["target"]["resource"] = "service/production"
        with self.assertRaisesRegex(PermitError, "action"):
            self.signer.verify(
                token,
                changed,
                tenant_id="alpha",
                audience="github-actions-deployer",
                enforced_controls=["retain_cancel_handle"],
                now=1_001,
            )
        with self.assertRaisesRegex(PermitError, "audience"):
            self.signer.verify(
                token,
                self.action,
                tenant_id="alpha",
                audience="different-executor",
                enforced_controls=["retain_cancel_handle"],
                now=1_001,
            )
        with self.assertRaisesRegex(PermitError, "expired"):
            self.signer.verify(
                token,
                self.action,
                tenant_id="alpha",
                audience="github-actions-deployer",
                enforced_controls=["retain_cancel_handle"],
                now=1_060,
            )
        with self.assertRaisesRegex(PermitError, "retain_cancel_handle"):
            self.signer.verify(
                token,
                self.action,
                tenant_id="alpha",
                audience="github-actions-deployer",
                enforced_controls=[],
                now=1_001,
            )

    def test_permits_require_enforcement_policy_and_permittable_posture(self):
        observe_decision = evaluate_language_action(self.action)
        observe_decision["tenant_id"] = "alpha"
        with self.assertRaisesRegex(PermitError, "ENFORCE"):
            self.signer.issue(
                observe_decision,
                self.action,
                tenant_id="alpha",
                audience="executor",
                now=1_000,
            )
        denied = evaluate_language_action(BASE_ACTION, RecoverabilityEngine(enforce_policy()))
        denied["tenant_id"] = "alpha"
        self.assertIn(denied["posture"], {"FREEZE", "DENY", "ESCALATE"})
        with self.assertRaisesRegex(PermitError, "ALLOW and THROTTLE"):
            self.signer.issue(
                denied,
                BASE_ACTION,
                tenant_id="alpha",
                audience="executor",
                now=1_000,
            )

    def test_throttle_permit_carries_constraints_into_consumption(self):
        constrained_action = low_risk_action()
        constrained_action["effects"]["external_side_effect"] = True
        decision = evaluate_language_action(constrained_action, RecoverabilityEngine(enforce_policy()))
        decision["tenant_id"] = "alpha"
        self.assertEqual(decision["posture"], "THROTTLE")
        issued = self.signer.issue(
            decision,
            constrained_action,
            tenant_id="alpha",
            audience="communications-adapter",
            now=1_000,
        )
        required = issued["permit"]["required_controls"]
        self.assertIn("limit_scope", required)
        self.assertIn("rate_limit_external_side_effect", required)
        with self.assertRaisesRegex(PermitError, "rate_limit_external_side_effect"):
            self.signer.verify(
                issued["permit_token"],
                constrained_action,
                tenant_id="alpha",
                audience="communications-adapter",
                enforced_controls=[item for item in required if item != "rate_limit_external_side_effect"],
                now=1_001,
            )

    def test_parser_requires_long_distinct_tenant_keys(self):
        signers = parse_permit_signers("alpha=alpha-key:" + "x" * 32)
        self.assertEqual(signers["alpha"].key_id, "alpha-key")
        with self.assertRaises(ValueError):
            parse_permit_signers("alpha=missing-key-format")
        with self.assertRaises(ValueError):
            parse_permit_signers("alpha=key:short")

    def test_audit_store_rejects_second_consumption(self):
        store = AuditStore(":memory:")
        try:
            store.record("alpha", self.decision, "request-hash")
            issued = self.issue()
            permit = issued["permit"]
            token_hash = hashlib.sha256(issued["permit_token"].encode("ascii")).hexdigest()
            with self.assertRaises(PermitNotIssuedError):
                store.consume_permit("alpha", permit, ["retain_cancel_handle"], token_hash)
            store.record_permit_issuance("alpha", permit, token_hash)
            with self.assertRaises(PermitIssuanceConflictError):
                store.record_permit_issuance("alpha", self.issue()["permit"], token_hash)
            first = store.consume_permit("alpha", permit, ["retain_cancel_handle"], token_hash)
            self.assertEqual(first["permit_id"], permit["permit_id"])
            with self.assertRaises(PermitReplayError):
                store.consume_permit("alpha", permit, ["retain_cancel_handle"], token_hash)
        finally:
            store.close()


class AuthorizationPermitAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(
            "127.0.0.1",
            0,
            audit_db=":memory:",
            api_keys={"alpha": "alpha-secret"},
            policy_registry=PolicyRegistry([enforce_policy()]),
            permit_signers={"alpha": PermitSigner("alpha-permit-2026-01", b"a" * 32)},
        )
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path, payload):
        request = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"authorization": "Bearer alpha-secret", "content-type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_issue_consume_and_replay_rejection(self):
        action = low_risk_action()
        status, decision = self.request("/v1/language/evaluate", action)
        self.assertEqual(status, 200)
        status, issued = self.request(
            "/v1/permits/issue",
            {
                "replay_id": decision["replay_id"],
                "action": action,
                "audience": "github-actions-deployer",
                "ttl_seconds": 120,
            },
        )
        self.assertEqual(status, 201)
        duplicate_status, duplicate = self.request(
            "/v1/permits/issue",
            {
                "replay_id": decision["replay_id"],
                "action": action,
                "audience": "github-actions-deployer",
                "ttl_seconds": 120,
            },
        )
        self.assertEqual(duplicate_status, 409)
        self.assertEqual(duplicate["error"], "permit_already_issued")
        consume_payload = {
            "permit_token": issued["permit_token"],
            "action": action,
            "audience": "github-actions-deployer",
            "enforced_controls": ["retain_cancel_handle"],
        }
        status, consumed = self.request("/v1/permits/consume", consume_payload)
        self.assertEqual(status, 200)
        self.assertTrue(consumed["valid"])
        status, replayed = self.request("/v1/permits/consume", consume_payload)
        self.assertEqual(status, 409)
        self.assertEqual(replayed["error"], "permit_already_consumed")


if __name__ == "__main__":
    unittest.main()

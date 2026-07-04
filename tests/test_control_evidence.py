import copy
import unittest

from api_server import create_server
from reference_engine.authorization_permit import PermitSigner
from reference_engine.control_evidence import (
    ControlEvidenceError,
    ControlEvidenceSigner,
    parse_control_evidence_signers,
)


def permit(**overrides):
    value = {
        "permit_id": "permit_0123456789abcdef0123456789abcdef",
        "tenant_id": "alpha",
        "audience": "github-actions-deployer",
        "action_hash": "a" * 64,
        "required_controls": ["retain_cancel_handle"],
    }
    value.update(overrides)
    return value


def control(**overrides):
    value = {
        "control_id": "retain_cancel_handle",
        "outcome": "applied",
        "mechanism": "github-environment-deployment-gate",
        "evidence_ref": "github-run:9001:job:deploy-canary",
        "observed_at": 1_000,
    }
    value.update(overrides)
    return value


class ControlEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.signer = ControlEvidenceSigner(
            "alpha",
            "github-actions-deployer",
            "github-actions-adapter",
            "alpha-control-evidence-2026-01",
            b"c" * 32,
        )

    def issue(self, **overrides):
        values = {"ttl_seconds": 60, "now": 1_000}
        values.update(overrides)
        return self.signer.issue(permit(), [control()], **values)

    def test_signed_receipt_binds_adapter_permit_action_controls_and_freshness(self):
        issued = self.issue()
        verified = self.signer.verify(
            issued["control_evidence_token"],
            tenant_id="alpha",
            audience="github-actions-deployer",
            action_hash="a" * 64,
            now=1_030,
        )
        self.assertEqual(verified["adapter_id"], "github-actions-adapter")
        self.assertEqual(verified["permit_id"], permit()["permit_id"])
        self.assertEqual(self.signer.applied_controls(verified), ["retain_cancel_handle"])
        self.assertNotIn("control_evidence_token", str(verified))

    def test_tampering_wrong_binding_and_expiry_fail_closed(self):
        token = self.issue()["control_evidence_token"]
        header, payload, signature = token.split(".")
        replacement = "A" if signature[0] != "A" else "B"
        corrupted = f"{header}.{payload}.{replacement}{signature[1:]}"
        with self.assertRaisesRegex(ControlEvidenceError, "signature"):
            self.signer.verify(
                corrupted,
                tenant_id="alpha",
                audience="github-actions-deployer",
                action_hash="a" * 64,
                now=1_001,
            )
        with self.assertRaisesRegex(ControlEvidenceError, "audience"):
            self.signer.verify(
                token,
                tenant_id="alpha",
                audience="different-executor",
                action_hash="a" * 64,
                now=1_001,
            )
        with self.assertRaisesRegex(ControlEvidenceError, "action"):
            self.signer.verify(
                token,
                tenant_id="alpha",
                audience="github-actions-deployer",
                action_hash="b" * 64,
                now=1_001,
            )
        with self.assertRaisesRegex(ControlEvidenceError, "expired"):
            self.signer.verify(
                token,
                tenant_id="alpha",
                audience="github-actions-deployer",
                action_hash="a" * 64,
                now=1_060,
            )

    def test_missing_failed_duplicate_or_stale_control_results_are_rejected(self):
        with self.assertRaisesRegex(ControlEvidenceError, "missing"):
            self.signer.issue(permit(), [], now=1_000)
        with self.assertRaisesRegex(ControlEvidenceError, "not applied"):
            self.signer.issue(permit(), [control(outcome="failed")], now=1_000)
        with self.assertRaisesRegex(ControlEvidenceError, "unique"):
            self.signer.issue(permit(), [control(), copy.deepcopy(control())], now=1_000)
        with self.assertRaisesRegex(ControlEvidenceError, "freshness"):
            self.signer.issue(permit(), [control(observed_at=800)], now=1_000)

    def test_parser_scopes_each_distinct_key_to_one_tenant_and_audience(self):
        parsed = parse_control_evidence_signers(
            "alpha:github-actions-deployer=github-adapter:control-key-1:"
            "control-evidence-secret-012345678901"
        )
        self.assertEqual(list(parsed), [("alpha", "github-actions-deployer")])
        self.assertEqual(parsed[("alpha", "github-actions-deployer")].adapter_id, "github-adapter")
        with self.assertRaisesRegex(ValueError, "format"):
            parse_control_evidence_signers("alpha=bad")
        with self.assertRaisesRegex(ValueError, "at least 32"):
            parse_control_evidence_signers("alpha:runner=adapter:key:short")

    def test_server_rejects_unverifiable_or_misbound_adapter_configuration(self):
        mapping = {("alpha", "github-actions-deployer"): self.signer}
        with self.assertRaisesRegex(ValueError, "permit signing"):
            create_server(
                "127.0.0.1",
                0,
                audit_db=":memory:",
                api_keys={},
                allow_unauthenticated=True,
                control_evidence_signers=mapping,
            )
        with self.assertRaisesRegex(ValueError, "mapping"):
            create_server(
                "127.0.0.1",
                0,
                audit_db=":memory:",
                api_keys={},
                allow_unauthenticated=True,
                permit_signers={"alpha": PermitSigner("permit-key", b"p" * 32)},
                control_evidence_signers={
                    ("alpha", "different-audience"): self.signer
                },
            )


if __name__ == "__main__":
    unittest.main()

import copy
import json
from pathlib import Path
import unittest

from reference_engine.decision_certificate import (
    CERTIFICATE_VERSION,
    build_decision_certificate,
    render_markdown,
    sign_decision_certificate,
    verify_decision_certificate,
)
from reference_engine.decision_lifecycle_ledger import build_example_ledger
from reference_engine.sparta_router import route_decision, sign_route_report


ROOT = Path(__file__).resolve().parents[1]


def route_report():
    decision = {
        "replay_id": "dll_example_ai_deploy_001",
        "posture": "THROTTLE",
        "reason_codes": ["EVIDENCE_INCOMPLETE", "RECOVERY_PATH_PARTIAL"],
        "controls": ["limit_scope", "preview_before_execution", "require_rollback_plan"],
        "policy": {"policy_id": "github-actions-strict", "policy_hash": "a" * 64},
    }
    plan = {
        "version": "smerc.sparta-plan.v1",
        "plan_id": "github-canary",
        "tool": "github_actions",
        "action": "deploy",
        "requested_capability": "production_deployment",
        "supports_dry_run": True,
        "supports_scope_limit": True,
        "supports_checkpoint": True,
        "supports_rollback": True,
        "supports_human_approval": True,
        "max_scope_units": 100,
        "requested_scope_units": 40,
        "side_effect_level": "external",
        "metadata": {"environment": "production"},
    }
    return sign_route_report(route_decision(decision, plan), "route-signing-key-012345")


class DecisionCertificateTests(unittest.TestCase):
    def test_builds_digest_bound_certificate_from_verified_ledger(self):
        ledger = build_example_ledger()
        certificate = build_decision_certificate(
            ledger,
            issuer="smerc-test-suite",
            issued_at="2026-07-14T12:00:00+00:00",
        )
        self.assertEqual(certificate["version"], CERTIFICATE_VERSION)
        self.assertTrue(certificate["verification"]["valid"])
        self.assertEqual(certificate["tenant_id"], "design-partner")
        self.assertEqual(certificate["evaluation"]["authorization_recommendation"], "THROTTLE")
        self.assertEqual(certificate["lifecycle_binding"]["record_count"], 7)
        self.assertTrue(certificate["lifecycle_binding"]["complete_lifecycle"])
        self.assertIn("does not provide immutable storage by itself", certificate["boundary"]["limits"])

    def test_signing_key_verifies_and_wrong_key_fails(self):
        certificate = build_decision_certificate(build_example_ledger())
        signed = sign_decision_certificate(certificate, "certificate-signing-key-012345", key_id="test-key")
        verified = verify_decision_certificate(signed, signing_key="certificate-signing-key-012345")
        self.assertTrue(verified["valid"])
        self.assertEqual(signed["signature"]["key_id"], "test-key")

        rejected = verify_decision_certificate(signed, signing_key="wrong-certificate-signing-key")
        self.assertFalse(rejected["valid"])
        self.assertIn("signature mismatch", rejected["errors"])

    def test_tampering_changes_digest_verification(self):
        signed = sign_decision_certificate(
            build_decision_certificate(build_example_ledger()),
            "certificate-signing-key-012345",
        )
        tampered = copy.deepcopy(signed)
        tampered["evaluation"]["authorization_recommendation"] = "ALLOW"
        verification = verify_decision_certificate(tampered, signing_key="certificate-signing-key-012345")
        self.assertFalse(verification["valid"])
        self.assertIn("certificate digest mismatch", verification["errors"])
        self.assertIn("signature digest mismatch", verification["errors"])

    def test_source_ledger_must_match_bound_head_hash(self):
        ledger = build_example_ledger()
        certificate = build_decision_certificate(ledger)
        changed = build_example_ledger()
        changed.append(
            "HUMAN_INTERACTION",
            "reviewer",
            {
                "interaction": "accepted",
                "reviewer_id": "reviewer",
                "original_recommendation": "THROTTLE",
                "final_recommendation": "THROTTLE",
                "rationale": "Second review creates a different head hash.",
            },
            recorded_at="2026-07-14T12:00:00+00:00",
        )
        verification = verify_decision_certificate(certificate, source_ledger=changed)
        self.assertFalse(verification["valid"])
        self.assertIn("source ledger head hash mismatch", verification["errors"])

    def test_route_report_binding_is_replayable(self):
        route = route_report()
        certificate = build_decision_certificate(build_example_ledger(), route_report=route)
        self.assertEqual(certificate["route_binding"]["route_state"], "CONSTRAINED_EXECUTE")
        self.assertTrue(verify_decision_certificate(certificate, route_report=route)["valid"])

        tampered_route = copy.deepcopy(route)
        tampered_route["route_state"] = "EXECUTE"
        rejected = verify_decision_certificate(certificate, route_report=tampered_route)
        self.assertFalse(rejected["valid"])
        self.assertIn("route report digest mismatch", rejected["errors"])

    def test_markdown_states_pilot_boundary(self):
        markdown = render_markdown(build_decision_certificate(build_example_ledger()))
        self.assertIn("SMERC Decision Certificate", markdown)
        self.assertIn("pilot-grade, digest-bound summary", markdown)
        self.assertIn("not, by itself, immutable storage", markdown)

    def test_schema_and_example_use_certificate_version(self):
        schema = json.loads((ROOT / "schemas" / "smerc-decision-certificate-v1.schema.json").read_text(encoding="utf-8"))
        example = json.loads((ROOT / "reports" / "decision_certificate_example.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["version"]["const"], CERTIFICATE_VERSION)
        self.assertEqual(example["version"], CERTIFICATE_VERSION)
        self.assertTrue(example["verification"]["valid"])


if __name__ == "__main__":
    unittest.main()

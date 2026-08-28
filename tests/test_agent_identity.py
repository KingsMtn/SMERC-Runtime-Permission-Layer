import copy
import unittest
from pathlib import Path

from reference_engine.agent_identity import evaluate_agent_identity, load_catalog
from reference_engine.pilot_intake_report import build_pilot_intake_report, load_payload


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "examples" / "agent_identity_catalog.json"
FILLED_INTAKE = ROOT / "examples" / "pilot_intake_filled_examples.json"


class AgentIdentityTests(unittest.TestCase):
    def test_verified_agent_passes_for_authorized_tool(self):
        catalog = load_catalog(CATALOG)
        result = evaluate_agent_identity(
            catalog["release_agent"],
            actor="release_agent",
            requested_tool="github_actions.production_deploy",
            requested_autonomy_level="execute",
            requested_side_effect_level="external",
        )

        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(result["identity_score"], 0.72)
        self.assertIn("AGENT_IDENTITY_VERIFIED", result["reason_codes"])

    def test_missing_required_identity_fails_closed(self):
        result = evaluate_agent_identity(
            None,
            actor="unknown_agent",
            requested_tool="github_actions.production_deploy",
            requested_autonomy_level="execute",
            requested_side_effect_level="external",
            required=True,
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertIn("AGENT_IDENTITY_MISSING", result["reason_codes"])

    def test_unlisted_tool_family_fails(self):
        catalog = load_catalog(CATALOG)
        result = evaluate_agent_identity(
            catalog["release_agent"],
            actor="release_agent",
            requested_tool="finance_ops.stablecoin_transfer",
            requested_autonomy_level="execute",
            requested_side_effect_level="financial",
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertIn("TOOL_FAMILY_NOT_AUTHORIZED", result["reason_codes"])

    def test_standard_trust_agent_without_blockers_is_watch_not_silent_pass(self):
        catalog = load_catalog(CATALOG)
        result = evaluate_agent_identity(
            catalog["support_resolution_agent"],
            actor="support_resolution_agent",
            requested_tool="customer_records_mcp.merge_preview",
            requested_autonomy_level="constrain",
            requested_side_effect_level="internal",
        )

        self.assertEqual(result["status"], "WATCH")
        self.assertIn("AGENT_IDENTITY_REQUIRES_MONITORING", result["reason_codes"])

    def test_autonomy_overreach_fails(self):
        catalog = load_catalog(CATALOG)
        result = evaluate_agent_identity(
            catalog["cloud_admin_agent"],
            actor="cloud_admin_agent",
            requested_tool="cloud_iam.policy_update",
            requested_autonomy_level="execute",
            requested_side_effect_level="external",
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertIn("REQUESTED_AUTONOMY_EXCEEDS_AGENT_AUTHORITY", result["reason_codes"])

    def test_financial_side_effect_requires_financial_scope(self):
        catalog = load_catalog(CATALOG)
        result = evaluate_agent_identity(
            catalog["treasury_agent"],
            actor="treasury_agent",
            requested_tool="finance_ops.stablecoin_transfer",
            requested_autonomy_level="execute",
            requested_side_effect_level="financial",
        )

        self.assertEqual(result["status"], "FAIL")
        self.assertIn("CREDENTIAL_SCOPE_TOO_WEAK_FOR_SIDE_EFFECT", result["reason_codes"])

    def test_pilot_intake_report_includes_identity_gate_counts(self):
        report = build_pilot_intake_report(load_payload(FILLED_INTAKE))

        self.assertIn("identity_gate_counts", report["customer_evaluation"]["summary"])
        self.assertGreaterEqual(report["customer_evaluation"]["summary"]["identity_gate_counts"].get("FAIL", 0), 1)
        self.assertEqual(report["customer_evaluation"]["records"][0]["identity_gate"]["status"], "PASS")

    def test_rejects_unknown_agent_identity_fields(self):
        catalog = load_catalog(CATALOG)
        payload = copy.deepcopy(catalog["release_agent"].to_dict())
        payload["extra_field"] = True

        with self.assertRaises(ValueError):
            evaluate_agent_identity(
                payload,
                actor="release_agent",
                requested_tool="github_actions.production_deploy",
                requested_autonomy_level="execute",
                requested_side_effect_level="external",
            )


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.autonomy_continuance import (
    AUTONOMY_CONTINUANCE_VERSION,
    evaluate_authority_provenance,
    evaluate_continuance,
    evaluate_intent_integrity,
    load_json,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "autonomy" / "continuance_case.json"
DOC = ROOT / "docs" / "Autonomy_Continuance_Framework.md"
TEST_OUTPUTS = ROOT / "test_outputs"
TEST_OUTPUTS.mkdir(exist_ok=True)


class AutonomyContinuanceTests(unittest.TestCase):
    def test_reference_case_requires_requalification_or_pause(self):
        report = evaluate_continuance(load_json(CASE))

        self.assertEqual(report["version"], AUTONOMY_CONTINUANCE_VERSION)
        self.assertEqual(report["authority_provenance"]["status"], "VERIFIED")
        self.assertEqual(report["intent_integrity"]["status"], "DIVERGED")
        self.assertEqual(report["consequence_horizon"]["horizon"], "LONG")
        self.assertEqual(report["collective_autonomy"]["state"], "COLLECTIVE_RISK_HIGH")
        self.assertEqual(report["right_to_continue"]["state"], "REQUALIFY")
        self.assertIn("intent_integrity_failed", report["right_to_continue"]["drivers"])

    def test_authority_failure_rejects_provenance(self):
        authority = {
            "identity_verified": True,
            "delegation_valid": False,
            "policy_binding_valid": True,
            "tool_grant_valid": True,
            "approval_required": True,
            "approval_present": False,
            "credential_age_minutes": 90,
            "max_credential_age_minutes": 30,
        }

        report = evaluate_authority_provenance(authority)

        self.assertEqual(report["status"], "REJECTED")
        self.assertIn("delegation_invalid", report["drivers"])
        self.assertIn("required_approval_missing", report["drivers"])
        self.assertIn("credential_too_old", report["drivers"])

    def test_intent_alignment_passes_for_matching_scope_tool_and_boundary(self):
        intent = {
            "declared_intent": "read deployment checklist",
            "operation_class": "read",
            "tool_name": "search_documents",
            "declared_allowed_tools": ["search_documents"],
            "declared_scope_units": 20,
            "requested_scope_units": 10,
            "declared_data_boundary": "internal-docs",
            "requested_data_boundary": "internal-docs",
        }

        report = evaluate_intent_integrity(intent)

        self.assertEqual(report["status"], "ALIGNED")
        self.assertEqual(report["drivers"], [])

    def test_clean_case_can_continue(self):
        case = {
            "version": AUTONOMY_CONTINUANCE_VERSION,
            "case_id": "CLEAN",
            "subject_id": "research_agent",
            "authority": {
                "identity_verified": True,
                "delegation_valid": True,
                "policy_binding_valid": True,
                "tool_grant_valid": True,
                "approval_required": False,
                "approval_present": False,
                "credential_age_minutes": 5,
                "max_credential_age_minutes": 30,
            },
            "intent": {
                "declared_intent": "read internal documentation",
                "operation_class": "read",
                "tool_name": "search_documents",
                "declared_allowed_tools": ["search_documents"],
                "declared_scope_units": 50,
                "requested_scope_units": 10,
                "declared_data_boundary": "internal-docs",
                "requested_data_boundary": "internal-docs",
            },
            "consequence_horizon": {
                "external_side_effect": False,
                "customer_impact_possible": False,
                "financial_settlement_possible": False,
                "rollback_window_minutes": 5,
                "downstream_system_count": 1,
            },
            "collective_autonomy": {
                "active_actor_count": 1,
                "shared_tool_actor_count": 1,
                "correlated_objective": False,
                "aggregate_scope_units": 10,
                "aggregate_scope_limit": 100,
            },
            "earned_autonomy": {"earned_tier": "TIER_2_CONSTRAINED"},
            "autonomy_budget": {"autonomy_state": "WATCH"},
        }

        report = evaluate_continuance(case)

        self.assertEqual(report["right_to_continue"]["state"], "CONTINUE")

    def test_markdown_and_doc_explain_all_checks(self):
        report = evaluate_continuance(load_json(CASE))
        markdown = render_markdown(report)
        doc = DOC.read_text(encoding="utf-8")

        for phrase in ["Authority provenance", "Intent integrity", "Consequence horizon", "Collective autonomy"]:
            self.assertIn(phrase, markdown)
        for phrase in ["Authority Provenance", "Intent Integrity", "Consequence Horizon", "Collective Autonomy", "Right To Continue"]:
            self.assertIn(phrase, doc)

    def test_writes_outputs(self):
        report = evaluate_continuance(load_json(CASE))
        json_path = TEST_OUTPUTS / "autonomy_continuance_test.json"
        markdown_path = TEST_OUTPUTS / "autonomy_continuance_test.md"

        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertIn(AUTONOMY_CONTINUANCE_VERSION, json_path.read_text(encoding="utf-8"))
        self.assertIn("SMERC Autonomy Continuance Report", markdown_path.read_text(encoding="utf-8"))

    def test_cli_generates_report(self):
        json_path = TEST_OUTPUTS / "autonomy_continuance_cli.json"
        markdown_path = TEST_OUTPUTS / "autonomy_continuance_cli.md"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "reference_engine.autonomy_continuance",
                "--case",
                str(CASE),
                "--json-output",
                str(json_path),
                "--markdown-output",
                str(markdown_path),
                "--pretty",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(report["version"], AUTONOMY_CONTINUANCE_VERSION)
        self.assertEqual(report["right_to_continue"]["state"], "REQUALIFY")


if __name__ == "__main__":
    unittest.main()

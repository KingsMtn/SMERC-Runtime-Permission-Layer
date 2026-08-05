import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.operator_status import (
    build_operator_status,
    export_opa_decision_logs,
    load_json,
    markdown_opa_export,
    markdown_status,
    write_json,
    write_text,
)


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "reports" / "github_actions_pilot_readiness.json"
CUSTOMER_INTAKE = ROOT / "reports" / "github_actions_customer_pilot_intake_report.json"
DECISIONS = ROOT / "reports" / "github_actions_shadow_mode_results.json"
POLICY_BUNDLE = ROOT / "reports" / "policy_bundle_manifest.json"
RUNTIME_HEALTH = ROOT / "reports" / "runtime_health_metrics.json"
DOC = ROOT / "docs" / "Operator_Status_And_OPA_Log_Export.md"
README = ROOT / "README.md"


class OperatorStatusTests(unittest.TestCase):
    def test_operator_status_summarizes_readiness_and_decision_activity(self):
        report = build_operator_status(
            pilot_readiness=load_json(READINESS),
            customer_intake=load_json(CUSTOMER_INTAKE),
            decision_artifacts=load_json(DECISIONS),
            runtime_health=load_json(RUNTIME_HEALTH),
            tenant_id="test-tenant",
            active_policy_version="policy-001",
            active_profile_version="profile-001",
        )
        self.assertEqual(report["schema"], "smerc.operator-status.v1")
        self.assertEqual(report["tenant_id"], "test-tenant")
        self.assertEqual(report["active_policy_version"], "policy-001")
        self.assertFalse(report["policy_bundle"]["present"])
        self.assertTrue(report["runtime_health"]["present"])
        self.assertEqual(report["runtime_health"]["health_status"], "healthy")
        self.assertEqual(report["decision_activity"]["decision_count"], 10)
        self.assertEqual(report["decision_activity"]["unavailable_count"], 0)
        self.assertIn(report["operator_status"], {"ready_for_review", "needs_attention"})
        self.assertIn("does not prove production", report["evidence_boundary"])

    def test_operator_status_reports_verified_policy_bundle(self):
        report = build_operator_status(
            pilot_readiness=load_json(READINESS),
            customer_intake=load_json(CUSTOMER_INTAKE),
            decision_artifacts=load_json(DECISIONS),
            runtime_health=load_json(RUNTIME_HEALTH),
            policy_bundle=load_json(POLICY_BUNDLE),
            policy_bundle_signing_key="local-policy-bundle-signing-key-012345",
            active_policy_version="github-actions-shadow-mode@2026.07.07",
            active_profile_version="github_actions_strict",
        )
        self.assertTrue(report["policy_bundle"]["present"])
        self.assertTrue(report["policy_bundle"]["valid"])
        self.assertTrue(report["policy_bundle"]["signature_checked"])
        self.assertEqual(report["policy_bundle"]["bundle_id"], "github-actions-shadow-mode-2026-07-07")
        checks = {check["name"]: check for check in report["operational_checks"]}
        self.assertEqual(checks["policy_bundle_verified"]["status"], "ready")
        self.assertEqual(checks["runtime_health"]["status"], "ready")

    def test_degraded_runtime_health_degrades_operator_status(self):
        runtime_health = load_json(RUNTIME_HEALTH)
        runtime_health["health_status"] = "degraded"
        runtime_health["latency"]["p95_ms"] = 750
        runtime_health["latency"]["slo_met"] = False
        report = build_operator_status(
            pilot_readiness=load_json(READINESS),
            customer_intake=load_json(CUSTOMER_INTAKE),
            decision_artifacts=load_json(DECISIONS),
            runtime_health=runtime_health,
        )
        self.assertEqual(report["operator_status"], "degraded")
        checks = {check["name"]: check for check in report["operational_checks"]}
        self.assertEqual(checks["runtime_health"]["status"], "warning")

    def test_tampered_policy_bundle_blocks_operator_status(self):
        bundle = load_json(POLICY_BUNDLE)
        bundle["policy"]["mode"] = "ENFORCE"
        report = build_operator_status(
            pilot_readiness=load_json(READINESS),
            customer_intake=load_json(CUSTOMER_INTAKE),
            decision_artifacts=load_json(DECISIONS),
            policy_bundle=bundle,
            policy_bundle_signing_key="local-policy-bundle-signing-key-012345",
        )
        self.assertEqual(report["operator_status"], "blocked")
        self.assertFalse(report["policy_bundle"]["valid"])
        checks = {check["name"]: check for check in report["operational_checks"]}
        self.assertEqual(checks["policy_bundle_verified"]["status"], "blocker")

    def test_opa_style_export_preserves_smerc_posture_and_replay(self):
        export = export_opa_decision_logs(load_json(DECISIONS), tenant_id="test-tenant", bundle_revision="policy-001")
        self.assertEqual(export["schema"], "smerc.opa-decision-log-export.v1")
        self.assertEqual(export["entry_count"], 10)
        first = export["entries"][0]
        self.assertIn("decision_id", first)
        self.assertEqual(first["input"]["tenant_id"], "test-tenant")
        self.assertIn(first["result"]["posture"], {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertIn("reason_codes", first["result"])
        self.assertIn("replay_id", first["result"])
        self.assertEqual(first["bundles"]["smerc"]["revision"], "policy-001")
        self.assertEqual(first["labels"]["compatibility"], "opa_decision_log_adjacent")
        self.assertIn("not OPA parity", export["evidence_boundary"])

    def test_markdown_and_writers_create_reports(self):
        status = build_operator_status(
            pilot_readiness=load_json(READINESS),
            customer_intake=load_json(CUSTOMER_INTAKE),
            decision_artifacts=load_json(DECISIONS),
        )
        export = export_opa_decision_logs(load_json(DECISIONS))
        status_md = markdown_status(status)
        export_md = markdown_opa_export(export)
        self.assertIn("SMERC Operator Status Report", status_md)
        self.assertIn("Policy Bundle", status_md)
        self.assertIn("Runtime Health", status_md)
        self.assertIn("OPA-Style Decision Log Export", export_md)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "status.json"
            md_path = Path(directory) / "status.md"
            write_json(json_path, status)
            write_text(md_path, status_md)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())

    def test_docs_and_readme_reference_operator_export(self):
        doc = DOC.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        self.assertIn("python -m reference_engine.operator_status --pretty", doc)
        self.assertIn("policy bundle", doc.lower())
        self.assertIn("not OPA parity", doc)
        self.assertIn("docs/Operator_Status_And_OPA_Log_Export.md", readme)


if __name__ == "__main__":
    unittest.main()

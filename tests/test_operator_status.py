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
DOC = ROOT / "docs" / "Operator_Status_And_OPA_Log_Export.md"
README = ROOT / "README.md"


class OperatorStatusTests(unittest.TestCase):
    def test_operator_status_summarizes_readiness_and_decision_activity(self):
        report = build_operator_status(
            pilot_readiness=load_json(READINESS),
            customer_intake=load_json(CUSTOMER_INTAKE),
            decision_artifacts=load_json(DECISIONS),
            tenant_id="test-tenant",
            active_policy_version="policy-001",
            active_profile_version="profile-001",
        )
        self.assertEqual(report["schema"], "smerc.operator-status.v1")
        self.assertEqual(report["tenant_id"], "test-tenant")
        self.assertEqual(report["active_policy_version"], "policy-001")
        self.assertEqual(report["decision_activity"]["decision_count"], 10)
        self.assertEqual(report["decision_activity"]["unavailable_count"], 0)
        self.assertIn(report["operator_status"], {"ready_for_review", "needs_attention"})
        self.assertIn("does not prove production", report["evidence_boundary"])

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
        self.assertIn("not OPA parity", doc)
        self.assertIn("docs/Operator_Status_And_OPA_Log_Export.md", readme)


if __name__ == "__main__":
    unittest.main()

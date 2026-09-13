import json
import unittest
from pathlib import Path

from reference_engine.customer_evaluation import load_payload
from reference_engine.public_agent_runtime_incident_replay import (
    build_report,
    load_rows,
    normalize_rows,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "public_agent_runtime_incident_patterns.json"


class PublicAgentRuntimeIncidentReplayTests(unittest.TestCase):
    def test_example_rows_are_metadata_only_and_cover_public_patterns(self):
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["schema_version"],
            "smerc.public_agent_runtime_incident_patterns.v1",
        )
        self.assertIn("Use public incident-pattern data", payload["source_boundary"])
        self.assertEqual(len(payload["rows"]), 6)
        self.assertEqual(
            {row["public_pattern"] for row in payload["rows"]},
            {
                "credential_exfiltration_pressure",
                "trust_boundary_before_consent",
                "approved_domain_exfiltration",
                "sandbox_or_filesystem_boundary_escape",
                "overbroad_remediation_blast_radius",
                "autonomous_workflow_acceleration",
            },
        )

        for row in payload["rows"]:
            self.assertIn("source_url", row)
            self.assertIn("sensitive_material_excluded", row)
            self.assertIn("likely_smerc_posture", row)
            self.assertIn("reason_codes", row)
            self.assertIn("recoverability_question", row)
            self.assertIn("postcondition_evidence_needed", row)
            self.assertIn("non_claim", row)

    def test_reason_codes_capture_agent_runtime_learning(self):
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        codes = {code for row in payload["rows"] for code in row["reason_codes"]}

        self.assertIn("CREDENTIAL_EXFILTRATION_PRESSURE", codes)
        self.assertIn("TRUST_BOUNDARY_BEFORE_CONSENT", codes)
        self.assertIn("APPROVED_DOMAIN_CAPABILITY_GRANT", codes)
        self.assertIn("SANDBOX_BOUNDARY_WEAK", codes)
        self.assertIn("REMEDIATION_BLAST_RADIUS_UNBOUNDED", codes)
        self.assertIn("AUTONOMOUS_WORKFLOW_VELOCITY_HIGH", codes)
        self.assertIn("RECOVERY_PATH_UNPROVEN", codes)

    def test_normalizes_to_customer_evaluation_contract(self):
        payload = normalize_rows(load_rows(EXAMPLE))

        self.assertEqual(payload["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(len(payload["actions"]), 6)
        self.assertIn("Safe metadata-only public incident-pattern replay", payload["data_boundary"])
        for action in payload["actions"]:
            self.assertEqual(action["context"]["source_name"], "Public Agent Runtime Incident Replay")
            self.assertTrue(action["context"]["metadata_only"])
            self.assertIn("public_pattern", action["context"])
            self.assertIn("ref_gate", action)
            self.assertIn("tool_plan", action)

    def test_builds_report_with_public_pattern_deltas(self):
        report = build_report(load_rows(EXAMPLE))

        self.assertEqual(report["version"], "smerc.public-agent-runtime-incident-replay.v1")
        self.assertEqual(report["record_count"], 6)
        self.assertEqual(report["normalized_action_count"], 6)
        self.assertEqual(report["valid_dll_ledgers"], 6)
        self.assertIn("credential_exfiltration_pressure", report["pattern_counts"])
        self.assertIn("CREDENTIAL_EXFILTRATION_PRESSURE", report["incident_reason_code_counts"])
        self.assertIn("SMERC_RESTRAINS_PUBLIC_PATTERN", report["delta_counts"])
        self.assertIn("leaked source code", report["evidence_boundary"])
        self.assertIn("real public agent-runtime failures", report["work_result_impact"]["impact"])

    def test_markdown_explains_boundaries_and_reviewer_question(self):
        markdown = render_markdown(build_report(load_rows(EXAMPLE)))

        self.assertIn("Public Agent Runtime Incident Replay Report", markdown)
        self.assertIn("Source Boundary", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("credential_exfiltration_pressure", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "public_agent_runtime_incident_replay"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_report(load_rows(EXAMPLE))
        normalized = scratch / "normalized.json"
        report_json = scratch / "report.json"
        report_md = scratch / "report.md"
        customer_json = scratch / "customer.json"
        customer_md = scratch / "customer.md"

        write_outputs(
            report,
            normalized_output=normalized,
            json_output=report_json,
            markdown_output=report_md,
            customer_json_output=customer_json,
            customer_markdown_output=customer_md,
        )

        self.assertEqual(len(load_payload(normalized)["actions"]), 6)
        self.assertIn("Public Agent Runtime Incident Replay Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))

    def test_docs_and_reviewer_assets_link_replay_and_preserve_boundary(self):
        doc = (ROOT / "docs" / "Public_Agent_Runtime_Incident_Replay.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(
            encoding="utf-8"
        )
        data_map = (ROOT / "docs" / "Runtime_Data_Source_Map.md").read_text(
            encoding="utf-8"
        )
        ai_doc = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(
            encoding="utf-8"
        )
        ai_json = json.loads((ROOT / "examples" / "ai_reviewer_bundle.json").read_text(encoding="utf-8"))
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("Use public incident-pattern data, not leaked implementation data", doc)
        self.assertIn("examples/public_agent_runtime_incident_patterns.json", doc)
        self.assertIn("python -m reference_engine.public_agent_runtime_incident_replay", doc)
        self.assertIn("reports/Public_Agent_Runtime_Incident_Replay_Report.md", doc)
        self.assertIn("What This Does Not Prove", doc)
        self.assertIn("proof that SMERC used leaked Claude Code source", doc)
        self.assertIn("docs/Public_Agent_Runtime_Incident_Replay.md", readme)
        self.assertIn("docs/Public_Agent_Runtime_Incident_Replay.md", indexing)
        self.assertIn("docs/Public_Agent_Runtime_Incident_Replay.md", data_map)
        self.assertIn("Public Agent Runtime Incident Replay", ai_doc)
        self.assertIn(
            "https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Public_Agent_Runtime_Incident_Replay.md",
            ai_json["current_evidence"]["public_agent_runtime_incident_replay"],
        )
        self.assertIn(
            "https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/reports/Public_Agent_Runtime_Incident_Replay_Report.md",
            ai_json["current_evidence"]["public_agent_runtime_incident_replay_report"],
        )
        self.assertIn("public agent-runtime incident replay pack", changelog)


if __name__ == "__main__":
    unittest.main()

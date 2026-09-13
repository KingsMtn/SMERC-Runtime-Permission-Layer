import json
import unittest
from pathlib import Path


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
        self.assertIn("public agent-runtime incident replay pack", changelog)


if __name__ == "__main__":
    unittest.main()

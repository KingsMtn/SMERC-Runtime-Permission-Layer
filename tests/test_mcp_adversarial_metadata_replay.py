import unittest
from pathlib import Path

from reference_engine.customer_evaluation import load_payload
from reference_engine.mcp_adversarial_metadata_replay import (
    build_report,
    load_rows,
    normalize_rows,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "mcp_adversarial_metadata.json"


class MCPAdversarialMetadataReplayTests(unittest.TestCase):
    def test_loads_all_adversarial_surfaces(self):
        rows = load_rows(INPUTS)

        self.assertEqual(len(rows), 8)
        self.assertEqual(
            {row["attack_surface"] for row in rows},
            {
                "tool_description_poisoning",
                "nested_schema_poisoning",
                "server_instructions_injection",
                "public_cache_poisoning",
                "schema_drift_after_approval",
                "benign_tool_dangerous_arguments",
                "encoded_instruction_evasion",
                "missing_recoverability_evidence",
            },
        )

    def test_normalizes_to_customer_evaluation_contract(self):
        payload = normalize_rows(load_rows(INPUTS))

        self.assertEqual(payload["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(len(payload["actions"]), 8)
        self.assertIn("Safe metadata-only MCP replay", payload["data_boundary"])
        for action in payload["actions"]:
            self.assertEqual(action["context"]["source_name"], "MCP Adversarial Metadata Replay")
            self.assertTrue(action["context"]["metadata_only"])
            self.assertIn("known_miss_pattern", action["context"])
            self.assertIn("ref_gate", action)
            self.assertIn("tool_plan", action)

    def test_builds_report_with_restrained_mcp_deltas(self):
        report = build_report(load_rows(INPUTS))

        self.assertEqual(report["version"], "smerc.mcp-adversarial-metadata-replay.v1")
        self.assertEqual(report["record_count"], 8)
        self.assertEqual(report["normalized_action_count"], 8)
        self.assertEqual(report["valid_dll_ledgers"], 8)
        self.assertIn("nested_schema_poisoning", report["attack_surface_counts"])
        self.assertIn("SMERC_RESTRAINS_MCP_ATTACK_SURFACE", report["delta_counts"])
        self.assertIn("SMERC_FREEZES_UNCERTAIN_MCP_RISK", report["delta_counts"])
        self.assertIn("SMERC_CONSTRAINS_MCP_RISK", report["delta_counts"])
        self.assertIn("missing evidence does not become permission", report["work_result_impact"]["impact"])

    def test_missing_recoverability_evidence_is_not_allow(self):
        report = build_report(load_rows(INPUTS))
        missing = next(item for item in report["deltas"] if item["record_id"] == "MCPADV-008")

        self.assertNotEqual(missing["smerc_posture"], "ALLOW")
        self.assertIn(missing["delta"], {"SMERC_CONSTRAINS_MCP_RISK", "NEEDS_HUMAN_LABEL_REVIEW"})

    def test_markdown_explains_work_result_impact_and_boundary(self):
        markdown = render_markdown(build_report(load_rows(INPUTS)))

        self.assertIn("MCP Adversarial Metadata Replay Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("nested schema poisoning", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "mcp_adversarial_metadata_replay"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_report(load_rows(INPUTS))
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

        self.assertEqual(len(load_payload(normalized)["actions"]), 8)
        self.assertIn("MCP Adversarial Metadata Replay Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))

    def test_docs_and_reviewer_bundle_link_replay(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        replay_doc = (ROOT / "docs" / "MCP_Adversarial_Metadata_Replay.md").read_text(encoding="utf-8")
        ai_bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        self.assertIn("docs/MCP_Adversarial_Metadata_Replay.md", readme)
        self.assertIn("docs/MCP_Adversarial_Metadata_Replay.md", ai_bundle)
        self.assertIn("python -m reference_engine.mcp_adversarial_metadata_replay", replay_doc)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from reference_engine.agent_security_benchmark_replay import (
    build_report,
    load_rows,
    normalize_rows,
    render_markdown,
    write_outputs,
)
from reference_engine.customer_evaluation import load_payload


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "agent_security_benchmark_metadata.json"


class AgentSecurityBenchmarkReplayTests(unittest.TestCase):
    def test_loads_metadata_only_rows_for_all_categories(self):
        rows = load_rows(INPUTS)

        self.assertEqual(len(rows), 6)
        self.assertEqual(
            {row["category"] for row in rows},
            {
                "exfiltration",
                "stored_injection",
                "privilege_escalation",
                "social_engineering",
                "multi_step",
                "inconsistency_probing",
            },
        )

    def test_normalizes_to_customer_evaluation_contract(self):
        payload = normalize_rows(load_rows(INPUTS))

        self.assertEqual(payload["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(len(payload["actions"]), 6)
        self.assertIn("upstream raw prompts", payload["data_boundary"])
        for action in payload["actions"]:
            self.assertEqual(action["context"]["source_name"], "Agent Security Benchmark")
            self.assertTrue(action["context"]["metadata_only"])
            self.assertIn("ref_gate", action)
            self.assertIn("tool_plan", action)

    def test_builds_report_with_restrained_attack_deltas_and_dll_evidence(self):
        report = build_report(load_rows(INPUTS))

        self.assertEqual(report["version"], "smerc.agent-security-benchmark-replay.v1")
        self.assertEqual(report["source_license"], "MIT")
        self.assertEqual(report["source_record_count"], 6)
        self.assertEqual(report["normalized_action_count"], 6)
        self.assertEqual(report["valid_dll_ledgers"], 6)
        self.assertIn("exfiltration", report["category_counts"])
        self.assertIn("SMERC_RESTRAINS_EXPECTED_ATTACK", report["delta_counts"])
        self.assertIn("SMERC_RESTRAINS_ENABLING_DISCLOSURE", report["delta_counts"])
        self.assertIn("not an official Agent Security Benchmark score", report["evidence_boundary"])

    def test_markdown_explains_work_result_impact_and_boundary(self):
        markdown = render_markdown(build_report(load_rows(INPUTS)))

        self.assertIn("Agent Security Benchmark Replay Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Governance Routing Workbench route counts", markdown)
        self.assertIn("not an official Agent Security Benchmark score", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_report_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "agent_security_benchmark_replay"
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

        self.assertEqual(len(load_payload(normalized)["actions"]), 6)
        self.assertIn("Agent Security Benchmark Replay Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))

    def test_docs_and_readme_link_replay(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        data_map = (ROOT / "docs" / "Runtime_Data_Source_Map.md").read_text(encoding="utf-8")
        replay_doc = (ROOT / "docs" / "Agent_Security_Benchmark_Replay.md").read_text(encoding="utf-8")
        ai_bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        for text in [readme, data_map, ai_bundle]:
            self.assertIn("docs/Agent_Security_Benchmark_Replay.md", text)
        self.assertIn("python -m reference_engine.agent_security_benchmark_replay", replay_doc)
        self.assertIn("not an official Agent Security Benchmark score", replay_doc)


if __name__ == "__main__":
    unittest.main()

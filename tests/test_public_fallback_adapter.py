import unittest
from pathlib import Path

from reference_engine.customer_evaluation import load_payload
from reference_engine.public_fallback_adapter import (
    build_fallback_adapter_report,
    load_fallback_examples,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "public_fallback_adapter_examples.json"


class PublicFallbackAdapterTests(unittest.TestCase):
    def test_loads_focused_source_profiles(self):
        rows = load_fallback_examples(INPUTS)

        self.assertEqual(len(rows), 6)
        self.assertEqual(
            {row["source_profile"] for row in rows},
            {"agent_action_boundary_benchmark", "agentshield_bench"},
        )

    def test_builds_customer_evaluation_backed_report(self):
        report = build_fallback_adapter_report(load_fallback_examples(INPUTS))

        self.assertEqual(report["version"], "smerc.public-fallback-adapter.v1")
        self.assertEqual(report["source_example_count"], 6)
        self.assertEqual(report["benchmark_report"]["customer_evaluation"]["summary"]["total_actions"], 6)
        self.assertEqual(report["benchmark_report"]["valid_dll_ledgers"], 6)
        self.assertIn("Agent Action Boundary-style drift", report["work_result_impact"]["result"])
        self.assertIn("replace these six public-pattern rows", report["replacement_metadata_ask"])

    def test_markdown_preserves_boundaries_and_ask(self):
        markdown = render_markdown(build_fallback_adapter_report(load_fallback_examples(INPUTS)))

        self.assertIn("Public Fallback Adapter Report", markdown)
        self.assertIn("Replacement Metadata Ask", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("not an official benchmark score", markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "public_fallback_adapter"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_fallback_adapter_report(load_fallback_examples(INPUTS))
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
        self.assertIn("Public Fallback Adapter Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))

    def test_docs_reference_runner(self):
        doc = (ROOT / "docs" / "Public_Fallback_Adapter.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.public_fallback_adapter", doc)
        self.assertIn("docs/Public_Fallback_Adapter.md", readme)


if __name__ == "__main__":
    unittest.main()

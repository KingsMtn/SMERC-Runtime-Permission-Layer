import unittest
from pathlib import Path

from reference_engine.customer_evaluation import load_payload
from reference_engine.public_benchmark_ingestion import (
    build_public_benchmark_ingestion_report,
    load_benchmark_examples,
    normalize_benchmark_examples,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "public_benchmark_ingestion_examples.json"


class PublicBenchmarkIngestionTests(unittest.TestCase):
    def test_loads_supported_public_benchmark_examples(self):
        rows = load_benchmark_examples(INPUTS)

        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["record_id"] for row in rows}), 10)

    def test_normalizes_examples_to_customer_evaluation_contract(self):
        payload = normalize_benchmark_examples(load_benchmark_examples(INPUTS))

        self.assertEqual(payload["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(len(payload["actions"]), 10)
        for action in payload["actions"]:
            self.assertIn("benchmark_family", action["context"])
            self.assertIn("source_reference", action["context"])
            self.assertIn("current_baseline_outcome", action["context"])
            self.assertIn("ref_gate", action)
            self.assertIn("tool_plan", action)

    def test_builds_report_with_deltas_and_valid_ledgers(self):
        report = build_public_benchmark_ingestion_report(load_benchmark_examples(INPUTS))

        self.assertEqual(report["version"], "smerc.public-benchmark-ingestion.v1")
        self.assertEqual(report["source_example_count"], 10)
        self.assertEqual(report["normalized_action_count"], 10)
        self.assertEqual(report["customer_evaluation"]["summary"]["total_actions"], 10)
        self.assertEqual(report["valid_dll_ledgers"], 10)
        self.assertGreaterEqual(report["delta_counts"].get("BASELINE_ALLOW_SMERC_ADDS_RESTRAINT", 0), 2)
        self.assertIn("mcp_tool_poisoning", report["benchmark_family_counts"])
        self.assertIn("official scores", report["evidence_boundary"])

    def test_markdown_explains_work_result_impact_and_boundary(self):
        markdown = render_markdown(build_public_benchmark_ingestion_report(load_benchmark_examples(INPUTS)))

        self.assertIn("Public Benchmark Ingestion Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("not official upstream datasets or scores", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_ingestion_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "public_benchmark_ingestion"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_public_benchmark_ingestion_report(load_benchmark_examples(INPUTS))
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

        self.assertEqual(len(load_payload(normalized)["actions"]), 10)
        self.assertIn("Public Benchmark Ingestion Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))

    def test_docs_and_readme_reference_public_benchmark_ingestion(self):
        docs = (ROOT / "docs" / "Public_Benchmark_Ingestion.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.public_benchmark_ingestion", docs)
        self.assertIn("representative public benchmark-shaped examples", docs)
        self.assertIn("docs/Public_Benchmark_Ingestion.md", readme)


if __name__ == "__main__":
    unittest.main()

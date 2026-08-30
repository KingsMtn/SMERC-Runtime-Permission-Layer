import unittest
from pathlib import Path

from reference_engine.serious_report_performance import (
    VERSION,
    build_performance_report,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class SeriousReportPerformanceTests(unittest.TestCase):
    def test_builds_performance_report_for_serious_paths(self):
        report = build_performance_report(root=ROOT, iterations=2)

        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["workload_count"], 4)
        self.assertEqual(report["iterations_per_workload"], 2)
        self.assertIn(report["status"], {"ready_for_local_review", "measure_in_customer_environment"})
        self.assertGreaterEqual(report["slowest_p95_ms"], 0)
        self.assertIn("not prove production", report["evidence_boundary"])

        workload_ids = {record["workload_id"] for record in report["records"]}
        self.assertIn("customer_evaluation_general", workload_ids)
        self.assertIn("cloud_metadata_connector", workload_ids)
        self.assertIn("public_benchmark_ingestion", workload_ids)
        self.assertIn("postcondition_evidence", workload_ids)

        for record in report["records"]:
            latency = record["latency_ms"]
            self.assertEqual(latency["sample_count"], 2)
            self.assertGreaterEqual(latency["p50_ms"], 0)
            self.assertGreaterEqual(latency["p95_ms"], 0)
            self.assertGreaterEqual(latency["maximum_ms"], 0)
            self.assertTrue(record["result_facts"])

    def test_markdown_includes_work_result_impact_and_reviewer_question(self):
        markdown = render_markdown(build_performance_report(root=ROOT, iterations=1))

        self.assertIn("# SMERC Serious Report Performance", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("public_benchmark_ingestion", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "serious_report_performance"
        report = build_performance_report(root=ROOT, iterations=1)
        json_path = scratch / "performance.json"
        markdown_path = scratch / "performance.md"

        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertIn("serious-report-performance", json_path.read_text(encoding="utf-8"))
        self.assertIn("SMERC Serious Report Performance", markdown_path.read_text(encoding="utf-8"))

    def test_docs_and_readme_reference_serious_report_performance(self):
        docs = (ROOT / "docs" / "Serious_Report_Performance.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.serious_report_performance", docs)
        self.assertIn("production latency", docs)
        self.assertIn("docs/Serious_Report_Performance.md", readme)
        self.assertIn("serious report performance", bundle.lower())


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from reference_engine.postcondition_evidence import load_json_object
from reference_engine.trace_evidence_adapter import (
    EVIDENCE_BOUNDARY,
    VERSION,
    build_trace_adapter_report,
    load_trace_evidence,
    render_trace_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "reports" / "public_benchmark_customer_evaluation" / "customer_evaluation_report.json"
TRACE_EXAMPLES = ROOT / "examples" / "trace_runtime_evidence_examples.json"


class TraceEvidenceAdapterTests(unittest.TestCase):
    def test_builds_trace_style_postcondition_report(self):
        report = build_trace_adapter_report(load_json_object(EVALUATION), load_trace_evidence(TRACE_EXAMPLES))

        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["status"], "limited_trace_style_review")
        self.assertEqual(report["accepted_rows"], 3)
        self.assertEqual(report["skipped_rows"], 1)
        self.assertIn("trace_style_metadata_only", report["attestation_class_counts"])
        self.assertIn("raw_attestation", report["skipped"][0]["reason"])
        self.assertIn("does not implement TRACE", report["evidence_boundary"])
        self.assertIn("prove Linux Foundation endorsement", report["evidence_boundary"])
        self.assertIsNotNone(report["postcondition_report"])
        self.assertEqual(report["postcondition_report"]["observed_actions"], 3)
        self.assertGreaterEqual(report["postcondition_report"]["postcondition_status_counts"].get("gap", 0), 1)

    def test_markdown_preserves_boundaries(self):
        report = build_trace_adapter_report(load_json_object(EVALUATION), load_trace_evidence(TRACE_EXAMPLES))
        markdown = render_trace_markdown(report)

        self.assertIn("TRACE-Style Evidence Adapter Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("does not implement TRACE", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "trace_evidence_adapter"
        report = build_trace_adapter_report(load_json_object(EVALUATION), load_trace_evidence(TRACE_EXAMPLES))

        write_outputs(
            report,
            json_path=scratch / "trace_evidence_adapter_report.json",
            markdown_path=scratch / "TRACE_Evidence_Adapter_Report.md",
        )

        self.assertIn("trace-evidence-adapter", (scratch / "trace_evidence_adapter_report.json").read_text(encoding="utf-8"))
        self.assertIn("TRACE-Style Evidence Adapter Report", (scratch / "TRACE_Evidence_Adapter_Report.md").read_text(encoding="utf-8"))
        self.assertIn("SMERC Postcondition Evidence Report", (scratch / "TRACE_Style_Postcondition_Evidence.md").read_text(encoding="utf-8"))

    def test_docs_and_alignment_reference_trace_adapter(self):
        docs = (ROOT / "docs" / "TRACE_Evidence_Adapter.md").read_text(encoding="utf-8")
        linux = (ROOT / "docs" / "Linux_Foundation_Standards_Alignment.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.trace_evidence_adapter", docs)
        self.assertIn("does not implement TRACE", docs)
        self.assertIn("future TRACE-compatible evidence adapter path", linux)
        self.assertIn("docs/TRACE_Evidence_Adapter.md", readme)
        self.assertIn("does not implement TRACE", EVIDENCE_BOUNDARY)
        self.assertIn("prove TRACE compatibility", EVIDENCE_BOUNDARY)
        self.assertIn("prove Linux Foundation endorsement", EVIDENCE_BOUNDARY)


if __name__ == "__main__":
    unittest.main()

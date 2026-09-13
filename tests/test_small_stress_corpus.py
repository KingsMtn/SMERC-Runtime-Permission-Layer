import unittest
from pathlib import Path

from reference_engine.customer_evaluation import load_payload
from reference_engine.small_stress_corpus import (
    build_small_stress_corpus,
    build_stress_corpus_report,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class SmallStressCorpusTests(unittest.TestCase):
    def test_builds_valid_customer_evaluation_payload(self):
        payload = build_small_stress_corpus()

        self.assertEqual(payload["version"], "smerc.customer-evaluation.v1")
        self.assertEqual(len(payload["actions"]), 12)
        self.assertIn("metadata-only", payload["data_boundary"])
        self.assertEqual(
            {action["context"]["data_origin"] for action in payload["actions"]},
            {"project_generated_stress_corpus"},
        )

    def test_report_runs_through_customer_evaluation(self):
        report = build_stress_corpus_report(build_small_stress_corpus())

        self.assertEqual(report["version"], "smerc.small-generated-stress-corpus.v1")
        self.assertEqual(report["corpus_action_count"], 12)
        self.assertEqual(report["customer_evaluation"]["summary"]["total_actions"], 12)
        self.assertEqual(report["customer_evaluation"]["summary"]["valid_ledgers"], 12)
        self.assertGreaterEqual(len(report["customer_evaluation"]["summary"]["posture_counts"]), 3)
        self.assertIn("financial_velocity_bounds", report["pattern_family_counts"])
        self.assertIn("not customer validation", report["evidence_boundary"])

    def test_markdown_preserves_replacement_ask_and_boundary(self):
        markdown = render_markdown(build_stress_corpus_report(build_small_stress_corpus()))

        self.assertIn("Small Generated Stress Corpus Report", markdown)
        self.assertIn("Replacement Metadata Ask", markdown)
        self.assertIn("5 to 25 metadata-only actions", markdown)
        self.assertIn("not customer validation", markdown)

    def test_writes_outputs_and_docs_reference_runner(self):
        scratch = ROOT / "tests" / "_tmp" / "small_stress_corpus"
        payload = build_small_stress_corpus()
        report = build_stress_corpus_report(payload)
        corpus = scratch / "corpus.json"
        report_json = scratch / "report.json"
        report_md = scratch / "report.md"
        customer_json = scratch / "customer.json"
        customer_md = scratch / "customer.md"

        write_outputs(
            payload,
            report,
            corpus_output=corpus,
            json_output=report_json,
            markdown_output=report_md,
            customer_json_output=customer_json,
            customer_markdown_output=customer_md,
        )

        self.assertEqual(len(load_payload(corpus)["actions"]), 12)
        self.assertIn("Small Generated Stress Corpus Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))
        self.assertIn(
            "python -m reference_engine.small_stress_corpus",
            (ROOT / "docs" / "Small_Generated_Stress_Corpus.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "docs/Small_Generated_Stress_Corpus.md",
            (ROOT / "README.md").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from reference_engine.reviewer_quickstart import build_reviewer_quickstart, render_markdown, write_report


ROOT = Path(__file__).resolve().parents[1]
TEST_OUTPUTS = ROOT / "test_outputs" / "reviewer_quickstart"
TEST_OUTPUTS.mkdir(parents=True, exist_ok=True)


class ReviewerQuickstartTests(unittest.TestCase):
    def test_reviewer_quickstart_generates_connected_artifacts(self):
        output_dir = TEST_OUTPUTS / "quickstart"
        audit_db = TEST_OUTPUTS / "quickstart.sqlite3"
        report = build_reviewer_quickstart(output_dir=output_dir, audit_db=audit_db)
        write_report(report, output_dir=output_dir)

        self.assertEqual(report["version"], "smerc.reviewer-quickstart.v1")
        self.assertEqual(report["review_question"], "Is SMERC credible enough to test in a bounded shadow-mode pilot?")
        self.assertIn("not customer validation", report["not_a_claim"])
        self.assertGreaterEqual(report["proof_highlights"]["benchmark_total_scenarios"], 1)
        self.assertGreaterEqual(report["proof_highlights"]["seeded_ciso_decisions"], 1)
        self.assertGreaterEqual(report["proof_highlights"]["ref_gate_failure_count"], 1)
        self.assertGreaterEqual(report["proof_highlights"]["ref_gated_scoring_capped_count"], 1)
        self.assertTrue(report["proof_highlights"]["dll_verification_valid"])

        for key in (
            "summary_markdown",
            "summary_json",
            "pr_guardian_demo",
            "sparta_route",
            "decision_lifecycle_ledger",
            "dll_intelligence",
            "ciso_seed_report",
            "runtime_benchmark",
            "ref_gated_runtime_proof",
        ):
            self.assertTrue((output_dir / Path(report["artifacts"][key]).name).exists())

        self.assertTrue((output_dir / "Reviewer_Quickstart_Report.md").exists())
        self.assertTrue((output_dir / "reviewer_quickstart.json").exists())

    def test_markdown_keeps_claim_boundary(self):
        output_dir = TEST_OUTPUTS / "markdown"
        audit_db = TEST_OUTPUTS / "markdown.sqlite3"
        report = build_reviewer_quickstart(output_dir=output_dir, audit_db=audit_db)
        markdown = render_markdown(report)

        self.assertIn("What This Proves", markdown)
        self.assertIn("What This Does Not Prove", markdown)
        self.assertIn("customer demand", markdown)
        self.assertIn("shadow-mode pilot", markdown)
        self.assertIn("Ref-gated requests", markdown)

    def test_readme_links_reviewer_quickstart(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Reviewer_Quickstart.md", readme)
        quickstart = (ROOT / "docs" / "Reviewer_Quickstart.md").read_text()
        self.assertIn("hard evidence gates before recoverability scoring", quickstart)


if __name__ == "__main__":
    unittest.main()

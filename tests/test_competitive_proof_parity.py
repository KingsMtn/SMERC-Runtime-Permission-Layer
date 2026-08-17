import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.competitive_proof_parity import (
    COMPETITIVE_PROOF_PARITY_VERSION,
    build_competitive_proof_parity_report,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "Competitive_Proof_Parity_Harness.md"
README = ROOT / "README.md"


class CompetitiveProofParityTests(unittest.TestCase):
    def test_builds_all_competitive_proof_categories(self):
        report = build_competitive_proof_parity_report(root=ROOT)

        self.assertEqual(report["version"], COMPETITIVE_PROOF_PARITY_VERSION)
        self.assertEqual(report["summary"]["proof_categories_covered"], 7)
        for key in [
            "catalog_evidence",
            "runtime_decision_evidence",
            "proxy_enforcement_evidence",
            "benchmark_evidence",
            "public_incident_replay_evidence",
            "production_like_simulation_evidence",
            "operational_evidence",
        ]:
            self.assertIn(key, report["sections"])
            self.assertGreater(report["sections"][key]["record_count"], 0)

    def test_report_has_benchmark_proxy_and_ledger_metrics(self):
        report = build_competitive_proof_parity_report(root=ROOT)

        self.assertGreater(report["sections"]["benchmark_evidence"]["key_metrics"]["decision_difference_rate"], 0)
        self.assertGreaterEqual(report["sections"]["proxy_enforcement_evidence"]["key_metrics"]["valid_ledger_count"], 3)
        self.assertEqual(
            report["sections"]["production_like_simulation_evidence"]["key_metrics"]["valid_ledger_count"],
            report["sections"]["production_like_simulation_evidence"]["record_count"],
        )
        self.assertEqual(report["sections"]["operational_evidence"]["key_metrics"]["operational_status"], "ready")

    def test_markdown_blocks_overclaims(self):
        markdown = render_markdown(build_competitive_proof_parity_report(root=ROOT))

        self.assertIn("proof-category parity", markdown)
        self.assertIn("does not claim that SMERC is better", markdown)
        self.assertIn("customer-validated incident reduction", markdown)
        self.assertIn("superiority over a named competitor", markdown)

    def test_output_writers_create_files(self):
        report = build_competitive_proof_parity_report(root=ROOT)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "parity.json"
            markdown_path = Path(directory) / "parity.md"
            write_outputs(report, json_path=json_path, markdown_path=markdown_path)
            parsed = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["version"], COMPETITIVE_PROOF_PARITY_VERSION)
            self.assertIn("# SMERC Competitive Proof Parity Report", markdown_path.read_text(encoding="utf-8"))

    def test_docs_and_readme_link_harness(self):
        self.assertIn("python -m reference_engine.competitive_proof_parity", DOC.read_text(encoding="utf-8"))
        self.assertIn("docs/Competitive_Proof_Parity_Harness.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

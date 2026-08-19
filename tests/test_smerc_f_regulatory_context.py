import unittest
from pathlib import Path

from reference_engine.smerc_f_regulatory_context import (
    build_regulatory_context_report,
    enrich_rows_with_regulatory_context,
    load_regulatory_contexts,
    render_markdown,
    score_regulatory_context,
    write_outputs,
)
from reference_engine.smerc_f_source_ingestion import load_source_exports, normalize_source_exports


ROOT = Path(__file__).resolve().parents[1]
SOURCE_EXPORTS = ROOT / "examples" / "smerc_f_source_exports.json"
CONTEXTS = ROOT / "examples" / "smerc_f_regulatory_context_examples.json"


class SMERCFRegulatoryContextTests(unittest.TestCase):
    def test_loads_regulatory_contexts(self):
        contexts = load_regulatory_contexts(CONTEXTS)

        self.assertEqual(len(contexts), 6)
        self.assertEqual(len({context["action_id"] for context in contexts}), 6)

    def test_scores_regulatory_context_without_legal_conclusion(self):
        context = load_regulatory_contexts(CONTEXTS)[4]
        score = score_regulatory_context(context)

        self.assertGreater(score["regulatory_context_score"], 0.5)
        self.assertIn(score["regulatory_context_tier"], {"watch", "elevated", "critical"})
        self.assertIn("CUSTOMER_IMPACT_RADIUS", score["regulatory_reason_codes"])

    def test_enriches_source_rows_before_replay(self):
        rows = normalize_source_exports(load_source_exports(SOURCE_EXPORTS))
        enriched = enrich_rows_with_regulatory_context(rows, load_regulatory_contexts(CONTEXTS))

        self.assertEqual(len(enriched), len(rows))
        by_id = {row["source_id"]: row for row in enriched}
        self.assertIn("regulatory_context_score", by_id["DEFILLAMA_ORACLE_INCIDENT_005"])
        self.assertLess(
            by_id["DEFILLAMA_ORACLE_INCIDENT_005"]["evidence_source_quality"],
            next(row for row in rows if row["source_id"] == "DEFILLAMA_ORACLE_INCIDENT_005")["evidence_source_quality"],
        )

    def test_builds_context_comparison_report(self):
        report = build_regulatory_context_report(
            load_source_exports(SOURCE_EXPORTS),
            load_regulatory_contexts(CONTEXTS),
        )

        self.assertEqual(report["version"], "smerc-f.regulatory-context.v1")
        self.assertEqual(report["source_export_count"], 6)
        self.assertEqual(report["regulatory_context_count"], 6)
        self.assertEqual(report["scenario_count"], 30)
        self.assertIn("Regulatory context overlay only", report["evidence_boundary"])
        self.assertIn("baseline_state_counts", report)
        self.assertIn("context_enriched_state_counts", report)

    def test_writes_context_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "smerc_f_regulatory_context"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_regulatory_context_report(
            load_source_exports(SOURCE_EXPORTS),
            load_regulatory_contexts(CONTEXTS),
        )
        enriched = scratch / "enriched.json"
        report_json = scratch / "report.json"
        report_md = scratch / "report.md"
        replay_json = scratch / "replay.json"
        replay_md = scratch / "replay.md"

        write_outputs(
            report,
            enriched_output=enriched,
            json_output=report_json,
            markdown_output=report_md,
            replay_json_output=replay_json,
            replay_markdown_output=replay_md,
        )

        self.assertIn("regulatory_context_score", enriched.read_text(encoding="utf-8"))
        self.assertIn("SMERC-F Regulatory Context Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC-F Financial Public-Data Replay Report", replay_md.read_text(encoding="utf-8"))

    def test_markdown_keeps_claims_bounded(self):
        markdown = render_markdown(
            build_regulatory_context_report(load_source_exports(SOURCE_EXPORTS), load_regulatory_contexts(CONTEXTS))
        )

        self.assertIn("without claiming legal compliance", markdown)
        self.assertIn("does not interpret law", markdown)
        self.assertIn("Do not use it as legal advice", markdown)

    def test_docs_and_readme_link_regulatory_context(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "SMERC_F_Regulatory_Context_Profile.md").read_text(encoding="utf-8")

        self.assertIn("reference_engine.smerc_f_regulatory_context", readme)
        self.assertIn("docs/SMERC_F_Regulatory_Context_Profile.md", readme)
        self.assertIn("permitted issuer status", docs)
        self.assertIn("not legal conclusions", docs)


if __name__ == "__main__":
    unittest.main()

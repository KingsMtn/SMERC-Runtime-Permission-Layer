import unittest
from pathlib import Path

from reference_engine.smerc_f_public_data_replay import load_public_rows
from reference_engine.smerc_f_source_ingestion import (
    build_ingestion_report,
    load_source_exports,
    normalize_source_exports,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "smerc_f_source_exports.json"


class SMERCFSourceIngestionTests(unittest.TestCase):
    def test_loads_supported_source_exports(self):
        rows = load_source_exports(INPUTS)

        self.assertEqual(len(rows), 6)
        self.assertEqual(len({row["record_id"] for row in rows}), 6)

    def test_normalizes_exports_to_public_replay_contract(self):
        normalized = normalize_source_exports(load_source_exports(INPUTS))

        self.assertEqual(len(normalized), 6)
        self.assertEqual(len({row["source_id"] for row in normalized}), 6)
        for row in normalized:
            self.assertIn(row["source_type"], {
                "chainabuse_report",
                "defillama_hack_incident",
                "dune_stablecoin_transfer",
                "elliptic_bitcoin_graph",
                "ethereum_bigquery_transfer",
            })
            for field in [
                "evidence_source_quality",
                "settlement_finality",
                "recipient_reputation",
                "liquidity_concentration_observed",
                "counterparty_concentration_observed",
                "market_stress_observed",
                "anomaly_observed",
                "automation_velocity_observed",
            ]:
                self.assertGreaterEqual(row[field], 0.0)
                self.assertLessEqual(row[field], 1.0)

    def test_builds_ingestion_report_and_replay_summary(self):
        report = build_ingestion_report(load_source_exports(INPUTS))

        self.assertEqual(report["version"], "smerc-f.source-ingestion.v1")
        self.assertEqual(report["source_export_count"], 6)
        self.assertEqual(report["normalized_row_count"], 6)
        self.assertEqual(report["scenario_count"], 30)
        self.assertGreater(report["restraint_rate"], 0)
        self.assertIn("does not call vendor APIs", report["evidence_boundary"])
        self.assertIn("defillama_hack_incident", report["source_format_counts"])

    def test_writes_ingestion_and_replay_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "smerc_f_source_ingestion"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_ingestion_report(load_source_exports(INPUTS))
        normalized = scratch / "normalized.json"
        report_json = scratch / "report.json"
        report_md = scratch / "report.md"
        replay_json = scratch / "replay.json"
        replay_md = scratch / "replay.md"

        write_outputs(
            report,
            normalized_output=normalized,
            json_output=report_json,
            markdown_output=report_md,
            replay_json_output=replay_json,
            replay_markdown_output=replay_md,
        )

        self.assertEqual(len(load_public_rows(normalized)), 6)
        self.assertIn("SMERC-F Source Ingestion Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC-F Financial Public-Data Replay Report", replay_md.read_text(encoding="utf-8"))

    def test_markdown_keeps_source_claims_bounded(self):
        markdown = render_markdown(build_ingestion_report(load_source_exports(INPUTS)))

        self.assertIn("not customer validation", markdown)
        self.assertIn("does not call vendor APIs", markdown)
        self.assertIn("Existing AML, fraud, blockchain analytics", markdown)

    def test_docs_and_readme_link_source_ingestion(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "SMERC_F_Financial_Source_Ingestion.md").read_text(encoding="utf-8")

        self.assertIn("reference_engine.smerc_f_source_ingestion", readme)
        self.assertIn("docs/SMERC_F_Financial_Source_Ingestion.md", readme)
        self.assertIn("Fortune 500 financial-services", docs)
        self.assertIn("exported metadata", docs)


if __name__ == "__main__":
    unittest.main()

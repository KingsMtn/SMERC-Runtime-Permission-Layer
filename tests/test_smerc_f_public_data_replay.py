import unittest
from pathlib import Path

from reference_engine.smerc_f_public_data_replay import (
    build_replay_report,
    expand_public_rows,
    load_public_rows,
    render_markdown,
    row_to_financial_action,
)


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "smerc_f_public_data_replay_inputs.json"


class SMERCFPublicDataReplayTests(unittest.TestCase):
    def test_loads_public_data_rows(self):
        rows = load_public_rows(INPUTS)

        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["source_id"] for row in rows}), 10)

    def test_expands_rows_into_50_replay_actions(self):
        actions = expand_public_rows(load_public_rows(INPUTS))

        self.assertEqual(len(actions), 50)
        self.assertEqual(len({action["action_id"] for action in actions}), 50)

    def test_row_to_financial_action_matches_smerc_f_contract(self):
        action = row_to_financial_action(load_public_rows(INPUTS)[0])

        for field in [
            "authorization_support",
            "evidence_validity",
            "reversibility",
            "liquidity_concentration",
            "collateral_stress",
            "settlement_anomaly",
            "stablecoin_imbalance",
            "counterparty_concentration",
            "market_instability",
            "model_disagreement",
            "agent_velocity",
        ]:
            self.assertGreaterEqual(action[field], 0.0)
            self.assertLessEqual(action[field], 1.0)

    def test_builds_bounded_public_data_replay_report(self):
        report = build_replay_report(load_public_rows(INPUTS))

        self.assertEqual(report["version"], "smerc-f.public-data-replay.v1")
        self.assertEqual(report["source_row_count"], 10)
        self.assertEqual(report["scenario_count"], 50)
        self.assertIn("Public-data-shaped replay only", report["evidence_boundary"])
        self.assertGreater(report["restraint_count"], 0)
        self.assertGreater(report["decision_delta_count"], 0)
        self.assertEqual(len(report["highest_exposure_records"]), 10)

    def test_markdown_keeps_financial_claims_bounded(self):
        markdown = render_markdown(build_replay_report(load_public_rows(INPUTS)))

        self.assertIn("SMERC-F Financial Public-Data Replay Report", markdown)
        self.assertIn("not customer validation", markdown)
        self.assertIn("not whether SMERC-F replaces", markdown)
        self.assertIn("Dune stablecoin", markdown)

    def test_docs_and_readme_link_public_data_replay(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "SMERC_F_Financial_Public_Data_Replay.md").read_text(encoding="utf-8")

        self.assertIn("reference_engine.smerc_f_public_data_replay", readme)
        self.assertIn("docs/SMERC_F_Financial_Public_Data_Replay.md", readme)
        self.assertIn("Fortune 500", docs)
        self.assertIn("metadata-only action examples", docs)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from reference_engine.smerc_f_external_signals import (
    FINANCIAL_ACTION_TAXONOMY,
    SUPPORTED_SIGNAL_PROVIDERS,
    build_external_signal_report,
    external_signals_to_financial_action,
    load_external_signal_actions,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "smerc_f_external_signal_examples.json"


class SMERCFExternalSignalsTests(unittest.TestCase):
    def test_loads_external_signal_actions(self):
        rows = load_external_signal_actions(INPUTS)

        self.assertEqual(len(rows), 6)
        self.assertIn("stablecoin_redemption", FINANCIAL_ACTION_TAXONOMY)
        self.assertIn("wallet_screening", SUPPORTED_SIGNAL_PROVIDERS)

    def test_normalizes_external_signals_to_financial_action(self):
        row = load_external_signal_actions(INPUTS)[0]
        action = external_signals_to_financial_action(row)

        self.assertEqual(action["action_id"], "SMERCF_EXT_STABLECOIN_REDEMPTION_001")
        self.assertEqual(action["action_type"], "stablecoin_redemption")
        self.assertGreater(action["stablecoin_imbalance"], 0.5)
        self.assertGreaterEqual(action["evidence_validity"], 0.0)
        self.assertLessEqual(action["evidence_validity"], 1.0)

    def test_builds_external_signal_report(self):
        report = build_external_signal_report(load_external_signal_actions(INPUTS))

        self.assertEqual(report["version"], "smerc-f.external-signals.v1")
        self.assertEqual(report["input_action_count"], 6)
        self.assertGreaterEqual(report["taxonomy_action_count"], 12)
        self.assertGreater(report["authorized_restraint_count"], 0)
        self.assertIn("stablecoin_reserve_monitor", report["provider_counts"])
        self.assertIn("does not perform AML compliance", report["evidence_boundary"])

    def test_markdown_explains_boundary_and_impact(self):
        markdown = render_markdown(build_external_signal_report(load_external_signal_actions(INPUTS)))

        self.assertIn("SMERC-F External Financial Signal Adapter Report", markdown)
        self.assertIn("not to replace AML", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Financial Action Taxonomy", markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "smerc_f_external_signals"
        scratch.mkdir(parents=True, exist_ok=True)
        json_output = scratch / "report.json"
        markdown_output = scratch / "report.md"

        write_outputs(
            build_external_signal_report(load_external_signal_actions(INPUTS)),
            json_output,
            markdown_output,
        )

        self.assertTrue(json_output.exists())
        self.assertIn("External Financial Signal", markdown_output.read_text(encoding="utf-8"))

    def test_docs_and_readme_reference_external_signals(self):
        docs = (ROOT / "docs" / "SMERC_F_External_Financial_Signals.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("SMERC-F can consume outputs", docs)
        self.assertIn("reference_engine.smerc_f_external_signals", readme)


if __name__ == "__main__":
    unittest.main()

import copy
import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.pilot_ledger_metrics import (
    PILOT_LEDGER_METRICS_VERSION,
    build_metrics,
    load_ledgers,
    render_markdown,
    summarize_ledgers,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "reports" / "pilot_ledger_intake_result.json"


class PilotLedgerMetricsTests(unittest.TestCase):
    def test_builds_metrics_with_explicit_denominators(self):
        metrics = build_metrics([RESULT])
        summary = metrics["summary"]
        self.assertEqual(metrics["version"], PILOT_LEDGER_METRICS_VERSION)
        self.assertEqual(summary["ledger_count"], 1)
        self.assertEqual(summary["valid_ledger_count"], 1)
        self.assertEqual(summary["complete_lifecycle_count"], 1)
        self.assertEqual(summary["human_reviewed_count"], 1)
        self.assertEqual(summary["reviewer_agreement_rate"], 1.0)
        self.assertEqual(summary["execution_success_rate"], 1.0)
        self.assertEqual(summary["judged_correct_rate"], 1.0)
        self.assertIn("below 30 ledgers", " ".join(metrics["caveats"]))

    def test_invalid_hash_chain_is_reported_without_contributing_metrics(self):
        ledger = load_ledgers([RESULT])[0]
        tampered = copy.deepcopy(ledger)
        tampered["records"][2]["payload"]["authorization_recommendation"] = "ALLOW"
        summary = summarize_ledgers([tampered])
        self.assertEqual(summary["valid_ledger_count"], 0)
        self.assertEqual(summary["invalid_ledger_count"], 1)
        self.assertEqual(summary["complete_lifecycle_count"], 0)

    def test_decision_time_only_ledgers_do_not_invent_rates(self):
        completed = load_ledgers([RESULT])[0]
        decision_time_only = copy.deepcopy(completed)
        decision_time_only["records"] = decision_time_only["records"][:3]
        decision_time_only["record_count"] = 3
        # Rebuild a valid shortened ledger through the stored first three records.
        from reference_engine.decision_lifecycle_ledger import DecisionLifecycleLedger

        shortened = DecisionLifecycleLedger(
            decision_time_only["decision_id"],
            decision_time_only["tenant_id"],
            decision_time_only["records"],
        ).to_dict()
        summary = summarize_ledgers([shortened])
        self.assertEqual(summary["complete_lifecycle_count"], 0)
        self.assertEqual(summary["execution_success_rate"], None)
        self.assertEqual(summary["judged_correct_rate"], None)

    def test_markdown_and_writers_disclose_caveats(self):
        metrics = build_metrics([RESULT])
        markdown = render_markdown(metrics)
        self.assertIn("not proof of production risk reduction", markdown)
        self.assertIn("Sample size is below 30", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "metrics.json"
            markdown_path = Path(directory) / "metrics.md"
            write_outputs(metrics, json_path, markdown_path)
            parsed = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["summary"]["ledger_count"], 1)
            self.assertIn("# SMERC Pilot Ledger Metrics Report", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

import copy
import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.pilot_ledger_intake import (
    PILOT_LEDGER_INTAKE_VERSION,
    PILOT_LEDGER_RESULT_VERSION,
    apply_pilot_intake,
    load_intake,
    load_ledger_source,
    render_result_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "reports" / "runtime_benchmark_dll_bundle.json"
INTAKE = ROOT / "examples" / "pilot_ledger_intake_example.json"


class PilotLedgerIntakeTests(unittest.TestCase):
    def test_example_intake_completes_decision_lifecycle_without_breaking_hash_chain(self):
        intake = load_intake(INTAKE)
        self.assertEqual(intake["version"], PILOT_LEDGER_INTAKE_VERSION)
        ledger = load_ledger_source(BUNDLE, decision_id=intake["decision_id"])
        result = apply_pilot_intake(ledger, intake)
        self.assertEqual(result["version"], PILOT_LEDGER_RESULT_VERSION)
        self.assertEqual(result["records_before"], 3)
        self.assertEqual(result["records_appended"], 4)
        self.assertEqual(result["records_after"], 7)
        self.assertTrue(result["verification"]["valid"])
        self.assertTrue(result["summary"]["judged_correct"])
        self.assertEqual(result["summary"]["pending_learning_recommendations"], 1)

    def test_rejects_intake_for_wrong_decision(self):
        intake = load_intake(INTAKE)
        bad = copy.deepcopy(intake)
        bad["decision_id"] = "dll:wrong"
        ledger = load_ledger_source(BUNDLE, decision_id=intake["decision_id"])
        with self.assertRaises(ValueError):
            apply_pilot_intake(ledger, bad)

    def test_rejects_out_of_order_outcome_before_execution(self):
        intake = load_intake(INTAKE)
        bad = copy.deepcopy(intake)
        bad["events"] = [event for event in bad["events"] if event["event_type"] == "OUTCOME"]
        ledger = load_ledger_source(BUNDLE, decision_id=intake["decision_id"])
        with self.assertRaises(ValueError):
            apply_pilot_intake(ledger, bad)

    def test_rejects_duplicate_execution_event(self):
        intake = load_intake(INTAKE)
        bad = copy.deepcopy(intake)
        execution = [event for event in intake["events"] if event["event_type"] == "EXECUTION"][0]
        bad["events"].insert(2, copy.deepcopy(execution))
        ledger = load_ledger_source(BUNDLE, decision_id=intake["decision_id"])
        with self.assertRaises(ValueError):
            apply_pilot_intake(ledger, bad)

    def test_markdown_and_writers_state_boundary(self):
        intake = load_intake(INTAKE)
        result = apply_pilot_intake(load_ledger_source(BUNDLE, decision_id=intake["decision_id"]), intake)
        markdown = render_result_markdown(result)
        self.assertIn("does not certify", markdown)
        with tempfile.TemporaryDirectory() as directory:
            json_path = Path(directory) / "result.json"
            markdown_path = Path(directory) / "result.md"
            ledger_markdown_path = Path(directory) / "ledger.md"
            write_outputs(result, json_path, markdown_path, ledger_markdown_path)
            parsed = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["records_after"], 7)
            self.assertIn("# SMERC Pilot Ledger Intake Result", markdown_path.read_text(encoding="utf-8"))
            self.assertIn("# SMERC Decision Lifecycle Ledger Report", ledger_markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.complete_lifecycle_proof import (
    COMPLETE_LIFECYCLE_PROOF_VERSION,
    build_complete_lifecycle_proof,
    load_json,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "complete_lifecycle" / "lifecycle_case.json"
DOC = ROOT / "docs" / "Complete_Lifecycle_Proof.md"
TEST_OUTPUTS = ROOT / "test_outputs"
TEST_OUTPUTS.mkdir(exist_ok=True)


class CompleteLifecycleProofTests(unittest.TestCase):
    def test_reference_case_completes_full_lifecycle(self):
        report = build_complete_lifecycle_proof(load_json(CASE))
        summary = report["summary"]

        self.assertEqual(report["version"], COMPLETE_LIFECYCLE_PROOF_VERSION)
        self.assertEqual(summary["overall_status"], "COMPLETE")
        self.assertEqual(summary["runtime_admission"], "ADMIT")
        self.assertFalse(summary["admission_skipped_scoring"])
        self.assertEqual(summary["initial_posture"], "FREEZE")
        self.assertEqual(summary["initial_route"], "PAUSE")
        self.assertEqual(summary["unlock_state"], "UNLOCK")
        self.assertEqual(summary["continuation_posture"], "THROTTLE")
        self.assertEqual(summary["continuation_route"], "CONSTRAINED_EXECUTE")
        self.assertTrue(summary["permit_issued"])
        self.assertTrue(summary["permit_verified"])
        self.assertEqual(summary["execution_status"], "succeeded")
        self.assertTrue(summary["ledger_valid"])

    def test_permit_is_bound_to_continuation_action_and_controls(self):
        report = build_complete_lifecycle_proof(load_json(CASE))
        permit = report["action_bound_permit"]
        continuation = report["continuation_decision"]
        route = report["continuation_sparta_route"]

        self.assertEqual(permit["permit"]["action_hash"], continuation["action_hash"])
        self.assertEqual(permit["verification"]["authorization"], "constrain")
        for control in permit["verification"]["required_controls"]:
            self.assertIn(control, set(continuation["controls"]) | set(route["applied_controls"]))

    def test_ledger_contains_all_required_lifecycle_events(self):
        report = build_complete_lifecycle_proof(load_json(CASE))
        ledger = report["decision_lifecycle_ledger"]
        events = [record["event_type"] for record in ledger["records"]]

        self.assertEqual(
            events,
            [
                "REQUEST",
                "EVIDENCE",
                "EVALUATION",
                "HUMAN_INTERACTION",
                "EXECUTION",
                "OUTCOME",
                "LEARNING_RECOMMENDATION",
            ],
        )
        self.assertTrue(ledger["verification"]["valid"])

    def test_self_unlock_attempt_does_not_complete(self):
        case = load_json(CASE)
        case["recovery_authority"]["unlock_actor"]["actor_id"] = case["proposed_action"]["action"]["actor"]

        report = build_complete_lifecycle_proof(case)

        self.assertEqual(report["summary"]["overall_status"], "REVIEW")
        self.assertEqual(report["summary"]["unlock_state"], "DENY_UNLOCK")
        self.assertFalse(report["summary"]["permit_issued"])
        self.assertEqual(report["summary"]["execution_status"], "blocked")

    def test_markdown_and_doc_explain_work_result_impact_and_boundary(self):
        report = build_complete_lifecycle_proof(load_json(CASE))
        markdown = render_markdown(report)
        doc = DOC.read_text(encoding="utf-8")

        for phrase in ["Work", "Result", "Impact", "Boundary"]:
            self.assertIn(phrase, markdown)
            self.assertIn(phrase, doc)
        self.assertIn("cannot unlock itself", doc)

    def test_writes_outputs(self):
        report = build_complete_lifecycle_proof(load_json(CASE))
        paths = write_outputs(report, TEST_OUTPUTS / "complete_lifecycle")

        json_path = ROOT / paths["json"]
        markdown_path = ROOT / paths["markdown"]
        self.assertIn(COMPLETE_LIFECYCLE_PROOF_VERSION, json_path.read_text(encoding="utf-8"))
        self.assertIn("SMERC Complete Lifecycle Proof Report", markdown_path.read_text(encoding="utf-8"))

    def test_cli_generates_report(self):
        output_dir = TEST_OUTPUTS / "complete_lifecycle_cli"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "reference_engine.complete_lifecycle_proof",
                "--case",
                str(CASE),
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = json.loads(result.stdout)
        self.assertEqual(stdout["summary"]["overall_status"], "COMPLETE")
        report = json.loads((output_dir / "complete_lifecycle_proof.json").read_text(encoding="utf-8"))
        self.assertEqual(report["summary"]["initial_route"], "PAUSE")


if __name__ == "__main__":
    unittest.main()

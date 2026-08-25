import json
import unittest
from pathlib import Path

from reference_engine.customer_proof_loop import (
    CUSTOMER_PROOF_LOOP_VERSION,
    build_customer_proof_loop,
    write_customer_proof_loop,
)


ROOT = Path(__file__).resolve().parents[1]


class CustomerProofLoopTests(unittest.TestCase):
    def _example(self):
        return json.loads((ROOT / "examples" / "customer_proof_action.json").read_text(encoding="utf-8"))

    def test_customer_proof_loop_builds_replayable_bundle(self):
        report = build_customer_proof_loop(self._example())

        self.assertEqual(report["version"], CUSTOMER_PROOF_LOOP_VERSION)
        self.assertEqual(report["admission"]["decision"], "ADMIT")
        self.assertFalse(report["recoverability_stage"]["skipped"])
        self.assertEqual(report["recoverability_decision"]["posture"], "THROTTLE")
        self.assertEqual(report["sparta_route"]["route_state"], "CONSTRAINED_EXECUTE")
        self.assertTrue(report["summary"]["hard_gates_passed"])
        self.assertTrue(report["summary"]["recoverability_permits_progression"])
        self.assertTrue(report["summary"]["route_executable"])
        self.assertTrue(report["summary"]["ledger_valid"])
        self.assertEqual(report["summary"]["overall_status"], "PASS")
        self.assertTrue(report["decision_lifecycle_ledger"]["verification"]["valid"])
        self.assertIn("SMERC Customer Proof Loop Report", report["markdown_report"])

    def test_failed_runtime_admission_fails_closed_before_recoverability(self):
        payload = self._example()
        payload["admission"]["checks"]["identity_valid"] = False

        report = build_customer_proof_loop(payload)

        self.assertEqual(report["admission"]["decision"], "REJECT")
        self.assertTrue(report["recoverability_stage"]["skipped"])
        self.assertEqual(report["recoverability_decision"]["posture"], "DENY")
        self.assertEqual(report["sparta_route"]["route_state"], "BLOCK")
        self.assertFalse(report["summary"]["hard_gates_passed"])
        self.assertFalse(report["summary"]["recoverability_permits_progression"])
        self.assertFalse(report["summary"]["route_executable"])
        self.assertTrue(report["summary"]["ledger_valid"])
        self.assertEqual(report["summary"]["overall_status"], "REVIEW")

    def test_write_customer_proof_loop_outputs_json_and_markdown(self):
        report = build_customer_proof_loop(self._example())
        output_dir = ROOT / "test_outputs" / "customer_proof_loop"

        paths = write_customer_proof_loop(report, output_dir)

        self.assertTrue(Path(paths["json"]).exists())
        self.assertTrue(Path(paths["markdown"]).exists())
        written = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
        self.assertEqual(written["version"], CUSTOMER_PROOF_LOOP_VERSION)
        self.assertIn("Customer Proof Loop", Path(paths["markdown"]).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.recovery_authority_gate import (
    RECOVERY_AUTHORITY_VERSION,
    evaluate_recovery_authority,
    load_json,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "recovery_authority" / "unlock_request.json"
DOC = ROOT / "docs" / "Recovery_Authority_Gate.md"
TEST_OUTPUTS = ROOT / "test_outputs"
TEST_OUTPUTS.mkdir(exist_ok=True)


class RecoveryAuthorityGateTests(unittest.TestCase):
    def test_reference_case_unlocks_with_verified_authority_and_evidence(self):
        report = evaluate_recovery_authority(load_json(CASE))

        self.assertEqual(report["version"], RECOVERY_AUTHORITY_VERSION)
        self.assertEqual(report["paused_decision"]["state"], "PAUSED_DECISION_VALID")
        self.assertEqual(report["unlock_actor"]["state"], "UNLOCK_ACTOR_VALID")
        self.assertEqual(report["unlock_evidence"]["state"], "UNLOCK_EVIDENCE_SUFFICIENT")
        self.assertEqual(report["recovery_path"]["state"], "RECOVERY_PATH_READY")
        self.assertEqual(report["recovery_authority"]["state"], "UNLOCK")

    def test_self_unlock_attempt_is_denied(self):
        case = load_json(CASE)
        case["unlock_actor"]["actor_id"] = case["paused_decision"]["proposing_actor_id"]

        report = evaluate_recovery_authority(case)

        self.assertEqual(report["recovery_authority"]["state"], "DENY_UNLOCK")
        self.assertIn("self_unlock_attempt", report["recovery_authority"]["drivers"])

    def test_missing_recovery_evidence_keeps_action_paused(self):
        case = load_json(CASE)
        case["unlock_evidence"]["fresh_scan_passed"] = False
        case["unlock_evidence"]["rollback_plan_verified"] = False

        report = evaluate_recovery_authority(case)

        self.assertEqual(report["recovery_authority"]["state"], "KEEP_PAUSED")
        self.assertIn("fresh_scan_not_passed", report["recovery_authority"]["drivers"])
        self.assertIn("rollback_plan_not_verified", report["recovery_authority"]["drivers"])

    def test_constrained_route_requires_constrained_unlock(self):
        case = load_json(CASE)
        case["recovery_path"]["post_unlock_monitoring_required"] = False

        report = evaluate_recovery_authority(case)

        self.assertEqual(report["recovery_authority"]["state"], "UNLOCK_CONSTRAINED")
        self.assertIn("post_unlock_monitoring_not_required", report["recovery_authority"]["drivers"])

    def test_non_paused_decision_requires_requalification(self):
        case = load_json(CASE)
        case["paused_decision"]["posture"] = "ALLOW"

        report = evaluate_recovery_authority(case)

        self.assertEqual(report["recovery_authority"]["state"], "REQUALIFY")
        self.assertIn("decision_not_paused", report["recovery_authority"]["drivers"])

    def test_markdown_and_doc_explain_work_result_impact(self):
        report = evaluate_recovery_authority(load_json(CASE))
        markdown = render_markdown(report)
        doc = DOC.read_text(encoding="utf-8")

        for phrase in ["Work", "Result", "Impact", "same agent or workflow"]:
            self.assertIn(phrase, markdown)
        for phrase in ["Unlock authority", "Evidence freshness", "Fallback complexity", "Partial recovery"]:
            self.assertIn(phrase, doc)

    def test_writes_outputs(self):
        report = evaluate_recovery_authority(load_json(CASE))
        json_path = TEST_OUTPUTS / "recovery_authority_gate_test.json"
        markdown_path = TEST_OUTPUTS / "recovery_authority_gate_test.md"

        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertIn(RECOVERY_AUTHORITY_VERSION, json_path.read_text(encoding="utf-8"))
        self.assertIn("SMERC Recovery Authority Gate Report", markdown_path.read_text(encoding="utf-8"))

    def test_cli_generates_report(self):
        json_path = TEST_OUTPUTS / "recovery_authority_gate_cli.json"
        markdown_path = TEST_OUTPUTS / "recovery_authority_gate_cli.md"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "reference_engine.recovery_authority_gate",
                "--case",
                str(CASE),
                "--json-output",
                str(json_path),
                "--markdown-output",
                str(markdown_path),
                "--pretty",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(report["recovery_authority"]["state"], "UNLOCK")


if __name__ == "__main__":
    unittest.main()

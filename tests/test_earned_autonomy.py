import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.earned_autonomy import (
    EARNED_AUTONOMY_VERSION,
    budget_context_for_tier,
    evaluate_earned_autonomy,
    load_history,
    render_markdown,
    write_outputs,
)
from reference_engine.mcp_governance_gateway import evaluate_gateway_session, load_json


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "examples" / "autonomy" / "agent_history.json"
REGISTRY = ROOT / "examples" / "mcp" / "governance_gateway_registry.json"
SESSION = ROOT / "examples" / "mcp" / "governance_gateway_session.json"
DOC = ROOT / "docs" / "Earned_Autonomy_Framework.md"
TEST_OUTPUTS = ROOT / "test_outputs"
TEST_OUTPUTS.mkdir(exist_ok=True)


class EarnedAutonomyTests(unittest.TestCase):
    def test_clean_history_earns_bounded_autonomy(self):
        payload = load_history(HISTORY)
        report = evaluate_earned_autonomy(subject_id=payload["subject_id"], history=payload["history"])

        self.assertEqual(report["version"], EARNED_AUTONOMY_VERSION)
        self.assertEqual(report["earned_tier"], "TIER_3_BOUNDED")
        self.assertEqual(report["budget_context"]["initial_state"], "HEALTHY")
        self.assertEqual(report["budget_context"]["budget_overrides"]["max_actions"], 7)
        self.assertGreaterEqual(report["metrics"]["reviewer_agreement_rate"], 0.9)

    def test_bad_history_requires_requalification(self):
        records = [
            {
                "posture": "ALLOW",
                "execution_outcome": "success",
                "reviewer_agreed": True,
                "human_override": False,
                "ref_gate_status": "pass",
                "false_release": False,
                "incident": False,
                "scope_violation": False,
                "evidence_quality": "trusted",
            }
            for _ in range(10)
        ]
        records[-1]["false_release"] = True

        report = evaluate_earned_autonomy(subject_id="unsafe_agent", history=records)

        self.assertEqual(report["earned_tier"], "TIER_5_REQUALIFY_REQUIRED")
        self.assertTrue(report["review_required"])
        self.assertIn("incident_or_false_release", report["drivers"])
        self.assertEqual(report["budget_context"]["budget_overrides"]["max_actions"], 0)

    def test_insufficient_history_stays_observe(self):
        report = evaluate_earned_autonomy(subject_id="new_agent", history=[])

        self.assertEqual(report["earned_tier"], "TIER_0_OBSERVE")
        self.assertTrue(report["review_required"])
        self.assertIn("insufficient_history", report["drivers"])

    def test_budget_context_rejects_unknown_tier(self):
        with self.assertRaises(ValueError):
            budget_context_for_tier("TIER_UNKNOWN")

    def test_gateway_uses_earned_tier_for_starting_budget(self):
        report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="enforce")

        self.assertEqual(report["earned_autonomy"]["earned_tier"], "TIER_3_BOUNDED")
        self.assertEqual(report["autonomy_budget"]["earned_autonomy"]["earned_tier"], "TIER_3_BOUNDED")
        self.assertEqual(report["autonomy_budget"]["budget"]["max_actions"], 7)
        self.assertEqual(report["autonomy_budget"]["autonomy_state"], "SUSPEND_AUTONOMY")

    def test_markdown_and_doc_explain_boundaries(self):
        payload = load_history(HISTORY)
        report = evaluate_earned_autonomy(subject_id=payload["subject_id"], history=payload["history"])
        markdown = render_markdown(report)
        doc = DOC.read_text(encoding="utf-8")

        for phrase in ["SMERC Earned Autonomy Report", "Earned tier", "Budget Context"]:
            self.assertIn(phrase, markdown)
        for phrase in ["Unproven systems start constrained", "TIER_5_REQUALIFY_REQUIRED", "not a production trust score"]:
            self.assertIn(phrase, doc)

    def test_writes_outputs(self):
        payload = load_history(HISTORY)
        report = evaluate_earned_autonomy(subject_id=payload["subject_id"], history=payload["history"])
        json_path = TEST_OUTPUTS / "earned_autonomy_test.json"
        markdown_path = TEST_OUTPUTS / "earned_autonomy_test.md"

        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertIn(EARNED_AUTONOMY_VERSION, json_path.read_text(encoding="utf-8"))
        self.assertIn("SMERC Earned Autonomy Report", markdown_path.read_text(encoding="utf-8"))

    def test_cli_generates_report(self):
        json_path = TEST_OUTPUTS / "earned_autonomy_cli.json"
        markdown_path = TEST_OUTPUTS / "earned_autonomy_cli.md"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "reference_engine.earned_autonomy",
                "--history",
                str(HISTORY),
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
        self.assertEqual(report["version"], EARNED_AUTONOMY_VERSION)
        self.assertEqual(report["earned_tier"], "TIER_3_BOUNDED")


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.autonomy_budget import (
    AUTONOMY_BUDGET_VERSION,
    evaluate_autonomy_budget,
    render_markdown,
    write_outputs,
)
from reference_engine.mcp_governance_gateway import evaluate_gateway_session, load_json


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "examples" / "mcp" / "governance_gateway_registry.json"
SESSION = ROOT / "examples" / "mcp" / "governance_gateway_session.json"
DOC = ROOT / "docs" / "Autonomy_Budgeting_Framework.md"
TEST_OUTPUTS = ROOT / "test_outputs"


class AutonomyBudgetTests(unittest.TestCase):
    def test_budget_shrinks_and_suspends_after_ref_gate_failure(self):
        gateway_report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="enforce")
        budget_report = gateway_report["autonomy_budget"]

        self.assertEqual(budget_report["version"], AUTONOMY_BUDGET_VERSION)
        self.assertEqual(budget_report["spent"]["actions"], 4)
        self.assertEqual(budget_report["spent"]["ref_gate_failures"], 1)
        self.assertEqual(budget_report["autonomy_state"], "SUSPEND_AUTONOMY")
        self.assertIn("ref_gate_failure", budget_report["review_triggers"])
        self.assertEqual(budget_report["allowed_tool_risk_tiers"], [])
        self.assertEqual(budget_report["decision_ledger"][-1]["autonomy_state_after"], "SUSPEND_AUTONOMY")

    def test_budget_can_remain_healthy_for_low_pressure_allow_decisions(self):
        decisions = [
            {
                "sequence": 1,
                "mcp_request_id": "LOW_001",
                "tool_name": "search_documents",
                "posture": "ALLOW",
                "requested_scope_units": 2,
                "gateway_pressure": {"score": 0.05},
                "ref_gate": {"status": "pass"},
            },
            {
                "sequence": 2,
                "mcp_request_id": "LOW_002",
                "tool_name": "search_documents",
                "posture": "ALLOW",
                "requested_scope_units": 3,
                "gateway_pressure": {"score": 0.08},
                "ref_gate": {"status": "pass"},
            },
        ]

        report = evaluate_autonomy_budget(decisions=decisions)

        self.assertEqual(report["autonomy_state"], "HEALTHY")
        self.assertGreater(report["remaining"]["actions"], 0)
        self.assertGreater(report["remaining"]["risk_spend"], 0)
        self.assertEqual(report["review_triggers"], [])

    def test_markdown_and_doc_explain_budgeting_boundaries(self):
        gateway_report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="enforce")
        markdown = render_markdown(gateway_report["autonomy_budget"])
        doc = DOC.read_text(encoding="utf-8")

        for phrase in ["Autonomy Budget", "Risk spend", "SUSPEND_AUTONOMY"]:
            self.assertIn(phrase, markdown)
        for phrase in ["Given the situation right now", "max_actions", "not a production entitlement service"]:
            self.assertIn(phrase, doc)

    def test_writes_outputs(self):
        report = evaluate_autonomy_budget(decisions=[])
        json_path = TEST_OUTPUTS / "autonomy_budget_test.json"
        markdown_path = TEST_OUTPUTS / "autonomy_budget_test.md"

        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertIn(AUTONOMY_BUDGET_VERSION, json_path.read_text(encoding="utf-8"))
        self.assertIn("SMERC Autonomy Budget Report", markdown_path.read_text(encoding="utf-8"))

    def test_cli_generates_budget_report(self):
        gateway_json = TEST_OUTPUTS / "autonomy_gateway_input.json"
        budget_json = TEST_OUTPUTS / "autonomy_budget_cli.json"
        budget_md = TEST_OUTPUTS / "autonomy_budget_cli.md"
        gateway_report = evaluate_gateway_session(registry=load_json(REGISTRY), session=load_json(SESSION), mode="enforce")
        gateway_json.write_text(json.dumps(gateway_report), encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "reference_engine.autonomy_budget",
                "--gateway-report",
                str(gateway_json),
                "--json-output",
                str(budget_json),
                "--markdown-output",
                str(budget_md),
                "--pretty",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(budget_json.read_text(encoding="utf-8"))
        self.assertEqual(report["version"], AUTONOMY_BUDGET_VERSION)
        self.assertEqual(report["autonomy_state"], "SUSPEND_AUTONOMY")


if __name__ == "__main__":
    unittest.main()

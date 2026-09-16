import copy
import json
import unittest
from pathlib import Path

from api_server import SMERCRequestHandler, _stricter_posture
from reference_engine.action_language import evaluate_language_action
from reference_engine.customer_evaluation import build_customer_evaluation, load_payload
from reference_engine.mcp_tool_governance import evaluate_mcp_tool_call
from reference_engine.recoverability_engine import RecoverabilityEngine
from reference_engine.runtime_admission_gate import evaluate_runtime_admission_gate


ROOT = Path(__file__).resolve().parents[1]
ACTION_LANGUAGE_SAMPLE = json.loads(
    (ROOT / "examples" / "action_language" / "production_database_change.json").read_text(encoding="utf-8")
)
CUSTOMER_SAMPLE = ROOT / "examples" / "customer_eval_actions.json"
MCP_SAMPLE = json.loads(
    (ROOT / "examples" / "mcp" / "tool_call_delete_customer_records.json").read_text(encoding="utf-8")
)
POSTURE_RANK = {"ALLOW": 0, "THROTTLE": 1, "FREEZE": 2, "ESCALATE": 3, "DENY": 4}


class CrossPathSafetyInvariantTests(unittest.TestCase):
    def test_missing_inline_admission_cannot_be_bypassed(self):
        admission = SMERCRequestHandler._evaluate_inline_admission(
            object(),
            {"action_id": "MISSING-ADMISSION"},
        )

        self.assertEqual(admission["decision"], "REJECT")
        self.assertEqual(admission["max_recommended_posture"], "DENY")
        self.assertIn("identity_valid", admission["missing_required_checks"])

    def test_empty_required_checks_cannot_neutralize_admission(self):
        admission = evaluate_runtime_admission_gate(
            {
                "version": "smerc.runtime-admission-input.v1",
                "request_id": "EMPTY-POLICY",
                "required_checks": [],
                "checks": {},
            }
        )

        self.assertEqual(admission["decision"], "REJECT")
        self.assertEqual(admission["max_recommended_posture"], "DENY")

    def test_combined_decisions_preserve_the_stricter_posture(self):
        for left, right, expected in (
            ("DENY", "FREEZE", "DENY"),
            ("THROTTLE", "DENY", "DENY"),
            ("ALLOW", "FREEZE", "FREEZE"),
            ("ESCALATE", "FREEZE", "ESCALATE"),
        ):
            with self.subTest(left=left, right=right):
                resolved = _stricter_posture(left, right)
                self.assertEqual(resolved, expected)
                self.assertGreaterEqual(POSTURE_RANK[resolved], POSTURE_RANK[left])
                self.assertGreaterEqual(POSTURE_RANK[resolved], POSTURE_RANK[right])

    def test_missing_high_impact_evidence_never_allows_across_paths(self):
        results = {
            "recoverability": self._recoverability_missing_evidence(),
            "action_language": self._action_language_missing_evidence(),
            "customer_evaluation": self._customer_missing_evidence(),
            "mcp": self._mcp_missing_evidence(),
        }

        for path, decision in results.items():
            with self.subTest(path=path):
                self.assertNotEqual(decision["posture"], "ALLOW")
                self.assertIn("RECOVERABILITY_EVIDENCE_UNAVAILABLE", decision["reason_codes"])
                unavailable = decision["replay"]["context"]["auto_unavailable_recoverability_signals"]
                self.assertIn("rollback_latency", unavailable)
                self.assertIn("containment_strength", unavailable)

    def test_unknown_contract_fields_fail_closed_across_structured_paths(self):
        language = copy.deepcopy(ACTION_LANGUAGE_SAMPLE)
        language["signals"]["unknown_signal"] = 0.1
        with self.assertRaisesRegex(ValueError, "unknown field"):
            evaluate_language_action(language)

        customer = copy.deepcopy(load_payload(CUSTOMER_SAMPLE))
        customer["actions"][0]["unknown_signal"] = 0.1
        with self.assertRaisesRegex(ValueError, "unknown field"):
            build_customer_evaluation(customer)

        mcp = copy.deepcopy(MCP_SAMPLE)
        mcp["unknown_section"] = {}
        with self.assertRaisesRegex(ValueError, "unknown field"):
            evaluate_mcp_tool_call(mcp)

    @staticmethod
    def _recoverability_missing_evidence():
        action = {
            "action_id": "CROSS-PATH-ENGINE",
            "description": "High-impact production mutation with missing recovery evidence",
            "actor": "deployment_agent",
            "tool": "cloud.deploy",
            "action_type": "production_deploy",
            "base_action_risk": 0.82,
            "reversibility": 0.52,
            "evidence_validity": 0.72,
            "anomaly_pressure": 0.20,
            "impact_scope": 0.82,
            "cancel_reliability": 0.64,
            "authorization_confidence": 0.78,
            "external_side_effect": True,
            "sensitive_data": False,
            "context": {},
        }
        del action["cancel_reliability"]
        return RecoverabilityEngine().evaluate(action)

    @staticmethod
    def _action_language_missing_evidence():
        payload = copy.deepcopy(ACTION_LANGUAGE_SAMPLE)
        del payload["recoverability"]["rollback_latency"]
        del payload["recoverability"]["containment_strength"]
        return evaluate_language_action(payload)

    @staticmethod
    def _customer_missing_evidence():
        payload = copy.deepcopy(load_payload(CUSTOMER_SAMPLE))
        del payload["actions"][0]["rollback_latency"]
        del payload["actions"][0]["containment_strength"]
        return build_customer_evaluation(payload)["records"][0]["decision"]

    @staticmethod
    def _mcp_missing_evidence():
        payload = copy.deepcopy(MCP_SAMPLE)
        del payload["risk_signals"]["rollback_latency"]
        del payload["risk_signals"]["containment_strength"]
        return evaluate_mcp_tool_call(payload)["decision"]


if __name__ == "__main__":
    unittest.main()

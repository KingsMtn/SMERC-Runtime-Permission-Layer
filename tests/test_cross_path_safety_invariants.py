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

        mcp_nested = copy.deepcopy(MCP_SAMPLE)
        mcp_nested["risk_signals"]["rollback_latency_alias"] = None
        with self.assertRaisesRegex(ValueError, "risk_signals contains unknown field"):
            evaluate_mcp_tool_call(mcp_nested)

    def test_representation_mutations_preserve_fail_closed_semantics(self):
        evaluators = {
            "recoverability": self._recoverability_variants,
            "action_language": self._action_language_variants,
            "customer_evaluation": self._customer_variants,
            "mcp": self._mcp_variants,
        }

        for path, build_variants in evaluators.items():
            canonical, equivalent, invalid_variants = build_variants()
            canonical_signature = self._safety_signature(canonical)
            with self.subTest(path=path, variant="equivalent"):
                self.assertEqual(self._safety_signature(equivalent), canonical_signature)
                self.assertEqual(canonical_signature[0], "DENY")
                self.assertIn("RECOVERABILITY_EVIDENCE_UNAVAILABLE", canonical_signature[1])
                self.assertIn("ROLLBACK_LATENCY_UNAVAILABLE", canonical_signature[1])

            for variant_name, invalid_call in invalid_variants.items():
                with self.subTest(path=path, variant=variant_name):
                    with self.assertRaises((TypeError, ValueError)):
                        invalid_call()

    def test_failed_inline_admission_never_weakens_deny(self):
        decision = self._recoverability_missing_evidence()
        self.assertEqual(decision["posture"], "DENY")
        admission = evaluate_runtime_admission_gate(
            {
                "version": "smerc.runtime-admission-input.v1",
                "request_id": "SEMANTIC-EQUIVALENCE-ADMISSION",
                "checks": {},
            }
        )
        combined = SMERCRequestHandler._apply_inline_admission(object(), decision, admission)

        self.assertEqual(combined["posture"], "DENY")
        self.assertEqual(combined["runtime_admission"]["decision"], "REJECT")
        self.assertIn("RECOVERABILITY_EVIDENCE_UNAVAILABLE", combined["reason_codes"])
        self.assertTrue(combined["admission_capped_recoverability_scoring"])

    def test_one_canonical_action_has_identical_safety_signature_across_paths(self):
        decisions = self._canonical_cross_path_decisions()
        expected = self._safety_signature(decisions["recoverability"])

        for path, decision in decisions.items():
            with self.subTest(path=path):
                self.assertEqual(self._safety_signature(decision), expected)
                self.assertEqual(decision["posture"], "DENY")
                self.assertIn("RECOVERABILITY_EVIDENCE_UNAVAILABLE", decision["reason_codes"])
                self.assertIn("ROLLBACK_LATENCY_UNAVAILABLE", decision["reason_codes"])
                self.assertIn("CONTAINMENT_STRENGTH_UNAVAILABLE", decision["reason_codes"])

    @staticmethod
    def _safety_signature(decision):
        return decision["posture"], frozenset(decision["reason_codes"])

    @classmethod
    def _canonical_cross_path_decisions(cls):
        action = cls._engine_action()
        engine_decision = RecoverabilityEngine().evaluate(action)

        language = copy.deepcopy(ACTION_LANGUAGE_SAMPLE)
        language["action"].update(
            {
                "id": action["action_id"],
                "description": action["description"],
                "actor": action["actor"],
                "tool": action["tool"],
                "type": action["action_type"],
            }
        )
        language["action"]["authority"]["confidence"] = action["authorization_confidence"]
        language["signals"] = {
            key: action[key]
            for key in ("base_action_risk", "evidence_validity", "anomaly_pressure", "impact_scope")
        }
        language["recoverability"] = {
            key: action[key]
            for key in ("reversibility", "cancel_reliability")
        }
        language["recoverability"]["rollback_method"] = "No verified rollback method"
        language["effects"] = {
            "external_side_effect": action["external_side_effect"],
            "sensitive_data": action["sensitive_data"],
        }
        language["context"] = copy.deepcopy(action["context"])

        customer = copy.deepcopy(load_payload(CUSTOMER_SAMPLE))
        customer_action = copy.deepcopy(customer["actions"][0])
        for key, value in action.items():
            if key != "context":
                customer_action[key] = value
        customer_action["context"] = copy.deepcopy(action["context"])
        customer_action.pop("rollback_latency", None)
        customer_action.pop("containment_strength", None)
        customer_action["ref_gate"] = {key: True for key in customer_action["ref_gate"]}
        customer_action["tool_plan"]["side_effect_level"] = "external"
        customer["actions"] = [customer_action]
        customer["agents"] = []

        mcp = copy.deepcopy(MCP_SAMPLE)
        mcp.pop("agent_identity", None)
        mcp["agent"]["agent_id"] = action["actor"]
        mcp["server"]["name"] = "cloud"
        mcp["tool_call"].update(
            {
                "tool_name": "deploy",
                "description": action["description"],
                "operation_class": "deploy",
                "domain_profile": "general",
                "external_side_effect": action["external_side_effect"],
                "sensitive_data": action["sensitive_data"],
            }
        )
        mcp["risk_signals"] = {
            key: action[key]
            for key in (
                "base_action_risk",
                "reversibility",
                "evidence_validity",
                "anomaly_pressure",
                "impact_scope",
                "cancel_reliability",
                "authorization_confidence",
            )
        }

        return {
            "recoverability": engine_decision,
            "action_language": evaluate_language_action(language),
            "customer_evaluation": build_customer_evaluation(customer)["records"][0]["decision"],
            "mcp": evaluate_mcp_tool_call(mcp)["decision"],
        }

    @classmethod
    def _recoverability_variants(cls):
        canonical_action = cls._engine_action()
        equivalent_action = copy.deepcopy(canonical_action)
        equivalent_action["context"] = {"unavailable_recoverability_signals": []}
        invalid_null = copy.deepcopy(canonical_action)
        invalid_null["rollback_latency"] = None
        invalid_alias = copy.deepcopy(canonical_action)
        invalid_alias["rollback_latency_alias"] = None
        return (
            RecoverabilityEngine().evaluate(canonical_action),
            RecoverabilityEngine().evaluate(equivalent_action),
            {
                "null": lambda: RecoverabilityEngine().evaluate(invalid_null),
                "alias": lambda: RecoverabilityEngine().evaluate(invalid_alias),
            },
        )

    @classmethod
    def _action_language_variants(cls):
        canonical = copy.deepcopy(ACTION_LANGUAGE_SAMPLE)
        del canonical["recoverability"]["rollback_latency"]
        equivalent = copy.deepcopy(canonical)
        equivalent["context"]["unavailable_recoverability_signals"] = []
        invalid_null = copy.deepcopy(canonical)
        invalid_null["recoverability"]["rollback_latency"] = None
        invalid_nested = copy.deepcopy(canonical)
        invalid_nested["recoverability"]["rollback_latency_alias"] = None
        return (
            evaluate_language_action(canonical),
            evaluate_language_action(equivalent),
            {
                "null": lambda: evaluate_language_action(invalid_null),
                "nested_unknown": lambda: evaluate_language_action(invalid_nested),
            },
        )

    @classmethod
    def _customer_variants(cls):
        canonical = copy.deepcopy(load_payload(CUSTOMER_SAMPLE))
        canonical["actions"] = [canonical["actions"][2]]
        del canonical["actions"][0]["rollback_latency"]
        equivalent = copy.deepcopy(canonical)
        equivalent["actions"][0]["context"]["unavailable_recoverability_signals"] = []
        invalid_null = copy.deepcopy(canonical)
        invalid_null["actions"][0]["rollback_latency"] = None
        invalid_nested = copy.deepcopy(canonical)
        invalid_nested["actions"][0]["rollback_latency_alias"] = None
        return (
            build_customer_evaluation(canonical)["records"][0]["decision"],
            build_customer_evaluation(equivalent)["records"][0]["decision"],
            {
                "null": lambda: build_customer_evaluation(invalid_null),
                "nested_unknown": lambda: build_customer_evaluation(invalid_nested),
            },
        )

    @classmethod
    def _mcp_variants(cls):
        canonical = copy.deepcopy(MCP_SAMPLE)
        del canonical["risk_signals"]["rollback_latency"]
        equivalent = copy.deepcopy(canonical)
        equivalent["tool_call"].pop("description", None)
        invalid_null = copy.deepcopy(canonical)
        invalid_null["risk_signals"]["rollback_latency"] = None
        invalid_nested = copy.deepcopy(canonical)
        invalid_nested["risk_signals"]["rollback_latency_alias"] = None
        return (
            evaluate_mcp_tool_call(canonical)["decision"],
            evaluate_mcp_tool_call(equivalent)["decision"],
            {
                "null": lambda: evaluate_mcp_tool_call(invalid_null),
                "nested_unknown": lambda: evaluate_mcp_tool_call(invalid_nested),
            },
        )

    @staticmethod
    def _recoverability_missing_evidence():
        action = CrossPathSafetyInvariantTests._engine_action()
        return RecoverabilityEngine().evaluate(action)

    @staticmethod
    def _engine_action():
        return {
            "action_id": "CROSS-PATH-ENGINE",
            "description": "High-impact production mutation with missing recovery evidence",
            "actor": "deployment_agent",
            "tool": "cloud.deploy",
            "action_type": "production_deploy",
            "base_action_risk": 0.99,
            "reversibility": 0.05,
            "evidence_validity": 0.20,
            "anomaly_pressure": 0.90,
            "impact_scope": 0.99,
            "cancel_reliability": 0.10,
            "authorization_confidence": 0.10,
            "external_side_effect": True,
            "sensitive_data": True,
            "context": {},
        }

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

import unittest

from reference_engine.agent_permission_layer import RuntimePermissionEngine


class RuntimePermissionEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = RuntimePermissionEngine()

    def test_allows_low_risk_replayable_action(self):
        result = self.engine.evaluate(
            {
                "action_id": "READ_PUBLIC_DOCS",
                "description": "Read public docs.",
                "tool": "docs.search",
                "actor": "support_agent",
                "confidence": 0.9,
                "harm": 0.08,
                "consent": 0.95,
                "reversibility": 0.9,
                "external_effect": False,
                "sensitive_data": False,
            }
        )
        self.assertEqual(result["posture"], "ALLOW")
        self.assertIn("log_replay", result["constraints"])

    def test_throttles_external_side_effect(self):
        result = self.engine.evaluate(
            {
                "action_id": "SEND_EMAIL",
                "description": "Send customer email.",
                "tool": "gmail.send",
                "actor": "sales_agent",
                "confidence": 0.72,
                "harm": 0.42,
                "consent": 0.66,
                "reversibility": 0.38,
                "external_effect": True,
                "sensitive_data": False,
            }
        )
        self.assertEqual(result["posture"], "THROTTLE")
        self.assertIn("rate_limit_external_effect", result["constraints"])

    def test_freezes_low_confidence_side_effect(self):
        result = self.engine.evaluate(
            {
                "action_id": "RUN_UNKNOWN_SCRIPT",
                "description": "Run unknown script.",
                "tool": "shell.exec",
                "actor": "coding_agent",
                "confidence": 0.20,
                "harm": 0.45,
                "consent": 0.55,
                "reversibility": 0.35,
                "external_effect": True,
                "sensitive_data": False,
            }
        )
        self.assertEqual(result["posture"], "FREEZE")
        self.assertIn("preserve_replay", result["constraints"])

    def test_denies_high_harm_low_consent_irreversible_action(self):
        result = self.engine.evaluate(
            {
                "action_id": "DELETE_PROD",
                "description": "Delete production records.",
                "tool": "database.delete",
                "actor": "ops_agent",
                "confidence": 0.58,
                "harm": 0.95,
                "consent": 0.32,
                "reversibility": 0.05,
                "external_effect": True,
                "sensitive_data": True,
            }
        )
        self.assertEqual(result["posture"], "DENY")
        self.assertIn("explain_denial", result["constraints"])

    def test_escalates_high_harm_external_sensitive_action(self):
        result = self.engine.evaluate(
            {
                "action_id": "WIRE_FUNDS",
                "description": "Wire vendor funds.",
                "tool": "payments.transfer",
                "actor": "finance_agent",
                "confidence": 0.78,
                "harm": 0.82,
                "consent": 0.52,
                "reversibility": 0.12,
                "external_effect": True,
                "sensitive_data": True,
            }
        )
        self.assertEqual(result["posture"], "ESCALATE")
        self.assertIn("require_explicit_approval", result["constraints"])

    def test_validates_required_fields(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate({"action_id": "BROKEN"})


if __name__ == "__main__":
    unittest.main()


import unittest

from reference_engine.financial_permission_profile import FinancialPermissionProfile


def request(**overrides):
    payload = {
        "action_id": "FIN_ACTION",
        "description": "Evaluate a proposed financial action.",
        "action_type": "treasury_rebalance",
        "actor": "treasury_agent",
        "authorization_support": 0.90,
        "evidence_validity": 0.90,
        "reversibility": 0.82,
        "liquidity_concentration": 0.15,
        "collateral_stress": 0.12,
        "settlement_anomaly": 0.10,
        "stablecoin_imbalance": 0.10,
        "counterparty_concentration": 0.16,
        "market_instability": 0.14,
        "model_disagreement": 0.08,
        "agent_velocity": 0.12,
    }
    payload.update(overrides)
    return payload


class FinancialPermissionProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile = FinancialPermissionProfile()

    def test_allows_low_stress_authorized_action(self):
        result = self.profile.evaluate(request())
        self.assertEqual(result["state"], "ALLOW")
        self.assertEqual(result["profile"], "SMERC-F")
        self.assertIn("retain_reversal_path", result["controls"])

    def test_throttles_concentrated_high_velocity_action(self):
        result = self.profile.evaluate(
            request(counterparty_concentration=0.78, agent_velocity=0.72, market_instability=0.58)
        )
        self.assertEqual(result["state"], "THROTTLE")
        self.assertIn("require_dual_approval", result["controls"])

    def test_freezes_on_model_disagreement(self):
        result = self.profile.evaluate(request(model_disagreement=0.82, collateral_stress=0.70))
        self.assertEqual(result["state"], "FREEZE")
        self.assertIn("secondary_validation", result["controls"])

    def test_denies_weakly_authorized_action(self):
        result = self.profile.evaluate(request(authorization_support=0.12, reversibility=0.10))
        self.assertEqual(result["state"], "DENY")
        self.assertIn("executive_override_required", result["controls"])

    def test_escalates_incomplete_evidence(self):
        result = self.profile.evaluate(request(evidence_validity=0.46))
        self.assertEqual(result["state"], "ESCALATE")
        self.assertIn("require_explicit_approval", result["controls"])

    def test_rejects_missing_signals(self):
        with self.assertRaises(ValueError):
            self.profile.evaluate({"action_id": "BROKEN"})

    def test_decision_hash_is_deterministic(self):
        first = self.profile.evaluate(request())
        second = self.profile.evaluate(request())
        self.assertEqual(first["decision_hash"], second["decision_hash"])
        self.assertNotEqual(first["replay_id"], "")

    def test_policy_name_and_version_are_reported(self):
        result = self.profile.evaluate(request())
        self.assertEqual(result["policy"], {"name": "balanced", "version": "1.0.0"})

    def test_unknown_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            FinancialPermissionProfile("unknown")

    def test_conservative_policy_is_not_less_restrictive(self):
        action = request(
            authorization_support=0.70,
            evidence_validity=0.66,
            reversibility=0.58,
            liquidity_concentration=0.52,
            counterparty_concentration=0.58,
            agent_velocity=0.48,
        )
        severity = {"ALLOW": 0, "THROTTLE": 1, "ESCALATE": 2, "FREEZE": 3, "DENY": 4}
        conservative = FinancialPermissionProfile("conservative").evaluate(action)["state"]
        balanced = FinancialPermissionProfile("balanced").evaluate(action)["state"]
        permissive = FinancialPermissionProfile("permissive").evaluate(action)["state"]
        self.assertGreaterEqual(severity[conservative], severity[balanced])
        self.assertGreaterEqual(severity[balanced], severity[permissive])


if __name__ == "__main__":
    unittest.main()

import unittest

from reference_engine.financial_permission_profile import FinancialPermissionProfile


def request(**overrides):
    payload = {
        "action_id": "FIN_ACTION",
        "description": "Evaluate a proposed financial action.",
        "action_type": "treasury_rebalance",
        "actor": "treasury_agent",
        "authorization_support": 0.90,
        "evidence_validity": 0.90,
        "reversibility": 0.82,
        "liquidity_concentration": 0.15,
        "collateral_stress": 0.12,
        "settlement_anomaly": 0.10,
        "stablecoin_imbalance": 0.10,
        "counterparty_concentration": 0.16,
        "market_instability": 0.14,
        "model_disagreement": 0.08,
        "agent_velocity": 0.12,
    }
    payload.update(overrides)
    return payload


class FinancialPermissionProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile = FinancialPermissionProfile()

    def test_allows_low_stress_authorized_action(self):
        result = self.profile.evaluate(request())
        self.assertEqual(result["state"], "ALLOW")
        self.assertEqual(result["profile"], "SMERC-F")
        self.assertIn("retain_reversal_path", result["controls"])

    def test_throttles_concentrated_high_velocity_action(self):
        result = self.profile.evaluate(
            request(counterparty_concentration=0.78, agent_velocity=0.72, market_instability=0.58)
        )
        self.assertEqual(result["state"], "THROTTLE")
        self.assertIn("require_dual_approval", result["controls"])

    def test_freezes_on_model_disagreement(self):
        result = self.profile.evaluate(request(model_disagreement=0.82, collateral_stress=0.70))
        self.assertEqual(result["state"], "FREEZE")
        self.assertIn("secondary_validation", result["controls"])

    def test_denies_weakly_authorized_action(self):
        result = self.profile.evaluate(request(authorization_support=0.12, reversibility=0.10))
        self.assertEqual(result["state"], "DENY")
        self.assertIn("executive_override_required", result["controls"])

    def test_escalates_incomplete_evidence(self):
        result = self.profile.evaluate(request(evidence_validity=0.46))
        self.assertEqual(result["state"], "ESCALATE")
        self.assertIn("require_explicit_approval", result["controls"])

    def test_rejects_missing_signals(self):
        with self.assertRaises(ValueError):
            self.profile.evaluate({"action_id": "BROKEN"})


if __name__ == "__main__":
    unittest.main()


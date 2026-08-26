from __future__ import annotations

import json
import unittest
from pathlib import Path

from reference_engine.fallback_policy import build_fallback_policy_report, evaluate_fallback_policy


ROOT = Path(__file__).resolve().parents[1]


def _examples():
    return json.loads((ROOT / "examples" / "fallback_policy_examples.json").read_text(encoding="utf-8"))


class FallbackPolicyTests(unittest.TestCase):
    def test_low_risk_action_keeps_allow_when_no_fallback_needed(self) -> None:
        result = evaluate_fallback_policy(_examples()["scenarios"][0])

        self.assertEqual(result["fallback_posture"], "ALLOW")
        self.assertFalse(result["fallback_applied"])
        self.assertIn("FALLBACK_NOT_APPLIED", result["reason_codes"])

    def test_unavailable_scanner_freezes_destructive_action(self) -> None:
        result = evaluate_fallback_policy(_examples()["scenarios"][1])

        self.assertEqual(result["fallback_posture"], "FREEZE")
        self.assertTrue(result["fallback_applied"])
        self.assertIn("FALLBACK_CONTENT_SCANNER_UNAVAILABLE", result["reason_codes"])

    def test_stale_policy_freezes_release(self) -> None:
        result = evaluate_fallback_policy(_examples()["scenarios"][2])

        self.assertEqual(result["fallback_posture"], "FREEZE")
        self.assertIn("FALLBACK_POLICY_STALE", result["reason_codes"])

    def test_missing_rollback_for_high_impact_money_movement_denies(self) -> None:
        result = evaluate_fallback_policy(_examples()["scenarios"][3])

        self.assertEqual(result["fallback_posture"], "DENY")
        self.assertIn("FALLBACK_ROLLBACK_PLAN_MISSING_FOR_HIGH_IMPACT", result["reason_codes"])
        self.assertIn("FALLBACK_LOW_RECOVERY_HIGH_EXPOSURE", result["reason_codes"])

    def test_unavailable_review_queue_for_held_high_impact_action_denies(self) -> None:
        result = evaluate_fallback_policy(_examples()["scenarios"][4])

        self.assertEqual(result["fallback_posture"], "DENY")
        self.assertIn("FALLBACK_REVIEW_QUEUE_UNAVAILABLE_FOR_HELD_HIGH_IMPACT_ACTION", result["reason_codes"])

    def test_report_renders_markdown(self) -> None:
        report = build_fallback_policy_report(_examples())

        self.assertEqual(report["scenario_count"], 5)
        self.assertGreaterEqual(report["fallback_applied_count"], 4)
        self.assertIn("Fallback Policy Layer Report", report["markdown_report"])


if __name__ == "__main__":
    unittest.main()

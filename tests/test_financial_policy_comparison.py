import json
import unittest
from pathlib import Path

from reference_engine.financial_policy_comparison import compare_policies, render_policy_report


ROOT = Path(__file__).resolve().parents[1]


class FinancialPolicyComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actions = json.loads(
            (ROOT / "examples" / "financial_action_requests.json").read_text(encoding="utf-8")
        )

    def test_comparison_preserves_monotonic_restraint(self):
        result = compare_policies(self.actions)
        self.assertEqual(result["monotonic_restraint_rate"], 1.0)
        self.assertEqual(result["action_count"], len(self.actions))

    def test_report_contains_all_profiles(self):
        report = render_policy_report(compare_policies(self.actions))
        self.assertIn("Conservative", report)
        self.assertIn("Balanced", report)
        self.assertIn("Permissive", report)

    def test_empty_actions_are_rejected(self):
        with self.assertRaises(ValueError):
            compare_policies([])


if __name__ == "__main__":
    unittest.main()


import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RefPatternAndAutonomyHealthDocsTests(unittest.TestCase):
    def test_ref_pattern_doc_states_hard_gate_and_boundaries(self):
        text = (ROOT / "docs" / "SMERC_And_The_Ref_Pattern.md").read_text(encoding="utf-8")

        for phrase in [
            "typed_contract_valid",
            "attestation_valid",
            "least_privilege_confirmed",
            "object_shape_expected",
            "fails closed",
            "does not replace",
            "IAM",
            "OPA",
            "MCP schemas",
        ]:
            self.assertIn(phrase, text)

    def test_autonomy_health_doc_separates_action_gate_from_independence_governor(self):
        text = (ROOT / "docs" / "Autonomy_Health_Framework.md").read_text(encoding="utf-8")

        for phrase in [
            "SMERC is the action gate",
            "Autonomy Health is the independence governor",
            "HEALTHY",
            "WATCH",
            "DEGRADE",
            "SUSPEND_AUTONOMY",
            "REQUALIFY",
            "should not be marketed as proven",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

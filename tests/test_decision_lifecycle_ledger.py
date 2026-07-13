import copy
import unittest

from reference_engine.decision_lifecycle_ledger import (
    DecisionLifecycleLedger,
    build_example_ledger,
    render_markdown,
)


class DecisionLifecycleLedgerTests(unittest.TestCase):
    def test_example_ledger_is_complete_and_valid(self):
        ledger = build_example_ledger()
        data = ledger.to_dict()
        self.assertEqual(data["version"], "smerc.decision-lifecycle-ledger.v1")
        self.assertTrue(data["verification"]["valid"])
        self.assertEqual(data["record_count"], 7)
        self.assertEqual(data["summary"]["pending_learning_recommendations"], 1)
        self.assertTrue(data["summary"]["judged_correct"])

    def test_tampering_is_detected(self):
        ledger = build_example_ledger()
        records = copy.deepcopy(ledger.records)
        records[2]["payload"]["authorization_recommendation"] = "ALLOW"
        tampered = DecisionLifecycleLedger(ledger.decision_id, ledger.tenant_id, records)
        verification = tampered.verify()
        self.assertFalse(verification["valid"])
        self.assertIn("record 3: record hash mismatch", verification["errors"])

    def test_learning_recommendation_cannot_auto_activate(self):
        ledger = DecisionLifecycleLedger("decision-1")
        with self.assertRaises(ValueError):
            ledger.append(
                "LEARNING_RECOMMENDATION",
                "smerc-dll",
                {
                    "expected_outcome": "Expected",
                    "actual_outcome": "Actual",
                    "prediction_error": "medium",
                    "human_override_effectiveness": "unknown",
                    "recommended_policy_updates": ["raise threshold"],
                    "confidence_calibration_changes": [],
                    "suggested_rule_modifications": [],
                    "activation_status": "active",
                },
            )

    def test_human_override_requires_valid_postures(self):
        ledger = DecisionLifecycleLedger("decision-1")
        with self.assertRaises(ValueError):
            ledger.append(
                "HUMAN_INTERACTION",
                "reviewer",
                {
                    "interaction": "overrode",
                    "reviewer_id": "reviewer",
                    "original_recommendation": "ALLOW",
                    "final_recommendation": "APPROVE",
                    "rationale": "Invalid posture must not be accepted.",
                },
            )

    def test_from_dict_round_trip(self):
        ledger = build_example_ledger()
        data = ledger.to_dict()
        restored = DecisionLifecycleLedger.from_dict(data)
        self.assertEqual(restored.to_dict()["head_record_hash"], data["head_record_hash"])

    def test_markdown_disclaims_production_ledger(self):
        markdown = render_markdown(build_example_ledger())
        self.assertIn("not a production immutable ledger", markdown)
        self.assertIn("Learning recommendations require human review", markdown)


if __name__ == "__main__":
    unittest.main()


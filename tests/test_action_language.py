import copy
import json
import unittest
from pathlib import Path

from reference_engine.action_language import (
    ACTION_VERSION,
    DECISION_VERSION,
    action_hash,
    compile_action,
    evaluate_language_action,
    transition_for,
    validate_action_envelope,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads(
    (ROOT / "examples" / "action_language" / "production_database_change.json").read_text(encoding="utf-8")
)


class ActionLanguageTests(unittest.TestCase):
    def test_example_compiles_without_mutating_source(self):
        source = copy.deepcopy(EXAMPLE)
        compiled = compile_action(source)
        self.assertEqual(source, EXAMPLE)
        self.assertEqual(compiled["action_id"], "db-change-2041")
        self.assertEqual(compiled["authorization_confidence"], 0.38)
        self.assertEqual(compiled["context"]["smerc_language"]["target"]["environment"], "production")

    def test_hash_is_deterministic_across_key_order(self):
        reordered = json.loads(json.dumps(EXAMPLE, sort_keys=True))
        self.assertEqual(action_hash(EXAMPLE), action_hash(reordered))
        self.assertEqual(len(action_hash(EXAMPLE)), 64)

    def test_strict_version_fields_ranges_and_context_limits(self):
        invalid = copy.deepcopy(EXAMPLE)
        invalid["language_version"] = "smerc.action.v2"
        with self.assertRaisesRegex(ValueError, ACTION_VERSION):
            validate_action_envelope(invalid)
        invalid = copy.deepcopy(EXAMPLE)
        invalid["signals"]["mystery"] = 0.2
        with self.assertRaisesRegex(ValueError, "unknown field"):
            validate_action_envelope(invalid)
        invalid = copy.deepcopy(EXAMPLE)
        invalid["signals"]["impact_scope"] = 1.1
        with self.assertRaisesRegex(ValueError, "between"):
            validate_action_envelope(invalid)
        invalid = copy.deepcopy(EXAMPLE)
        invalid["context"] = {"oversized": "x" * 17_000}
        with self.assertRaisesRegex(ValueError, "16384"):
            validate_action_envelope(invalid)

    def test_decision_is_structured_replayable_and_restrained(self):
        decision = evaluate_language_action(EXAMPLE)
        self.assertEqual(decision["language_version"], DECISION_VERSION)
        self.assertEqual(decision["action_language_version"], ACTION_VERSION)
        self.assertIn(decision["posture"], {"FREEZE", "DENY", "ESCALATE"})
        self.assertTrue(decision["reasons"])
        self.assertTrue(all({"code", "title"} <= set(item) for item in decision["reasons"]))
        self.assertEqual(decision["replay"]["action_hash"], decision["action_hash"])

    def test_posture_transitions_are_explicit(self):
        self.assertEqual(transition_for("ALLOW", ["execute"])["mode"], "maintain")
        self.assertEqual(transition_for("THROTTLE", ["limit_scope"])["eligible_target_posture"], "ALLOW")
        self.assertEqual(transition_for("FREEZE", ["collect_more_evidence"])["eligible_target_posture"], "THROTTLE")
        denied = transition_for("DENY", ["require_new_request"])
        self.assertTrue(denied["requires_new_request"])
        self.assertIsNone(denied["eligible_target_posture"])
        escalated = transition_for("ESCALATE", ["require_explicit_approval"])
        self.assertEqual(escalated["conditions"][0]["code"], "APPROVAL_RECORDED")


if __name__ == "__main__":
    unittest.main()

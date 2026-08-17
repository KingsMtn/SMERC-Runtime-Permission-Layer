import copy
import json
import unittest
from pathlib import Path

from reference_engine.self_governance_sandbox import (
    build_self_governance_report,
    evaluate_self_governance_change,
)


ROOT = Path(__file__).resolve().parents[1]


def _examples():
    return json.loads((ROOT / "examples" / "self_governance_change_proposals.json").read_text(encoding="utf-8"))


class SelfGovernanceSandboxTests(unittest.TestCase):
    def test_good_governance_change_is_capped_to_test_only(self):
        proposal = _examples()["proposals"][0]

        result = evaluate_self_governance_change(proposal)

        self.assertEqual(result["base_smerc_posture"], "ALLOW")
        self.assertEqual(result["self_governed_posture"], "THROTTLE")
        self.assertTrue(result["self_change_ceiling_applied"])
        self.assertTrue(result["test_only_allowed"])
        self.assertFalse(result["activation_allowed"])
        self.assertIn("ALLOW_CAPPED_FOR_GOVERNANCE_LAYER_CHANGE", result["self_governance_reason_codes"])
        self.assertIn("record_policy_change_dll", result["required_controls"])

    def test_threshold_relaxation_is_constrained_and_requires_review(self):
        proposal = _examples()["proposals"][1]

        result = evaluate_self_governance_change(proposal)

        self.assertEqual(result["self_governed_posture"], "THROTTLE")
        self.assertIn("PRODUCTION_POLICY_CHANGE", result["self_governance_reason_codes"])
        self.assertIn("shadow_mode_before_activation", result["required_controls"])
        self.assertTrue(result["policy_update_requires_review"])

    def test_autonomous_policy_mutation_is_denied(self):
        proposal = _examples()["proposals"][2]

        result = evaluate_self_governance_change(proposal)

        self.assertEqual(result["self_governed_posture"], "DENY")
        self.assertFalse(result["activation_allowed"])
        self.assertIn("AUTONOMOUS_POLICY_MUTATION_PROHIBITED", result["self_governance_reason_codes"])
        self.assertIn("do_not_activate_policy_change", result["required_controls"])

    def test_missing_review_evidence_freezes_otherwise_reasonable_change(self):
        proposal = copy.deepcopy(_examples()["proposals"][0])
        proposal["reviewer_evidence"]["human_reviewer_required"] = False

        result = evaluate_self_governance_change(proposal)

        self.assertEqual(result["self_governed_posture"], "FREEZE")
        self.assertIn("SELF_CHANGE_EVIDENCE_INCOMPLETE", result["self_governance_reason_codes"])
        self.assertIn("require_human_reviewer", result["required_controls"])

    def test_batch_report_has_no_activation_allowed(self):
        report = build_self_governance_report(_examples())

        self.assertEqual(report["proposal_count"], 3)
        self.assertEqual(report["activation_allowed_count"], 0)
        self.assertGreaterEqual(report["ceiling_applied_count"], 1)
        self.assertIn("Self-Governance Sandbox Report", report["markdown_report"])

    def test_readme_links_self_governance_doc(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/Self_Governance_Sandbox.md", readme)


if __name__ == "__main__":
    unittest.main()

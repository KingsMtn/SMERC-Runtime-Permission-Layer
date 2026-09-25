import unittest

from reference_engine.iam_smerc_decision_comparison import build_comparison, render_markdown


class IAMSmercDecisionComparisonTests(unittest.TestCase):
    def test_authorized_action_produces_three_recovery_deltas(self):
        report = build_comparison()
        deltas = {row["recovery_case"]: row["decision_delta"] for row in report["rows"]}
        self.assertEqual(deltas["missing"], "AUTHORIZED_BUT_RECOVERY_DENIED")
        self.assertEqual(deltas["stale"], "AUTHORIZED_BUT_RECOVERY_REVIEW_REQUIRED")
        self.assertEqual(deltas["verified"], "AUTHORIZED_BUT_RECOVERY_CONSTRAINED")
        self.assertEqual(report["delta_count"], 3)

    def test_iam_deny_is_preserved(self):
        report = build_comparison(iam_authorized=False)
        self.assertTrue(all(row["decision_delta"] == "IAM_DENY_PRESERVED" for row in report["rows"]))
        self.assertTrue(all(row["authority_effect"] == "NONE" for row in report["rows"]))

    def test_inconsistent_iam_evidence_fails_closed(self):
        evidence = {"evidence_class": "synthetic_policy_evaluation", "principal": "role/test",
            "action": "cloudformation:UpdateStack", "resource": "stack/test", "decision": "denied"}
        with self.assertRaisesRegex(ValueError, "does not match"):
            build_comparison(iam_authorized=True, iam_evidence=evidence)

    def test_report_is_zero_spend_and_claim_bounded(self):
        report = build_comparison()
        markdown = render_markdown(report)
        self.assertFalse(report["aws_resources_created_or_modified"])
        self.assertEqual(report["incremental_aws_cost_usd"], 0.0)
        self.assertIn("does not claim that IAM", report["interpretation"])
        self.assertIn("not a live IAM Policy Simulator", report["evidence_boundary"])
        self.assertIn("Decision Deltas", markdown)


if __name__ == "__main__":
    unittest.main()

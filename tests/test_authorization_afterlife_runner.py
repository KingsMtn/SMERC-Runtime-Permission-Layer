import tempfile
import unittest
from pathlib import Path

from reference_engine.authorization_afterlife_runner import build_report, render_markdown


ROOT = Path(__file__).resolve().parents[1]


class AuthorizationAfterlifeRunnerTests(unittest.TestCase):
    def test_three_labeled_scenarios_cover_settle_quarantine_and_compensate(self):
        report = build_report(ROOT)
        self.assertEqual(report["scenario_count"], 3)
        self.assertEqual(report["decision_counts"], {"SETTLE": 1, "QUARANTINE": 1, "COMPENSATE": 1})
        self.assertEqual(
            [item["evidence_source"] for item in report["scenarios"]],
            ["CONTROLLED_AWS_PROOF", "SYNTHETIC", "CONTROLLED_AWS_PROOF"],
        )

    def test_sensitive_aws_identifiers_and_credentials_are_not_carried_forward(self):
        rendered = str(build_report(ROOT)).lower()
        for prohibited in ("account_id\":", "arn:aws", "access_key", "secret_access_key", "session_token"):
            self.assertNotIn(prohibited, rendered)

    def test_report_preserves_source_and_claim_boundaries(self):
        report = build_report(ROOT)
        mutation = report["scenarios"][2]
        self.assertEqual(mutation["observed_recovery"]["residual_count"], 0)
        self.assertEqual(mutation["observed_recovery"]["estimated_incremental_cost_usd"], 0.0)
        self.assertIn("AWS did not observe", report["scenarios"][1]["synthetic_extension"])
        self.assertIn("not customer validation", report["claim_boundary"])
        markdown = render_markdown(report)
        self.assertIn("`SETTLE`", markdown)
        self.assertIn("`QUARANTINE`", markdown)
        self.assertIn("`COMPENSATE`", markdown)


if __name__ == "__main__":
    unittest.main()

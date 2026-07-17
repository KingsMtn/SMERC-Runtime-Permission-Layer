import copy
import unittest
from pathlib import Path

from reference_engine.governance_report import (
    GOVERNANCE_REPORT_VERSION,
    build_report,
    load_bundle,
    render_markdown,
)


BUNDLE = Path("examples/governance_report/github_actions_governance_bundle.json")


class GovernanceReportTests(unittest.TestCase):
    def test_example_bundle_builds_replayable_report(self):
        report = build_report(BUNDLE)
        self.assertEqual(report["version"], GOVERNANCE_REPORT_VERSION)
        self.assertEqual(report["summary"]["posture"], "THROTTLE")
        self.assertEqual(report["summary"]["route_state"], "CONSTRAINED_EXECUTE")
        self.assertTrue(report["summary"]["control_mapping_executable"])
        self.assertTrue(report["summary"]["ledger_valid"])
        self.assertEqual(report["summary"]["evidence_artifact_count"], 4)
        self.assertEqual(report["summary"]["permit_id"], "permit_0123456789abcdef0123456789abcdef")
        self.assertEqual(report["summary"]["execution_outcome"], "SUCCEEDED")
        self.assertEqual(report["summary"]["reviewer_verdict"], "agree")
        self.assertTrue(all(check["passed"] for check in report["cross_checks"]))
        self.assertIn("control_evidence_satisfies_permit", {check["check_id"] for check in report["cross_checks"]})
        self.assertIn("execution_sparta_route_matches_route_report", {check["check_id"] for check in report["cross_checks"]})
        self.assertIn("pilot review evidence", report["recommended_next_action"])

    def test_markdown_is_ciso_readable_and_does_not_overclaim(self):
        markdown = render_markdown(build_report(BUNDLE))
        self.assertIn("SMERC GitHub Actions Governance Report", markdown)
        self.assertIn("not production certification", markdown)
        self.assertIn("Control mapping executable", markdown)
        self.assertIn("Evidence artifacts", markdown)
        self.assertIn("Reviewer verdict", markdown)
        self.assertIn("known_limits", markdown.lower().replace(" ", "_"))

    def test_bundle_validation_is_strict(self):
        bundle = load_bundle(BUNDLE)
        bundle["extra"] = True
        with self.assertRaisesRegex(ValueError, "unknown"):
            from reference_engine.governance_report import _strict_object, BUNDLE_FIELDS

            _strict_object(bundle, BUNDLE_FIELDS, "governance_bundle")

    def test_cross_check_failure_blocks_recommendation(self):
        report = build_report(BUNDLE)
        altered = copy.deepcopy(report)
        altered["cross_checks"][0]["passed"] = False
        from reference_engine.governance_report import _recommended_next_action

        recommendation = _recommended_next_action(altered["cross_checks"])
        self.assertIn("Do not use this bundle", recommendation)

    def test_paths_cannot_escape_repository_root(self):
        bundle = load_bundle(BUNDLE)
        bundle["decision_path"] = "../outside.json"
        temp = Path("test_outputs/bad_governance_bundle.json")
        temp.parent.mkdir(exist_ok=True)
        temp.write_text(__import__("json").dumps(bundle), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "inside the repository root"):
            build_report(temp)

    def test_evidence_paths_are_required_and_strict(self):
        bundle = load_bundle(BUNDLE)
        del bundle["evidence_paths"]["execution_report_path"]
        temp = Path("test_outputs/bad_governance_evidence_bundle.json")
        temp.parent.mkdir(exist_ok=True)
        temp.write_text(__import__("json").dumps(bundle), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing required"):
            load_bundle(temp)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from reference_engine.end_to_end_reviewer_flow import build_flow_report, render_markdown


ROOT = Path(__file__).resolve().parents[1]


class EndToEndReviewerFlowTests(unittest.TestCase):
    def test_builds_clean_reviewer_flow(self):
        report = build_flow_report()

        self.assertEqual(report["version"], "smerc.end-to-end-reviewer-flow.v1")
        self.assertEqual(
            report["flow"],
            [
                "metadata_intake",
                "schema_validation",
                "policy_evaluation",
                "posture_output",
                "evidence_report",
            ],
        )
        self.assertEqual(report["metadata_intake"]["accepted_action_count"], 5)
        self.assertEqual(report["schema_validation"]["tool_call_count"], 7)
        self.assertEqual(report["policy"]["policy_id"], "github-actions-shadow-mode")
        self.assertEqual(report["posture_output"]["posture_counts"]["FREEZE"], 2)
        self.assertEqual(report["posture_output"]["posture_counts"]["THROTTLE"], 2)
        self.assertEqual(report["posture_output"]["posture_counts"]["DENY"], 1)

    def test_posture_rows_bind_policy_and_routes(self):
        report = build_flow_report()
        rows = report["posture_output"]["rows"]

        self.assertEqual(len(rows), 5)
        by_id = {row["action_id"]: row for row in rows}
        self.assertEqual(by_id["ACT-001"]["route_hint"], "CONSTRAINED_EXECUTE")
        self.assertEqual(by_id["ACT-003"]["route_hint"], "BLOCK")
        self.assertEqual(by_id["ACT-004"]["route_hint"], "PAUSE")
        self.assertEqual(by_id["ACT-001"]["policy_hash"], report["policy"]["policy_hash"])

    def test_markdown_and_docs_are_reviewer_readable(self):
        markdown = render_markdown(build_flow_report())
        doc = (ROOT / "docs" / "End_To_End_Reviewer_Flow.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("metadata intake -> schema validation -> policy evaluation", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("python -m reference_engine.end_to_end_reviewer_flow", doc)
        self.assertIn("docs/End_To_End_Reviewer_Flow.md", readme)


if __name__ == "__main__":
    unittest.main()

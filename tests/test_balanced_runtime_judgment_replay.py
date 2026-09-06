import unittest
from pathlib import Path

from reference_engine.balanced_runtime_judgment_replay import build_report, render_markdown, write_outputs
from reference_engine.customer_evaluation import load_payload


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "examples" / "balanced_runtime_judgment_actions.json"


class BalancedRuntimeJudgmentReplayTests(unittest.TestCase):
    def test_builds_one_of_each_runtime_posture(self):
        report = build_report(load_payload(INPUTS))

        self.assertEqual(report["version"], "smerc.balanced-runtime-judgment-replay.v1")
        self.assertEqual(report["record_count"], 5)
        self.assertEqual(report["valid_dll_ledgers"], 5)
        self.assertEqual(
            report["expected_posture_counts"],
            {"ALLOW": 1, "DENY": 1, "ESCALATE": 1, "FREEZE": 1, "THROTTLE": 1},
        )
        self.assertEqual(
            report["smerc_posture_counts"],
            {"ALLOW": 1, "DENY": 1, "ESCALATE": 1, "FREEZE": 1, "THROTTLE": 1},
        )
        self.assertEqual(report["delta_counts"], {"MATCH": 5})

    def test_includes_all_governance_route_states(self):
        report = build_report(load_payload(INPUTS))

        self.assertEqual(
            report["governance_route_counts"],
            {
                "BLOCK": 1,
                "CONSTRAINED_EXECUTE": 1,
                "EXECUTE": 1,
                "PAUSE": 1,
                "REVIEW_REQUIRED": 1,
            },
        )

    def test_markdown_explains_work_result_impact_and_boundary(self):
        markdown = render_markdown(build_report(load_payload(INPUTS)))

        self.assertIn("Balanced Runtime Judgment Replay Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("Reviewer Question", markdown)
        self.assertIn("`ALLOW`", markdown)
        self.assertIn("`ESCALATE`", markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "balanced_runtime_judgment_replay"
        scratch.mkdir(parents=True, exist_ok=True)
        report = build_report(load_payload(INPUTS))
        report_json = scratch / "report.json"
        report_md = scratch / "report.md"
        customer_json = scratch / "customer.json"
        customer_md = scratch / "customer.md"

        write_outputs(
            report,
            json_output=report_json,
            markdown_output=report_md,
            customer_json_output=customer_json,
            customer_markdown_output=customer_md,
        )

        self.assertIn("Balanced Runtime Judgment Replay Report", report_md.read_text(encoding="utf-8"))
        self.assertIn("SMERC Customer Evaluation Report", customer_md.read_text(encoding="utf-8"))
        self.assertEqual(load_payload(customer_json)["summary"]["valid_ledgers"], 5)

    def test_docs_and_reviewer_bundle_link_replay(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        replay_doc = (ROOT / "docs" / "Balanced_Runtime_Judgment_Replay.md").read_text(encoding="utf-8")
        ai_bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        for text in [readme, ai_bundle]:
            self.assertIn("docs/Balanced_Runtime_Judgment_Replay.md", text)
        self.assertIn("python -m reference_engine.balanced_runtime_judgment_replay", replay_doc)


if __name__ == "__main__":
    unittest.main()

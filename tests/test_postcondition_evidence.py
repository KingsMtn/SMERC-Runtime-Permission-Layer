import unittest
from pathlib import Path

from reference_engine.postcondition_evidence import (
    build_postcondition_report,
    load_json_object,
    load_observations,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "reports" / "public_benchmark_customer_evaluation" / "customer_evaluation_report.json"
OBSERVATIONS = ROOT / "examples" / "postcondition_observations.json"


class PostconditionEvidenceTests(unittest.TestCase):
    def test_builds_postcondition_report_from_customer_evaluation(self):
        report = build_postcondition_report(load_json_object(EVALUATION), load_observations(OBSERVATIONS))

        self.assertEqual(report["version"], "smerc.postcondition-evidence.v1")
        self.assertEqual(report["evaluated_actions"], 10)
        self.assertEqual(report["observed_actions"], 5)
        self.assertEqual(report["coverage_counts"]["observed"], 5)
        self.assertEqual(report["coverage_counts"]["unobserved"], 5)
        self.assertGreaterEqual(report["postcondition_status_counts"].get("pass", 0), 3)
        self.assertGreaterEqual(report["postcondition_status_counts"].get("gap", 0), 1)
        self.assertIn("not live cloud", report["evidence_boundary"])

    def test_detects_missing_required_control_for_constrained_route(self):
        report = build_postcondition_report(load_json_object(EVALUATION), load_observations(OBSERVATIONS))
        by_id = {record["action_id"]: record for record in report["records"]}

        constrained = by_id["PUBLIC_BENCH_009_apply_production_network_and_role_change"]
        self.assertEqual(constrained["postcondition_status"], "gap")
        self.assertIn("require_rollback_plan", constrained["missing_controls"])
        self.assertIn("Missing required control evidence", " ".join(constrained["findings"]))

    def test_markdown_explains_work_result_impact_and_reviewer_question(self):
        markdown = render_markdown(build_postcondition_report(load_json_object(EVALUATION), load_observations(OBSERVATIONS)))

        self.assertIn("SMERC Postcondition Evidence Report", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Observed actions", markdown)
        self.assertIn("Reviewer Question", markdown)

    def test_writes_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "postcondition_evidence"
        report = build_postcondition_report(load_json_object(EVALUATION), load_observations(OBSERVATIONS))
        json_path = scratch / "postconditions.json"
        markdown_path = scratch / "postconditions.md"

        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertIn("postcondition-evidence", json_path.read_text(encoding="utf-8"))
        self.assertIn("SMERC Postcondition Evidence Report", markdown_path.read_text(encoding="utf-8"))

    def test_docs_and_readme_reference_postcondition_evidence(self):
        docs = (ROOT / "docs" / "Postcondition_Evidence.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.postcondition_evidence", docs)
        self.assertIn("controls actually happened", docs)
        self.assertIn("docs/Postcondition_Evidence.md", readme)


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path

from reference_engine.serious_reviewer_bundle import (
    VERSION,
    build_serious_reviewer_bundle,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class SeriousReviewerBundleTests(unittest.TestCase):
    def test_builds_financial_bundle_across_serious_review_path(self):
        bundle = build_serious_reviewer_bundle(
            root=ROOT,
            workflow_family="financial",
            requested_actions=12,
            performance_iterations=1,
        )

        self.assertEqual(bundle["version"], VERSION)
        self.assertEqual(bundle["workflow_family"], "financial")
        self.assertIn(bundle["bundle_status"], {"ready_for_shadow_mode_discussion", "ready_for_limited_review"})
        self.assertIn("customer_evaluation", bundle["reports"])
        self.assertIn("postcondition_evidence", bundle["reports"])
        self.assertIn("performance", bundle["reports"])
        self.assertIn("customer_owned_metadata_request", bundle["reports"])
        self.assertIn("external_reviewer_metadata_response_assessment", bundle["reports"])
        self.assertEqual(
            bundle["reports"]["external_reviewer_metadata_response_assessment"]["disposition"],
            "ready_for_customer_metadata_evaluation",
        )
        self.assertIn("production access", bundle["evidence_boundary"])

    def test_blocks_not_ready_reviewer_response(self):
        payload = json.loads((ROOT / "examples" / "external_reviewer_metadata_response_example.json").read_text())
        payload["sensitive_data_included"] = True
        scratch = ROOT / "tests" / "_tmp" / "serious_reviewer_bundle"
        response_path = scratch / "unsafe_response.json"
        response_path.parent.mkdir(parents=True, exist_ok=True)
        response_path.write_text(json.dumps(payload), encoding="utf-8")

        bundle = build_serious_reviewer_bundle(
            root=ROOT,
            response_path=response_path.relative_to(ROOT),
            performance_iterations=1,
        )

        self.assertEqual(bundle["bundle_status"], "not_ready_for_pilot")
        self.assertIn("external reviewer response is not ready", bundle["readiness"]["blockers"])

    def test_markdown_summarizes_work_result_impact_and_next_action(self):
        markdown = render_markdown(
            build_serious_reviewer_bundle(root=ROOT, workflow_family="general", performance_iterations=1)
        )

        self.assertIn("# SMERC Serious Reviewer Bundle", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Included Reports", markdown)
        self.assertIn("Next Action", markdown)
        self.assertIn("production SLA", markdown)

    def test_writes_bundle_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "serious_reviewer_bundle_outputs"
        bundle = build_serious_reviewer_bundle(root=ROOT, workflow_family="cloud", performance_iterations=1)

        write_outputs(bundle, output_dir=scratch)

        self.assertEqual(
            json.loads((scratch / "serious_reviewer_bundle.json").read_text(encoding="utf-8"))["version"],
            VERSION,
        )
        self.assertIn("SMERC Serious Reviewer Bundle", (scratch / "Serious_Reviewer_Bundle.md").read_text())
        self.assertTrue((scratch / "Customer_Evaluation_Report.md").exists())
        self.assertTrue((scratch / "Postcondition_Evidence_Report.md").exists())
        self.assertTrue((scratch / "Serious_Report_Performance.md").exists())
        self.assertTrue((scratch / "Customer_Owned_Metadata_Request.md").exists())
        self.assertTrue((scratch / "External_Reviewer_Metadata_Response_Assessment.md").exists())

    def test_docs_and_readme_reference_bundle(self):
        docs = (ROOT / "docs" / "Serious_Reviewer_Bundle.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ai_bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.serious_reviewer_bundle", docs)
        self.assertIn("docs/Serious_Reviewer_Bundle.md", readme)
        self.assertIn("serious reviewer bundle", ai_bundle.lower())


if __name__ == "__main__":
    unittest.main()

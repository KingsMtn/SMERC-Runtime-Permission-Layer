import json
import unittest
from pathlib import Path

from reference_engine.external_reviewer_metadata_response import (
    VERSION,
    assess_response,
    load_payload,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "external_reviewer_metadata_response_example.json"


class ExternalReviewerMetadataResponseTests(unittest.TestCase):
    def test_assesses_ready_response(self):
        report = assess_response(load_payload(EXAMPLE))

        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["disposition"], "ready_for_customer_metadata_evaluation")
        self.assertTrue(report["ready_for_customer_metadata_evaluation"])
        self.assertEqual(report["blockers"], [])
        self.assertIn("postcondition evidence", report["recommended_next_action"])

    def test_blocks_sensitive_or_live_access_response(self):
        payload = load_payload(EXAMPLE)
        payload["sensitive_data_included"] = True
        payload["live_access_requested"] = True

        report = assess_response(payload)

        self.assertEqual(report["disposition"], "not_ready")
        joined = " ".join(report["blockers"])
        self.assertIn("sensitive data", joined)
        self.assertIn("live access", joined)

    def test_warns_when_labels_or_postconditions_are_missing(self):
        payload = load_payload(EXAMPLE)
        payload["reviewer_labels_available"] = False
        payload["postcondition_observation_possible"] = False

        report = assess_response(payload)

        self.assertEqual(report["disposition"], "ready_with_review_limits")
        self.assertGreaterEqual(len(report["warnings"]), 2)

    def test_markdown_and_outputs_are_reviewable(self):
        report = assess_response(load_payload(EXAMPLE))
        markdown = render_markdown(report)

        self.assertIn("# External Reviewer Metadata Response Assessment", markdown)
        self.assertIn("Work / Result / Impact", markdown)
        self.assertIn("Evidence Boundary", markdown)

        scratch = ROOT / "tests" / "_tmp" / "external_reviewer_metadata_response"
        json_path = scratch / "assessment.json"
        markdown_path = scratch / "assessment.md"
        write_outputs(report, json_path=json_path, markdown_path=markdown_path)

        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8"))["version"], VERSION)
        self.assertIn("External Reviewer", markdown_path.read_text(encoding="utf-8"))

    def test_docs_and_readme_reference_response_assessment(self):
        docs = (ROOT / "docs" / "External_Reviewer_Metadata_Response.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.external_reviewer_metadata_response", docs)
        self.assertIn("docs/External_Reviewer_Metadata_Response.md", readme)


if __name__ == "__main__":
    unittest.main()

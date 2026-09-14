import json
import unittest
from pathlib import Path

from reference_engine.aws_decision_api_surface import (
    OPENAPI_PATH,
    OPERATION_ID,
    VERSION,
    build_decision_api_surface,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class AWSDecisionAPISurfaceTests(unittest.TestCase):
    def test_builds_reviewable_decision_surface(self):
        report = build_decision_api_surface(root=ROOT)

        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["status"], "reviewable_aws_decision_surface")
        self.assertEqual(report["operation_id"], OPERATION_ID)
        self.assertEqual(report["openapi_path"], OPENAPI_PATH)
        self.assertEqual(report["request_id"], "AWS_BEDROCK_ACTION_GROUP_LAMBDA_001")
        self.assertIn(report["posture"], {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertTrue(report["ledger_valid"])
        self.assertEqual(report["readiness_blockers"], [])
        self.assertIn("AgentCore Gateway-style OpenAPI tool surface", report["compatibility_targets"])
        self.assertIn("does not call AWS", report["evidence_boundary"])

    def test_openapi_has_gateway_friendly_operation(self):
        contract = json.loads((ROOT / OPENAPI_PATH).read_text(encoding="utf-8"))
        operation = contract["paths"]["/smerc/decision"]["post"]
        response_schema = contract["components"]["schemas"]["AwsDecisionResponse"]

        self.assertEqual(contract["openapi"], "3.1.0")
        self.assertEqual(operation["operationId"], OPERATION_ID)
        self.assertIn("metadata-only", operation["description"])
        self.assertIn("ledger_valid", response_schema["required"])
        self.assertIn("evidence_boundary", response_schema["required"])
        self.assertIn("AWS endorsement", contract["info"]["description"])

    def test_markdown_and_docs_link_surface(self):
        markdown = render_markdown(build_decision_api_surface(root=ROOT))
        docs = (ROOT / "docs" / "AWS_Decision_API_Surface.md").read_text(encoding="utf-8")
        ecosystem = (ROOT / "docs" / "AWS_Ecosystem_Entry_Path.md").read_text(encoding="utf-8")
        quickstart = (ROOT / "docs" / "AWS_Reviewer_Quickstart.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("# AWS Decision API Surface", markdown)
        self.assertIn("operationId", docs)
        self.assertIn("evaluateAwsActionRecoverability", docs)
        self.assertIn("docs/AWS_Decision_API_Surface.md", ecosystem)
        self.assertIn("docs/AWS_Decision_API_Surface.md", quickstart)
        self.assertIn("docs/AWS_Decision_API_Surface.md", readme)

    def test_writes_decision_surface_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "aws_decision_api_surface"
        report = build_decision_api_surface(root=ROOT)

        write_outputs(report, output_dir=scratch)

        self.assertEqual(
            json.loads((scratch / "aws_decision_api_surface.json").read_text(encoding="utf-8"))["version"],
            VERSION,
        )
        self.assertTrue((scratch / "AWS_Decision_API_Surface.md").exists())
        self.assertTrue((scratch / "sample_decision_request.json").exists())
        self.assertTrue((scratch / "sample_decision_response.json").exists())


if __name__ == "__main__":
    unittest.main()

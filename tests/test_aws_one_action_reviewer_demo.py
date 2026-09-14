import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.aws_one_action_reviewer_demo import build_report, load_payload, render_markdown, write_outputs


ROOT = Path(__file__).resolve().parents[1]


class AWSOneActionReviewerDemoTests(unittest.TestCase):
    def test_builds_small_aws_style_reviewer_report(self):
        report = build_report(load_payload(ROOT / "examples" / "aws_one_action_reviewer_samples.json"))

        self.assertEqual(report["version"], "smerc.aws-one-action-reviewer-demo.v1")
        self.assertEqual(report["sample_count"], 8)
        self.assertIn("iam", report["summary"]["aws_surface_counts"])
        self.assertIn("rds", report["summary"]["aws_surface_counts"])
        self.assertIn("cost_management", report["summary"]["aws_surface_counts"])
        self.assertGreaterEqual(report["summary"]["non_executable_routes"], 1)
        self.assertIn(report["summary"]["highest_exposure_action"], {record["action_id"] for record in report["records"]})

    def test_can_select_one_action(self):
        payload = load_payload(ROOT / "examples" / "aws_one_action_reviewer_samples.json")
        report = build_report(payload, action_id="AWS_ONE_RDS_CLUSTER_DELETE")

        self.assertEqual(report["sample_count"], 1)
        record = report["records"][0]
        self.assertEqual(record["action_id"], "AWS_ONE_RDS_CLUSTER_DELETE")
        self.assertIn(record["posture"], {"FREEZE", "DENY", "ESCALATE"})
        self.assertFalse(record["executable"])

    def test_markdown_explains_boundary_and_reviewer_ask(self):
        report = build_report(load_payload(ROOT / "examples" / "aws_one_action_reviewer_samples.json"), action_id="AWS_ONE_IAM_ROLE_EXPANSION")
        markdown = render_markdown(report)

        self.assertIn("AWS One-Action Reviewer Demo", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("does not connect to AWS", markdown)
        self.assertIn("Recommended Reviewer Ask", markdown)

    def test_write_outputs_and_cli(self):
        temp = ROOT / "reports" / "aws_one_action_reviewer_demo"
        temp.mkdir(parents=True, exist_ok=True)
        json_path = temp / "_test_report.json"
        md_path = temp / "_test_report.md"
        cli_json = temp / "_test_cli.json"
        cli_md = temp / "_test_cli.md"
        try:
            report = build_report(
                load_payload(ROOT / "examples" / "aws_one_action_reviewer_samples.json"),
                action_id="AWS_ONE_ECS_SCALE_SHIFT",
            )
            write_outputs(report, json_path, md_path)

            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8"))["sample_count"], 1)
            self.assertIn("AWS_ONE_ECS_SCALE_SHIFT", md_path.read_text(encoding="utf-8"))

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reference_engine.aws_one_action_reviewer_demo",
                    "--action-id",
                    "AWS_ONE_SECRETS_ROTATION",
                    "--json-output",
                    str(cli_json),
                    "--markdown-output",
                    str(cli_md),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("AWS_ONE_SECRETS_ROTATION", result.stdout)
            self.assertEqual(json.loads(cli_json.read_text(encoding="utf-8"))["sample_count"], 1)
        finally:
            for path in (json_path, md_path, cli_json, cli_md):
                if path.exists():
                    path.unlink()

    def test_docs_and_readme_reference_reviewer_demo(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        doc = (ROOT / "docs" / "Try_SMERC_On_One_Action.md").read_text(encoding="utf-8")
        bundle = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        self.assertIn("reference_engine.aws_one_action_reviewer_demo", readme)
        self.assertIn("reference_engine.aws_one_action_reviewer_demo", doc)
        self.assertIn("AWS One-Action Reviewer Demo", bundle)


if __name__ == "__main__":
    unittest.main()

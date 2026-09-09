import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AWSReviewerQuickstartTests(unittest.TestCase):
    def test_quickstart_points_to_one_command_and_three_outputs(self):
        text = (ROOT / "docs" / "AWS_Reviewer_Quickstart.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.aws_reviewer_bundle", text)
        self.assertIn("AWS_Reviewer_Bundle.md", text)
        self.assertIn("AWS_Agent_Action_Chain.md", text)
        self.assertIn("AWS_Metadata_Adapter_Report.md", text)
        self.assertIn("What This Does Not Prove", text)

    def test_customer_metadata_template_is_valid_and_safe(self):
        template = json.loads((ROOT / "examples" / "aws_customer_metadata_template.json").read_text(encoding="utf-8"))

        self.assertIsInstance(template, list)
        self.assertEqual(len(template), 1)
        row = template[0]
        self.assertIn("policy_engine_decision", row)
        self.assertIn("derived_output_contains_restricted_summary", row)
        self.assertIn("parameter_constraints_present", row)
        prohibited = {"account_id", "arn", "raw_log", "secret", "credentials", "production_command"}
        self.assertTrue(prohibited.isdisjoint({key.lower() for key in row}))

    def test_readme_and_bundle_reference_quickstart(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        bundle = (ROOT / "docs" / "AWS_Reviewer_Bundle.md").read_text(encoding="utf-8")

        self.assertIn("docs/AWS_Reviewer_Quickstart.md", readme)
        self.assertIn("docs/AWS_Reviewer_Quickstart.md", bundle)


if __name__ == "__main__":
    unittest.main()

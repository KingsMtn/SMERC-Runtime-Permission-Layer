from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/aws-oidc-readonly-proof.yml"
TEMPLATE = ROOT / "infrastructure/aws/github-oidc-readonly.yaml"
DOC = ROOT / "docs/GitHub_AWS_OIDC_ReadOnly_Proof.md"


class GitHubAWSOIDCReadOnlyProofTests(unittest.TestCase):
    def test_workflow_is_manual_and_identity_only(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("push:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("id-token: write", text)
        self.assertIn("contents: read", text)
        self.assertIn("environment: aws-readonly-pilot", text)
        self.assertIn("aws sts get-caller-identity", text)
        self.assertNotIn("AWS_ACCESS_KEY_ID", text)
        for mutation in ("cloudformation deploy", "lambda update", "s3 cp", "eventbridge", "bedrock"):
            self.assertNotIn(mutation, text.lower())

    def test_external_action_is_pinned_and_account_is_bounded(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn(
            "aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd",
            text,
        )
        self.assertIn('allowed-account-ids: "497790081591"', text)
        self.assertIn("role-to-assume: ${{ vars.AWS_READONLY_ROLE_ARN }}", text)

    def test_iam_trust_is_exact_and_role_has_no_service_policy(self):
        text = TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("token.actions.githubusercontent.com:aud: sts.amazonaws.com", text)
        self.assertIn("repo:${GitHubOwner}/${GitHubRepository}:environment:${GitHubEnvironment}", text)
        self.assertIn("Action: sts:AssumeRoleWithWebIdentity", text)
        self.assertNotIn("Policies:", text)
        self.assertNotIn('Action: "*"', text)
        self.assertNotIn("Resource: '*'", text)

    def test_documentation_preserves_identity_execution_separation(self):
        text = DOC.read_text(encoding="utf-8")

        self.assertIn("role has no AWS service permissions", text)
        self.assertIn("Do not add AWS service permissions to this role", text)
        self.assertIn("A later enforcement role must", text)
        self.assertIn("be separate, action-specific, cost-reviewed, and admitted through SMERC", text)


if __name__ == "__main__":
    unittest.main()

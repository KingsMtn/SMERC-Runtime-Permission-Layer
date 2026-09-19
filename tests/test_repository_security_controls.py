import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_ACTION = re.compile(r"^\s*uses:\s*([^./][^@\s]*)@([^\s#]+)", re.MULTILINE)
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


class RepositorySecurityControlTests(unittest.TestCase):
    def test_external_github_actions_are_pinned_to_commit_shas(self):
        violations = []
        for workflow in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
            text = workflow.read_text(encoding="utf-8")
            for action, revision in EXTERNAL_ACTION.findall(text):
                if not COMMIT_SHA.fullmatch(revision):
                    violations.append(f"{workflow.name}: {action}@{revision}")
        self.assertEqual(violations, [], "External actions must use immutable 40-character commit SHAs")

    def test_owner_and_dependency_controls_exist(self):
        codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
        dependabot = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")

        self.assertIn("* @KingsMtn", codeowners)
        self.assertIn("/reference_engine/ @KingsMtn", codeowners)
        self.assertIn("package-ecosystem: github-actions", dependabot)

    def test_public_private_boundary_is_documented(self):
        boundary = (ROOT / "docs" / "Public_Private_Product_Boundary.md").read_text(encoding="utf-8")

        self.assertIn("authenticated production AWS MCP executors", boundary)
        self.assertIn("Removal from Git", boundary)


if __name__ == "__main__":
    unittest.main()

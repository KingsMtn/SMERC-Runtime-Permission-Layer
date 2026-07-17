import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SPARTaV2FrameworkTests(unittest.TestCase):
    def test_sparta_docs_define_current_and_future_role(self):
        operations = (ROOT / "docs" / "SPARTa_Router_Operations.md").read_text(encoding="utf-8")
        framework = (ROOT / "docs" / "SPARTa_v2_Execution_Adapter_Framework.md").read_text(encoding="utf-8")

        self.assertIn("Stateful Posture-Aware Routing and Tooling Adapter", operations)
        self.assertIn("Adapter registry exists", operations)
        self.assertNotIn("No adapter registry yet", operations)
        self.assertIn("Stateful Posture-Aware Routing and Tooling Adapter", framework)
        self.assertIn("GitHub Actions Adapter", framework)
        self.assertIn("ServiceNow Or Jira Adapter", framework)
        self.assertIn("Slack Or Teams Review Adapter", framework)
        self.assertIn("Return To Ledger", framework)
        self.assertIn("fail closed", framework)
        self.assertIn("not production certification", framework)
        self.assertIn("SPARTa should become SMERC's execution-control layer", framework)

    def test_readme_links_to_sparta_v2_framework(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/SPARTa_v2_Execution_Adapter_Framework.md", readme)
        self.assertIn("execution-adapter layer", readme)


if __name__ == "__main__":
    unittest.main()

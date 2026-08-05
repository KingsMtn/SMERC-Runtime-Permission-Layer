import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "AI_Assisted_Build_And_Red_Team_Strategy.md"


class AIAssistedBuildStrategyTests(unittest.TestCase):
    def test_strategy_assigns_tool_roles_without_overclaiming(self):
        text = DOC.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("primary coding agent", lowered)
        self.assertIn("second-opinion coding agent", lowered)
        self.assertIn("github-native coding agent", lowered)
        self.assertIn("human expert", lowered)
        self.assertIn("should not be treated as proof", lowered)

    def test_strategy_preserves_human_validation_boundary(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("AI-generated reviewer labels are drafts only", text)
        self.assertIn("Human reviewers must approve final labels", text)
        self.assertIn("buyer willingness to pay", text)
        self.assertIn("production deployment approval", text)

    def test_strategy_defines_red_team_and_simulation_prompts(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Review this SMERC branch as a skeptical CISO", text)
        self.assertIn("Create a pull request that modifies a production deployment workflow", text)
        self.assertIn("Generate only", text)
        self.assertIn("metadata suitable for SMERC review", text)


if __name__ == "__main__":
    unittest.main()

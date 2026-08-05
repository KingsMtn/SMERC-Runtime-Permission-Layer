import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "Search_Visibility_Launch_Plan.md"
FINDABILITY = ROOT / "docs" / "Findability_And_AI_Discovery.md"
COMMUNITY = ROOT / "docs" / "Community_Submission_Kit.md"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"


class SearchVisibilityLaunchPlanTests(unittest.TestCase):
    def test_launch_plan_targets_specific_classification(self):
        text = PLAN.read_text(encoding="utf-8")

        self.assertIn("recoverability checkpoint before automated actions execute", text)
        self.assertIn("Microsoft-style security response replay", text)
        self.assertIn("MCP tool-call governance", text)
        self.assertIn("Visibility is not validation", text)

    def test_launch_plan_lists_owner_required_steps(self):
        text = PLAN.read_text(encoding="utf-8")

        for phrase in (
            "Recommended GitHub Topics",
            "repository owner access",
            "Search Console Steps",
            "Submit `https://admirable-sorbet-9986d5.netlify.app/sitemap.xml`",
            "Bing Webmaster Tools",
        ):
            self.assertIn(phrase, text)

    def test_findability_and_submission_language_reflect_checkpoint_wedge(self):
        combined = FINDABILITY.read_text(encoding="utf-8") + "\n" + COMMUNITY.read_text(encoding="utf-8")

        self.assertIn("recoverability checkpoint", combined)
        self.assertIn("microsoft-security-replay.html", combined)
        self.assertIn("mcp-governance.html", combined)
        self.assertIn("does not claim incident reduction", combined.lower())

    def test_readme_and_changelog_link_visibility_plan(self):
        self.assertIn("docs/Search_Visibility_Launch_Plan.md", README.read_text(encoding="utf-8"))
        self.assertIn("search visibility", CHANGELOG.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CommunityPartnerDocsTests(unittest.TestCase):
    def test_partner_docs_invite_interest_without_overclaiming(self):
        community = (ROOT / "COMMUNITY.md").read_text(encoding="utf-8")
        partner = (ROOT / "docs" / "Partner_Program.md").read_text(encoding="utf-8")
        outreach = (ROOT / "docs" / "Community_Outreach_Kit.md").read_text(encoding="utf-8")
        public_review = (ROOT / "docs" / "Public_Review_And_Feedback.md").read_text(encoding="utf-8")
        submission = (ROOT / "docs" / "Community_Submission_Kit.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(encoding="utf-8")

        combined = "\n".join([community, partner, outreach, public_review, submission, indexing])
        self.assertIn("Design Partners", community)
        self.assertIn("Integration Partners", community)
        self.assertIn("Research Reviewers", community)
        self.assertIn("Azure/Microsoft", public_review)
        self.assertIn("allowed", public_review)
        self.assertIn("recoverable enough to execute now", public_review)
        self.assertIn("Microsoft Tech Community Draft", submission)
        self.assertIn("Hacker News Draft", submission)
        self.assertIn("Product Hunt Draft", submission)
        self.assertIn("Do not claim incident reduction", submission)
        self.assertIn("llms.txt", indexing)
        self.assertIn("humans.txt", indexing)
        self.assertIn("project.json", indexing)
        self.assertIn("Structured Profile", indexing)
        self.assertIn("Project status", indexing)
        self.assertIn("not production-certified", indexing)
        self.assertIn("proxy evidence, not production validation", outreach)
        self.assertIn("production certification", partner)
        self.assertNotIn("SMERC prevents incidents", combined.replace('"SMERC prevents incidents."', ""))

    def test_issue_templates_cover_partner_and_scenario_paths(self):
        templates = ROOT / ".github" / "ISSUE_TEMPLATE"

        self.assertTrue((templates / "design_partner_interest.md").exists())
        self.assertTrue((templates / "integration_partner_interest.md").exists())
        self.assertTrue((templates / "public_review_feedback.md").exists())
        self.assertTrue((templates / "scenario_contribution.md").exists())

        design = (templates / "design_partner_interest.md").read_text(encoding="utf-8")
        public = (templates / "public_review_feedback.md").read_text(encoding="utf-8")
        scenario = (templates / "scenario_contribution.md").read_text(encoding="utf-8")
        self.assertIn("Shadow Mode Feasibility", design)
        self.assertIn("Recoverability Question", public)
        self.assertIn("Missing Evidence", public)
        self.assertIn("Recoverability Analysis", scenario)
        self.assertIn("Do not include secrets", design)
        self.assertIn("Do not include secrets", public)

    def test_pull_request_template_requires_claims_check(self):
        template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")

        self.assertIn("Evidence Type", template)
        self.assertIn("Claims Check", template)
        self.assertIn("does not claim production validation", template)


if __name__ == "__main__":
    unittest.main()

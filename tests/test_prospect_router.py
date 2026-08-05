import copy
import unittest
from pathlib import Path

from reference_engine.prospect_router import load_payload, render_markdown, route_prospect


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "prospect_route_sample.json"


class ProspectRouterTests(unittest.TestCase):
    def test_routes_stablecoin_prospect_to_financial_shadow_mode(self):
        report = route_prospect(load_payload(SAMPLE))

        self.assertEqual(report["recommended_route"], "smerc_f_financial_shadow_mode")
        self.assertGreater(report["smerc_f_financial_score"], report["core_github_actions_score"])
        self.assertFalse(report["blockers"])
        self.assertIn("SMERC_F_Financial_Shadow_Mode_Pilot_Path.md", " ".join(report["recommended_materials"]))
        self.assertIn("not proof of buyer intent", report["evidence_boundary"])

    def test_routes_github_actions_prospect_to_core_pilot(self):
        payload = load_payload(SAMPLE)
        payload["organization"] = "Example Platform Team"
        payload["workflow_signals"]["github_actions_or_ci_cd_workflow"] = True
        payload["workflow_signals"]["financial_or_stablecoin_workflow"] = False
        report = route_prospect(payload)

        self.assertEqual(report["recommended_route"], "core_github_actions_shadow_mode")
        self.assertIn("Pilot_Handoff_Checklist.md", " ".join(report["recommended_materials"]))

    def test_blocks_bad_financial_expectations(self):
        payload = copy.deepcopy(load_payload(SAMPLE))
        payload["workflow_signals"]["expects_aml_compliance_replacement"] = True
        payload["workflow_signals"]["live_fund_movement_required_for_first_test"] = True
        report = route_prospect(payload)

        self.assertEqual(report["recommended_route"], "review_only")
        self.assertIn("replace AML compliance", " ".join(report["blockers"]))
        self.assertIn("live fund movement", " ".join(report["blockers"]))

    def test_markdown_contains_recommendation(self):
        markdown = render_markdown(route_prospect(load_payload(SAMPLE)))

        self.assertIn("Recommendation", markdown)
        self.assertIn("smerc_f_financial_shadow_mode", markdown)
        self.assertIn("Evidence Boundary", markdown)

    def test_readme_links_prospect_routing(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Prospect_Routing.md", readme)


if __name__ == "__main__":
    unittest.main()

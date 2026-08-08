import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SelfServicePilotLayerTests(unittest.TestCase):
    def test_self_service_start_here_is_founder_light_and_specific(self):
        text = (ROOT / "pilot_package" / "Self_Service_Pilot_Start_Here.md").read_text(encoding="utf-8")

        self.assertIn("founder-light path", text)
        self.assertIn("one GitHub Actions workflow", text)
        self.assertIn("metadata-only boundary", text)
        self.assertIn("10 to 25 plain-language sample action descriptions", text)
        self.assertIn("reference_engine.github_actions_customer_pilot_intake", text)
        self.assertIn("reference_engine.github_actions_pilot_readiness", text)
        self.assertIn("reference_engine.core_pilot_package", text)
        self.assertIn("Do not move to enforcement", text)
        self.assertIn("does not prove demand", text)

    def test_hand_off_email_points_to_public_self_service_links_and_boundaries(self):
        text = (ROOT / "docs" / "Self_Service_Pilot_Hand_Off_Email.md").read_text(encoding="utf-8")

        self.assertIn("self-service GitHub Actions pilot path", text)
        self.assertIn("self-service-pilot.html", text)
        self.assertIn("github-action.html", text)
        self.assertIn("ilion-benchmark.html", text)
        self.assertIn("Please do not send secrets", text)
        self.assertIn("not a contract", text)

    def test_readme_and_changelog_expose_self_service_pilot_layer(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("pilot_package/Self_Service_Pilot_Start_Here.md", readme)
        self.assertIn("docs/Self_Service_Pilot_Hand_Off_Email.md", readme)
        self.assertIn("self-service pilot", changelog.lower())


if __name__ == "__main__":
    unittest.main()

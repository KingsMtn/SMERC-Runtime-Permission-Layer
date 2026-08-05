import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSITIONING = ROOT / "docs" / "Recoverability_Checkpoint_Positioning.md"
PILOT = ROOT / "pilot_package" / "Automated_Response_Shadow_Mode_Pilot.md"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"


class RecoverabilityCheckpointPositioningTests(unittest.TestCase):
    def test_positioning_defines_sharper_product_wedge(self):
        text = POSITIONING.read_text(encoding="utf-8")

        self.assertIn("A recoverability checkpoint before automated actions execute", text)
        self.assertIn("after detection, identity, and policy, but before execution", text)
        self.assertIn("insertable shadow-mode checkpoint", text)
        self.assertIn("design-partner shadow-mode data", text)

    def test_positioning_preserves_non_replacement_boundaries(self):
        text = POSITIONING.read_text(encoding="utf-8")

        for phrase in (
            "does not claim to replace",
            "Microsoft Sentinel",
            "SOAR, SIEM, EDR",
            "MCP, OAuth",
            "human accountability",
        ):
            self.assertIn(phrase, text)

    def test_automated_response_pilot_is_specific_and_measurable(self):
        text = PILOT.read_text(encoding="utf-8")

        for phrase in (
            "metadata only",
            "25 to 100 historical events",
            "reviewer agreement rate",
            "false release rate",
            "false constraint rate",
            "latency impact",
            "Go / No-Go Gate",
        ):
            self.assertIn(phrase, text)

    def test_readme_and_changelog_link_new_wedge(self):
        readme = README.read_text(encoding="utf-8")
        changelog = CHANGELOG.read_text(encoding="utf-8")

        self.assertIn("recoverability checkpoint", readme)
        self.assertIn("docs/Recoverability_Checkpoint_Positioning.md", readme)
        self.assertIn("pilot_package/Automated_Response_Shadow_Mode_Pilot.md", readme)
        self.assertIn("recoverability-checkpoint", changelog)


if __name__ == "__main__":
    unittest.main()

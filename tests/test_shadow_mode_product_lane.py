import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ShadowModeProductLaneTests(unittest.TestCase):
    def test_lane_defines_single_reviewer_flow(self):
        text = (ROOT / "docs" / "Shadow_Mode_Product_Lane.md").read_text(encoding="utf-8")

        for phrase in [
            "one input",
            "one command",
            "one report",
            "one reviewer ask",
            "examples/pilot_intake_template.json",
            "reports/pilot_intake/Pilot_Intake_Report.md",
            "5 to 25 metadata-only actions",
            "where it will execute",
            "execution environment boundary can contain failure",
            "metadata-only and shadow-mode",
            "no live access",
        ]:
            self.assertIn(phrase, text)

    def test_lane_is_linked_from_primary_product_surfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs" / "Product_Readiness_Index.md").read_text(encoding="utf-8")

        for text in [readme, readiness]:
            self.assertIn("docs/Shadow_Mode_Product_Lane.md", text)


if __name__ == "__main__":
    unittest.main()

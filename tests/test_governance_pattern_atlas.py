import tempfile
import unittest
from pathlib import Path

from reference_engine.governance_pattern_atlas import build_atlas, render_markdown, write_outputs


ROOT = Path(__file__).resolve().parents[1]


class GovernancePatternAtlasTests(unittest.TestCase):
    def test_atlas_consolidates_all_operating_models(self):
        atlas = build_atlas()

        self.assertEqual(atlas["version"], "smerc.governance-pattern-atlas.v1")
        self.assertEqual(atlas["pattern_count"], 5)
        self.assertEqual(atlas["total_scenarios"], 40)
        self.assertGreaterEqual(atlas["total_delta_count"], 1)
        self.assertGreater(atlas["weighted_delta_rate"], 0)
        disciplines = [pattern["discipline"] for pattern in atlas["patterns"]]
        self.assertIn("AML-inspired financial governance", disciplines)
        self.assertIn("SRE/incident-management-inspired reliability governance", disciplines)

    def test_patterns_preserve_boundaries_and_strong_examples(self):
        atlas = build_atlas()

        for pattern in atlas["patterns"]:
            self.assertIn("does_not_replace", pattern)
            self.assertIn("evidence_boundary", pattern)
            self.assertIn("strongest_example", pattern)
            self.assertTrue(pattern["strongest_example"]["scenario_id"])
            self.assertIn("not", str(pattern["evidence_boundary"]).lower())

    def test_markdown_explains_one_system_and_partner_readiness(self):
        markdown = render_markdown(build_atlas())

        self.assertIn("# SMERC Governance Pattern Atlas", markdown)
        self.assertIn("Why This Makes SMERC One System", markdown)
        self.assertIn("Credibility Partner Readiness", markdown)
        self.assertIn("customer validation", markdown)

    def test_writes_outputs(self):
        atlas = build_atlas()
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "atlas.json"
            markdown_output = Path(tmp) / "atlas.md"
            write_outputs(atlas, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_readme_links_atlas(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Governance_Pattern_Atlas.md", readme)
        self.assertIn("reports/Governance_Pattern_Atlas.md", readme)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from reference_engine.pilot_in_a_box import (
    PILOT_IN_A_BOX_VERSION,
    build_pilot_in_a_box,
    render_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
TEST_OUTPUTS = ROOT / "test_outputs" / "pilot_in_a_box"
TEST_OUTPUTS.mkdir(parents=True, exist_ok=True)


class PilotInABoxTests(unittest.TestCase):
    def test_builds_multi_pack_reviewer_bundle(self):
        manifest = build_pilot_in_a_box(root=ROOT, output_dir=TEST_OUTPUTS)

        self.assertEqual(manifest["version"], PILOT_IN_A_BOX_VERSION)
        self.assertEqual(manifest["summary"]["evaluation_pack_count"], 3)
        self.assertGreaterEqual(manifest["summary"]["total_actions"], 15)
        self.assertGreaterEqual(manifest["summary"]["non_executable_routes"], 1)
        self.assertEqual(
            manifest["summary"]["valid_ledgers"],
            manifest["summary"]["total_actions"],
        )
        self.assertIn("single_action_proof_loop", manifest)
        self.assertIn("manifest_paths", manifest)
        self.assertTrue((ROOT / manifest["manifest_paths"]["json"]).exists())
        self.assertTrue((ROOT / manifest["manifest_paths"]["markdown"]).exists())

    def test_markdown_explains_work_result_and_impact(self):
        manifest = build_pilot_in_a_box(root=ROOT, output_dir=TEST_OUTPUTS)
        markdown = render_markdown(manifest)

        self.assertIn("Work, Result, Impact", markdown)
        self.assertIn("metadata-only", markdown)
        self.assertIn("shadow-mode pilot", markdown)
        self.assertIn("does not prove production safety", markdown)

    def test_readme_links_pilot_in_a_box(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/Pilot_In_A_Box.md", readme)
        self.assertIn("reference_engine.pilot_in_a_box", readme)


if __name__ == "__main__":
    unittest.main()

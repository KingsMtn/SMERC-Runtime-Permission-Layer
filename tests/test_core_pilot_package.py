import tempfile
import unittest
from pathlib import Path

from reference_engine.core_pilot_package import build_core_pilot_package, render_index, write_outputs


ROOT = Path(__file__).resolve().parents[1]


class CorePilotPackageTests(unittest.TestCase):
    def test_builds_core_package_without_metrics_for_observe_start(self):
        package = build_core_pilot_package()

        self.assertEqual(package["schema"], "smerc.core-pilot-package.v1")
        self.assertEqual(package["route"], "core_github_actions_shadow_mode")
        self.assertEqual(package["pilot_decision"], "start_observe")
        self.assertIn("prospect_route", package["reports"])
        self.assertIn("customer_action_intake", package["reports"])
        self.assertIn("pilot_evidence_summary", package["reports"])
        self.assertIn("not production certification", package["evidence_boundary"])

    def test_builds_core_package_with_metrics_for_recommend_mode(self):
        package = build_core_pilot_package(pilot_metrics=ROOT / "examples" / "pilot_metrics_summary_sample.json")

        self.assertEqual(package["pilot_decision"], "move_to_recommend")
        self.assertEqual(package["reports"]["pilot_evidence_summary"]["pilot_metrics_summary"]["reviewer_agreement_rate"], 0.8333)

    def test_writes_review_folder(self):
        package = build_core_pilot_package()
        with tempfile.TemporaryDirectory() as tmp:
            written = write_outputs(package, tmp)
            for name in (
                "README.md",
                "core-pilot-package.json",
                "prospect-route.md",
                "customer-action-intake.md",
                "pilot-evidence-summary.md",
                "pilot-handoff.json",
            ):
                self.assertIn(name, written)
                self.assertTrue((Path(tmp) / name).exists())

    def test_index_names_review_order_and_boundary(self):
        index = render_index(build_core_pilot_package())

        self.assertIn("Review Order", index)
        self.assertIn("Recommended Next Action", index)
        self.assertIn("Evidence Boundary", index)

    def test_readme_links_core_pilot_package(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Core_Pilot_Package.md", readme)


if __name__ == "__main__":
    unittest.main()

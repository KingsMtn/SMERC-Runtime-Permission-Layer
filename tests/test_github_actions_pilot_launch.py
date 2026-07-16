import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "pilot_package" / "GitHub_Actions_Pilot_Launch_Runbook.md"
MANIFEST = ROOT / "examples" / "github_actions_pilot_manifest.json"


class GitHubActionsPilotLaunchTests(unittest.TestCase):
    def test_runbook_defines_launch_modes_boundary_and_stop_conditions(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("not production certification", lowered)
        self.assertIn("observe", lowered)
        self.assertIn("recommend", lowered)
        self.assertIn("enforce", lowered)
        self.assertIn("do not send production secrets", lowered)
        self.assertIn("stop conditions", lowered)
        self.assertIn("false release", lowered)
        self.assertIn("false constraint", lowered)

    def test_runbook_includes_copyable_local_static_and_oidc_paths(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("source: local", text)
        self.assertIn("SMERC_API_KEY", text)
        self.assertIn("auth-mode: github-oidc", text)
        self.assertIn("id-token: write", text)
        self.assertIn("COMMIT_SHA", text)

    def test_pilot_manifest_is_structured_and_bounded(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], "smerc.github_actions_pilot_manifest.v1")
        self.assertEqual(manifest["pilot_boundary"]["mode"], "observe")
        self.assertTrue(manifest["pilot_boundary"]["not_production_certified"])
        self.assertEqual(manifest["authentication_options"]["preferred"], "github-oidc")
        self.assertIn("metadata boundary violation", manifest["stop_conditions"])
        self.assertIn("move_to_recommend", manifest["go_no_go_options"])

    def test_manifest_references_existing_repository_evidence(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for relative_path in manifest["required_repository_evidence"]:
            self.assertTrue((ROOT / relative_path).exists(), relative_path)


if __name__ == "__main__":
    unittest.main()


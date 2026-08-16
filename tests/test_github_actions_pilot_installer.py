import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from reference_engine.github_actions_pilot_installer import (
    build_pilot_package,
    render_markdown,
    write_pilot_package,
)


ROOT = Path(__file__).resolve().parents[1]
SPARK = ROOT / "examples" / "spark" / "github_actions_spark_evidence.json"
PLAN = ROOT / "examples" / "sparta" / "github_actions_deploy_plan.json"
TIMING = ROOT / "examples" / "timing" / "github_actions_timing_evidence.json"


class GitHubActionsPilotInstallerTests(unittest.TestCase):
    def load_inputs(self):
        return {
            "spark_evidence": json.loads(SPARK.read_text(encoding="utf-8")),
            "sparta_plan": json.loads(PLAN.read_text(encoding="utf-8")),
            "timing_evidence": json.loads(TIMING.read_text(encoding="utf-8")),
        }

    def test_package_connects_runtime_vehicle_layers(self):
        package = build_pilot_package(**self.load_inputs())
        summary = package["package_summary"]
        artifacts = package["artifacts"]

        self.assertEqual(package["version"], "smerc.github-actions-pilot-installer.v1")
        self.assertEqual(package["primary_workflow"], "GitHub Actions")
        self.assertIn(summary["effective_posture"], {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertEqual(artifacts["effective_decision"]["posture"], summary["effective_posture"])
        self.assertEqual(
            artifacts["sparta_route"]["route_report"]["source_posture"],
            summary["effective_posture"],
        )
        self.assertTrue(artifacts["decision_lifecycle_ledger"]["verification"]["valid"])
        self.assertEqual(artifacts["decision_lifecycle_ledger"]["record_count"], 7)
        self.assertEqual(artifacts["dll_intelligence"]["summary"]["ledger_count"], 1)
        self.assertEqual(artifacts["timing_report"]["operational_status"], summary["timing_status"])
        self.assertIn("constraint_eligibility_ms", package["local_generation_latency"])

    def test_constraint_eligibility_can_override_raw_posture(self):
        inputs = self.load_inputs()
        metadata = inputs["spark_evidence"]["action_metadata"]
        metadata["action_id"] = "pilot-delete-logs"
        metadata["description"] = "AI agent proposes deleting production audit logs before deployment"
        metadata["operation"] = "delete_logs"
        metadata["authority_confidence"] = 0.72
        signals = inputs["spark_evidence"]["recoverability_signals"]
        signals["reversibility"] = 0.72
        signals["containment_strength"] = 0.74
        signals["rollback_latency"] = 0.32
        signals["cancel_reliability"] = 0.80

        package = build_pilot_package(**inputs)
        effective = package["artifacts"]["effective_decision"]

        self.assertEqual(package["package_summary"]["effective_posture"], "DENY")
        self.assertFalse(package["package_summary"]["constraint_eligible"])
        self.assertIn("CONSTRAINT_ELIGIBILITY_GATE", effective["reason_codes"])
        self.assertEqual(effective["raw_posture_before_eligibility"], package["package_summary"]["raw_engine_posture"])

    def test_markdown_is_a_guided_pilot_briefing(self):
        markdown = render_markdown(build_pilot_package(**self.load_inputs()))

        self.assertIn("# SMERC GitHub Actions Pilot Package", markdown)
        self.assertIn("SPARK evidence -> Action Language -> Constraint Eligibility", markdown)
        self.assertIn("Metrics To Collect In A Real Pilot", markdown)
        self.assertIn("Evidence Boundary", markdown)

    def test_writes_self_contained_package_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_pilot_package(build_pilot_package(**self.load_inputs()), tmp)
            expected = {
                "pilot_package",
                "spark_intake_report",
                "constraint_eligibility",
                "effective_decision",
                "sparta_route",
                "decision_lifecycle_ledger",
                "dll_intelligence",
                "timing_report",
                "briefing",
            }
            self.assertEqual(set(paths), expected)
            for path in paths.values():
                self.assertTrue(Path(path).exists(), path)
            self.assertIn("GitHub Actions", Path(paths["briefing"]).read_text(encoding="utf-8"))

    def test_cli_generates_package_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reference_engine.github_actions_pilot_installer",
                    "--output-dir",
                    tmp,
                    "--pretty",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=20,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["summary"]["ledger_valid"], True)
            self.assertTrue((Path(tmp) / "pilot_package.json").exists())
            self.assertTrue((Path(tmp) / "README.md").exists())


if __name__ == "__main__":
    unittest.main()

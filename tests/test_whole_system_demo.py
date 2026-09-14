import json
import subprocess
import sys
import unittest
from pathlib import Path

from reference_engine.complete_lifecycle_proof import load_json
from reference_engine.whole_system_demo import VERSION, build_whole_system_demo, render_markdown, write_outputs


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "complete_lifecycle" / "lifecycle_case.json"


class WholeSystemDemoTests(unittest.TestCase):
    def test_builds_whole_system_demo_from_lifecycle_case(self):
        report = build_whole_system_demo(load_json(CASE))

        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["status"], "whole_system_complete")
        self.assertEqual(report["summary"]["initial_posture"], "FREEZE")
        self.assertEqual(report["summary"]["initial_route"], "PAUSE")
        self.assertEqual(report["summary"]["unlock_state"], "UNLOCK")
        self.assertEqual(report["summary"]["continuation_route"], "CONSTRAINED_EXECUTE")
        self.assertTrue(report["summary"]["ledger_valid"])
        self.assertEqual(len(report["stages"]), 9)
        stage_names = [stage["name"] for stage in report["stages"]]
        self.assertIn("Identity / Context", stage_names)
        self.assertIn("Recoverability Engine", stage_names)
        self.assertIn("SPARTa Route Controls", stage_names)
        self.assertIn("Postcondition Evidence", stage_names)
        self.assertIn("Decision Lifecycle Ledger", stage_names)

    def test_markdown_explains_whole_system_roles_and_boundaries(self):
        markdown = render_markdown(build_whole_system_demo(load_json(CASE)))

        self.assertIn("SMERC Whole-System Demo", markdown)
        self.assertIn("System Flow", markdown)
        self.assertIn("Identity / Context", markdown)
        self.assertIn("Recoverability Engine", markdown)
        self.assertIn("Decision Lifecycle Ledger", markdown)
        self.assertIn("Evidence Boundary", markdown)
        self.assertIn("does not execute production commands", markdown)

    def test_writes_outputs_and_cli_runs(self):
        scratch = ROOT / "tests" / "_tmp" / "whole_system_demo"
        report = build_whole_system_demo(load_json(CASE))
        paths = write_outputs(report, scratch)

        self.assertIn("whole-system-demo", (ROOT / paths["json"]).read_text(encoding="utf-8"))
        self.assertIn("SMERC Whole-System Demo", (ROOT / paths["markdown"]).read_text(encoding="utf-8"))

        cli_out = ROOT / "tests" / "_tmp" / "whole_system_demo_cli"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "reference_engine.whole_system_demo",
                "--case",
                str(CASE),
                "--output-dir",
                str(cli_out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        stdout = json.loads(result.stdout)
        self.assertEqual(stdout["summary"]["overall_status"], "COMPLETE")
        self.assertTrue((cli_out / "Whole_System_Demo.md").exists())

    def test_docs_and_readme_reference_whole_system(self):
        docs = (ROOT / "docs" / "SMERC_Whole_System.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ai_doc = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.whole_system_demo", docs)
        self.assertIn("SMERC is the recoverability brain", docs)
        self.assertIn("docs/SMERC_Whole_System.md", readme)
        self.assertIn("SMERC Whole System", ai_doc)


if __name__ == "__main__":
    unittest.main()

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from reference_engine.end_to_end_pr_guardian_demo import build_end_to_end_demo, render_markdown


ROOT = Path(__file__).resolve().parents[1]


class EndToEndPRGuardianDemoTests(unittest.TestCase):
    def test_demo_builds_connected_flow(self):
        bundle = build_end_to_end_demo()
        decision = bundle["decision_report"]["decision"]
        certificate = bundle["pr_guardian"]["certificate"]
        route = bundle["sparta_route"]["route_report"]
        ledger = bundle["decision_lifecycle_ledger"]
        intelligence = bundle["dll_intelligence"]
        latency = bundle["performance_latency"]

        self.assertEqual(bundle["version"], "smerc.end-to-end-pr-guardian-demo.v1")
        self.assertIn(decision["posture"], {"ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"})
        self.assertEqual(certificate["posture"], decision["posture"])
        self.assertEqual(certificate["replay_id"], decision["replay_id"])
        self.assertIn("SMERC PR Guardian", bundle["pr_guardian"]["comment_markdown"])
        self.assertEqual(route["decision_replay_id"], decision["replay_id"])
        self.assertEqual(route["source_posture"], decision["posture"])
        self.assertEqual(len(bundle["sparta_route"]["route_report_digest"]), 64)
        self.assertTrue(ledger["verification"]["valid"])
        self.assertEqual(ledger["record_count"], 7)
        self.assertEqual(intelligence["summary"]["ledger_count"], 1)
        self.assertIn("AI-assisted PR request", "\n".join(bundle["integrated_flow"]))
        self.assertEqual(latency["version"], "smerc.demo-latency.v1")
        self.assertGreaterEqual(latency["decision_evaluation_ms"], 0)
        self.assertGreaterEqual(latency["total_generation_ms"], latency["decision_evaluation_ms"])
        self.assertIn("operational overhead", latency["ciso_interpretation"])
        self.assertIn("not production performance evidence", " ".join(latency["boundary"]))

    def test_markdown_names_all_runtime_layers(self):
        markdown = render_markdown(build_end_to_end_demo())
        self.assertIn("# SMERC End-To-End PR Guardian Demo", markdown)
        self.assertIn("SMERC Runtime Decision", markdown)
        self.assertIn("PR Guardian Visible Review Artifact", markdown)
        self.assertIn("SPARTa Route", markdown)
        self.assertIn("Decision Lifecycle Ledger", markdown)
        self.assertIn("DLL Intelligence", markdown)
        self.assertIn("Performance And Latency", markdown)
        self.assertIn("operational overhead", markdown)
        self.assertIn("Synthetic end-to-end demo", markdown)

    def test_cli_writes_all_demo_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reference_engine.end_to_end_pr_guardian_demo",
                    "--json-output",
                    str(out / "bundle.json"),
                    "--markdown-output",
                    str(out / "report.md"),
                    "--pr-comment-output",
                    str(out / "comment.md"),
                    "--certificate-output",
                    str(out / "certificate.json"),
                    "--route-output",
                    str(out / "route.json"),
                    "--ledger-output",
                    str(out / "ledger.json"),
                    "--intelligence-output",
                    str(out / "intelligence.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in [
                "bundle.json",
                "report.md",
                "comment.md",
                "certificate.json",
                "route.json",
                "ledger.json",
                "intelligence.json",
            ]:
                self.assertTrue((out / name).exists(), name)

            bundle = json.loads((out / "bundle.json").read_text(encoding="utf-8"))
            self.assertEqual(bundle["pr_guardian"]["certificate"]["version"], "smerc.github-pr-guardian-certificate.v1")
            self.assertIn("SMERC PR Guardian", (out / "comment.md").read_text(encoding="utf-8"))

    def test_checked_in_report_is_demo_ready(self):
        report = (ROOT / "reports" / "End_To_End_PR_Guardian_Demo.md").read_text(encoding="utf-8")
        self.assertIn("AI-assisted PR request -> SMERC decision", report)
        self.assertIn("## 4. SPARTa Route", report)
        self.assertIn("## Boundary", report)


if __name__ == "__main__":
    unittest.main()

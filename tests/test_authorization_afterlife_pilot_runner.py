import json
import unittest
from pathlib import Path

from reference_engine.authorization_afterlife_pilot_runner import render_markdown, run_manifest


ROOT = Path(__file__).resolve().parents[1]


class AuthorizationAfterlifePilotRunnerTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(
            (ROOT / "examples" / "authorization_afterlife_evidence_manifest.json").read_text(encoding="utf-8")
        )

    def test_manifest_runs_through_three_consequence_time_outcomes(self):
        report = run_manifest(self.payload)
        self.assertEqual(report["record_count"], 3)
        self.assertEqual(
            report["decision_counts"],
            {"SETTLE": 1, "QUARANTINE": 1, "COMPENSATE": 1, "DENY": 0},
        )
        self.assertEqual(
            [item["decision"] for item in report["decisions"]],
            ["SETTLE", "QUARANTINE", "COMPENSATE"],
        )

    def test_decisions_preserve_provenance_and_claim_boundary(self):
        report = run_manifest(self.payload)
        for item in report["decisions"]:
            self.assertEqual(len(item["source_sha256"]), 64)
            self.assertIn(item["evidence_class"], {"CONTROLLED_AWS_PROOF", "SYNTHETIC"})
        self.assertIn("does not verify upstream truth", report["evidence_boundary"])
        markdown = render_markdown(report)
        self.assertIn("`SETTLE`", markdown)
        self.assertIn("`QUARANTINE`", markdown)
        self.assertIn("`COMPENSATE`", markdown)


if __name__ == "__main__":
    unittest.main()

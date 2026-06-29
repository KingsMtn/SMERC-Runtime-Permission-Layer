import tempfile
import unittest
from pathlib import Path

from reference_engine.audit_store import AuditStore
from reference_engine.pilot_metrics_report import build_report, to_markdown, write_bundle


class PilotMetricsReportTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.database = Path(self.temp_dir.name) / "audit.sqlite3"
        store = AuditStore(self.database)
        store.record(
            "alpha",
            {
                "action_id": "deploy-1",
                "posture": "THROTTLE",
                "replay_id": "replay-1",
                "scores": {"irreversible_exposure_score": 0.6},
                "replay": {"evaluated_at": "2026-06-28T12:00:00+00:00"},
            },
            "decision-hash",
        )
        store.record_review(
            "alpha",
            "replay-1",
            {
                "review_id": "review-1",
                "tenant_id": "alpha",
                "replay_id": "replay-1",
                "reviewer_id": "security-1",
                "verdict": "agree",
                "decision_posture": "THROTTLE",
                "recommended_posture": None,
                "false_release": False,
                "false_constraint": False,
                "useful_constraint": True,
                "review_latency_ms": 2500,
                "comment": None,
            },
            "review-hash",
        )
        store.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_report_marks_pilot_evidence_and_discloses_denominators(self):
        report = build_report(self.database, "alpha")
        self.assertEqual(report["evidence_status"], "pilot_observation")
        self.assertEqual(report["metrics"]["reviewer_agreement_rate"], 1.0)
        self.assertEqual(report["denominators"]["determinate_reviews"], 1)
        markdown = to_markdown(report)
        self.assertIn("Interpretation Boundary", markdown)
        self.assertIn("1 determinate reviews", markdown)

    def test_write_bundle_creates_json_and_markdown(self):
        report = build_report(self.database, "alpha")
        json_path, markdown_path = write_bundle(report, Path(self.temp_dir.name) / "output")
        self.assertTrue(json_path.exists())
        self.assertTrue(markdown_path.exists())

    def test_missing_database_is_not_silently_created(self):
        missing = Path(self.temp_dir.name) / "missing.sqlite3"
        with self.assertRaises(FileNotFoundError):
            build_report(missing, "alpha")
        self.assertFalse(missing.exists())

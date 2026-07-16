import json
import unittest
from pathlib import Path

from reference_engine.github_actions_pilot_summary import (
    load_reports,
    markdown_report,
    summarize,
    write_json,
    write_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "test_outputs" / "github_actions_pilot_summary"


def evaluated_report(posture="THROTTLE"):
    return {
        "mode": "observe",
        "source": "remote",
        "integration_status": "evaluated",
        "enforcement": {"fail_on": ["DENY", "FREEZE"], "would_fail": posture in {"DENY", "FREEZE"}, "active": False},
        "decision": {
            "posture": posture,
            "scores": {
                "irreversible_exposure_score": 0.62,
                "confidence_score": 0.71,
            },
            "reason_codes": ["IRREVERSIBLE_EXPOSURE_ELEVATED", "ROLLBACK_LATENCY_HIGH"],
            "controls": ["require_rollback_plan", "limit_scope"],
            "plain_english_summary": "Action should be constrained before execution.",
            "replay_id": f"replay-{posture.lower()}",
        },
    }


class GitHubActionsPilotSummaryTests(unittest.TestCase):
    def setUp(self):
        TEST_DIR.mkdir(parents=True, exist_ok=True)
        for path in TEST_DIR.glob("*.json"):
            path.unlink()

    def write_report(self, name, payload):
        path = TEST_DIR / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_loads_directory_and_summarizes_decision_artifacts(self):
        self.write_report("allow.json", evaluated_report("ALLOW"))
        self.write_report(
            "unavailable.json",
            {
                "mode": "observe",
                "source": "remote",
                "integration_status": "unavailable",
                "enforcement": {"would_fail": True},
                "decision": None,
                "error": {"code": "api_unavailable", "message": "SMERC API unavailable."},
            },
        )
        reports = load_reports([TEST_DIR])
        summary = summarize(reports)

        self.assertEqual(summary["total_reports"], 2)
        self.assertEqual(summary["evaluated_reports"], 1)
        self.assertEqual(summary["unavailable_reports"], 1)
        self.assertEqual(summary["posture_counts"]["ALLOW"], 1)
        self.assertEqual(summary["posture_counts"]["UNAVAILABLE"], 1)
        self.assertEqual(summary["top_controls"][0][0], "require_rollback_plan")

    def test_markdown_discloses_missing_customer_outcome_evidence(self):
        path = self.write_report("throttle.json", evaluated_report("THROTTLE"))
        reports = load_reports([path])
        report = markdown_report(reports, summarize(reports))

        self.assertIn("pilot artifact evidence, not production validation", report)
        self.assertIn("false release", report)
        self.assertIn("Required Human Review", report)
        self.assertIn("GitHub Actions decision artifacts", report)

    def test_writers_create_json_and_markdown(self):
        path = self.write_report("freeze.json", evaluated_report("FREEZE"))
        reports = load_reports([path])
        summary = summarize(reports)
        json_output = TEST_DIR / "summary.json"
        markdown_output = TEST_DIR / "summary.md"

        write_json(json_output, reports, summary)
        write_markdown(markdown_output, reports, summary)

        payload = json.loads(json_output.read_text(encoding="utf-8"))
        self.assertEqual(payload["summary"]["would_fail_count"], 1)
        self.assertIn("# SMERC GitHub Actions Pilot Artifact Summary", markdown_output.read_text(encoding="utf-8"))

    def test_rejects_invalid_report_shape(self):
        path = self.write_report("bad.json", {"integration_status": "evaluated", "decision": None})
        with self.assertRaisesRegex(ValueError, "missing a decision"):
            load_reports([path])


if __name__ == "__main__":
    unittest.main()


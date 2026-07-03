import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.evidence_program import (
    _deployment_ceiling,
    evaluate_evidence,
    markdown_report,
    validate_program,
    write_report,
)


ROOT = Path(__file__).resolve().parents[1]
PROGRAM = json.loads((ROOT / "examples" / "evidence_program" / "core_assumptions.json").read_text(encoding="utf-8"))
SYNTHETIC = json.loads((ROOT / "examples" / "evidence_program" / "synthetic_observations.json").read_text(encoding="utf-8"))


class EvidenceProgramTests(unittest.TestCase):
    def test_core_program_is_strict_and_unique(self):
        validated = validate_program(PROGRAM)
        self.assertEqual(len(validated["claims"]), 8)
        invalid = json.loads(json.dumps(PROGRAM))
        invalid["claims"][0]["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "unknown field"):
            validate_program(invalid)

    def test_no_evidence_limits_deployment_to_observe(self):
        report = evaluate_evidence(PROGRAM, [])
        self.assertEqual(report["deployment_ceiling"], "OBSERVE")
        self.assertEqual(report["claim_counts"]["UNTESTED"], 8)
        self.assertIn("TECH-001", report["blocking_claim_ids"])

    def test_challenged_critical_claim_stops_progression(self):
        report = evaluate_evidence(PROGRAM, SYNTHETIC)
        self.assertEqual(report["deployment_ceiling"], "STOP")
        self.assertEqual(report["blocking_claim_ids"], ["ADVR-001"])
        statuses = {item["claim_id"]: item["status"] for item in report["claims"]}
        self.assertEqual(statuses["TECH-001"], "SUPPORTED")
        self.assertEqual(statuses["ADVR-001"], "CHALLENGED")

    def test_underpowered_or_low_quality_evidence_is_insufficient(self):
        observation = dict(SYNTHETIC[0], sample_size=99, source_quality=0.69)
        report = evaluate_evidence(PROGRAM, [observation])
        result = report["claims"][0]["criteria"][0]
        self.assertEqual(result["status"], "INSUFFICIENT")
        self.assertIsNone(result["latest_value"])

    def test_unknown_claim_observation_is_rejected(self):
        observation = dict(SYNTHETIC[0], claim_id="MISSING")
        with self.assertRaisesRegex(ValueError, "does not exist"):
            evaluate_evidence(PROGRAM, [observation])

    def test_conflicting_qualified_evidence_cannot_be_overwritten(self):
        supporting = SYNTHETIC[0]
        challenging = dict(
            supporting,
            observation_id="synthetic-tech-conflict",
            value=0.1,
            dataset_id="synthetic-conflicting-dataset",
            collected_at="2026-06-03T00:00:00Z",
        )
        report = evaluate_evidence(PROGRAM, [supporting, challenging])
        self.assertEqual(report["deployment_ceiling"], "STOP")
        self.assertEqual(report["claims"][0]["status"], "CONFLICTED")

    def test_duplicate_observation_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate observation_id"):
            evaluate_evidence(PROGRAM, [SYNTHETIC[0], SYNTHETIC[0]])

    def test_observation_must_match_the_registered_metric(self):
        observation = dict(SYNTHETIC[0], metric="unregistered_metric")
        with self.assertRaisesRegex(ValueError, "does not match"):
            evaluate_evidence(PROGRAM, [observation])

    def test_observation_timestamp_requires_a_timezone(self):
        observation = dict(SYNTHETIC[0], collected_at="2026-06-01T00:00:00")
        with self.assertRaisesRegex(ValueError, "timezone"):
            evaluate_evidence(PROGRAM, [observation])

    def test_all_deployment_ceiling_tiers_are_ordered_by_unresolved_risk(self):
        supported = {"claim_id": "C", "risk_level": "critical", "status": "SUPPORTED"}
        self.assertEqual(_deployment_ceiling([dict(supported, status="CHALLENGED")])[0], "STOP")
        self.assertEqual(_deployment_ceiling([dict(supported, status="UNTESTED")])[0], "OBSERVE")
        self.assertEqual(
            _deployment_ceiling([supported, {"claim_id": "H", "risk_level": "high", "status": "UNTESTED"}])[0],
            "RECOMMEND",
        )
        self.assertEqual(
            _deployment_ceiling([supported, {"claim_id": "M", "risk_level": "moderate", "status": "UNTESTED"}])[0],
            "LIMITED_ENFORCE",
        )
        self.assertEqual(_deployment_ceiling([supported])[0], "CALIBRATED_ENFORCE")

    def test_reports_disclose_the_non_certification_limit(self):
        report = evaluate_evidence(PROGRAM, [])
        rendered = markdown_report(report)
        self.assertIn("not a production certification", rendered)
        temporary_root = ROOT / ".tmp_tests"
        temporary_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            json_path = Path(directory) / "report.json"
            markdown_path = Path(directory) / "report.md"
            write_report(report, json_path, markdown_path)
            self.assertTrue(json_path.exists())
            self.assertIn("OBSERVE", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

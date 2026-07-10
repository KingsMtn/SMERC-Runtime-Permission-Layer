import copy
import json
import unittest
from pathlib import Path

from reference_engine.pilot_readiness_assessment import assess, validate_payload, write_markdown


ROOT = Path(__file__).resolve().parents[1]
READINESS = json.loads((ROOT / "examples" / "pilot_level5_readiness.json").read_text(encoding="utf-8"))


class PilotReadinessAssessmentTests(unittest.TestCase):
    def test_level5_readiness_example_links_to_existing_required_evidence(self):
        report = assess(READINESS, repo_root=ROOT)

        self.assertTrue(report["level5_shadow_mode_ready"])
        self.assertEqual(report["required_failures"], [])
        self.assertEqual(report["required_met_count"], report["required_gate_count"])
        required_gates = [gate for gate in report["gates"] if gate["required"]]
        self.assertTrue(required_gates)
        self.assertTrue(all(gate["evidence_present"] for gate in required_gates))

    def test_optional_unmet_gates_keep_production_claims_out_of_level5(self):
        report = assess(READINESS, repo_root=ROOT)
        optional = {gate["id"]: gate for gate in report["gates"] if not gate["required"]}

        self.assertEqual(optional["external_pilot_data"]["status"], "not_met")
        self.assertEqual(optional["production_security_review"]["status"], "not_met")
        self.assertEqual(optional["signed_sparta_routes"]["status"], "partial")
        self.assertLess(report["optional_met_count"], report["optional_gate_count"])

    def test_missing_required_evidence_or_unmet_required_gate_blocks_readiness(self):
        payload = copy.deepcopy(READINESS)
        payload["gates"][0]["evidence_paths"].append("missing/file.md")
        report = assess(payload, repo_root=ROOT)
        self.assertFalse(report["level5_shadow_mode_ready"])
        self.assertIn("working_engine:missing_evidence", report["required_failures"])

        payload = copy.deepcopy(READINESS)
        payload["gates"][0]["status"] = "partial"
        report = assess(payload, repo_root=ROOT)
        self.assertFalse(report["level5_shadow_mode_ready"])
        self.assertIn("working_engine", report["required_failures"])

    def test_validation_is_strict(self):
        payload = copy.deepcopy(READINESS)
        payload["extra"] = True
        with self.assertRaisesRegex(ValueError, "unknown field"):
            validate_payload(payload)

        payload = copy.deepcopy(READINESS)
        payload["gates"][0]["status"] = "done"
        with self.assertRaisesRegex(ValueError, "status"):
            validate_payload(payload)

        payload = copy.deepcopy(READINESS)
        payload["gates"][0]["evidence_paths"] = ["C:\\secret\\file.txt"]
        with self.assertRaisesRegex(ValueError, "repository-relative"):
            validate_payload(payload)

    def test_markdown_report_disclaims_production_readiness(self):
        markdown = write_markdown(assess(READINESS, repo_root=ROOT))

        self.assertIn("Level 5 shadow-mode ready: yes", markdown)
        self.assertIn("does not assert production readiness", markdown)
        self.assertIn("customer validation", markdown)


if __name__ == "__main__":
    unittest.main()

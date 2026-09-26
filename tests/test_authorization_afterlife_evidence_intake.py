import json
import unittest
from copy import deepcopy
from pathlib import Path

from reference_engine.authorization_afterlife_evidence_intake import build_intake_report, validate_manifest


ROOT = Path(__file__).resolve().parents[1]


class AuthorizationAfterlifeEvidenceIntakeTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(
            (ROOT / "examples" / "authorization_afterlife_evidence_manifest.json").read_text(encoding="utf-8")
        )

    def test_valid_manifest_produces_reconciliation_readiness(self):
        report = build_intake_report(self.payload)
        self.assertEqual(report["record_count"], 3)
        self.assertEqual(report["records_requiring_reconciliation"], 2)
        self.assertEqual(report["readiness"], "ready_for_scenario_reconciliation")
        self.assertEqual(report["evidence_class_counts"]["SYNTHETIC"], 2)

    def test_rejects_secret_shaped_fields_recursively(self):
        payload = deepcopy(self.payload)
        payload["records"][0]["observations"]["session_token"] = "not-a-real-token"
        with self.assertRaisesRegex(ValueError, "prohibited"):
            validate_manifest(payload)

    def test_rejects_unknown_fields_and_bad_digests(self):
        payload = deepcopy(self.payload)
        payload["records"][0]["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "unknown field"):
            validate_manifest(payload)
        payload = deepcopy(self.payload)
        payload["records"][0]["source_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            validate_manifest(payload)

    def test_rejects_duplicate_evidence_ids(self):
        payload = deepcopy(self.payload)
        payload["records"][1]["evidence_id"] = payload["records"][0]["evidence_id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_manifest(payload)


if __name__ == "__main__":
    unittest.main()

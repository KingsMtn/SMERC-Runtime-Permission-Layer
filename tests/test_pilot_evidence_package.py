import copy
import unittest

from reference_engine.decision_certificate import build_decision_certificate
from reference_engine.decision_lifecycle_ledger import build_example_ledger
from reference_engine.pilot_evidence_package import (
    PILOT_EVIDENCE_PACKAGE_VERSION,
    build_pilot_evidence_package,
)


class PilotEvidencePackageTests(unittest.TestCase):
    def test_builds_ciso_readable_package_from_verified_ledger(self):
        ledger = build_example_ledger()
        certificate = build_decision_certificate(ledger, issuer="package-test")
        package = build_pilot_evidence_package(
            ledger,
            certificate=certificate,
            security_events=[
                {
                    "event_version": "smerc.security-event.v1",
                    "event_id": "event_1",
                    "tenant_id": "design-partner",
                    "principal_id": "auditor",
                    "event_type": "pilot.dll_ledger.stored",
                    "resource_id": ledger.decision_id,
                    "metadata": {"decision_id": ledger.decision_id},
                    "created_at": "2026-07-14T12:00:00+00:00",
                },
                {
                    "event_version": "smerc.security-event.v1",
                    "event_id": "event_unrelated",
                    "tenant_id": "design-partner",
                    "principal_id": "auditor",
                    "event_type": "unrelated",
                    "resource_id": "other-decision",
                    "metadata": {},
                    "created_at": "2026-07-14T12:01:00+00:00",
                },
            ],
            generated_by="package-test",
            generated_at="2026-07-14T12:02:00+00:00",
        )

        self.assertEqual(package["version"], PILOT_EVIDENCE_PACKAGE_VERSION)
        self.assertEqual(package["decision_id"], ledger.decision_id)
        self.assertTrue(package["certificate_verification"]["valid"])
        self.assertEqual(package["audit_event_summary"]["included_event_count"], 1)
        self.assertIn("pilot.dll_ledger.stored", package["audit_event_summary"]["event_types"])
        self.assertIn("SMERC Pilot Evidence Package", package["markdown_report"])
        self.assertIn("pilot evidence package, not production certification", package["markdown_report"])

    def test_rejects_certificate_that_no_longer_matches_source_ledger(self):
        ledger = build_example_ledger()
        certificate = build_decision_certificate(ledger)
        tampered = copy.deepcopy(certificate)
        tampered["decision_id"] = "different-decision"

        with self.assertRaises(ValueError):
            build_pilot_evidence_package(ledger, certificate=tampered)


if __name__ == "__main__":
    unittest.main()

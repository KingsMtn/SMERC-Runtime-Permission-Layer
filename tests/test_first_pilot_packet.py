import copy
import json
import unittest
from pathlib import Path

from reference_engine.first_pilot_packet import build_packet, markdown, validate_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "examples" / "github_actions_pilot_manifest.json").read_text(encoding="utf-8"))
FIT = json.loads((ROOT / "examples" / "design_partner_fit_example.json").read_text(encoding="utf-8"))


class FirstPilotPacketTests(unittest.TestCase):
    def test_builds_ready_to_start_packet_from_manifest_and_fit_screen(self):
        packet = build_packet(MANIFEST, FIT)

        self.assertEqual(packet["schema"], "smerc.first-pilot-packet.v1")
        self.assertTrue(packet["ready_to_start"])
        self.assertEqual(packet["fit"]["fit_band"], "moderate")
        self.assertIn("30-Day Shadow-Mode Pilot", packet["recommended_offer"])
        self.assertEqual(packet["pilot_boundary"]["mode"], "observe")
        self.assertIn("Week one", " ".join(packet["first_30_days"]))
        self.assertIn("metadata boundary violation", packet["stop_conditions"])
        self.assertIn("not prove production readiness", packet["evidence_boundary"])

    def test_blocked_fit_is_not_ready_to_start(self):
        fit = copy.deepcopy(FIT)
        fit["scores"]["reviewer_capacity"] = 0
        packet = build_packet(MANIFEST, fit)

        self.assertFalse(packet["ready_to_start"])
        self.assertIn("No reviewer capacity", " ".join(packet["fit"]["blockers"]))

    def test_manifest_validation_is_strict_and_observe_only(self):
        manifest = copy.deepcopy(MANIFEST)
        manifest["extra"] = True
        with self.assertRaisesRegex(ValueError, "unknown field"):
            validate_manifest(manifest)

        manifest = copy.deepcopy(MANIFEST)
        manifest["pilot_boundary"]["mode"] = "enforce"
        with self.assertRaisesRegex(ValueError, "observe mode"):
            validate_manifest(manifest)

        manifest = copy.deepcopy(MANIFEST)
        manifest["pilot_boundary"]["not_production_certified"] = False
        with self.assertRaisesRegex(ValueError, "not_production_certified"):
            validate_manifest(manifest)

    def test_markdown_contains_customer_review_sections(self):
        report = markdown(build_packet(MANIFEST, FIT))

        self.assertIn("## Start Decision", report)
        self.assertIn("Ready to start: `true`", report)
        self.assertIn("## Pilot Boundary", report)
        self.assertIn("## Stop Conditions", report)
        self.assertIn("Pilot packet only", report)


if __name__ == "__main__":
    unittest.main()

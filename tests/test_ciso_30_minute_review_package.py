import json
import unittest
from pathlib import Path


DOC = Path("docs/CISO_30_Minute_Review_Package.md")
CHECKLIST = Path("examples/ciso_30_minute_review_checklist.json")


class CISO30MinuteReviewPackageTests(unittest.TestCase):
    def test_package_uses_bounded_language(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("bounded shadow-mode pilot", text)
        self.assertIn("not production certification", text)
        self.assertIn("not yet ready to be described as production-certified", text)
        self.assertNotIn("guaranteed", text.lower())

    def test_package_links_to_existing_evidence(self):
        text = DOC.read_text(encoding="utf-8")
        required = [
            "docs/Plain_English_Product_Overview.md",
            "docs/Maturity_Model.md",
            "reference_engine/action_language.py",
            "reference_engine/recoverability_engine.py",
            "docs/SPARTa_Router_Operations.md",
            "docs/Control_Mapping_Library.md",
            "docs/Governance_Report_Generator.md",
            "reports/Governance_Report_Example.md",
            "pilot_package/Level_5_Shadow_Mode_Pilot_Packet.md",
        ]
        for path in required:
            self.assertIn(path, text)
            self.assertTrue(Path(path).exists(), path)

    def test_checklist_is_structured_and_references_existing_files(self):
        data = json.loads(CHECKLIST.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], "smerc.ciso-30-minute-review-checklist.v1")
        self.assertEqual(sum(section["timebox_minutes"] for section in data["sections"]), 30)
        self.assertGreaterEqual(len(data["sections"]), 6)
        for section in data["sections"]:
            self.assertIn("question", section)
            self.assertIn("pass_signal", section)
            for evidence in section["evidence"]:
                self.assertTrue(Path(evidence).exists(), evidence)

    def test_checklist_blocks_overclaims(self):
        data = json.loads(CHECKLIST.read_text(encoding="utf-8"))
        blocked = " ".join(data["do_not_claim"]).lower()
        self.assertIn("production-certified", blocked)
        self.assertIn("proven incident reduction", blocked)
        self.assertIn("replacement for iam", blocked)


if __name__ == "__main__":
    unittest.main()

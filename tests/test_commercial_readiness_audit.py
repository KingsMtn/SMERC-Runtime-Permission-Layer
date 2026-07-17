import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.commercial_readiness_audit import audit_repository, markdown


ROOT = Path(__file__).resolve().parents[1]


class CommercialReadinessAuditTests(unittest.TestCase):
    def test_valid_public_materials_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._write_public_materials(repo)

            report = audit_repository(repo, public_files=["README.md", "docs/Plain_English_Product_Overview.md"])

            self.assertTrue(report["passed"])
            self.assertEqual(report["blocking_count"], 0)
            self.assertEqual(report["warning_count"], 0)

    def test_missing_evidence_boundary_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._write_public_materials(repo)
            (repo / "README.md").write_text(
                "SMERC is runtime permission infrastructure with recoverability scoring.",
                encoding="utf-8",
            )

            report = audit_repository(repo, public_files=["README.md", "docs/Plain_English_Product_Overview.md"])

            self.assertFalse(report["passed"])
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("readme_missing_evidence_boundary", codes)

    def test_risky_claims_are_warnings_not_blockers(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._write_public_materials(repo)
            readme = (repo / "README.md").read_text(encoding="utf-8")
            (repo / "README.md").write_text(readme + "\nSMERC is the world's first guaranteed AI safety layer.\n", encoding="utf-8")

            report = audit_repository(repo, public_files=["README.md", "docs/Plain_English_Product_Overview.md"])

            self.assertTrue(report["passed"])
            self.assertGreaterEqual(report["warning_count"], 2)
            messages = " ".join(item["message"] for item in report["findings"])
            self.assertIn("novelty", messages)
            self.assertIn("guaranteed", messages)

    def test_markdown_explains_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._write_public_materials(repo)

            text = markdown(audit_repository(repo, public_files=["README.md", "docs/Plain_English_Product_Overview.md"]))

            self.assertIn("SMERC Commercial Readiness Language Audit", text)
            self.assertIn("Passed: `true`", text)
            self.assertIn("does not prove legal clearance", text)

    def test_checked_in_report_records_current_audit(self):
        payload = json.loads((ROOT / "reports" / "commercial_readiness_audit.json").read_text(encoding="utf-8"))
        report = (ROOT / "reports" / "Commercial_Readiness_Language_Audit.md").read_text(encoding="utf-8")

        self.assertEqual(payload["schema"], "smerc.commercial-readiness-audit.v1")
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["blocking_count"], 0)
        self.assertIn("runtime permission", payload["required_positioning_terms"])
        self.assertIn("recoverability", payload["required_positioning_terms"])
        self.assertIn("Passed: `true`", report)
        self.assertIn("does not prove legal clearance", report)

    def _write_public_materials(self, repo: Path) -> None:
        (repo / "docs").mkdir()
        readme = (
            "# SMERC\n\n"
            "SMERC is runtime permission infrastructure for AI-agent actions. "
            "It uses recoverability scoring before automated actions execute.\n\n"
            "The current project is ready for shadow-mode pilot discussion, "
            "not production-certified, and not proven to reduce incidents in live environments.\n"
        )
        overview = (
            "SMERC supports runtime permission decisions, recoverability review, "
            "shadow-mode evaluation, and not production-certified pilot boundaries."
        )
        (repo / "README.md").write_text(readme, encoding="utf-8")
        (repo / "docs" / "Plain_English_Product_Overview.md").write_text(overview, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

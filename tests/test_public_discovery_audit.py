import json
import tempfile
import unittest
from pathlib import Path

from reference_engine.public_discovery_audit import audit_site, markdown


ROOT = Path(__file__).resolve().parents[1]


class PublicDiscoveryAuditTests(unittest.TestCase):
    def test_valid_site_export_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            self._write_valid_site(site)

            report = audit_site(site)

            self.assertTrue(report["passed"])
            self.assertEqual(report["blocking_count"], 0)
            self.assertIn("Search appearance", report["evidence_boundary"] + " Search appearance")

    def test_missing_required_file_and_term_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            self._write_valid_site(site)
            (site / "llms.txt").unlink()
            (site / "project.json").write_text(json.dumps({"full_name": "Wrong"}), encoding="utf-8")

            report = audit_site(site)

            self.assertFalse(report["passed"])
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("missing_file", codes)
            self.assertIn("project_acronym", codes)
            self.assertIn("project_tagline", codes)

    def test_markdown_reports_findings_and_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            self._write_valid_site(site)
            report = markdown(audit_site(site))

            self.assertIn("SMERC Public Discovery Audit", report)
            self.assertIn("Passed: `true`", report)
            self.assertIn("Local site-export audit only", report)

    def test_checked_in_report_records_current_public_discovery_audit(self):
        payload = json.loads((ROOT / "reports" / "public_discovery_audit.json").read_text(encoding="utf-8"))
        report = (ROOT / "reports" / "Public_Discovery_Audit.md").read_text(encoding="utf-8")

        self.assertEqual(payload["schema"], "smerc.public-discovery-audit.v1")
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["blocking_count"], 0)
        self.assertEqual(payload["warning_count"], 0)
        self.assertIn("Structural Momentum Entropy Range Confidence", payload["required_terms"])
        self.assertIn("AI agent governance", payload["required_terms"])
        self.assertIn("Passed: `true`", report)
        self.assertIn("does not prove search indexing", report)

    def _write_valid_site(self, site: Path) -> None:
        (site / ".well-known").mkdir()
        title = "SMERC | Runtime Permission Infrastructure for AI Agents"
        home = (
            f"<html><head><title>{title}</title>"
            '<meta property="og:title" content="SMERC | Runtime Permission Infrastructure for AI Agents" />'
            "</head><body>Structural Momentum Entropy Range Confidence. "
            "AI agent governance. recoverability scoring. runtime permission layer.</body></html>"
        )
        (site / "index.html").write_text(home, encoding="utf-8")
        (site / "ai-agent-governance.html").write_text(
            "<html><body>SMERC AI agent governance recoverability scoring runtime permission.</body></html>",
            encoding="utf-8",
        )
        (site / "llms.txt").write_text(
            "SMERC Structural Momentum Entropy Range Confidence AI agent governance runtime permission layer recoverability scoring",
            encoding="utf-8",
        )
        (site / "sitemap.xml").write_text(
            "<urlset><loc>/</loc><loc>/ai-agent-governance.html</loc><loc>/llms.txt</loc><loc>/project.json</loc><loc>/smerc-beacon.json</loc></urlset>",
            encoding="utf-8",
        )
        profile = {
            "full_name": title,
            "acronym_expansion": "Structural Momentum Entropy Range Confidence",
            "standard_tagline": "Recoverability scoring before automated actions execute.",
            "one_line_summary": "SMERC is runtime permission infrastructure for AI agents.",
        }
        beacon = {
            "name": title,
            "acronym_expansion": "Structural Momentum Entropy Range Confidence",
            "standard_tagline": "Recoverability scoring before automated actions execute.",
            "search_categories": ["AI agent governance", "runtime permission layer"],
        }
        (site / "project.json").write_text(json.dumps(profile), encoding="utf-8")
        (site / "smerc-beacon.json").write_text(json.dumps(beacon), encoding="utf-8")
        (site / ".well-known" / "smerc.json").write_text(json.dumps(beacon), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

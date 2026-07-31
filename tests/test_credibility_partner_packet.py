import tempfile
import unittest
from pathlib import Path

from reference_engine.credibility_partner_packet import build_packet, load_atlas, render_markdown, write_outputs


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "reports" / "governance_pattern_atlas.json"


class CredibilityPartnerPacketTests(unittest.TestCase):
    def test_packet_builds_from_atlas(self):
        packet = build_packet(load_atlas(ATLAS))

        self.assertEqual(packet["version"], "smerc.credibility-partner-review-packet.v1")
        self.assertEqual(packet["atlas_summary"]["total_scenarios"], 40)
        self.assertIn("github_repository", packet["public_links"])
        self.assertIn("GitHub Actions", packet["positioning"]["primary_wedge"])
        self.assertGreaterEqual(len(packet["review_questions"]), 5)
        self.assertGreaterEqual(len(packet["pilot_fit_questions"]), 5)

    def test_packet_keeps_boundary_language(self):
        packet = build_packet(load_atlas(ATLAS))
        not_claiming = " ".join(packet["not_claiming"])

        self.assertIn("not production-certified", not_claiming)
        self.assertIn("not customer-validated", not_claiming)
        self.assertIn("shadow mode", not_claiming)

    def test_markdown_contains_review_path_and_outreach(self):
        markdown = render_markdown(build_packet(load_atlas(ATLAS)))

        self.assertIn("# SMERC Credibility Partner Review Packet", markdown)
        self.assertIn("30-Minute Review Path", markdown)
        self.assertIn("Suggested Outreach Paragraph", markdown)
        self.assertIn("https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer", markdown)

    def test_writes_outputs(self):
        packet = build_packet(load_atlas(ATLAS))
        with tempfile.TemporaryDirectory() as tmp:
            json_output = Path(tmp) / "packet.json"
            markdown_output = Path(tmp) / "packet.md"
            write_outputs(packet, json_output, markdown_output)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())

    def test_readme_links_credibility_packet(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/Credibility_Partner_Review_Packet.md", readme)
        self.assertIn("reports/Credibility_Partner_Review_Packet.md", readme)


if __name__ == "__main__":
    unittest.main()

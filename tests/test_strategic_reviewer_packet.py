import tempfile
import unittest
from pathlib import Path

from reference_engine.strategic_reviewer_packet import (
    VERSION,
    collect_evidence,
    render_markdown,
    write_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


class StrategicReviewerPacketTests(unittest.TestCase):
    def test_packet_collects_expected_evidence(self):
        packet = collect_evidence(output_dir=ROOT / "test_outputs" / "strategic_reviewer_packet")

        self.assertEqual(packet["version"], VERSION)
        self.assertGreaterEqual(packet["summary"]["evidence_items"], 10)
        self.assertEqual(packet["summary"]["missing_count"], 0)
        self.assertIn("strategic_review_page", packet["public_links"])
        self.assertIn("pilot-grade", " ".join(packet["claim_boundaries"]))

    def test_markdown_contains_outbound_message_and_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = collect_evidence(output_dir=tmp)
            markdown = render_markdown(packet)

        self.assertIn("# SMERC Strategic Reviewer Evidence Packet", markdown)
        self.assertIn("Suggested Outbound Message", markdown)
        self.assertIn("not production-certified", markdown)
        self.assertIn("recoverability-aware permissioning", markdown)

    def test_write_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet = collect_evidence(output_dir=Path(tmp) / "bundle")
            write_outputs(packet, output_dir=Path(tmp) / "bundle")

            self.assertTrue((Path(tmp) / "bundle" / "strategic_reviewer_packet.json").exists())
            self.assertTrue((Path(tmp) / "bundle" / "Strategic_Reviewer_Evidence_Packet.md").exists())

    def test_docs_and_readme_link_packet(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        brief = (ROOT / "docs" / "Strategic_Reviewer_Brief.md").read_text(encoding="utf-8")

        self.assertIn("docs/Strategic_Reviewer_Brief.md", readme)
        self.assertIn("reference_engine.strategic_reviewer_packet", brief)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from reference_engine.smerc_f_pilot_evidence_packet import build_packet, load_json, render_markdown, write_outputs


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "smerc_f_source_ingestion_report.json"
REGULATORY = ROOT / "reports" / "smerc_f_regulatory_context_report.json"
PUBLIC_REPLAY = ROOT / "reports" / "smerc_f_public_data_replay_report.json"


class SMERCFPilotEvidencePacketTests(unittest.TestCase):
    def test_builds_packet_from_existing_reports(self):
        packet = build_packet(
            source_ingestion=load_json(SOURCE),
            regulatory_context=load_json(REGULATORY),
            public_replay=load_json(PUBLIC_REPLAY),
        )

        self.assertEqual(packet["version"], "smerc-f.pilot-evidence-packet.v1")
        self.assertEqual(packet["artifact_summary"]["source_export_rows"], 6)
        self.assertEqual(packet["artifact_summary"]["regulatory_context_rows"], 6)
        self.assertEqual(packet["artifact_summary"]["public_replay_scenarios"], 50)
        self.assertGreater(packet["artifact_summary"]["public_replay_decision_delta_rate"], 0)
        self.assertGreater(len(packet["most_useful_examples"]), 0)

    def test_markdown_is_reviewer_ready_and_bounded(self):
        packet = build_packet(
            source_ingestion=load_json(SOURCE),
            regulatory_context=load_json(REGULATORY),
            public_replay=load_json(PUBLIC_REPLAY),
        )
        markdown = render_markdown(packet)

        self.assertIn("SMERC-F Pilot Evidence Packet", markdown)
        self.assertIn("Pilot Go Conditions", markdown)
        self.assertIn("Stop Conditions", markdown)
        self.assertIn("Reviewer Questions", markdown)
        for phrase in [
            "AML compliance",
            "legal compliance",
            "fraud detection",
            "sanctions screening",
            "custody",
            "settlement",
            "payment execution",
            "production certification",
        ]:
            self.assertIn(phrase, markdown)

    def test_writes_packet_outputs(self):
        scratch = ROOT / "tests" / "_tmp" / "smerc_f_pilot_evidence_packet"
        scratch.mkdir(parents=True, exist_ok=True)
        packet = build_packet(
            source_ingestion=load_json(SOURCE),
            regulatory_context=load_json(REGULATORY),
            public_replay=load_json(PUBLIC_REPLAY),
        )
        json_output = scratch / "packet.json"
        markdown_output = scratch / "packet.md"

        write_outputs(packet, json_output, markdown_output)

        self.assertIn("smerc-f.pilot-evidence-packet.v1", json_output.read_text(encoding="utf-8"))
        self.assertIn("30-day metadata-only", markdown_output.read_text(encoding="utf-8"))

    def test_docs_and_readme_link_packet(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs = (ROOT / "docs" / "SMERC_F_Pilot_Evidence_Packet.md").read_text(encoding="utf-8")

        self.assertIn("reference_engine.smerc_f_pilot_evidence_packet", readme)
        self.assertIn("docs/SMERC_F_Pilot_Evidence_Packet.md", readme)
        self.assertIn("source export", docs)
        self.assertIn("metadata-only shadow-mode", docs)


if __name__ == "__main__":
    unittest.main()

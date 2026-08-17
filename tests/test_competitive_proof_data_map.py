import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "Competitive_Proof_Data_Map.md"
README = ROOT / "README.md"


class CompetitiveProofDataMapTests(unittest.TestCase):
    def test_doc_maps_competitor_proof_patterns_to_smerc_artifacts(self):
        text = DOC.read_text(encoding="utf-8")

        for phrase in [
            "Catalog evidence",
            "Runtime decision evidence",
            "Proxy/enforcement evidence",
            "Audit evidence",
            "Benchmark evidence",
            "Operational evidence",
            "MCP Tool Risk Scanner",
            "ILION_Bench_Replay",
            "Real_Public_Incident_Replay",
        ]:
            self.assertIn(phrase, text)

    def test_doc_blocks_overclaims_from_public_data(self):
        text = DOC.read_text(encoding="utf-8")

        for phrase in [
            "incident reduction",
            "production security certification",
            "customer willingness to pay",
            "external pilot data",
            "not customer-validated risk reduction",
        ]:
            self.assertIn(phrase, text)

    def test_readme_links_competitive_proof_data_map(self):
        self.assertIn("docs/Competitive_Proof_Data_Map.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

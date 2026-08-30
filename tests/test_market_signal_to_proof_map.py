import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "Market_Signal_To_Proof_Map.md"
README = ROOT / "README.md"


class MarketSignalToProofMapTests(unittest.TestCase):
    def test_doc_maps_public_pain_to_smerc_proof(self):
        text = DOC.read_text(encoding="utf-8")

        for phrase in [
            "AI agent governance",
            "MCP security",
            "action-boundary drift",
            "Cloud Metadata Connector",
            "SMERC_F_Financial_Public_Data_Replay",
            "Decision Lifecycle Ledger",
            "Work: observe public technical concerns",
        ]:
            self.assertIn(phrase, text)

    def test_doc_keeps_market_signal_boundary(self):
        text = DOC.read_text(encoding="utf-8")

        for phrase in [
            "not customer validation",
            "customer demand",
            "willingness to pay",
            "production safety",
            "benchmark performance on official upstream datasets",
        ]:
            self.assertIn(phrase, text)

    def test_readme_links_market_signal_to_proof_map(self):
        self.assertIn("docs/Market_Signal_To_Proof_Map.md", README.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

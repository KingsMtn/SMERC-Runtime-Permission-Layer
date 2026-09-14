import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicRuntimePainPointsTests(unittest.TestCase):
    def test_pain_point_map_tracks_aws_and_mcp_signals(self):
        text = (ROOT / "docs" / "Public_Runtime_Pain_Points_To_SMERC.md").read_text(encoding="utf-8")

        for phrase in [
            "AgentCore Gateway bypass",
            "Session-to-user binding",
            "Execution role credential exposure",
            "Command execution authority",
            "MCP token passthrough and confused deputy",
            "MCP tool metadata poisoning",
            "hidden-instruction",
        ]:
            self.assertIn(phrase, text)

        self.assertIn("docs.aws.amazon.com/bedrock-agentcore", text)
        self.assertIn("modelcontextprotocol.io/specification", text)
        self.assertIn("owasp.org/www-community/attacks/MCP_Tool_Poisoning", text)
        self.assertIn("not customer validation", text)
        self.assertIn("not customer proof", text)

    def test_pain_point_map_is_linked_from_review_surfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        market = (ROOT / "docs" / "Market_Signal_To_Proof_Map.md").read_text(encoding="utf-8")
        data_map = (ROOT / "docs" / "Runtime_Data_Source_Map.md").read_text(encoding="utf-8")
        indexing = (ROOT / "docs" / "Public_Indexing_Assets.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        for text in [readme, market, data_map, indexing]:
            self.assertIn("docs/Public_Runtime_Pain_Points_To_SMERC.md", text)

        self.assertIn("AWS AgentCore public security guidance", market)
        self.assertIn("MCP authorization and tool poisoning", market)
        self.assertIn("public runtime pain-point map", changelog)


if __name__ == "__main__":
    unittest.main()

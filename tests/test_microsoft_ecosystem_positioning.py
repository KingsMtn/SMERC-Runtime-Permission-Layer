import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
MICROSOFT_DOC = ROOT / "docs" / "Microsoft_Ecosystem_Positioning.md"
MCP_POSITIONING_DOC = ROOT / "docs" / "MCP_Runtime_Governance_Positioning.md"
TECH_COMMUNITY_DRAFT = ROOT / "docs" / "Microsoft_Tech_Community_Post_Draft.md"


class MicrosoftEcosystemPositioningTests(unittest.TestCase):
    def test_docs_exist_and_anchor_to_existing_working_artifacts(self):
        for path in (MICROSOFT_DOC, MCP_POSITIONING_DOC, TECH_COMMUNITY_DRAFT):
            self.assertTrue(path.exists(), path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("recoverability", text)
            self.assertIn("MCP", text)
            self.assertIn("SMERC", text)

        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (MICROSOFT_DOC, MCP_POSITIONING_DOC, TECH_COMMUNITY_DRAFT)
        )
        self.assertIn("reference_engine/mcp_tool_governance.py", combined)
        self.assertIn("docs/MCP_Tool_Governance.md", combined)
        self.assertIn("SPARTa", combined)

    def test_positioning_preserves_evidence_boundaries(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (MICROSOFT_DOC, MCP_POSITIONING_DOC, TECH_COMMUNITY_DRAFT)
        )

        for required_boundary in (
            "does not replace",
            "pilot-grade",
            "not production-certified",
            "not microsoft-certified",
            "does not claim mcp compliance",
        ):
            self.assertIn(required_boundary, combined)

        unsupported_claims = (
            "microsoft certified",
            "microsoft endorsed",
            "marketplace approved",
            "has proven to reduce incidents",
            "replaces mcp",
            "replaces iam",
            "replaces opa",
        )
        for claim in unsupported_claims:
            self.assertNotIn(claim, combined)

    def test_readme_and_changelog_surface_microsoft_mcp_lane(self):
        readme = README.read_text(encoding="utf-8")
        changelog = CHANGELOG.read_text(encoding="utf-8")

        for expected in (
            "docs/Microsoft_Ecosystem_Positioning.md",
            "docs/MCP_Runtime_Governance_Positioning.md",
            "docs/Microsoft_Tech_Community_Post_Draft.md",
        ):
            self.assertIn(expected, readme)

        self.assertIn("MCP-style tool calls", readme)
        self.assertIn("Microsoft ecosystem", changelog)


if __name__ == "__main__":
    unittest.main()

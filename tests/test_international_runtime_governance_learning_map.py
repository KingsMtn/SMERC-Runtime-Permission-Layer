import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InternationalRuntimeGovernanceLearningMapTests(unittest.TestCase):
    def test_learning_map_names_sources_and_boundaries(self):
        text = (ROOT / "docs" / "International_Runtime_Governance_Learning_Map.md").read_text(
            encoding="utf-8"
        )

        for phrase in [
            "UK AI Security Institute Inspect Sandboxing Toolkit",
            "SandboxEscapeBench",
            "Project Moonshot",
            "Japan AISI AI Incident Response Approach Book",
            "Canada CAISI evaluator-disclosure guidance",
            "EU AI Act / GPAI Code of Practice",
            "Microsoft Agent Governance Toolkit",
            "Nightfall MCP Gateway",
        ]:
            self.assertIn(phrase, text)

        for phrase in [
            "tooling_isolation",
            "host_isolation",
            "network_isolation",
            "sandbox_escape_surface",
            "execution_environment_boundary",
            "public examples",
            "trusted reviewer examples",
            "private regression cases",
        ]:
            self.assertIn(phrase, text)

        for boundary in [
            "does not claim",
            "endorsed by",
            "regulatory compliance",
            "leaked proprietary source code",
            "private prompts",
        ]:
            self.assertIn(boundary, text)

    def test_learning_map_is_linked_from_review_surfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        data_map = (ROOT / "docs" / "Runtime_Data_Source_Map.md").read_text(encoding="utf-8")

        for text in [readme, data_map]:
            self.assertIn("docs/International_Runtime_Governance_Learning_Map.md", text)


if __name__ == "__main__":
    unittest.main()

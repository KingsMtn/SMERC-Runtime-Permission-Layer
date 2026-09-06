import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeDataSourceMapTests(unittest.TestCase):
    def test_runtime_data_source_map_names_priority_sources_and_boundaries(self):
        text = (ROOT / "docs" / "Runtime_Data_Source_Map.md").read_text(encoding="utf-8")

        for source in [
            "Agent Security Benchmark",
            "CrossMCP-Bench",
            "AgentShield-Bench",
            "SyFI TraceLab",
            "Toolathlon",
            "Blackstable",
        ]:
            self.assertIn(source, text)

        self.assertIn("Governance Routing Workbench routes", text)
        self.assertIn("license-compatible", text)
        self.assertIn("source version or commit", text)
        self.assertIn("skipped rows and why", text)
        self.assertIn("not benchmark certification", text)
        self.assertIn("customer-owned metadata", text)

    def test_runtime_data_source_map_is_linked_from_review_surfaces(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        public_benchmark = (ROOT / "docs" / "Public_Benchmark_Ingestion.md").read_text(encoding="utf-8")
        front_door = (ROOT / "docs" / "Company_Reviewer_Front_Door.md").read_text(encoding="utf-8")
        ai_bundle_doc = (ROOT / "docs" / "AI_Readable_Reviewer_Bundle.md").read_text(encoding="utf-8")
        ai_bundle = json.loads((ROOT / "examples" / "ai_reviewer_bundle.json").read_text(encoding="utf-8"))

        for text in [readme, public_benchmark, front_door, ai_bundle_doc]:
            self.assertIn("docs/Runtime_Data_Source_Map.md", text)

        self.assertIn("runtime_data_source_map", ai_bundle["current_evidence"])


if __name__ == "__main__":
    unittest.main()

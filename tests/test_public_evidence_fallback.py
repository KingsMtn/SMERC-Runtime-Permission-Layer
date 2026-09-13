import unittest

from reference_engine.public_evidence_fallback import build_report, render_markdown


class PublicEvidenceFallbackTests(unittest.TestCase):
    def test_builds_source_provenance_report(self):
        report = build_report()

        self.assertEqual(report["version"], "smerc.public-evidence-fallback.v1")
        self.assertGreaterEqual(report["source_count"], 7)
        source_ids = {profile["source_id"] for profile in report["profiles"]}
        self.assertIn("agent_action_boundary_benchmark", source_ids)
        self.assertIn("agentshield_bench", source_ids)
        self.assertIn("lakmus_agent_failures", source_ids)
        self.assertIn("nika_network_incidents", source_ids)

    def test_profiles_preserve_boundaries_and_mapping(self):
        report = build_report()

        for profile in report["profiles"]:
            self.assertIn("metadata_origin", profile)
            self.assertIn("smerc_mapping", profile)
            self.assertIn("url", profile)
            self.assertNotIn("customer validation", profile["smerc_mapping"].lower())

        self.assertIn("license and version checks", report["evidence_boundary"])
        self.assertIn("not customer validation", report["work_result_impact"]["impact"])

    def test_markdown_is_reviewer_readable(self):
        markdown = render_markdown(build_report())

        self.assertIn("Public Evidence Fallback Plan", markdown)
        self.assertIn("Source Provenance", markdown)
        self.assertIn("replace these examples with 5 to 25 metadata-only actions", markdown)
        self.assertIn("Evidence Boundary", markdown)


if __name__ == "__main__":
    unittest.main()

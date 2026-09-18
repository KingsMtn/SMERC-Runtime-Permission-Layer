import unittest
from pathlib import Path

from reference_engine.aws_boundary_contrast import build_boundary_pairs, build_contrast_report
from reference_engine.aws_metadata_adapter import build_adapter_report, load_source_exports


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "aws_open_source_validation_corpus.json"


class AWSBoundaryContrastTests(unittest.TestCase):
    def test_pairs_change_only_boundary_fixture_fields_and_identity(self):
        rows = build_boundary_pairs(load_source_exports(SOURCE))
        self.assertEqual(len(rows), 4)
        for index in range(0, len(rows), 2):
            bounded, broad = rows[index], rows[index + 1]
            for field in [
                "proposed_action",
                "tool",
                "reversibility",
                "containment_strength",
                "rollback_latency",
                "evidence_quality",
                "impact_scope",
                "cancel_reliability",
                "authorization_confidence",
            ]:
                self.assertEqual(bounded[field], broad[field])
            self.assertEqual(bounded["sandbox_escape_surface"], ["none_known"])
            self.assertIn("production_credentials", broad["sandbox_escape_surface"])

    def test_broad_environment_is_strictly_more_restrictive(self):
        rows = build_boundary_pairs(load_source_exports(SOURCE))
        report = build_contrast_report(build_adapter_report(rows))

        self.assertTrue(report["all_broad_variants_stricter"])
        self.assertEqual(report["source_record_count"], 2)
        self.assertEqual(report["variant_count"], 4)
        for comparison in report["comparisons"]:
            self.assertNotIn("EXECUTION_BOUNDARY_EVIDENCE_INCOMPLETE", comparison["bounded_reason_codes"])
            self.assertIn("SANDBOX_ESCAPE_OR_CREDENTIAL_SURFACE", comparison["broad_reason_codes"])
            self.assertIn("PRODUCTION_NETWORK_REACHABLE", comparison["broad_reason_codes"])

    def test_docs_state_test_and_evidence_boundaries(self):
        text = (ROOT / "docs" / "AWS_Execution_Boundary_Contrast.md").read_text(encoding="utf-8")
        self.assertIn("same action", text)
        self.assertIn("strictly more restrictive", text)
        self.assertIn("not observed AWS configurations", text)


if __name__ == "__main__":
    unittest.main()

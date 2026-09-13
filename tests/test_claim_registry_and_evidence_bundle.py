import copy
import unittest
from pathlib import Path

from reference_engine.claim_registry import build_claim_registry, render_markdown as render_claims
from reference_engine.evidence_bundle import build_evidence_bundle, render_markdown, verify_evidence_bundle


ROOT = Path(__file__).resolve().parents[1]


class ClaimRegistryAndEvidenceBundleTests(unittest.TestCase):
    def test_claim_registry_separates_supported_and_unsupported_claims(self):
        registry = build_claim_registry(root=ROOT)

        self.assertEqual(registry["version"], "smerc.claim-registry.v1")
        self.assertGreaterEqual(registry["status_counts"]["supported"], 4)
        self.assertGreaterEqual(registry["status_counts"]["not_supported"], 3)
        claims = {claim["claim_id"]: claim for claim in registry["claims"]}
        self.assertEqual(claims["customer_owned_metadata_received"]["status"], "not_supported")
        self.assertEqual(claims["public_pattern_fallback_adapter_runs"]["status"], "supported")
        self.assertEqual(claims["production_aws_connector_ready"]["status"], "not_supported")
        for claim in registry["claims"]:
            self.assertEqual(claim["evidence_status"]["missing_count"], 0)

    def test_claim_registry_markdown_is_reviewer_readable(self):
        markdown = render_claims(build_claim_registry(root=ROOT))

        self.assertIn("SMERC Claim Registry", markdown)
        self.assertIn("not_supported", markdown)
        self.assertIn("customer validation", markdown)

    def test_evidence_bundle_hashes_and_verifies_artifacts(self):
        bundle = build_evidence_bundle(root=ROOT)
        verification = verify_evidence_bundle(bundle, root=ROOT)

        self.assertEqual(bundle["version"], "smerc.evidence-bundle.v1")
        self.assertEqual(bundle["artifact_count"], len(bundle["artifacts"]))
        self.assertTrue(verification["valid"])
        self.assertEqual(verification["verified_artifact_count"], bundle["artifact_count"])

    def test_evidence_bundle_detects_tampering(self):
        bundle = build_evidence_bundle(root=ROOT)
        tampered = copy.deepcopy(bundle)
        tampered["artifacts"][0]["sha256"] = "0" * 64
        verification = verify_evidence_bundle(tampered, root=ROOT)

        self.assertFalse(verification["valid"])
        self.assertGreaterEqual(verification["error_count"], 1)

    def test_evidence_bundle_markdown_includes_boundary(self):
        bundle = build_evidence_bundle(root=ROOT)
        markdown = render_markdown(bundle, verify_evidence_bundle(bundle, root=ROOT))

        self.assertIn("SMERC Evidence Bundle", markdown)
        self.assertIn("SHA-256", markdown)
        self.assertIn("customer validation", markdown)

    def test_docs_reference_commands(self):
        claim_doc = (ROOT / "docs" / "Claim_Registry.md").read_text(encoding="utf-8")
        bundle_doc = (ROOT / "docs" / "Evidence_Bundle.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python -m reference_engine.claim_registry", claim_doc)
        self.assertIn("python -m reference_engine.evidence_bundle", bundle_doc)
        self.assertIn("docs/Claim_Registry.md", readme)
        self.assertIn("docs/Evidence_Bundle.md", readme)


if __name__ == "__main__":
    unittest.main()

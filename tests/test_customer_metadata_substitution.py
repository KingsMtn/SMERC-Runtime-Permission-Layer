import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CustomerMetadataSubstitutionTests(unittest.TestCase):
    def test_guide_defines_safe_customer_replacement_process(self):
        text = (ROOT / "pilot_package" / "Customer_Metadata_Substitution_Guide.md").read_text()

        self.assertIn("Do not overwrite the public samples", text)
        self.assertIn("10 to 25 metadata-only actions", text)
        self.assertIn("Before a pilot runs, omit `--pilot-metrics`", text)
        self.assertIn("Do not use sample metrics in external claims", text)
        self.assertIn("not production certification", text)

    def test_checklist_starts_unconfirmed_and_blocks_sensitive_payloads(self):
        payload = json.loads((ROOT / "examples" / "customer_metadata_substitution_checklist.json").read_text())

        self.assertEqual(payload["schema"], "smerc.customer-metadata-substitution-checklist.v1")
        confirmations = {item["item"]: item for item in payload["required_confirmations"]}
        self.assertFalse(confirmations["no_sensitive_payloads"]["confirmed"])
        self.assertFalse(confirmations["sample_metrics_removed_before_external_claims"]["confirmed"])
        self.assertIn("does not prove customer demand", payload["evidence_boundary"])

    def test_readme_links_substitution_guide(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn("pilot_package/Customer_Metadata_Substitution_Guide.md", readme)


if __name__ == "__main__":
    unittest.main()

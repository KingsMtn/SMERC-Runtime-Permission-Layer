import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "SMERC_F_Metadata_Intake_Contract.md"
TEMPLATE = ROOT / "examples" / "smerc_f_metadata_intake_template.json"
README = ROOT / "README.md"


class SMERCFMetadataIntakeContractTests(unittest.TestCase):
    def test_contract_is_linked_and_bounded(self):
        doc = DOC.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("metadata-only", doc)
        self.assertIn("shadow-mode", doc)
        self.assertIn("no live fund movement", doc)
        self.assertIn("Prohibited First-Pilot Inputs", doc)
        self.assertIn("AML compliance", doc)
        self.assertIn("production certification", doc)
        self.assertIn("docs/SMERC_F_Metadata_Intake_Contract.md", readme)

    def test_template_contains_required_fields_without_prohibited_values(self):
        records = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        required_fields = {
            "record_id",
            "workflow_family",
            "proposed_action",
            "actor_type",
            "existing_control_outcome",
            "amount_band_usd",
            "asset_type",
            "settlement_finality",
            "rollback_latency",
            "containment_strength",
            "evidence_quality",
            "anomaly_pressure",
            "counterparty_concentration",
            "market_stress",
            "customer_impact_radius",
        }
        prohibited_fields = {
            "customer_name",
            "account_number",
            "private_key",
            "seed_phrase",
            "access_token",
            "raw_transaction_payload",
            "production_credentials",
        }

        self.assertGreaterEqual(len(records), 3)
        for record in records:
            self.assertTrue(required_fields.issubset(record))
            self.assertTrue(prohibited_fields.isdisjoint(record))
            self.assertIn(record["amount_band_usd"], {"under_10k", "10k_100k", "100k_1m", "1m_10m", "over_10m"})


if __name__ == "__main__":
    unittest.main()

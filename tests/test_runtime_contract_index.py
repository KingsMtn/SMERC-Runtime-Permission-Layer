import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "examples" / "runtime_contract_index.json"
SCHEMA = ROOT / "schemas" / "smerc-runtime-contract-index-v1.schema.json"


class RuntimeContractIndexTests(unittest.TestCase):
    def test_index_has_required_runtime_chain_contracts(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        contracts = {item["contract"]: item for item in index["contracts"]}
        required = {
            "smerc.beacon.v1",
            "smerc.action.v1",
            "smerc.decision.v1",
            "smerc.policy.v1",
            "smerc.spl.v0",
            "smerc.agent_handshake.v1",
            "smerc.sparta-route.v1",
            "smerc.sparta-vocabulary.v1",
            "smerc.permit.v1",
            "smerc.control-evidence.v1",
            "smerc.execution-report.v1",
            "smerc.decision-certificate.v1",
            "smerc.decision-lifecycle-ledger.v1",
            "smerc.dll-intelligence.v1",
        }
        self.assertEqual(index["version"], "smerc.runtime-contract-index.v1")
        self.assertTrue(required.issubset(contracts))
        self.assertIn("route_with_sparta", index["canonical_loop"])

    def test_index_handoff_rules_preserve_fail_closed_chain(self):
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        handoffs = {(item["from"], item["to"]): item for item in index["handoff_rules"]}
        self.assertIn(("smerc.decision.v1", "smerc.sparta-route.v1"), handoffs)
        self.assertIn(("smerc.sparta-route.v1", "smerc.control-evidence.v1"), handoffs)
        self.assertIn(("smerc.decision-lifecycle-ledger.v1", "smerc.dll-intelligence.v1"), handoffs)
        self.assertIn("verified_hash_chain", handoffs[("smerc.decision-lifecycle-ledger.v1", "smerc.dll-intelligence.v1")]["required_artifact"])
        self.assertIn("cannot be relaxed", " ".join(index["interpretation_rules"]))

    def test_schema_and_docs_link_index(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        doc = (ROOT / "docs" / "Runtime_Contract_Index.md").read_text(encoding="utf-8")
        spec = (ROOT / "specification" / "SMERC_Runtime_Contract_Index_v1.md").read_text(encoding="utf-8")
        self.assertEqual(schema["properties"]["version"]["const"], "smerc.runtime-contract-index.v1")
        for text in [readme, doc, spec]:
            self.assertIn("smerc.runtime-contract-index.v1", text)
        self.assertIn("examples/runtime_contract_index.json", readme)


if __name__ == "__main__":
    unittest.main()

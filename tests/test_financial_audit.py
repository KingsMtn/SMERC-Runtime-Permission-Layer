import copy
import unittest

from reference_engine.financial_audit import FinancialAuditChain
from reference_engine.financial_permission_profile import FinancialPermissionProfile
from tests.test_financial_permission_profile import request


class FinancialAuditTests(unittest.TestCase):
    def setUp(self):
        self.decision = FinancialPermissionProfile().evaluate(request())

    def test_decision_and_override_form_valid_chain(self):
        chain = FinancialAuditChain()
        decision_record = chain.append_decision("FIN_ACTION", self.decision, "2026-01-01T00:00:00+00:00")
        override = chain.append_override(
            "FIN_ACTION",
            self.decision["state"],
            "THROTTLE",
            "reviewer-42",
            "Reduce transaction scope pending validation.",
            "2026-01-01T00:01:00+00:00",
        )
        verification = chain.verify()
        self.assertTrue(verification["valid"])
        self.assertEqual(override["previous_hash"], decision_record["record_hash"])

    def test_tampering_is_detected(self):
        chain = FinancialAuditChain()
        chain.append_decision("FIN_ACTION", self.decision, "2026-01-01T00:00:00+00:00")
        records = copy.deepcopy(chain.records)
        records[0]["state"] = "DENY"
        verification = FinancialAuditChain(records).verify()
        self.assertFalse(verification["valid"])
        self.assertIn("record 1: record hash mismatch", verification["errors"])

    def test_override_requires_identity_and_rationale(self):
        chain = FinancialAuditChain()
        with self.assertRaises(ValueError):
            chain.append_override("FIN_ACTION", "FREEZE", "ALLOW", "", "short")


if __name__ == "__main__":
    unittest.main()


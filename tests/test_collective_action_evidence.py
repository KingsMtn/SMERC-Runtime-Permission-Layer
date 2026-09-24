import copy
import hashlib
import json
import unittest

from reference_engine.collective_action_evidence import evaluate_collective_action_evidence


def sha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def envelope(decision="NO_COLLECTIVE_RISK_OBSERVED", predecessor=None):
    value = {
        "contract_version": "smerc.collective-decision-envelope.v1",
        "producer_report_version": "smerc.collective-action-assurance.v1",
        "issued_at_ms": 1_000, "expires_at_ms": 2_000,
        "scope": {"resource": "aws:s3:customer-export", "action": "export",
            "operation_id": "op-export"},
        "collective_decision": decision,
        "risk_group_count": 1 if decision == "ADVISE_REVIEW" else 0,
        "participant_ids": ["agent-a", "agent-b"],
        "quorum": {"required": 2, "observed": 2, "satisfied": True},
        "continuity": {"predecessor_envelope_sha256": predecessor},
        "evidence": {"report_sha256": "a" * 64, "finding_ids": ["finding-a"]},
        "authority_effect": "NONE", "advisory_only": True,
    }
    value["envelope_sha256"] = sha(value)
    value["envelope_id"] = f"aa_{value['envelope_sha256'][:24]}"
    return value


def evaluate(value, **overrides):
    arguments = {"now_ms": 1_500, "expected_resource": "aws:s3:customer-export",
        "expected_action": "export", "expected_operation_id": "op-export"}
    arguments.update(overrides)
    return evaluate_collective_action_evidence(value, **arguments)


class CollectiveActionEvidenceTests(unittest.TestCase):
    def test_verified_low_risk_evidence_adds_no_permission_or_posture(self):
        result = evaluate(envelope())
        self.assertEqual(result["decision"], "ACCEPT_EVIDENCE")
        self.assertIsNone(result["max_recommended_posture"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertIn("Collective Action Assurance (AA)", result["plain_english_summary"])
        self.assertIn("Runtime Assurance (RA)", result["plain_english_summary"])

    def test_review_advice_caps_runtime_at_freeze(self):
        result = evaluate(envelope("ADVISE_REVIEW"))
        self.assertEqual(result["decision"], "ESCALATE")
        self.assertEqual(result["max_recommended_posture"], "FREEZE")

    def test_tampered_evidence_fails_closed(self):
        value = envelope()
        value["risk_group_count"] = 99
        result = evaluate(value)
        self.assertEqual(result["decision"], "REJECT")
        self.assertEqual(result["max_recommended_posture"], "DENY")

    def test_expired_evidence_fails_closed(self):
        result = evaluate(envelope(), now_ms=2_000)
        self.assertEqual(result["decision"], "REJECT")
        self.assertIn("expired", result["plain_english_summary"])

    def test_scope_mismatch_fails_closed(self):
        result = evaluate(envelope(), expected_resource="aws:iam:role/admin")
        self.assertEqual(result["max_recommended_posture"], "DENY")
        self.assertIn("scope.resource", result["plain_english_summary"])

    def test_continuity_mismatch_fails_closed(self):
        result = evaluate(envelope(predecessor="b" * 64),
            expected_predecessor_sha256="c" * 64)
        self.assertEqual(result["max_recommended_posture"], "DENY")
        self.assertIn("continuity", result["plain_english_summary"])

    def test_claimed_authority_is_rejected(self):
        value = copy.deepcopy(envelope())
        value["authority_effect"] = "ALLOW"
        unsigned = {k: v for k, v in value.items()
            if k not in {"envelope_sha256", "envelope_id"}}
        value["envelope_sha256"] = sha(unsigned)
        value["envelope_id"] = f"aa_{value['envelope_sha256'][:24]}"
        result = evaluate(value)
        self.assertEqual(result["decision"], "REJECT")
        self.assertIn("cannot grant authority", result["plain_english_summary"])


if __name__ == "__main__":
    unittest.main()

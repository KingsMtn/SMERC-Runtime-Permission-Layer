import copy
import unittest

from reference_engine.aws_external_outcome_label import build_external_outcome_label, verify_external_outcome_label
from reference_engine.aws_mcp_enforced_live_proof import run_proof


class AWSExternalOutcomeLabelTests(unittest.TestCase):
    KEY = b"external-outcome-label-test-key-32-bytes"

    def setUp(self):
        self.record = run_proof(lambda *_args: {"content": [], "isError": False})["portable_evidence"]

    def label(self):
        return build_external_outcome_label(
            self.record,
            label_id="customer-review-001",
            source_type="CUSTOMER_POSTCONDITION",
            reviewer_id="customer-platform-team",
            observed_at="2026-09-23T03:00:00Z",
            judged_correct=True,
            unexpected_consequences=False,
            controls_sufficient=True,
            rationale="Customer-owned postcondition review found the controls sufficient.",
            key_id="customer-review-key-1",
            signing_key=self.KEY,
        )

    def test_label_is_authenticated_and_bound_to_exact_record(self):
        result = verify_external_outcome_label(self.label(), self.record, verification_key=self.KEY)
        self.assertEqual(result["status"], "AUTHENTICATED")
        self.assertEqual(result["record_id"], self.record["record_id"])

    def test_tampered_label_is_rejected(self):
        label = copy.deepcopy(self.label())
        label["judged_correct"] = False
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            verify_external_outcome_label(label, self.record, verification_key=self.KEY)

    def test_short_signing_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least 32 bytes"):
            build_external_outcome_label(
                self.record,
                label_id="review-short-key",
                source_type="HUMAN_REVIEW",
                reviewer_id="reviewer",
                observed_at="2026-09-23T03:00:00Z",
                judged_correct=True,
                unexpected_consequences=False,
                controls_sufficient=True,
                rationale="Independent review.",
                key_id="key-1",
                signing_key=b"short",
            )


if __name__ == "__main__":
    unittest.main()

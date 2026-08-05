import copy
import json
import unittest
from pathlib import Path

from integrations.human_review.review_adapter import (
    HumanReviewError,
    build_review_request,
    build_review_response,
    validate_review_request,
    validate_review_response,
)


ROOT = Path(__file__).resolve().parents[1]
ROUTE = json.loads((ROOT / "reports" / "signed_sparta_route_example.json").read_text(encoding="utf-8-sig"))


class HumanReviewAdapterTests(unittest.TestCase):
    def test_signed_request_and_response_are_bound_to_route_and_replay(self):
        route = copy.deepcopy(ROUTE)
        route["route_state"] = "REVIEW_REQUIRED"
        route["executable"] = False
        route["source_posture"] = "ESCALATE"
        route["applied_controls"] = ["route_to_accountable_reviewer", "require_explicit_approval", "preserve_replay"]
        request = build_review_request(
            route,
            requester="smerc-api",
            reviewer_group="security-operations",
            callback_ref="pilot://review/replay_example_throttle_001",
            ttl_seconds=120,
            now=1_800_000_000,
            secret="request-secret-0123456789",
        )
        validated_request = validate_review_request(request, secret="request-secret-0123456789")
        self.assertEqual(validated_request["decision_replay_id"], route["decision_replay_id"])
        self.assertTrue(validated_request["signature_verification"]["valid"])

        response = build_review_response(
            request,
            reviewer_id="security-reviewer-7",
            verdict="approve",
            rationale="Approve constrained execution only.",
            final_posture="THROTTLE",
            now=1_800_000_030,
            secret="response-secret-0123456789",
        )
        validated_response = validate_review_response(
            response,
            request,
            secret="response-secret-0123456789",
        )
        self.assertEqual(validated_response["route_id"], request["route_id"])
        self.assertEqual(validated_response["request_digest"], response["request_digest"])
        self.assertTrue(validated_response["signature_verification"]["valid"])

    def test_non_review_route_cannot_create_request(self):
        with self.assertRaisesRegex(HumanReviewError, "review-required"):
            build_review_request(
                ROUTE,
                requester="smerc-api",
                reviewer_group="security-operations",
                callback_ref="pilot://review/not-review-required",
            )

    def test_tampered_response_is_rejected(self):
        route = copy.deepcopy(ROUTE)
        route["route_state"] = "REVIEW_REQUIRED"
        route["source_posture"] = "ESCALATE"
        request = build_review_request(
            route,
            requester="smerc-api",
            reviewer_group="security-operations",
            callback_ref="pilot://review/tamper",
            now=1_800_000_000,
            secret="request-secret-0123456789",
        )
        response = build_review_response(
            request,
            reviewer_id="security-reviewer-7",
            verdict="approve",
            rationale="Approve constrained execution only.",
            final_posture="THROTTLE",
            now=1_800_000_030,
            secret="response-secret-0123456789",
        )
        response["decision_replay_id"] = "different-replay"
        with self.assertRaisesRegex(HumanReviewError, "does not match"):
            validate_review_response(response, request, secret="response-secret-0123456789")

    def test_expired_request_blocks_response(self):
        route = copy.deepcopy(ROUTE)
        route["route_state"] = "REVIEW_REQUIRED"
        route["source_posture"] = "ESCALATE"
        request = build_review_request(
            route,
            requester="smerc-api",
            reviewer_group="security-operations",
            callback_ref="pilot://review/expired",
            ttl_seconds=1,
            now=1_800_000_000,
        )
        with self.assertRaisesRegex(HumanReviewError, "expired"):
            build_review_response(
                request,
                reviewer_id="security-reviewer-7",
                verdict="approve",
                rationale="Too late.",
                final_posture="THROTTLE",
                now=1_800_000_002,
            )


if __name__ == "__main__":
    unittest.main()

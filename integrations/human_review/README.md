# SMERC Human Review Adapter

This is a vendor-neutral SPARTa review adapter prototype.

It does not call Slack, Teams, Jira, ServiceNow, or email directly. Instead, it creates a signed review package that those systems can carry without changing the SMERC evidence model.

## Purpose

When SPARTa returns `REVIEW_REQUIRED`, the review adapter creates:

- a signed review request bound to the SPARTa route
- a signed reviewer response bound to the request
- verification that the response matches the request, route, replay ID, reviewer group, and request digest

This proves the review handoff contract before a live vendor integration is added.

## Example

```bash
python integrations/human_review/review_adapter.py request \
  --route-report reports/signed_sparta_route_example.json \
  --requested-by smerc-api \
  --reviewer-group security-operations \
  --callback-ref pilot://github-actions/review/replay_example_throttle_001 \
  --secret development-human-review-request-secret \
  --output reports/human_review_request_example.json \
  --pretty

python integrations/human_review/review_adapter.py response \
  --review-request reports/human_review_request_example.json \
  --reviewer-id security-reviewer-7 \
  --verdict approve \
  --rationale "Approve constrained canary only; preserve rollback and route report." \
  --final-posture THROTTLE \
  --secret development-human-review-response-secret \
  --output reports/human_review_response_example.json \
  --pretty

python integrations/human_review/review_adapter.py verify-response \
  --review-request reports/human_review_request_example.json \
  --review-response reports/human_review_response_example.json \
  --request-secret development-human-review-request-secret \
  --response-secret development-human-review-response-secret \
  --pretty
```

## Evidence Boundary

This adapter verifies package integrity and binding. It does not prove the external identity assurance of Slack, Teams, Jira, ServiceNow, or any other system.

A live adapter must preserve the signed payload, capture external reviewer identity, record delivery status, record timeout behavior, and return the verified response to the Decision Lifecycle Ledger.

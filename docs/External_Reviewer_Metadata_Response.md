# External Reviewer Metadata Response

This report checks whether an external reviewer response is safe and useful enough to move from public examples to reviewer-owned metadata.

Run:

```bash
python -m reference_engine.external_reviewer_metadata_response examples/external_reviewer_metadata_response_example.json --pretty
```

Outputs:

- `reports/External_Reviewer_Metadata_Response_Assessment.md`
- `reports/external_reviewer_metadata_response_assessment.json`

## Work / Result / Impact

Work: assess whether a reviewer supplied usable metadata-only action examples without secrets, live access, raw customer records, regulated payloads, or production logs.

Result: SMERC returns `ready_for_customer_metadata_evaluation`, `ready_with_review_limits`, or `not_ready`.

Impact: the project can avoid wasting time on vague interest while also avoiding unsafe customer-data collection. A reviewer response must cross this gate before it should be treated as meaningful pilot evidence.

## What It Checks

- metadata-only boundary confirmed
- 5 to 25 supplied action records
- no sensitive data included
- no live access requested
- current control outcomes available
- reviewer labels available
- p95 performance threshold available
- postcondition observation possible

## Evidence Boundary

This is a readiness screen. It does not prove customer demand, production safety, incident reduction, compliance, or approval for enforcement.

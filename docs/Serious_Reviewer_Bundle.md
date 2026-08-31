# Serious Reviewer Bundle

## Purpose

The Serious Reviewer Bundle gives a company reviewer one command that assembles the current SMERC proof-to-pilot path.

It answers a practical question:

> Can SMERC generate a complete local review package before a company shares production access, secrets, regulated payloads, or live workflow authority?

## Run

From the repository root:

```bash
python -m reference_engine.serious_reviewer_bundle --workflow-family general --requested-actions 10 --pretty
```

For financial-services review:

```bash
python -m reference_engine.serious_reviewer_bundle --workflow-family financial --requested-actions 12 --pretty
```

Generated files:

```text
reports/serious_reviewer_bundle/Serious_Reviewer_Bundle.md
reports/serious_reviewer_bundle/serious_reviewer_bundle.json
reports/serious_reviewer_bundle/Customer_Evaluation_Report.md
reports/serious_reviewer_bundle/Postcondition_Evidence_Report.md
reports/serious_reviewer_bundle/Serious_Report_Performance.md
reports/serious_reviewer_bundle/Customer_Owned_Metadata_Request.md
reports/serious_reviewer_bundle/External_Reviewer_Metadata_Response_Assessment.md
```

## What It Includes

- Customer evaluation for one workflow family: general, cloud, or financial.
- Postcondition evidence comparing SPARTa-required controls with observed control and execution evidence.
- Serious report performance metrics for local p50, p95, and maximum proof-path timing.
- Customer-owned metadata request for 5 to 25 safe action examples.
- External reviewer metadata response assessment.
- A bundle readiness status and recommended next action.

## Work / Result / Impact

Work: assemble customer evaluation, postcondition evidence, performance metrics, metadata request, and reviewer-response assessment into one local package.

Result: the reviewer receives one report that summarizes pilot fit, postcondition gaps or violations, local p95 timing, metadata safety, and next action.

Impact: SMERC becomes easier for a real company to test without founder-led explanation or unsafe data sharing.

## Readiness Statuses

- `ready_for_shadow_mode_discussion`: the package has no blockers and no serious review warnings.
- `ready_for_limited_review`: the package is usable, but a reviewer should resolve warnings before a pilot.
- `not_ready_for_pilot`: blockers exist and the team should not pitch a pilot from this package.

## Evidence Boundary

This is a local, metadata-only technical review package. It does not prove customer demand, production safety, hosted API latency, compliance, incident reduction, or enforce-mode readiness.

The next real proof remains external: a reviewer replaces the examples with 10 to 25 safe metadata-only actions from one owned workflow and decides whether recoverability before execution changes their judgment enough to justify shadow-mode testing.

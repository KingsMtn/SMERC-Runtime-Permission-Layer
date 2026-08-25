# Cloud Admin Customer Evaluation

## Purpose

This evaluation pack lets a cloud security, SRE, platform, or infrastructure reviewer run SMERC against realistic cloud-administration action metadata without connecting SMERC to a live cloud account.

It is designed for one question:

> Would recoverability-aware runtime permissioning change how we review AI-assisted cloud administration before production side effects occur?

## Run Locally

From the repository root:

```bash
python -m reference_engine.customer_evaluation \
  examples/cloud_admin_customer_eval_actions.json \
  --json-output reports/cloud_admin_customer_evaluation/customer_evaluation_report.json \
  --markdown-output reports/cloud_admin_customer_evaluation/Customer_Evaluation_Report.md \
  --pretty
```

## Run From This Repository's Actions Tab

Open:

```text
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/customer-evaluations.yml
```

Select **Run workflow**, then choose:

```text
evaluation_set = cloud-admin
```

The workflow uploads an artifact named `smerc-customer-evaluations` with Markdown and JSON reports.

## Included Scenarios

The pack includes eight metadata-only cloud administration scenarios:

- production IAM permission expansion
- production database network-boundary change
- database cluster deletion from incomplete evidence
- Kubernetes canary rollout under reliability pressure
- DNS cutover to a new regional endpoint
- staged service authentication rotation
- production capacity reduction under latency pressure
- backup-retention reduction after a cost anomaly

## What Reviewers Should Inspect

Look for:

- actions where hard Ref-gate failures cap the decision to `DENY`
- actions that are constrained instead of fully blocked
- actions where weak rollback or weak containment increases irreversible exposure
- whether execution routing applies useful controls before a cloud action proceeds
- whether Decision Lifecycle Ledger evidence is complete enough for review
- whether the autonomy-budget result matches reviewer intuition

## Evidence Boundary

This pack proves that the public SMERC repository can evaluate cloud-administration metadata and generate repeatable review artifacts. It does not prove production safety, cloud provider certification, incident reduction, compliance, prompt-injection defense, or readiness to enforce against live infrastructure.

## Recommended Next Step

If the sample report is useful, replace the examples with 10 to 25 metadata-only actions from one real cloud workflow, such as production IAM changes, infrastructure-as-code applies, Kubernetes rollouts, database administration, network-policy updates, or backup-policy changes.

# Prospect Routing

## Purpose

Prospect routing decides which SMERC path fits an interested organization:

- core GitHub Actions shadow-mode pilot
- SMERC-F financial shadow-mode pilot
- review-only / not ready

This prevents SMERC from treating every interested company the same way.

## Run

```bash
python -m reference_engine.prospect_router examples/prospect_route_sample.json --pretty
```

Generated outputs:

```text
reports/Prospect_Route_Report.md
reports/prospect_route_report.json
```

## Route Logic

Use the core GitHub Actions path when the prospect has:

- AI-agent or automation actions
- CI/CD, deployment, or infrastructure workflows
- side effects
- reviewer labels
- metadata-only intake
- observe-mode feasibility

Use the SMERC-F financial path when the prospect has:

- automated financial, stablecoin, payment, treasury, custody, or blockchain workflows
- meaningful irreversible exposure
- reviewer labels
- metadata-only intake
- observe-mode feasibility
- no requirement for live fund movement in the first test
- no expectation that SMERC-F replaces AML compliance

Use review-only when the prospect lacks side-effecting actions, reviewer capacity, metadata boundaries, or observe-mode feasibility.

## Boundary

Prospect routing is a screening tool. It does not prove buyer intent, product-market fit, AML compliance, production readiness, pilot success, or incident reduction.

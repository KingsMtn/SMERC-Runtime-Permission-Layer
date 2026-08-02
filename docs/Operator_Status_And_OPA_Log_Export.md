# Operator Status And OPA-Style Decision Log Export

## Purpose

SMERC should be understandable to teams that already operate policy engines, IAM, approval workflows, and log pipelines.

This module adds two operator-facing artifacts:

- a SMERC operator status report
- an OPA-style decision log export

The goal is compatibility and reviewability, not OPA parity.

## Why This Exists

Mature authorization systems usually provide:

- active policy or bundle version
- health or readiness status
- runtime latency and unavailable-rate signals
- decision counts
- unavailable evaluation counts
- decision logs
- audit/debug information
- exportable records for existing pipelines

SMERC already has stronger recoverability and lifecycle evidence than a simple decision log, but operators still need a familiar status surface.

## Generate Reports

```bash
python -m reference_engine.operator_status --pretty
```

Generated outputs:

```text
reports/operator_status.json
reports/Operator_Status_Report.md
reports/opa_decision_log_export.json
reports/OPA_Decision_Log_Export.md
```

When `reports/policy_bundle_manifest.json` exists, the command includes policy bundle status in the operator report. To verify the sample signed bundle:

```bash
python -m reference_engine.operator_status --pretty \
  --policy-bundle-signing-key local-policy-bundle-signing-key-012345
```

## API

```bash
curl -H "Authorization: Bearer $SMERC_API_KEY" \
  "http://127.0.0.1:8000/v1/operator/status?limit=50&latency_slo_ms=250"
```

The API endpoint is tenant-scoped and requires `metrics.read`. It summarizes stored decision activity, API-observed runtime health, active policy identity, and readiness caveats. The API-generated report does not verify the full customer intake checklist, business sponsor, or data-boundary readiness; those remain pilot-package artifacts.

## Operator Status

The operator status report includes:

- tenant
- active policy version
- active profile version
- optional signed policy bundle verification
- runtime health summary
- pilot readiness state
- customer intake readiness state
- decision count
- posture distribution
- unavailable evaluation count and rate
- p95 evaluation latency when runtime observations exist
- top reason codes
- top controls
- operational checks

If a policy bundle is supplied but does not verify, operator status becomes `blocked`. That prevents a pilot reviewer from treating an unverified or drifted policy bundle as safe to activate.

If a runtime health report is supplied, operator status includes health status, p95 latency, SLO status, unavailable rate, and observed evaluation count. A blocked runtime health report blocks operator status; a degraded report degrades operator status. Missing runtime health remains a warning because early imported benchmarks may not contain API observations.

This gives a platform team a compact answer to:

> Is the pilot package, customer intake, and decision activity coherent enough to operate or discuss?

## OPA-Style Decision Log Export

The OPA-style export maps SMERC decision artifacts into entries with:

- decision ID
- timestamp
- policy path
- input
- result
- bundle revision
- labels

SMERC-specific fields are preserved inside `result`:

- posture
- risk score
- confidence score
- reason codes
- controls
- replay ID

This helps teams ingest SMERC decisions into existing policy/audit pipelines without pretending SMERC is OPA or Rego.

## Correct Interpretation

Say:

> SMERC can export OPA-style decision logs for review and ingestion.

Do not say:

> SMERC is OPA-compatible or a replacement for OPA.

Say:

> The operator status report summarizes pilot readiness, active policy/profile versions, runtime health, decision distribution, and unavailable evaluations.

Do not say:

> This proves production availability or incident reduction.

## Evidence Boundary

These exports are pilot-grade operator artifacts. They do not prove production availability, compliance, customer validation, incident reduction, OPA parity, or production enforcement.

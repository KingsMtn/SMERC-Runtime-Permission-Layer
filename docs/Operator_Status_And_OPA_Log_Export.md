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

## Operator Status

The operator status report includes:

- tenant
- active policy version
- active profile version
- pilot readiness state
- customer intake readiness state
- decision count
- posture distribution
- unavailable evaluation count and rate
- top reason codes
- top controls
- operational checks

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

> The operator status report summarizes pilot readiness, active policy/profile versions, decision distribution, and unavailable evaluations.

Do not say:

> This proves production availability or incident reduction.

## Evidence Boundary

These exports are pilot-grade operator artifacts. They do not prove production availability, compliance, customer validation, incident reduction, OPA parity, or production enforcement.

# SMERC And The Ref Pattern

## Purpose

SMERC benefits from a deterministic pre-execution checkpoint before recoverability scoring is allowed to influence a runtime decision.

This document uses the phrase **ref pattern** to describe that checkpoint: a non-generative, mechanical validation step that checks whether the proposed action still matches the trusted tool contract, attested runtime evidence, least-privilege boundary, and expected object shape.

The pattern is useful because high-impact agent actions should not be approved by scoring alone when basic execution facts are wrong.

## Where The Ref Pattern Fits

The practical flow is:

1. Identity and workload session are established.
2. Tool contract and allowed operation shape are loaded.
3. The proposed tool call is checked against trusted metadata.
4. SMERC evaluates recoverability, confidence, anomaly pressure, and impact.
5. SPARTa maps the posture into route controls.
6. The Decision Lifecycle Ledger records request, evidence, decision, route, execution, outcome, and learning recommendations.

In short:

`identity -> typed contract -> attestation -> least privilege -> object-shape check -> SMERC -> SPARTa -> execution or review -> DLL`

## Required Checks

The reference MCP Governance Gateway now supports four explicit ref-gate checks:

- `typed_contract_valid`: the tool call matches the expected contract.
- `attestation_valid`: the metadata comes from a trusted runtime, proxy, adapter, or reviewed record.
- `least_privilege_confirmed`: the action is inside the granted workload scope.
- `object_shape_expected`: the target object shape matches the expected class, schema, or operation boundary.

If a required check is explicitly false, SMERC fails closed. The gateway raises pressure to `1.0`, caps confidence and evidence validity, and records the failure driver in the replayable report.

## Why This Matters

Recoverability scoring is strongest after basic execution facts are trusted. A bad contract, missing attestation, privilege mismatch, or unexpected object shape is not a nuance to average away. It is a reason to stop or hold the action before it can create side effects.

This makes SMERC sharper:

- Policy engines can say whether something is permitted.
- MCP and tool registries can describe what a tool does.
- Identity systems can authenticate who or what is acting.
- SMERC can decide whether the action is recoverable enough to proceed.
- The ref pattern prevents SMERC from treating untrusted or malformed action metadata as merely another risk input.

## What SMERC Does Not Replace

This pattern does not replace:

- IAM, OAuth, mTLS, workload identity, or session issuance.
- OPA, Cedar, Rego, RBAC, ABAC, or existing policy-as-code systems.
- Type systems, JSON Schema, protobuf, OpenAPI, MCP schemas, or object validation libraries.
- Row-level security, database constraints, endpoint authorization, or secrets management.
- Prompt-injection defense, sandboxing, SIEM, SOAR, EDR, or data-loss prevention.
- Legal, compliance, financial-crime, or production certification review.

SMERC consumes trusted outputs from those systems and adds recoverability-aware runtime posture, route controls, and replay evidence.

## Reference Example

The MCP Governance Gateway example includes a repeated stablecoin treasury transfer. The request fails the ref gate because `object_shape_expected` is false. Even before commercial policy tuning, this produces a fail-closed path and makes the failure visible in the report.

Run:

```bash
python -m reference_engine.mcp_governance_gateway --mode enforce --pretty
```

Generated outputs:

- `reports/mcp_governance_gateway_report.json`
- `reports/MCP_Governance_Gateway_Report.md`

## Evidence Boundary

This is a reference implementation for technical review and shadow-mode pilot design. It is not a claim that SMERC has solved production MCP security, identity, sandboxing, financial settlement, or enterprise compliance.

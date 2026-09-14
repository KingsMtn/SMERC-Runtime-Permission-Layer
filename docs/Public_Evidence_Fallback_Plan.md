# Public Evidence Fallback Plan

## Purpose

This plan is for the case where outside reviewers do not provide 5 to 25 customer-owned metadata actions.

The fallback is not to wait forever and not to fake customer validation. The fallback is to build from public-pattern evidence with strict provenance.

For the shorter operating brief, see `docs/Known_Data_Fallback_Brief.md`.

## Rule

Use public, synthetic, generated, emulated, or benchmark-shaped evidence only when the source boundary is clear.

Do not use leaked source code, private architecture, credentials, raw logs, private prompts, customer data, confidential incidents, or copied proprietary datasets.

## Run

```bash
python -m reference_engine.public_evidence_fallback --pretty
```

Generated outputs:

- `reports/public_evidence_fallback.json`
- `reports/Public_Evidence_Fallback_Plan.md`

## What We Learned From Adjacent Projects

Strong adjacent projects did not wait for private customer telemetry. They created or curated structured metadata:

- generated task banks run across models
- synthetic action-boundary corpora
- adversarial MCP/tool-call scenarios
- deterministic local runtime states
- failure-to-correction records
- emulated network incidents and traces

The useful lesson for SMERC is the method, not a claim that their data proves SMERC.

## SMERC Fallback Evidence Labels

- `customer-owned`: supplied by an external reviewer from one real workflow
- `public-pattern`: derived from public reports, advisories, docs, or benchmark descriptions
- `synthetic`: generated examples designed to test a control boundary
- `emulated`: produced by a controlled lab or sandbox environment
- `benchmark-shaped`: representative of an upstream benchmark but not an official score
- `official-benchmark`: only when source license, version, and documented runner are used

## Next Build

Build source-specific metadata adapters in this order:

1. Agent Action Boundary Benchmark-style adapter
2. AgentShield-Bench-style adapter
3. Lakmus Agent Failures calibration mapping
4. CrossMCP-Bench authorization-condition mapping
5. Agent Reliability Lab-style state-transition evidence
6. NIKA-style infrastructure remediation mapping

The first focused adapter combines the first two source shapes:

```bash
python -m reference_engine.public_fallback_adapter --pretty
```

See `docs/Public_Fallback_Adapter.md`.

## Evidence Boundary

This path does not prove customer demand, willingness to pay, production safety, incident reduction, compliance, AWS endorsement, or acquisition value.

It proves that SMERC can map known public failure and benchmark patterns into recoverability-aware posture, route, and evidence outputs while waiting for customer-owned metadata.

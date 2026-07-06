# CISO GitHub Inspection Guide

## Purpose

This guide helps a security, platform, or AI governance reviewer inspect SMERC without needing a live founder explanation.

The question is not "is this finished enterprise software?" The correct review question is:

> Is this pilot-grade runtime permission architecture credible enough to test against our AI-agent or automation workflows?

## What To Inspect First

### 1. Plain-English Overview

File: `docs/Plain_English_Product_Overview.md`

Use this to understand the product claim, the current state, and what is deliberately not claimed.

### 2. Runtime Permission Model

Files:

- `docs/Runtime_Permission_Infrastructure.md`
- `reference_engine/recoverability_engine.py`
- `reference_engine/action_language.py`
- `specification/SMERC_Action_Language_v1.md`

Look for the core pattern:

```text
proposed action -> structured signals -> posture -> controls -> replay record
```

### 3. API And Audit Path

Files:

- `api_server.py`
- `reference_engine/audit_store.py`
- `docs/API_Deployment_Guide.md`

Review how decisions are evaluated, stored, replayed, reviewed, and measured.

### 4. Action-Bound Permit Path

Files:

- `reference_engine/authorization_permit.py`
- `docs/Action_Bound_Permit_Operations.md`
- `specification/SMERC_Action_Bound_Permit_v1.md`

Review whether authorization is bound to the exact action, policy hash, replay ID, executor audience, controls, and expiry.

### 5. GitHub Deployment Adapter

Files:

- `integrations/github_deployment/deployment_adapter.py`
- `integrations/github_deployment/README.md`
- `docs/GitHub_Deployment_Adapter_Operations.md`
- `examples/github_deployment/execution_plan.json`
- `examples/github_deployment/protected_deployment.yml`

Review the execution sequence:

```text
validate plan
authenticate and reserve permit
run required native controls
sign control evidence
consume reserved permit once
execute command with bounded environment
timeout/cancel/rollback when needed
write non-secret report
```

### 6. Test Coverage

Files:

- `tests/test_github_deployment_adapter.py`
- `tests/test_github_permit_issuer.py`
- `tests/test_authorization_permit.py`
- `tests/test_control_evidence.py`
- `tests/test_api_server.py`

Look for adversarial tests around forged permits, missing controls, failed controls, timeout, rollback, action mutation, wrong audience, and replay.

## What A Reviewer Should Expect To See

SMERC should demonstrate:

- structured action intake rather than free-form judgement
- deterministic action hashes and replay IDs
- runtime postures beyond simple allow/block
- explicit controls for constrained execution
- permit-bound execution rather than loose approvals
- audit records that can explain why an action was allowed, constrained, frozen, denied, or escalated
- honest limits around sandboxing, key management, datastore scope, and proof of business-state rollback

## What A Reviewer Should Not Expect Yet

SMERC does not yet provide:

- full enterprise federation
- managed KMS/HSM-backed key lifecycle
- multi-region replay prevention
- independent attestation of native control truth
- production runner isolation
- final compliance certification
- a complete commercial admin console
- customer-validated pricing or demand

## Pilot Decision Criteria

A CISO or platform team should consider a shadow-mode pilot if:

- AI agents or automation can trigger high-impact workflows
- existing controls are too blunt or hard to replay
- the organization wants to measure recoverability before execution
- GitHub Actions, CI/CD, infrastructure automation, or agent tool calls are in scope
- the pilot can run without blocking production at first

A team should reject or defer a pilot if:

- there are no AI-agent or automated side-effecting workflows
- existing approval and rollback controls already provide enough visibility
- the organization cannot allocate reviewer time for calibration
- the team expects a certified production security platform immediately

## Recommended First Pilot

Start with a two-to-four week shadow-mode GitHub Actions pilot:

1. Select several non-production or low-risk production workflows.
2. Run SMERC in observe mode without blocking.
3. Collect decisions, reason codes, controls, and replay records.
4. Ask reviewers to agree, disagree, or override.
5. Measure false release, false constraint, useful constraint, agreement rate, and latency.
6. Decide whether limited enforcement is justified.

The pilot succeeds only if SMERC changes the team's understanding of action risk in a measurable way.


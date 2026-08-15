# AI Agent Recoverability Governance

## Purpose

This guide explains the control gap SMERC is designed to test:

> AI-agent governance should not only ask whether an action is allowed. It should also ask whether the organization can recover if the action is wrong.

SMERC is one working implementation of that idea. This document is written for institutional reviewers who may not yet use terms like recoverability scoring, irreversible exposure, reversible capacity, SPARTa, or Decision Lifecycle Ledger.

## The Normal Control Stack

Most automated systems already have useful controls:

| Layer | Question Answered |
| --- | --- |
| Identity | Who or what is making the request? |
| Authentication | Is the actor genuine? |
| Authorization | Is the actor allowed to access this tool, API, data, or workflow? |
| Policy | Does the request violate a rule? |
| Validation | Is the request well-formed and within expected bounds? |
| Execution | Should the system perform the action now? |
| Logging | What happened? |
| Monitoring | Did something fail or look abnormal afterward? |
| Incident response | How do humans respond after harm or instability appears? |

These controls are necessary. SMERC does not replace them.

## The Missing Question

For AI agents and high-impact automation, a technically authorized action can still be unsafe to execute.

Examples:

- an agent is allowed to send email, but wants to send 10,000 external messages
- a deployment workflow is authorized, but rollback evidence is weak
- a cloud automation can change firewall rules, but blast radius is broad
- a support agent can issue refunds, but anomaly pressure is elevated
- a security agent can disable accounts, but the action may disrupt incident response
- a financial workflow can move funds, but recovery is slow and evidence is incomplete

The missing runtime question is:

> If this action is wrong, how recoverable is it?

## Recoverability Signals

A recoverability governance layer should consider:

| Signal | Meaning |
| --- | --- |
| Reversibility | Can the action be undone? |
| Rollback latency | How long would recovery take? |
| Containment strength | Can blast radius be limited? |
| Evidence validity | Is the evidence current, complete, and decision-grade? |
| Anomaly pressure | Are abnormal conditions present? |
| Impact scope | How many systems, users, accounts, dollars, or records are affected? |
| Authorization confidence | Is the action supported by the right policy, identity, and context? |
| Cancel reliability | Can the action be stopped once initiated? |

These signals do not replace policy. They add operational context before execution.

## Why Allow / Deny Is Incomplete

Binary authorization is often too coarse for AI-agent actions:

| Binary Outcome | Problem |
| --- | --- |
| Allow | May permit actions that are technically authorized but difficult to recover from. |
| Deny | May block useful automation even when a constrained or reviewed version would be safe enough. |

Middle states are useful when the organization should preserve recovery options:

| Posture | Meaning |
| --- | --- |
| `ALLOW` | Execute normally. |
| `THROTTLE` | Execute only with scope, rate, size, or blast-radius limits. |
| `FREEZE` | Pause automation until evidence or conditions improve. |
| `DENY` | Block automated execution. |
| `ESCALATE` | Route to accountable review. |

## Where SMERC Fits

SMERC fits between authorization/policy and execution:

```text
Request
  -> identity/authentication
  -> authorization/policy
  -> validation
  -> recoverability governance
  -> execution, constraint, pause, denial, or escalation
  -> ledger, replay, audit, and metrics
```

SMERC's specific implementation includes:

- recoverability scoring
- irreversible exposure score
- reversible capacity score
- runtime posture
- SPARTa route generation
- control mapping
- Decision Lifecycle Ledger records
- replay reports
- GitHub Actions shadow-mode pilot path
- external benchmark replay against ILION-Bench v2

## Institutional Review Checklist

Before allowing an AI agent or automation to execute high-impact actions, ask:

1. What is the action's worst credible consequence?
2. Can the action be reversed?
3. How long would rollback take?
4. Can the action be constrained by size, scope, rate, or environment?
5. Is evidence current and complete enough to support execution?
6. Are anomaly or instability signals present?
7. Who or what can cancel the action after it starts?
8. What will be recorded for replay and review?
9. How will human overrides be judged after the outcome is known?
10. What policy changes should be recommended, and who must approve them?

## First Pilot Pattern

The safest first pilot is shadow mode:

1. Select one GitHub Actions workflow.
2. Describe proposed actions using metadata only.
3. Run SMERC in observe mode.
4. Preserve decision artifacts.
5. Compare SMERC posture against existing reviewer judgment.
6. Measure reviewer agreement, false release candidates, false constraint candidates, useful constraint rate, override rate, unavailable evaluations, and latency.
7. Decide after 30 days whether to stop, narrow, continue observe, or move to recommendation.

Do not begin with production enforcement.

## Evidence Boundary

What exists now:

- public reference implementation
- GitHub Actions integration
- REST API and local evaluation paths
- SPARTa routing and signed evidence artifacts
- Decision Lifecycle Ledger components
- benchmark replay tooling
- passing automated tests

What is not proven yet:

- customer demand
- willingness to pay
- incident reduction
- production certification
- compliance attestation
- enterprise-specific calibration

## Summary

Recoverability governance is the discipline of deciding whether automated actions are recoverable enough to execute.

SMERC is a working implementation of that discipline, currently best tested through a GitHub Actions shadow-mode pilot.

# Recoverability Checkpoint Positioning

## The Sharper Product Wedge

SMERC should be positioned first as:

> A recoverability checkpoint before automated actions execute.

The broader category remains runtime permission infrastructure for AI agents and high-impact automation, but the commercial wedge is narrower and easier to test:

> When an automated system is about to take an action with real side effects, SMERC scores whether that action is recoverable enough to run now.

## Why This Changes The Product Story

Security, cloud, DevOps, and AI-governance teams already have many systems that detect risk, authorize identities, enforce policy, route approvals, and execute playbooks.

SMERC should not compete with those systems head-on.

SMERC adds the missing question at the action boundary:

> If this response, deployment, tool call, or workflow action is wrong, can we contain it, reverse it, explain it, and learn from it?

## Before And After

| Earlier Framing | Sharper Framing |
| --- | --- |
| AI governance platform | recoverability checkpoint for automated actions |
| AI action firewall | runtime control before irreversible side effects |
| broad agent governance | action-bound recoverability scoring |
| alternative to policy engines | complement after policy and before execution |
| framework for decision governance | insertable shadow-mode checkpoint |

## Where SMERC Fits

```text
Detection / model output / workflow trigger
  -> identity and policy checks
  -> proposed action
  -> SMERC recoverability checkpoint
  -> SPARTa route and controls
  -> execute, constrain, pause, block, or escalate
  -> replay and lifecycle evidence
```

## What SMERC Does Not Claim

SMERC does not claim to replace:

- Microsoft Sentinel, Defender, Entra, Azure, or Purview
- SOAR, SIEM, EDR, XDR, IAM, OPA, or policy-as-code
- GitHub branch protection, deployment approvals, or code review
- MCP, OAuth, AI gateways, prompt-injection defense, or model-safety systems
- compliance programs, legal judgment, or human accountability

## First Commercial Test

The first customer test should be shadow mode against one of these action streams:

- Microsoft-style security response actions
- GitHub Actions deployment or infrastructure workflows
- MCP-style agent tool calls
- security automation playbooks

The pilot should compare:

- existing workflow outcome
- proposed action
- SMERC posture
- reason codes
- required controls
- reviewer agreement
- false release risk
- false constraint rate
- latency impact

## Practical Positioning Statement

> SMERC is a recoverability checkpoint for automated actions. It sits after detection, identity, and policy, but before execution, and decides whether an action should be allowed, throttled, frozen, denied, or escalated based on recoverability and evidence.

## Evidence Boundary

The current evidence is implementation, tests, synthetic benchmark/replay data, generated reports, and public review material. The next evidence required is design-partner shadow-mode data from real workflow metadata.

# SMERC Plain-English Product Overview

## One Sentence

SMERC helps companies stop AI agents and automation from causing hard-to-reverse damage before an action executes.

## Slightly Longer

SMERC is runtime permission infrastructure for AI-agent actions. It sits between an agent, tool, workflow, or deployment system and the action that would create a real side effect.

Before the action runs, SMERC asks:

> If this action goes wrong, can the organization contain it, reverse it, explain it, and prove why it was allowed?

SMERC then returns one of five postures:

- `ALLOW`: proceed normally
- `THROTTLE`: proceed only with limits or controls
- `FREEZE`: pause because the situation is unstable or under-evidenced
- `DENY`: block the action
- `ESCALATE`: route to a higher-trust review path

## The Problem

AI agents are moving from conversation into execution. They can propose or trigger actions such as:

- editing code
- deploying software
- changing infrastructure
- deleting or exporting data
- sending external communications
- issuing refunds or transfers
- modifying security workflows

Traditional systems often ask whether an action is permitted by policy. That is necessary, but it misses a critical operational question:

> Is this action recoverable enough to let it happen now?

A technically authorized action can still be dangerous if it has a large blast radius, weak rollback path, poor evidence, or signs of abnormal pressure.

## What SMERC Does

SMERC evaluates structured information about a proposed action, including:

- action risk
- reversibility
- containment strength
- rollback latency
- evidence validity
- anomaly pressure
- impact scope
- actor and tool identity
- policy and execution context

It then produces:

- a posture decision
- scores for exposure and recoverability
- reason codes
- required controls
- a replayable audit record
- optional short-lived action-bound permits for eligible execution

## What Exists In This Repository

This repository contains working pilot-grade software, not just documents.

The current build includes:

- Python reference engines for action and recoverability evaluation
- strict action, decision, permit, evidence, execution-plan, and execution-report schemas
- a REST API service for authenticated pilot evaluation
- a SQLite pilot audit and replay store
- action-bound permits with preparation, reservation, and single-use consumption
- scoped workload principals and short-lived sessions
- GitHub Actions OIDC trust support
- signed control-evidence receipts
- a GitHub Actions gate
- a GitHub deployment adapter that validates, prepares, controls, executes, rolls back, and reports
- tests and CI coverage for critical security and execution behavior

## What This Is Not Yet

SMERC is not yet a production-certified enterprise security platform.

It is not yet:

- a hosted multi-tenant cloud service
- a complete policy-language platform with compiler and SDKs
- a certified compliance product
- a sandbox
- a replacement for IAM, CI/CD approval rules, SIEM, EDR, code review, or human security ownership
- proof that customers will buy recoverability scoring

The honest current state is:

> SMERC is a working pilot product architecture ready for technical review, CISO discussion, and controlled design-partner pilots.

## Why It May Matter

As AI agents become more capable, organizations will need controls that decide not just whether an agent can act, but whether it should act under the current conditions.

SMERC's wedge is recoverability-aware authorization:

- high-confidence, reversible actions can move faster
- risky but useful actions can be constrained instead of fully blocked
- unstable or irreversible actions can be frozen, denied, or escalated
- every decision can be replayed and reviewed later

That makes SMERC most useful at the boundary between automation and real consequences.

## First Practical Use Case

The first focused pilot is GitHub Actions and deployment governance.

In shadow mode, SMERC can score AI-assisted or automated workflow actions without blocking them. A design partner can compare SMERC's posture against existing approvals and answer:

- Did SMERC identify actions reviewers also considered risky?
- Did it constrain actions that would otherwise have been bluntly blocked?
- Did it highlight weak rollback and containment paths?
- Did it create useful audit records?
- Did it add too much friction?

If the signal is useful, the next stage is limited enforcement in non-production or narrowly scoped production workflows.


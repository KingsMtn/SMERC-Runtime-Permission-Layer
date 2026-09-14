# Linux Foundation Standards Alignment

## Purpose

Linux Foundation activity around agentic AI, runtime evidence, agent identity, and open AI security strengthens SMERC's direction.

This document records what SMERC can learn from that ecosystem without claiming Linux Foundation adoption, certification, membership, endorsement, or standards status.

## Short Answer

SMERC benefits because the open infrastructure conversation is moving toward the same missing layer:

```text
identity and discovery -> tool/action protocol -> runtime evidence -> governance record
```

SMERC should fit into that chain as:

```text
pre-execution recoverability decision -> route controls -> postcondition evidence -> replayable ledger
```

SMERC should not try to replace Linux Foundation projects. It should become easy to understand beside them.

## Signals To Learn From

### TRACE

TRACE, Trust Runtime Attestation and Compliance Evidence, points toward portable, verifiable runtime evidence for AI workloads and confidential workloads.

What SMERC learns:

- runtime evidence should be portable
- runtime evidence should be independently verifiable
- evidence should bind workload context, policy context, data classification, tool usage, and execution environment
- evidence should not depend only on the vendor operating the runtime

How SMERC should use this:

- keep SMERC postcondition evidence explicitly exportable
- keep Decision Lifecycle Ledger records digest-bound and replayable
- add a future TRACE-compatible evidence adapter path
- treat hardware attestation as stronger evidence input, not as a replacement for recoverability judgment

### Agentic AI Foundation, MCP, Goose, And AGENTS.md

The Agentic AI Foundation validates that agents, tools, instructions, and protocols need neutral open governance.

What SMERC learns:

- MCP and adjacent tool protocols make action metadata more portable
- AGENTS.md-style project guidance can become part of local execution context
- agent frameworks need common language for tool use, permissions, evidence, and review

How SMERC should use this:

- keep SMERC decisions machine-readable
- keep `smerc_beacon.json`, posture outputs, and decision-language contracts small enough for other frameworks to consume
- continue mapping MCP tool-call metadata into recoverability decisions
- avoid making SMERC depend on one agent framework

### Agent Name Service

Agent Name Service points toward identity, discovery, verification, and agent provenance.

What SMERC learns:

- identity is becoming a first-class agent infrastructure problem
- agent provenance and operational history matter
- systems will need to verify which agent is acting before deciding what it may do

How SMERC should use this:

- position SMERC after identity and discovery
- consume verified agent identity where available
- return recoverability posture for the proposed action
- record whether identity confidence changed the action decision

SMERC should say:

```text
Agent identity can tell us who is acting.
SMERC decides whether the action is recoverable enough to execute.
```

### Open Secure AI And Agent Harness Work

Open AI security work points toward better tracing, testing, auditing, and governing of AI agents.

What SMERC learns:

- security teams want traceability and control across agent harnesses
- runtime decisions need audit evidence, not only policy text
- open tools can make safety evidence easier to inspect

How SMERC should use this:

- keep reports runnable from the repository
- keep benchmark and replay examples metadata-only
- keep evidence boundaries explicit
- keep local proof independent from any private data or live production access

## SMERC Fit

SMERC complements these standards by focusing on a narrower question:

```text
Even if the agent is known, the tool call is valid, and the actor is authorized,
is the proposed action recoverable, bounded, observable, and safe enough to execute now?
```

The best standards-aligned SMERC path is:

1. Accept identity, protocol, policy, runtime, and evidence signals from open ecosystems.
2. Calculate recoverability and route posture before execution.
3. Emit a machine-readable posture and required controls.
4. Verify postcondition evidence after the decision.
5. Preserve a replayable decision ledger for review.

## What To Build Next

Near-term:

- document `smerc.trace_evidence_adapter.v0` as a future adapter boundary
- add TRACE, ANS, MCP, AGENTS.md, and AAIF terms to the AI-readable reviewer bundle
- keep AWS, MCP, GitHub Actions, and cloud-admin examples framed as metadata-only proof

Medium-term:

- add a sample evidence envelope showing how SMERC could ingest attested runtime evidence
- add a sample agent identity field group that can later map to ANS-style identity or other agent identity systems
- add a standards alignment section to the reviewer quickstart

Do not do yet:

- claim Linux Foundation affiliation
- claim TRACE compatibility
- claim ANS compatibility
- claim AAIF participation
- claim MCP conformance beyond the existing local metadata examples and tests
- imply that SMERC is a standard

## Reviewer Language

Use this language:

```text
SMERC is standards-adjacent, not standards-approved. It is designed to complement emerging agent identity, tool protocol, and runtime evidence work by adding a pre-execution recoverability decision and postcondition evidence loop.
```

Avoid this language:

```text
SMERC is a Linux Foundation standard.
SMERC is TRACE-compatible.
SMERC is ANS-certified.
SMERC is adopted by AAIF.
```

## Work / Result / Impact

Work:

Map Linux Foundation agentic AI and runtime-evidence signals into SMERC's current proof path.

Result:

SMERC has clearer standards-adjacent language for TRACE-style runtime evidence, MCP and AGENTS.md-style agent context, Agent Name Service-style identity, and open secure AI governance.

Impact:

Reviewers can understand SMERC as a recoverability layer that complements open agent infrastructure instead of competing with identity, tool protocol, or attestation standards.

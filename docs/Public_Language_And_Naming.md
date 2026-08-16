# Public Language And Naming

SMERC should lead with familiar buyer and reviewer language.

Do not use internal layer names as the public front door.

## Public Front Door

Use these phrases first:

- recoverability-aware runtime permission infrastructure
- recoverability-aware permission checks before automated actions execute
- cloud automation guardrails
- MCP tool-call governance
- GitHub Actions shadow-mode pilot
- AI agent action governance
- blast-radius reduction for automated actions
- replayable decision evidence

## Architecture Explanation

After the reader understands the product, explain the internal flow:

```text
signal and evidence intake
  -> recoverability decision
  -> execution routing and controls
  -> decision lifecycle evidence
```

Then name the reference layers:

- SPARK is the signal and evidence intake path.
- SMERC is the recoverability decision engine.
- SPARTa is the execution-routing and control-translation path.
- DLL is the Decision Lifecycle Ledger.

## Preferred One-Liner

SMERC is recoverability-aware runtime permission infrastructure for AI agents, MCP tool calls, GitHub Actions, cloud automation, and high-impact workflows.

## Avoid As First-Touch Language

Avoid leading with:

- SPARK
- SPARTa
- DLL
- macro language model
- proprietary internal acronyms

These terms are useful in technical documentation, but they require explanation and should not be the first thing a CISO, platform engineer, cloud engineer, or AI governance reviewer sees.

## How To Phrase Internal Layers

Use:

> The reference implementation calls this signal intake path SPARK.

Instead of:

> SPARK ingests signals.

Use:

> The execution-routing layer maps a posture into tool behavior. In the reference implementation, that layer is called SPARTa.

Instead of:

> SPARTa routes posture.

## Evidence Boundary

Clear language improves discovery and review. It does not prove buyer demand, production readiness, legal protectability, incident reduction, or customer value without pilot evidence.

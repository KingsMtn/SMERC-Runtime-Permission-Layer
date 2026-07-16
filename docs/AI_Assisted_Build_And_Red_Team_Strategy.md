# AI-Assisted Build And Red-Team Strategy

## Purpose

SMERC can use AI systems to accelerate engineering, critique, and pilot simulation, but AI systems should not be treated as proof that SMERC is commercially valid, legally protectable, secure, or production-ready.

This document defines how AI tools can help the project while preserving human accountability and external-review discipline.

## Recommended Tool Roles

| Tool category | Best use | Not sufficient for |
| --- | --- | --- |
| Primary coding agent | Implement repository changes, tests, docs, SDKs, API paths, pilot tools, and integration examples. | Security certification, customer validation, legal review. |
| Second-opinion coding agent | Review architecture, identify unclear abstractions, inspect tests, challenge claims, and propose refactors. | Final technical approval. |
| GitHub-native coding agent | Simulate code and workflow changes that SMERC can score inside GitHub Actions. | Proving SMERC works for all agent platforms. |
| Long-running software agent | Simulate larger refactors, multi-file changes, migration tasks, and repeated engineering workflows. | Buyer demand or enterprise trust. |
| General reasoning model | Draft interview questions, competitive critique, positioning, and review checklists. | Patentability, legal opinion, customer intent, production readiness. |
| Human expert | Validate security, architecture, legal, customer discovery, procurement, and deployment risk. | Fully automated scaling of routine repo work. |

## Practical Operating Model

Use AI systems in four lanes:

1. Build acceleration

The primary coding agent can continue building SMERC's reference implementation, tests, documentation, pilot tooling, and public review materials.

2. Red-team review

A second AI agent can inspect a branch or pull request and answer:

- What is unclear?
- What is overclaimed?
- What breaks under a realistic customer pilot?
- What would a CISO reject?
- What tests are missing?
- What security assumptions are weak?

3. Agent-under-governance simulation

GitHub-native or long-running coding agents can act as the proposed action source. They generate workflow changes, deployment changes, code edits, or infrastructure tasks. SMERC then scores those proposed actions before execution or in shadow mode.

4. Human validation

Humans still decide whether the outputs are useful, whether the claims are acceptable, whether a pilot should continue, and whether enforcement is appropriate.

## Red-Team Prompts For A Second AI Reviewer

Use prompts like:

```text
Review this SMERC branch as a skeptical CISO and platform-security architect.
Focus on production-readiness gaps, overclaims, unclear threat boundaries,
weak tests, missing integration steps, and reasons a buyer would reject it.
Do not praise the project unless the evidence supports it.
```

```text
Review the SMERC pilot package as if your company might run a 30-day
GitHub Actions shadow-mode pilot. Identify every ambiguity that would
slow approval, confuse reviewers, or create security concerns.
```

```text
Review the SMERC runtime engine and scoring rules. Identify where the
math is under-justified, where thresholds may be arbitrary, and what
customer data would be required before enforcement.
```

## Agent Simulation Prompts

Use coding agents or GitHub-native agents to propose realistic actions:

```text
Create a pull request that modifies a production deployment workflow.
Do not merge it. Produce a structured action metadata file that SMERC
can evaluate in observe mode.
```

```text
Propose a database migration workflow change with rollback assumptions,
impact scope, containment strength, and rollback latency. Generate only
metadata suitable for SMERC review; do not include secrets or customer data.
```

```text
Simulate an AI coding agent trying to update authentication middleware.
Generate a SMERC action request, expected existing policy outcome, and
the evidence a human reviewer would need.
```

## Evidence Rules

AI-generated critique is useful, but it should be labeled as AI-assisted review.

AI-generated scenarios are useful, but they are synthetic evidence.

AI-generated reviewer labels are drafts only. Human reviewers must approve final labels for:

- agreement
- override
- false release candidate
- false constraint candidate
- useful constraint
- go/no-go recommendation

## Where This Helps Most

AI assistance is most useful for:

- expanding scenario coverage
- finding documentation confusion
- generating integration test cases
- producing adversarial action examples
- identifying obvious overclaims
- creating pilot setup checklists
- simulating agent proposals for SMERC to score

AI assistance is least sufficient for:

- buyer willingness to pay
- customer trust
- security assurance
- legal/patent strategy
- production deployment approval
- proof of incident reduction

## Commercial Position

SMERC should not claim that multiple AI systems validated the product.

The stronger claim is:

> SMERC can govern AI-generated actions, and AI systems can help generate test cases, but customer humans remain responsible for validating whether the governance signal is useful.

## Next Build Implication

The next useful product step is to make AI-agent simulation easier:

- add sample action requests from different agent types
- run them through SMERC in batch
- summarize posture differences
- require human review labels before calling any result pilot evidence


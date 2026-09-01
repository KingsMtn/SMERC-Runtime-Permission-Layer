# Accelerator Readiness Track

## Purpose

This document defines when SMERC should move from technical review to accelerator applications or investor-facing submissions.

The immediate goal is not to apply everywhere. The goal is to make the project credible enough that a cyber accelerator, design partner, or security investor can quickly understand:

- what has been built
- what problem it addresses
- what evidence exists
- what remains unproven
- what a first pilot would measure

## Current Position

SMERC is pre-execution recoverability control for AI-agent actions. The reference implementation is recoverability-aware runtime permission infrastructure. The first wedge is GitHub Actions and AI-assisted pull request governance.

The current repository can demonstrate:

- recoverability-aware action scoring
- replayable posture decisions
- GitHub PR Guardian review output
- SPARTa route generation
- action-bound permits
- control-evidence receipts
- Decision Lifecycle Ledger records
- DLL Intelligence summaries
- runtime contract discovery
- synthetic benchmark and replay evidence
- local latency and overhead reporting

This is enough for technical review and shadow-mode pilot discussion.

It is not yet enough to claim customer-proven risk reduction, production certification, or repeatable sales demand.

## Best Accelerator Lane

The strongest accelerator lane is cybersecurity and enterprise infrastructure, not a general consumer startup track.

SMERC should be positioned as:

> Pre-execution recoverability control for AI-agent actions, implemented as recoverability-aware runtime permission infrastructure.

The most relevant accelerator target is a cybersecurity-focused program such as MACH37 because the first buyer is likely a CISO, security architect, or platform security leader reviewing AI-agent blast-radius risk.

YC remains useful if the application can show strong founder execution and early pull from users. However, a cyber-focused accelerator may provide more direct access to CISOs, security mentors, and design partners.

## When To Raise MACH37

Bring up a MACH37 application when at least four of the following six conditions are true:

1. The public repository has a clear external-review path and passing tests.
2. A nontechnical reviewer can explain SMERC in one minute without founder coaching.
3. At least one external reviewer has inspected the GitHub Actions / PR Guardian path.
4. At least one design-partner candidate has said the GitHub Actions shadow-mode pilot is relevant.
5. The benchmark and fake-customer reports are easy to find from the README.
6. The first-pilot package can be sent without additional explanation.

If fewer than four are true, the next step is product proof, not an accelerator application.

## Evidence To Collect Before Applying

Use real evidence only. Do not convert internal analysis into market proof.

| Evidence | Minimum Useful Proof | Why It Matters |
| --- | --- | --- |
| Reviewer feedback | 2 written comments from security, platform, or AI-governance reviewers | Shows the problem is understandable outside the founder's head. |
| Pilot fit | 1 organization willing to discuss a GitHub Actions shadow-mode pilot | Shows the wedge is plausible. |
| Action samples | 25 to 50 realistic customer-context actions scored through SMERC | Shows the engine can handle real workflow language and metadata. |
| Reviewer agreement | Human labels compared with SMERC posture output | Shows whether the decision logic is credible. |
| Latency/overhead | Local and pilot-environment timing results | Shows whether insertion into a workflow is operationally tolerable. |
| Buying signal | Direct answer on whether this is budget-worthy, pilot-worthy, or only interesting | Separates curiosity from commercial demand. |

## Accelerator Narrative

The strongest narrative is:

1. AI agents are gaining tool access faster than enterprises can review every action.
2. Existing controls are good at identity, policy, content filtering, and audit logs, but many do not explicitly score recoverability before action execution.
3. SMERC evaluates whether a proposed action can be safely released, constrained, paused, blocked, or escalated.
4. The first product is a GitHub Actions / PR Guardian pilot that scores AI-assisted code, deployment, and infrastructure workflows in shadow mode.
5. The proof question is not whether SMERC sounds useful. The proof question is whether recoverability-weighted posture decisions improve reviewer agreement, reduce irreversible exposure, and preserve audit evidence without adding unacceptable friction.

## Application Boundary

Do not claim:

- production-certified security platform
- proven incident reduction
- CISO-validated demand
- patentable novelty as fact
- replacement for OPA, IAM, SIEM, GRC, AI gateways, or approval workflows

It is acceptable to claim:

- working reference implementation
- public technical review repository
- pilot-ready GitHub Actions shadow-mode path
- recoverability-aware scoring model
- replayable decision evidence
- clear evidence gaps

## Next Build Priority

Before any accelerator application, the highest-value build priority is a single reviewer path:

```text
Open README
Run one command
See PR Guardian decision
See SPARTa route
See DLL record
See benchmark comparison
See pilot package
Know what to test next
```

That path is what converts SMERC from an impressive repository into something a busy security reviewer can actually evaluate.

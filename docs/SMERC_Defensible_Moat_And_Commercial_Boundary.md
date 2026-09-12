# SMERC Defensible Moat And Commercial Boundary

## Purpose

This note separates what is public-reviewable from what makes SMERC strategically defensible.

SMERC should be useful enough for reviewers to inspect, run, critique, and improve. It should also be clear that production deployment, commercial embedding, hosted use, resale, or integration into a revenue-generating platform requires separate written permission.

## Defensible Moat

SMERC's value is not secrecy alone.

The defensible part is the control pattern and evidence structure:

- recoverability-before-execution scoring
- hard evidence gates before runtime scoring
- posture routing across `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, and `ESCALATE`
- Governance Routing Workbench controls
- Decision Lifecycle Ledger evidence
- postcondition proof that required route controls happened
- autonomy budgeting and earned autonomy logic
- customer-owned metadata review path
- AWS-style and financial-action profiles
- work / result / impact reporting that makes reviewer judgment easier

## Open Source Dependency Posture

Before any serious strategic, acquisition, or commercial discussion, SMERC should maintain:

- dependency list
- license list
- files that are original project work
- files adapted from public standards or examples
- tests proving the public examples run locally
- commercial-use boundary in `COMMERCIAL_USE.md` and license materials

## Acquisition-Relevant Framing

Do not say:

> This is proprietary because nobody else can copy the code.

Say:

> SMERC's defensibility is the recoverability-before-execution control model, the posture-routing vocabulary, the evidence replay structure, and the growing set of domain profiles that make authorized but risky actions reviewable before side effects occur.

## Commercial Boundary

Public review, research, non-production evaluation, and metadata-only pilot testing are governed by the public review license and commercial-use notice.

Production deployment, commercial embedding, hosted use, resale, revenue-generating use, or integration into a commercial product, internal enterprise platform, cloud service, agent framework, financial workflow, security product, or managed service requires a separate written commercial license or agreement.

Commercial discussions should also preserve field-of-use clarity. AWS/cloud action governance is one implementation package, not the whole SMERC platform. See `docs/SMERC_Field_Of_Use_Strategy.md`.

## Work / Result / Impact

Work:

Keep the project inspectable while documenting the recoverability control pattern, evidence model, and commercial-use boundary.

Result:

Reviewers can test the project without confusion about what is free to inspect versus what requires a commercial agreement.

Impact:

SMERC becomes safer to share publicly while preserving acquisition, licensing, and strategic-partner optionality.

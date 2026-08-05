# YC Application Evidence Draft

This draft is for a future YC application. It should be updated only with real evidence as it arrives.

## Company One-Liner

SMERC is recoverability-aware runtime permission infrastructure for AI-agent actions, starting with GitHub PR Guardian for AI-assisted pull requests.

## What Are You Building?

AI agents are starting to make code, deployment, data, and workflow changes faster than human teams can review their consequences.

Most systems ask whether an actor is allowed or whether a policy passes. SMERC asks a second runtime question:

> If this action is wrong, can the organization recover?

The first product is GitHub PR Guardian. It runs in or alongside GitHub Actions and comments on AI-assisted pull requests with:

- posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- risk and confidence scores
- required controls
- reason codes
- replay ID
- certificate digest
- SPARTa route
- Decision Lifecycle Ledger evidence
- latency and operational-overhead measurements

## Who Needs This?

Initial buyer:

- CISO or security leader responsible for AI-agent governance

Initial users:

- security architects
- platform engineering leaders
- DevSecOps teams
- AI governance teams
- teams adopting coding agents or deployment automation

## What Is The First Narrow Use Case?

AI-assisted pull requests that touch production-facing code, deployment workflows, authentication, permissions, secrets, infrastructure, or data handling.

The product is useful before enforcement. In shadow mode, it lets teams compare SMERC's posture against human reviewer judgment without blocking production workflows.

## Why Now?

AI coding agents and workflow agents are moving closer to systems that create real side effects. Existing controls are necessary, but they often do not score recoverability before action. A technically authorized action may still be operationally dangerous if rollback is slow, containment is weak, evidence is incomplete, or impact scope is high.

## What Exists Now?

- Runtime scoring engine
- GitHub Actions integration path
- GitHub PR Guardian comment and certificate
- SPARTa route layer
- SPARTa machine vocabulary
- Runtime Contract Index
- Decision Lifecycle Ledger
- DLL Intelligence
- latency and operational-overhead report
- Python test suite
- public GitHub repository
- public Netlify review site

## What Still Needs Validation?

- whether CISOs care enough about recoverability scoring to buy
- whether platform teams will insert SMERC into workflow review
- reviewer agreement in real customer workflows
- false release and false constraint rates
- GitHub Actions latency overhead in live workflow conditions
- willingness to pay for a 90-day pilot

## Evidence Slots To Fill Before Submission

Do not invent these. Fill them only when real evidence exists.

| Evidence | Current Status | Update When Real |
|---|---|---|
| Security/platform conversations | pending | count and summary |
| Design-partner candidates | pending | names only if approved |
| Customer-context scored actions | pending | count |
| Reviewer agreement | pending | rate and denominator |
| GitHub workflow overhead | local only | median, p95, max |
| Willingness to pay | pending | pilot price discussion |

## Safe Founder Explanation

SMERC does not replace existing security tools. It sits beside them as a runtime permission layer focused on recoverability.

OPA, IAM, AI gateways, code review, and approval systems are still necessary. SMERC adds a specific missing question: whether the proposed action can be recovered, constrained, paused, blocked, or escalated before it creates unacceptable side effects.

## What Changed Since The Missed Deadline?

Use this section only after new evidence exists.

Good examples:

- "We spoke with 8 security and platform reviewers."
- "The strongest objection was integration friction, so we narrowed the first pilot to GitHub PR comments in observe mode."
- "Reviewers preferred seeing a PR comment over a separate dashboard."
- "The pilot metric they cared about most was reviewer agreement, not raw risk score."

## Boundary

This draft should stay evidence-based. Do not turn roadmap, synthetic reports, or AI-generated analysis into claims of market proof.

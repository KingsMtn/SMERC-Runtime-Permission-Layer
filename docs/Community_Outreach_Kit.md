# SMERC Community Outreach Kit

This kit gives consistent language for inviting technical review without overclaiming.

## Short Description

SMERC is runtime permission infrastructure for AI-agent and automation actions. It evaluates whether an action is recoverable enough to allow, throttle, freeze, deny, or escalate before execution.

## Community Post

We are building SMERC, a runtime permission layer for AI agents and high-stakes automation.

Most systems ask whether an actor is allowed to do something. SMERC asks a second question before execution:

> If this automated action is wrong, how recoverable is it?

The public repo includes:

- recoverability-aware decision engine
- REST API
- replay and audit store
- GitHub Actions integration
- GitHub deployment adapter
- Python and JavaScript SDKs
- starter policy language
- proxy incident-replay benchmark
- pilot review metrics

We are looking for:

- security architects
- CISOs and AI governance leads
- platform engineers
- DevSecOps teams
- agent-framework builders
- researchers interested in runtime governance

The current evidence is intentionally labeled: proxy evidence and pilot readiness, not production validation. We are especially interested in feedback on scenarios where an action is technically authorized but difficult to undo.

GitHub:
`https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer`

## Direct Message To A Potential Technical Reviewer

I am working on SMERC, a runtime permission layer for AI-agent and automation actions.

The core idea is recoverability-weighted authorization: before an agent sends an email, deploys code, deletes data, changes cloud infrastructure, or triggers a workflow, SMERC asks whether the action can be safely recovered if it is wrong.

The repo now has a working engine, API, SDKs, GitHub integration, replay/audit path, and a proxy incident-replay benchmark.

I would value a skeptical technical review, especially around:

- whether the recoverability signals are useful
- whether the GitHub Actions shadow-mode pilot is realistic
- where this overlaps with existing policy tools
- what would block adoption in a real security review

Repo:
`https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer`

## Design Partner Note

SMERC may be a fit if your team is evaluating AI-agent governance, AI coding agents, deployment automation, or internal automation that can create real side effects.

The recommended first pilot is shadow mode. SMERC scores actions, records replayable decisions, and compares posture with reviewer judgment without blocking production.

The goal is to answer a narrow question:

> Does recoverability scoring identify risky automated actions in a way reviewers find useful?

## Language To Avoid

Avoid saying:

- "SMERC solves AI safety."
- "SMERC replaces OPA/IAM/SIEM."
- "SMERC prevents incidents."
- "SMERC is proven in production."
- "SMERC is the only AI firewall."

Use instead:

- "SMERC adds a recoverability-weighted permission layer."
- "SMERC complements existing controls."
- "SMERC is ready for technical review and shadow-mode pilots."
- "The current benchmark is proxy evidence, not production validation."

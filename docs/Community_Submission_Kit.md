# Community Submission Kit

This kit gives SMERC a consistent public voice when asking for feedback in technical communities.

The goal is not to advertise a finished security product. The goal is to invite useful critique, design-partner interest, and integration feedback from people who understand AI-agent execution, platform automation, cloud workflows, security operations, and governance.

## Primary Links

- Public review page: `https://admirable-sorbet-9986d5.netlify.app/community.html`
- CISO overview: `https://admirable-sorbet-9986d5.netlify.app/ciso.html`
- GitHub Actions pilot: `https://admirable-sorbet-9986d5.netlify.app/github-action.html`
- Repository: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer`
- Public review issue: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/issues/new?template=public_review_feedback.md`

## One-Sentence Description

SMERC is runtime permission infrastructure for AI-agent and automation actions, evaluating whether a technically authorized action is recoverable enough to execute now.

## Short Description

SMERC sits between AI-agent/tool output and real-world execution. Before an agent edits code, deploys infrastructure, sends messages, deletes data, moves money, or triggers a workflow, SMERC scores recoverability signals and returns `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`.

The project is pilot-grade. It is seeking critique on whether recoverability scoring fills a real gap in AI-agent governance.

## Microsoft Tech Community Draft

Title:

```text
Looking for feedback: recoverability-aware runtime permission layer for AI-agent actions
```

Body:

```text
I am looking for technical feedback on SMERC, a runtime permission layer for AI-agent and automation actions.

SMERC sits between model/tool output and real-world execution. Before an AI agent edits code, deploys infrastructure, sends messages, deletes data, or triggers a workflow, SMERC evaluates recoverability signals and returns ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE.

The specific question is not only whether the actor is allowed in a traditional IAM or policy sense. The question is whether the proposed action is recoverable enough to execute now.

I am especially interested in feedback from CISOs, security architects, platform engineers, DevSecOps teams, AI governance teams, Azure/Microsoft ecosystem builders, and agent-framework developers.

Useful critique:
- Is recoverability scoring a real gap in current AI-agent governance?
- Where would this fit or fail in existing approval workflows?
- Would GitHub Actions, Azure DevOps, Copilot Studio, or internal automation be a credible first shadow-mode pilot?
- What evidence would you need before taking this seriously?

Public review page:
https://admirable-sorbet-9986d5.netlify.app/community.html

GitHub repo:
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer
```

## GitHub Community Draft

Title:

```text
Feedback requested: runtime permission layer for AI-agent actions
```

Body:

```text
I am looking for open-source and developer feedback on SMERC, a runtime permission layer for AI-agent and automation actions.

SMERC evaluates whether a proposed action is recoverable enough to execute, then returns ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE.

The working repository includes a Python reference engine, REST API, SDKs, audit/replay path, GitHub Actions pilot materials, action-bound permits, signed control evidence, domain profiles, and tests.

The project is not claiming production certification. I am looking for critique on the core mechanism and pilot path.

Repo:
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer

Public review page:
https://admirable-sorbet-9986d5.netlify.app/community.html
```

## LinkedIn Draft

```text
I am looking for feedback from CISOs, security architects, platform engineers, DevSecOps teams, and AI governance leaders.

SMERC is runtime permission infrastructure for AI-agent actions. It evaluates whether a technically authorized action is recoverable enough to execute now.

The premise is simple: in agentic systems, "allowed" is not the same as "safe to execute." Some actions can be reversed quickly. Others create irreversible exposure.

SMERC returns ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE before actions such as code changes, deployments, customer messages, data deletion, tool calls, or infrastructure workflows execute.

I am not asking people to accept a finished product claim. I am asking for critique:
- Is recoverability scoring a real gap?
- Where would this fit or fail?
- What evidence would make a shadow-mode pilot credible?

Public review page:
https://admirable-sorbet-9986d5.netlify.app/community.html
```

## Hacker News Draft

Title:

```text
Show HN: SMERC, recoverability-aware permission layer for AI-agent actions
```

Body:

```text
I built SMERC as a runtime permission layer for AI-agent and automation actions.

The idea is to evaluate not just whether an action is allowed, but whether it is recoverable enough to execute now. The engine returns ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE based on signals such as reversibility, containment, rollback latency, evidence validity, anomaly pressure, and impact scope.

Current repo includes a Python reference engine, REST API, SDKs, audit/replay mechanics, GitHub Actions pilot materials, action-bound permits, signed control evidence, domain profiles, and tests.

This is pilot-grade, not production-certified. I am looking for technical criticism, especially around whether recoverability scoring is useful or already solved by existing systems.

Repo: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer
Public review page: https://admirable-sorbet-9986d5.netlify.app/community.html
```

## Product Hunt Draft

Tagline:

```text
Runtime permission infrastructure for AI-agent actions
```

Description:

```text
SMERC evaluates whether AI-agent and automation actions are recoverable enough to execute before they create real-world side effects. It returns ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE based on reversibility, containment, rollback latency, evidence validity, anomaly pressure, and impact scope.

The first pilot path is GitHub Actions shadow-mode scoring for AI-assisted code, deployment, and infrastructure workflows.
```

First comment:

```text
SMERC is intentionally presented as pilot-grade infrastructure, not a production-certified security platform.

The core question is whether recoverability scoring helps security and platform teams govern AI-agent actions better than simple allow/deny controls.

I am looking for feedback from CISOs, platform engineers, DevSecOps teams, AI governance leaders, and agent-framework builders.
```

## Posting Guidance

- Ask for critique, not praise.
- Lead with the recoverability question.
- Do not claim incident reduction without live pilot evidence.
- Do not claim SMERC replaces IAM, OPA, AI gateways, SIEM, EDR, approval systems, or policy engines.
- Do not post secrets, customer data, confidential incidents, private prompts, or non-public architecture details.
- Use the public review page first when a community does not allow direct GitHub issue links.

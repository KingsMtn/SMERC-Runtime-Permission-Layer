# Public Review And Feedback

SMERC is looking for practical critique from people who work near AI-agent execution, cloud automation, CI/CD, security operations, platform engineering, and AI governance.

The project is not asking reviewers to accept a broad claim. It is asking reviewers to test a narrower question:

> When an automated action is technically authorized, is it recoverable enough to execute now?

## Best Places To Start

- CISO overview: `https://admirable-sorbet-9986d5.netlify.app/ciso.html`
- GitHub Actions pilot: `https://admirable-sorbet-9986d5.netlify.app/github-action.html`
- Public feedback page: `https://admirable-sorbet-9986d5.netlify.app/community.html`
- Repository: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer`
- Community guide: `COMMUNITY.md`
- Community submission kit: `docs/Community_Submission_Kit.md`
- Technical quickstart: `docs/Developer_Quickstart.md`
- Engine trace guide: `docs/Engine_Profile_And_Trace.md`

## Review Questions

Useful public feedback usually answers one or more of these:

- Is recoverability scoring a real gap in current AI-agent governance?
- Where would this decision need to happen in your workflow?
- Which actions should be constrained instead of fully blocked?
- Which signals are missing from the current model?
- Which default thresholds or domain profiles look wrong?
- What evidence would make a shadow-mode pilot credible?
- What would stop your organization from evaluating this?

## Good Feedback Formats

Use GitHub Issues for specific, testable feedback:

- `CISO review feedback: [area]`
- `Scenario contribution: [category]`
- `Integration idea: [tool/platform]`
- `Research review: [metric or benchmark]`
- `Security review: [risk or control]`

Examples:

- "This deployment scenario should be `FREEZE`, not `THROTTLE`, because rollback requires database restoration."
- "This signal is missing: downstream workflow count should increase impact scope."
- "The decision should happen before tool-call dispatch, not after a CI job starts."
- "This is useful for shadow mode, but we would reject enforcement until tenant isolation and key management are hardened."

## Public Post Draft

Use this when asking for community critique:

```text
I am looking for technical feedback on SMERC, a runtime permission layer for AI-agent and automation actions.

SMERC sits between model/tool output and real-world execution. Before an AI agent edits code, deploys infrastructure, sends messages, deletes data, or triggers a workflow, SMERC evaluates recoverability signals and returns ALLOW, THROTTLE, FREEZE, DENY, or ESCALATE.

The specific question is not whether the actor is allowed in a traditional IAM sense. The question is whether the proposed action is recoverable enough to execute now.

I am especially looking for critique from CISOs, security architects, platform engineers, AI governance teams, Azure/Microsoft ecosystem builders, and agent-framework developers.

Useful feedback:
- Is recoverability scoring a real gap?
- Where would this fit or fail in existing approval workflows?
- What evidence would be needed before a shadow-mode pilot?
- Which scenarios should be constrained instead of blocked?

CISO overview: https://admirable-sorbet-9986d5.netlify.app/ciso.html
GitHub repo: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer
```

## Safety Boundaries

Do not post secrets, customer data, regulated data, private incident details, private prompts, or non-public architecture diagrams in public issues.

SMERC is pilot-grade software. It is not production-certified, not a replacement for IAM or policy engines, and not proven to reduce incidents without live design-partner evidence.

# Potential Company Value

## Short Answer

SMERC is designed to help companies safely use more automation by scoring whether high-impact actions are recoverable before they execute.

The current project does not claim proven incident reduction. That claim requires design-partner shadow-mode data and later production evidence.

## Where The Value Could Appear

| Potential Value | Why It Matters | Evidence Needed |
| --- | --- | --- |
| reduced blast radius | automated actions can isolate systems, revoke access, change infrastructure, move data, or affect customers | pilot records showing SMERC identified high-exposure actions reviewers agreed should be constrained, frozen, denied, or escalated |
| safer automation adoption | teams can use `THROTTLE`, `FREEZE`, and `ESCALATE` instead of blunt allow/deny choices | reviewer agreement and false constraint analysis |
| better audit and replay evidence | teams can preserve why an action was allowed, constrained, blocked, or escalated | Decision Lifecycle Ledger records from customer workflow metadata |
| improved security response control | response tools may detect correctly but still execute actions with business side effects | shadow-mode replay against security response actions |
| clearer AI-agent governance | agents can be technically authorized but still need action-level recoverability checks | MCP or agent tool-call pilot evidence |
| workflow learning | outcomes can show which policies, overrides, and controls improved or worsened results | reviewed outcome records, not automatic retraining |

## Company Buyers Who May Care

- CISOs evaluating automation blast radius
- security architects designing AI-agent and response guardrails
- platform engineering leaders managing CI/CD and cloud automation
- DevSecOps teams reviewing AI-assisted code and deployment actions
- SOC automation leaders expanding playbook execution
- AI governance leaders trying to control tool-using agents

## What To Say Publicly

Use:

> SMERC is designed to help companies reduce the blast radius of automated actions by scoring recoverability before execution.

Use:

> SMERC could help teams increase automation safely by adding constrained, frozen, denied, or escalated postures between allow and block.

Use:

> SMERC creates replayable evidence that can support review, audit, and policy improvement during a pilot.

Do not use:

- SMERC reduces incidents.
- SMERC prevents outages.
- SMERC saves companies millions.
- SMERC is better than Microsoft, OPA, Sentinel, SOAR, SIEM, or IAM.
- SMERC is production-certified.

## Commercial Interpretation

The likely early commercial value is pilot value, not yet platform value. A buyer would pay to learn whether recoverability scoring catches risky automated actions that existing workflows either allow too easily or block too bluntly.

The step from pilot value to enterprise value requires:

- real customer metadata,
- reviewer agreement,
- low false release risk,
- acceptable latency,
- evidence that SMERC outputs are understandable,
- at least one workflow owner who wants to keep running it.

## Evidence Boundary

Current SMERC evidence includes implementation, tests, synthetic benchmarks, Microsoft-style replay data, generated reports, and public review materials. It does not yet include live customer risk reduction, audited compliance evidence, or production incident outcomes.

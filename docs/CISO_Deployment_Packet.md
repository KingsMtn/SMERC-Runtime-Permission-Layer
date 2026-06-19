# SMERC CISO Deployment Packet

## Executive Positioning

SMERC is runtime permission infrastructure for AI-agent actions. It sits between agents and high-impact tools, scoring whether a proposed action should be allowed, throttled, frozen, denied, or escalated before execution.

The first deployment target is deliberately narrow:

> A 90-day GitHub Actions shadow-mode pilot for AI-assisted code, deployment, and infrastructure workflows.

## Why A CISO Should Care

AI agents and automated workflows increasingly operate near privileged systems. The security problem is not only whether a user or agent has permission. It is whether a proposed action is recoverable, appropriately constrained, and safe to execute under uncertainty.

SMERC focuses on the action boundary:

```text
agent proposes action -> SMERC scores runtime posture -> workflow executes, constrains, pauses, denies, or escalates
```

## Recommended Initial Scope

Use SMERC only for workflows where automation can create meaningful operational side effects:

- AI-assisted code changes
- infrastructure-as-code changes
- production deployment steps
- privileged GitHub Actions workflows
- workflow dispatch events triggered by agents or automation
- high-impact pull requests affecting infrastructure, auth, secrets, data movement, or deployment configuration

Avoid first-pilot use on:

- safety-critical systems
- regulated production approvals
- financial transfers
- live customer data actions
- workflows where blocking behavior has not been approved

## Deployment Modes

| Mode | Behavior | CISO Use |
| --- | --- | --- |
| `observe` | Score and report only. Never block. | Baseline decision quality and noise. |
| `recommend` | Surface posture, reason codes, and constraints. | Compare against reviewer judgment. |
| `enforce` | Fail or route selected postures. | Use only after calibration and approval. |

Recommended start: `observe`.

## What SMERC Evaluates

The GitHub Actions pilot evaluates structured action metadata, not raw secrets or full source code:

- action identity
- tool or workflow
- actor or agent
- confidence
- harm potential
- consent or authorization support
- reversibility
- external side effects
- sensitive-data involvement
- optional context

## What SMERC Outputs

- posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- risk score
- confidence score
- reason codes
- recommended constraints
- replay ID
- JSON decision report
- GitHub step summary

## Data Handling Position

For the first pilot, SMERC should receive action metadata rather than sensitive payloads.

SMERC should not require:

- production secrets
- customer PII
- private model prompts
- raw credentials
- full repository contents
- privileged cloud credentials

Decision reports should be stored as workflow artifacts or routed to existing security-review tooling according to the customer's retention policy.

## Failure And Safety Defaults

Shadow-mode default:

- never block
- write a replayable decision record
- compare against existing reviewer behavior

Recommend-mode default:

- do not block
- flag `FREEZE`, `DENY`, and `ESCALATE` for review
- measure reviewer agreement

Enforce-mode default after approval:

- fail on `DENY` and `FREEZE`
- route `ESCALATE` to accountable human review
- continue to log all decisions

## Pilot Success Metrics

Measure:

- reviewer agreement rate
- false release rate
- false throttle/freeze/deny rate
- override rate
- approval latency impact
- percentage of high-impact actions receiving useful constraints
- number of replay records reviewed
- number of existing workflow improvements discovered

## CISO Objections And Direct Answers

### Is this replacing OPA, IAM, branch protection, or code review?

No. SMERC is an action-boundary scoring and posture layer. It should complement existing controls.

### Is this a prompt-injection firewall?

No. Prompt protection is adjacent. SMERC evaluates proposed side-effecting actions before execution.

### Is the scoring production-proven?

No. The current implementation is an MVP/reference engine. The first pilot should validate scoring behavior in shadow mode before enforcement.

### Does this create workflow friction?

It should not in `observe` mode. Friction should be measured before any enforcement decision.

### What if SMERC is wrong?

During the first pilot, existing approvals remain authoritative. SMERC records posture, reasons, and constraints for comparison. Enforcement should require calibration, review, and explicit approval.

## Suggested Pilot Architecture

```text
GitHub workflow event
        |
        v
action metadata JSON
        |
        v
SMERC GitHub Action in observe mode
        |
        v
decision report artifact + step summary
        |
        v
security/platform review and calibration
```

## What A CISO Should Ask For Before Enforcement

- reviewed threat model
- approved fail-open/fail-closed behavior
- threshold calibration against internal workflows
- reviewer agreement analysis
- false release and false constraint review
- artifact retention policy
- operational owner for overrides
- incident process for disputed decisions

## Deployment Readiness Judgment

SMERC is ready for CISO review and controlled shadow-mode pilot discussion.

SMERC is not yet ready to be represented as a mature production-certified security platform. It should be introduced as a focused pilot for AI-agent action governance with transparent limitations and measurable success criteria.

## Sendable Summary

SMERC helps security teams evaluate whether AI-agent actions are recoverable and defensible before execution. The first pilot uses GitHub Actions in shadow mode to score AI-assisted code, deployment, and infrastructure actions without blocking existing workflows.

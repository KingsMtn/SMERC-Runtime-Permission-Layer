# SMERC Security Model

## Status

SMERC is an MVP/reference implementation for runtime permission decisions. It is not a production-certified security control, safety-certified controller, compliance certification system, or replacement for IAM, code review, branch protection, approval workflows, or incident response.

## Security Boundary

SMERC is designed to sit at the action boundary:

```text
AI agent or automation proposes action
        |
        v
SMERC evaluates action context and risk signals
        |
        v
ALLOW / THROTTLE / FREEZE / DENY / ESCALATE
        |
        v
Tool, workflow, reviewer, or enforcement system responds
```

SMERC should run before side-effecting actions such as:

- sending external messages
- deploying code
- modifying infrastructure
- deleting data
- accessing sensitive data
- triggering financial workflows
- changing security controls
- calling high-impact internal APIs

## What SMERC Sees

The runtime permission engine expects structured action metadata:

- action ID
- action description
- tool name
- actor or agent name
- confidence score
- harm score
- consent or authorization score
- reversibility score
- external side-effect flag
- sensitive-data flag
- optional context

## What SMERC Should Not Need

In a first pilot, SMERC should not need:

- production secrets
- API tokens beyond normal CI permissions
- raw customer data
- private model prompts
- full source-code contents
- privileged cloud credentials

The preferred pilot pattern is to send SMERC action metadata, not raw sensitive payloads.

## Replay Records

Every decision should create a replayable record containing:

- posture
- risk score
- confidence score
- reason codes
- constraints
- replay ID
- evaluated action metadata
- timestamp

Replay records are intended for security review, audit discussion, reviewer agreement analysis, and pilot calibration.

## Failure Modes

Recommended defaults:

| Context | Recommended Default |
| --- | --- |
| Shadow mode | Never block; record decision only. |
| Recommend mode | Warn and request review for `FREEZE`, `DENY`, or `ESCALATE`. |
| Enforce mode | Fail closed for `DENY` and `FREEZE`; route `ESCALATE` to human review. |

Production deployments must explicitly decide fail-open versus fail-closed behavior with accountable owners.

## Secrets Handling

SMERC should not log secrets. Integrations should avoid passing:

- access tokens
- passwords
- private keys
- customer PII
- raw secrets-detection output containing secret values

If action context includes sensitive references, pass identifiers or summaries rather than raw data.

## Known Limitations

- Current scoring thresholds are reference defaults, not validated production policy.
- The MVP does not authenticate callers by itself.
- The GitHub Action assumes the workflow controls when SMERC runs.
- Replay records are only as reliable as the action metadata supplied.
- The current integration does not prove causality between agent intent and tool action.
- Production use requires threat modeling, legal review, security review, and calibration.


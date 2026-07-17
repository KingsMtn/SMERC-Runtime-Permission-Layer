# SPARTa v2 Execution Adapter Framework

## Purpose

SPARTa means **Stateful Posture-Aware Routing and Tooling Adapter**.

SMERC decides whether an action is structurally defensible. SPARTa determines how the execution environment should respond.

In product terms:

```text
agent proposes action -> SMERC scores posture -> SPARTa routes tool behavior -> evidence returns to the ledger
```

SPARTa v1 proves the core routing idea. SPARTa v2 should make the adapter layer explicit enough for real integrations.

## Current v1 Capability

SPARTa v1 already includes:

- strict tool-plan contract
- static adapter registry
- posture-to-route translation
- route states such as `EXECUTE`, `CONSTRAINED_EXECUTE`, `PAUSE`, `BLOCK`, `REVIEW_REQUIRED`, and `BLOCKED_ESCALATION_UNAVAILABLE`
- signed route reports
- API route endpoint
- integration with SMERC replay IDs and decision digests
- fail-closed behavior when a tool cannot apply required controls

This is enough for technical review and pilot discussion. It is not yet a general execution-control platform.

## v2 Design Goal

SPARTa v2 should become the standard bridge between SMERC decisions and real execution systems.

The goal is not to replace GitHub Actions, ServiceNow, Slack, Jira, Kubernetes, cloud APIs, CI/CD systems, or human approval workflows.

The goal is to provide one consistent contract:

> Given a SMERC posture, what native controls can this execution system actually apply, and what evidence proves those controls were attempted?

## Adapter Lifecycle

Every SPARTa adapter should follow this lifecycle:

1. **Declare**
   - tool identity
   - supported actions
   - supported capabilities
   - supported side-effect levels
   - native controls available
   - maximum scope limits
   - human review path availability

2. **Plan**
   - convert a requested action into a strict SPARTa tool plan
   - reject unsupported actions, capabilities, or side-effect levels
   - reject requested scope beyond adapter maximum

3. **Route**
   - receive a SMERC decision
   - map posture to route state
   - calculate effective scope
   - identify applied and blocked controls
   - produce signed route report when configured

4. **Prepare**
   - verify action-bound permit when enforcement is enabled
   - reserve idempotent execution attempt
   - check that required native controls are available

5. **Execute Or Hold**
   - execute only if route state permits automation
   - constrain execution if route state is `CONSTRAINED_EXECUTE`
   - pause, block, or escalate otherwise

6. **Collect Evidence**
   - record execution attempt
   - record native control result
   - record cancel handle, rollback reference, review ID, or environment gate
   - sign control-evidence receipt when configured

7. **Return To Ledger**
   - append execution and control evidence to the Decision Lifecycle Ledger
   - preserve outcome and learning recommendations separately from active policy

## Standard Adapter Types

### GitHub Actions Adapter

First production-adjacent adapter.

Native controls:

- environment protection
- required reviewers
- concurrency group
- deployment cancellation
- artifact retention
- dry-run mode
- branch/ref checks
- GitHub OIDC workload identity

### ServiceNow Or Jira Adapter

Useful for enterprises where workflow approval already exists.

Native controls:

- ticket creation
- change request association
- reviewer assignment
- approval status polling
- evidence attachment
- escalation queue

### Slack Or Teams Review Adapter

Useful for lightweight pilots and escalation demos.

Native controls:

- reviewer notification
- explicit approve/deny action
- timeout
- reviewer identity capture
- decision comment capture

## Current Mock Review Adapters

The example registry now includes two non-vendor mock review adapters:

- `service-ticket-review` maps review-required actions to a ticket-style review plan.
- `chat-review-bridge` maps review-required actions to a chat-style review plan.

Example requests live in:

- `examples/sparta/service_ticket_review_request.json`
- `examples/sparta/chat_review_request.json`

These examples are intentionally marked with `production_boundary: example_adapter_only`. They prove the SPARTa contract can route an `ESCALATE` posture into accountable human review without pretending that a live ServiceNow, Jira, Slack, or Teams integration exists.

### Kubernetes Or Cloud Deployment Adapter

Higher risk and later-stage.

Native controls:

- namespace or account scope limit
- dry-run or plan mode
- rollout pause
- rollout undo reference
- canary percentage
- deployment health check

### Finance Operations Adapter

SMERC-F candidate, later than GitHub Actions.

Native controls:

- transaction size reduction
- dual approval
- settlement delay
- counterparty allowlist
- liquidity threshold
- treasury review

## Required Adapter Output

Every adapter should produce:

- adapter ID
- route ID
- decision replay ID
- route state
- executable true/false
- effective scope
- applied controls
- blocked controls
- native control references
- execution attempt ID when applicable
- evidence digest
- timestamp
- non-secret metadata
- failure mode

## Failure Rules

SPARTa should fail closed when:

- the adapter is unknown
- the action is unsupported
- the capability is unsupported
- the requested scope exceeds adapter maximum
- SMERC requires a control the adapter cannot apply
- a permit is missing, expired, consumed, or bound to a different action
- native control evidence is missing or stale
- escalation is required but no reviewer path exists
- execution result cannot be recorded

## Commercial Value

SPARTa is commercially important because it moves SMERC from analysis into operational control.

Without SPARTa:

- SMERC can score risk and recommend posture.

With SPARTa:

- SMERC can drive tool-specific behavior.
- Integrations can prove why they executed, constrained, paused, blocked, or escalated.
- Customers can compare recommended controls against controls that actually exist.
- The Decision Lifecycle Ledger can capture what happened after the posture decision.

## Evidence Boundary

SPARTa v2 would still require customer validation.

It should not claim:

- not production certification
- not universal adapter coverage
- not independent attestation
- no guaranteed incident reduction
- not replacement for IAM, CI/CD controls, ticketing, SIEM, EDR, or human accountability

Its proper claim is narrower:

> SPARTa provides a consistent adapter contract for translating SMERC postures into tool-specific execution routes and evidence records.

## Recommended Build Order

1. Standardize the adapter lifecycle contract.
2. Extend the GitHub deployment adapter to emit complete SPARTa v2 evidence.
3. Promote the mock ticket-review adapter into a live ServiceNow or Jira integration prototype.
4. Promote the mock chat-review adapter into a live Slack or Teams integration prototype.
5. Append route and execution evidence into the Decision Lifecycle Ledger.
6. Generate one replayable governance report that includes SMERC decision, SPARTa route, permit, control evidence, execution result, and reviewer outcome.
7. Use the 30-minute workflow proof to show the difference between allow/deny and SPARTa-constrained execution.

## Bottom Line

SPARTa should become SMERC's execution-control layer.

The mature product story is:

```text
SMERC decides what posture is defensible.
SPARTa translates that posture into tool behavior.
DLL records what happened and whether the decision held up.
```

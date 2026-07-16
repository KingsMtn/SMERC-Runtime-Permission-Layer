# SMERC Customer Integration Questionnaire

## Goal

Use this questionnaire before a pilot begins. The purpose is to determine whether SMERC can be tested safely and whether the customer has a workflow where recoverability-aware scoring may add value.

## Organization Fit

1. Which team owns AI-agent or automation governance?
2. Who owns CI/CD, workflow automation, or agent tool execution?
3. Who can approve a shadow-mode pilot?
4. Who can approve limited enforcement if the pilot later supports it?
5. What existing tools govern these workflows today?

## Workflow Fit

1. Which workflow should be tested first?
2. What actions can the workflow trigger?
3. Which actions create external side effects?
4. Which actions are hard to reverse?
5. Which actions already require review?
6. Which actions are allowed automatically today?
7. Which actions are blocked today?
8. What actions create the most concern for the security team?

## Action Metadata

For each action, can the customer provide:

- action ID
- actor or automation identity
- tool or workflow name
- action type
- risk estimate
- reversibility estimate
- containment strength
- rollback latency
- evidence validity
- anomaly pressure
- impact scope
- authorization confidence
- external side-effect flag
- sensitive-data flag

## Data Boundary

1. Can the pilot avoid raw source code, secrets, credentials, private prompts, customer data, and payload bodies?
2. Can action metadata be generated without exposing regulated or confidential content?
3. Where will audit records be stored?
4. Who may view SMERC decisions and reports?
5. What retention period is acceptable for pilot records?
6. Are any fields prohibited from leaving the customer environment?

## Reviewer Process

1. Who will review SMERC decisions?
2. How many reviewers are available weekly?
3. What makes a SMERC recommendation useful?
4. What would count as a false release?
5. What would count as a false constraint?
6. What review latency is acceptable?
7. What level of explanation is required?

## Integration Readiness

1. Can the customer run a local or hosted SMERC API?
2. Can the workflow call an HTTP API?
3. Can the workflow pass a scoped bearer token or workload identity?
4. Can the workflow produce JSON action metadata?
5. Can pilot reports be attached to pull requests, workflow runs, tickets, or review records?
6. Does the customer prefer local-only, Render-hosted, or customer-hosted deployment?

## Decision Criteria

The customer should define before starting:

- minimum decision count
- required reviewer agreement threshold
- maximum false release tolerance
- maximum false constraint tolerance
- maximum latency impact
- minimum useful constraint rate
- stop conditions
- expansion criteria

## Fit Assessment

Strong fit:

- automated actions can create meaningful side effects
- recoverability is not explicitly scored today
- reviewers can label decisions
- action metadata can be generated safely
- customer is willing to run shadow mode before enforcement

Weak fit:

- no meaningful automation side effects
- no reviewers available
- metadata cannot be generated without sensitive payloads
- customer wants immediate production blocking without calibration
- current controls already solve the recoverability question well

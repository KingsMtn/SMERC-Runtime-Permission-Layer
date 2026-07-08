# SMERC Partner Program

SMERC is looking for practical partners who can help test recoverability-weighted authorization in real execution environments.

This is not a reseller program and not a claim that SMERC is production-certified. It is a structured path for serious technical review, pilot learning, and integration exploration.

## Primary Partner Types

### 1. Design Partners

Design partners run SMERC in shadow mode against realistic or live internal workflows.

Best fit:

- CISO or security architecture sponsor
- platform engineering team with CI/CD ownership
- AI governance team evaluating agent workflows
- DevSecOps team near deployment controls

Recommended first pilot:

- GitHub Actions shadow mode
- 90 days
- observe, recommend, enforce only if justified
- no production blocking until review evidence supports it

Partner contribution:

- representative workflow examples
- reviewer feedback
- false release and false constraint labels
- latency and review-burden feedback
- security review findings

SMERC contribution:

- reference API
- GitHub Action path
- SDK support
- pilot metrics
- replay/audit report
- integration support through public issues or private design-partner review

### 2. Integration Partners

Integration partners connect SMERC to tools where pre-execution decisions matter.

Best fit:

- agent-framework maintainers
- CI/CD platforms
- cloud automation platforms
- internal developer platform teams
- API gateway teams
- security orchestration teams

Evaluation question:

> Can SMERC sit before a meaningful action and return a useful, replayable posture without slowing normal work too much?

### 3. Research Partners

Research partners challenge the model, metrics, benchmark design, and evidence boundaries.

Useful review areas:

- recoverability scoring
- benchmark scenario realism
- reviewer agreement definitions
- proxy evidence limits
- policy calibration
- replay integrity
- human factors in constrained authorization

## Pilot Entry Criteria

A good partner has at least one workflow where:

- automated actions can create real side effects
- some actions are reversible and others are not
- existing controls are mostly allow/deny or approval-based
- reviewer feedback can be collected
- the organization can tolerate shadow-mode instrumentation

## Pilot Exit Criteria

A pilot is useful if it can answer:

- Did SMERC change decisions compared with existing controls?
- Did reviewers agree with those changed decisions?
- Did `THROTTLE`, `FREEZE`, or `ESCALATE` preserve useful options?
- Were false constraints acceptable?
- Were false releases reduced or at least surfaced?
- Was latency acceptable?
- Did the audit/replay trail help review?

## What Partners Should Not Expect Yet

Partners should not expect:

- production certification
- compliance attestation
- managed SaaS operations
- guaranteed incident reduction
- calibrated thresholds for their environment without pilot data
- replacement of existing IAM, policy, EDR, SIEM, code review, or approval tools

## How To Express Interest

Open a GitHub Issue using one of these titles:

- `Design partner interest: [workflow]`
- `Integration partner interest: [platform/tool]`
- `Research review interest: [topic]`

Include:

- organization type
- workflow category
- current approval or governance approach
- why recoverability matters
- whether shadow mode is possible
- any constraints around data sharing

Do not include secrets, private customer data, regulated data, or confidential incident details in public issues.

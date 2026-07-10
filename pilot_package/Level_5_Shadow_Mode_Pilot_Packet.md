# SMERC Level 5 Shadow-Mode Pilot Packet

## Status

SMERC is ready for bounded shadow-mode pilot review. It is not production-certified and should not block production workflows without customer security, platform, and legal approval.

## Target Buyer

Primary buyer:

- Chief Information Security Officer

Primary reviewers:

- security architects
- platform engineering leaders
- DevSecOps teams
- AI governance teams

## Pilot Objective

Determine whether recoverability-weighted authorization and SPARTa route selection provide useful governance signals for AI-assisted code, deployment, and infrastructure workflows.

## Pilot Boundary

Recommended first environment:

- GitHub Actions
- pull request, workflow dispatch, or deployment workflow events
- AI-assisted code, infrastructure, or release actions
- shadow mode only during the first phase

Out of scope for the first pilot:

- direct money movement
- production blocking without approval
- replacing existing approval workflows
- compliance certification
- automated executive override

## What The Pilot Tests

The pilot tests whether SMERC can provide useful answers to these questions:

- Is the proposed action recoverable enough to execute now?
- Should the action be allowed, constrained, paused, blocked, or escalated?
- Can SPARTa identify whether the execution tool can enforce the needed route?
- Do reviewers agree with SMERC's posture and reason codes?
- Does recoverability scoring reveal risk that allow/deny policy misses?

## 30-Day Minimum Pilot

### Week 1: Setup

Tasks:

- choose one repository or workflow family
- configure SMERC in observe mode
- define action metadata shape
- identify reviewers
- confirm stop conditions

Evidence produced:

- successful local or hosted API health check
- first decision report
- first replay record

### Weeks 2-3: Observe

Tasks:

- score real or representative workflow actions
- do not block workflows
- record reviewer agreement and overrides
- collect false release, false constraint, and useful constraint labels

Evidence produced:

- decision count
- posture distribution
- reviewer agreement rate
- route-state distribution
- qualitative reviewer notes

### Week 4: Review

Tasks:

- inspect metrics
- identify whether constraints were useful
- decide whether to continue, stop, narrow, or expand

Evidence produced:

- pilot metrics report
- recommendation memo
- integration gap list

## 90-Day Pilot Expansion

### Phase 1: Observe

Run shadow-mode scoring. No workflow blocking.

### Phase 2: Recommend

Surface SMERC recommendations into existing review workflows.

### Phase 3: Enforce

Only after written approval, test narrow non-production enforcement. Initial enforcement should be limited to clearly unsafe `DENY` or `FREEZE` cases.

## Success Metrics

Required metrics:

- decision count
- reviewer agreement rate
- false release rate
- false constraint rate
- useful constraint rate
- review latency
- route-state distribution
- number of missing-evidence or insufficient-control outcomes

Useful optional metrics:

- approval latency before and after SMERC recommendation
- number of actions constrained instead of blocked
- number of actions routed to review due to missing adapter controls
- number of workflow policy changes discovered

## Stop Conditions

Stop or narrow the pilot if:

- reviewers cannot understand the reason codes
- false release concerns are material
- false constraints create unacceptable noise
- action metadata cannot be generated reliably
- SMERC recommendations duplicate existing controls without adding useful signal
- integration overhead exceeds expected governance value

## Required Evidence Before Claiming Level 6

SMERC should not claim enterprise beta status until at least one outside pilot produces:

- real customer or design-partner data
- measured reviewer agreement
- measured false release and false constraint rates
- documented pilot decision
- external feedback on integration burden
- security review notes

## YC Framing

Accurate statement:

> SMERC is a Level 5 candidate: a working runtime permission prototype ready for bounded shadow-mode pilot review.

Avoid:

> SMERC is a production-ready enterprise AI governance platform.

## Relevant Repository Evidence

- `docs/Maturity_Model.md`
- `reports/Pilot_Level_5_Readiness_Assessment.md`
- `examples/pilot_level5_readiness.json`
- `docs/Pilot_Readiness.md`
- `docs/Pilot_Evaluation_Checklist.md`
- `docs/API_Deployment_Guide.md`
- `docs/SPARTa_Router_Operations.md`
- `integrations/github_actions/README.md`

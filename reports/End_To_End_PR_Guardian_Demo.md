# SMERC End-To-End PR Guardian Demo

## Executive Summary

This demo proves the current SMERC modules work as one runtime governance loop for an AI-assisted pull request.

```text
AI-assisted PR request -> SMERC decision -> PR Guardian comment/certificate -> SPARTa route -> Decision Lifecycle Ledger -> DLL Intelligence
```

## 1. Action Request

- Action ID: `AI_AUTH_MIDDLEWARE_PR`
- Actor: `coding_agent`
- Tool: `github.pull_request`
- Description: AI coding agent proposes changing authentication middleware and deployment configuration in a pull request.

## 2. SMERC Runtime Decision

- Posture: `ESCALATE`
- Risk score: `0.656`
- Confidence score: `0.535`
- Replay ID: `replay_AI_AUTH_MIDDLEWARE_PR_1785203296935`
- Reason codes: `['EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA_ACCESS', 'HIGH_HARM_POTENTIAL']`
- Controls: `['route_to_human_review', 'preserve_replay', 'require_explicit_approval']`

## 3. PR Guardian Visible Review Artifact

- Certificate digest: `fdbe0686f71d3c1eeb566cbc3ad8ef60331673dd02501f1d4b595d14cf8b212b`
- Comment posture: `ESCALATE`

```markdown
<!-- smerc-pr-guardian:v1 -->
## SMERC PR Guardian

**Posture:** `ESCALATE`  
**Risk score:** `0.656`  
**Confidence score:** `0.535`  
**Replay ID:** `replay_AI_AUTH_MIDDLEWARE_PR_1785203296935`

**Action:** AI coding agent proposes changing authentication middleware and deployment configuration in a pull request.
**Pull request:** `#101`

### Recommendation

Route to accountable human review before execution.

### Required Controls

- `route_to_human_review`
- `preserve_replay`
- `require_explicit_approval`

### Reason Codes

- `EXTERNAL_SIDE_EFFECT`
- `SENSITIVE_DATA_ACCESS`
- `HIGH_HARM_POTENTIAL`

### Decision Certificate

- Certificate digest: `fdbe0686f71d3c1eeb566cbc3ad8ef60331673dd02501f1d4b595d14cf8b212b`
- Integration status: `evaluated`
- Mode: `observe`

<sub>SMERC PR Guardian is pilot-grade evidence for review. It does not replace branch protection, code review, security review, deployment approvals, or human accountability.</sub>
```

## 4. SPARTa Route

- Route state: `REVIEW_REQUIRED`
- Executable: `False`
- Effective scope units: `0`
- Applied controls: `['route_to_accountable_reviewer', 'require_explicit_approval', 'preserve_replay']`
- Route report digest: `3c175377239549a1da65fe794a971ddea7603bb933bbb5967ac4614847477254`

## 5. Decision Lifecycle Ledger

- Ledger ID: `dll_replay_AI_AUTH_MIDDLEWARE_PR_1785203296935`
- Record count: `7`
- Head hash: `d60b8eac9356fe7081938310942962d750cd934172e14f97d3f713271df62b3b`
- Verification valid: `True`
- Event counts: `{'EVALUATION': 1, 'EVIDENCE': 1, 'EXECUTION': 1, 'HUMAN_INTERACTION': 1, 'LEARNING_RECOMMENDATION': 1, 'OUTCOME': 1, 'REQUEST': 1}`

## 6. DLL Intelligence

- Ledger count: `1`
- Near-miss count: `1`
- Recovery failure count: `0`
- Policy review queue items: `2`
- Recommended next action: Collect at least 30 customer-context DLL records before presenting rates as pilot evidence.

## Integrated Flow

- AI-assisted PR request declared
- SMERC runtime engine evaluated recoverability posture
- PR Guardian rendered pull-request comment and certificate
- SPARTa routed posture into executable, constrained, paused, blocked, or review-required behavior
- Decision Lifecycle Ledger recorded request, evidence, evaluation, review, execution, outcome, and learning
- DLL Intelligence summarized the verified lifecycle record

## Boundary

- Synthetic end-to-end demo; not customer production evidence.
- PR Guardian does not replace branch protection, code review, security review, deployment approvals, or human accountability.
- Customer-context pilot records are required before claiming operational risk reduction.

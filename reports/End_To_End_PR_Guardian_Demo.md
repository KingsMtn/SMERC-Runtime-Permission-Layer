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
- Replay ID: `replay_AI_AUTH_MIDDLEWARE_PR_1785203868401`
- Reason codes: `['EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA_ACCESS', 'HIGH_HARM_POTENTIAL']`
- Controls: `['route_to_human_review', 'preserve_replay', 'require_explicit_approval']`

## 3. PR Guardian Visible Review Artifact

- Certificate digest: `08f1df72fe2185e7100e30d9c92563cb5c0223d5a48f92d14a9bf3f2b04148c1`
- Comment posture: `ESCALATE`

```markdown
<!-- smerc-pr-guardian:v1 -->
## SMERC PR Guardian

**Posture:** `ESCALATE`  
**Risk score:** `0.656`  
**Confidence score:** `0.535`  
**Replay ID:** `replay_AI_AUTH_MIDDLEWARE_PR_1785203868401`

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

- Certificate digest: `08f1df72fe2185e7100e30d9c92563cb5c0223d5a48f92d14a9bf3f2b04148c1`
- Integration status: `evaluated`
- Mode: `observe`

<sub>SMERC PR Guardian is pilot-grade evidence for review. It does not replace branch protection, code review, security review, deployment approvals, or human accountability.</sub>
```

## 4. SPARTa Route

- Route state: `REVIEW_REQUIRED`
- Executable: `False`
- Effective scope units: `0`
- Applied controls: `['route_to_accountable_reviewer', 'require_explicit_approval', 'preserve_replay']`
- Route report digest: `854fc1209ecdb682f6dbb3723f104d8e668d8b419fdb2902037599b6392e7241`

## 5. Decision Lifecycle Ledger

- Ledger ID: `dll_replay_AI_AUTH_MIDDLEWARE_PR_1785203868401`
- Record count: `7`
- Head hash: `77367fd79cf524896e92f049f6450a65b1595c175f0e05c75a6196cf8e6da587`
- Verification valid: `True`
- Event counts: `{'EVALUATION': 1, 'EVIDENCE': 1, 'EXECUTION': 1, 'HUMAN_INTERACTION': 1, 'LEARNING_RECOMMENDATION': 1, 'OUTCOME': 1, 'REQUEST': 1}`

## 6. DLL Intelligence

- Ledger count: `1`
- Near-miss count: `1`
- Recovery failure count: `0`
- Policy review queue items: `2`
- Recommended next action: Collect at least 30 customer-context DLL records before presenting rates as pilot evidence.

## 7. Performance And Latency

- Measurement type: `single_local_process_run`
- Decision evaluation: `0.095 ms`
- PR certificate: `0.512 ms`
- PR comment render: `0.026 ms`
- SPARTa route: `0.407 ms`
- DLL build: `0.28 ms`
- DLL Intelligence: `1.715 ms`
- Total local proof-loop generation: `3.184 ms`
- CISO interpretation: Use latency as operational overhead evidence, not as the core value claim. A pilot should measure median and p95 decision latency, total workflow time added, reviewer agreement, approval delay, false constraints, and false releases.

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

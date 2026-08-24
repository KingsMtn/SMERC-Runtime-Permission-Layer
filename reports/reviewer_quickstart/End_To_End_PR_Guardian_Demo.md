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
- Replay ID: `replay_AI_AUTH_MIDDLEWARE_PR_1787608420912`
- Reason codes: `['EXTERNAL_SIDE_EFFECT', 'SENSITIVE_DATA_ACCESS', 'HIGH_HARM_POTENTIAL']`
- Controls: `['route_to_human_review', 'preserve_replay', 'require_explicit_approval']`

## 3. PR Guardian Visible Review Artifact

- Certificate digest: `4cacc913ab6b5f342bd49b1a6628420d205fcfefc6e3cb4f281ed1295ef1911b`
- Comment posture: `ESCALATE`

```markdown
<!-- smerc-pr-guardian:v1 -->
## SMERC PR Guardian

**Posture:** `ESCALATE`  
**Risk score:** `0.656`  
**Confidence score:** `0.535`  
**Replay ID:** `replay_AI_AUTH_MIDDLEWARE_PR_1787608420912`

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

- Certificate digest: `4cacc913ab6b5f342bd49b1a6628420d205fcfefc6e3cb4f281ed1295ef1911b`
- Integration status: `evaluated`
- Mode: `observe`

<sub>SMERC PR Guardian is pilot-grade evidence for review. It does not replace branch protection, code review, security review, deployment approvals, or human accountability.</sub>
```

## 4. SPARTa Route

- Route state: `REVIEW_REQUIRED`
- Executable: `False`
- Effective scope units: `0`
- Applied controls: `['route_to_accountable_reviewer', 'require_explicit_approval', 'preserve_replay']`
- Route report digest: `da34a35877ac3a27f050e796e00b3b6138d9d9a1332d1809dff0d1a05fcc67e2`

## 5. Decision Lifecycle Ledger

- Ledger ID: `dll_replay_AI_AUTH_MIDDLEWARE_PR_1787608420912`
- Record count: `7`
- Head hash: `07eb113ba416f879885ceb298245231e0094b496e6a3dc1603be51897ab7d62e`
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
- Decision evaluation: `0.135 ms`
- PR certificate: `0.216 ms`
- PR comment render: `0.031 ms`
- SPARTa route: `0.514 ms`
- DLL build: `0.35 ms`
- DLL Intelligence: `2.712 ms`
- Total local proof-loop generation: `4.152 ms`
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

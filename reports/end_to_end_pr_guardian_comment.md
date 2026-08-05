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

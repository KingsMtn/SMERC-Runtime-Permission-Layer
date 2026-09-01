<!-- smerc-pr-guardian:v1 -->
## SMERC PR Guardian

**Posture:** `ESCALATE`  
**Risk score:** `0.656`  
**Confidence score:** `0.535`  
**Replay ID:** `replay_AI_AUTH_MIDDLEWARE_PR_1788272742369`

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

- Certificate digest: `73b988bf0ad0876faad3db9da52db34ca5ea3bd03ff37b6ae9568bec96c2cb55`
- Integration status: `evaluated`
- Mode: `observe`

<sub>SMERC PR Guardian is pilot-grade evidence for review. It does not replace branch protection, code review, security review, deployment approvals, or human accountability.</sub>

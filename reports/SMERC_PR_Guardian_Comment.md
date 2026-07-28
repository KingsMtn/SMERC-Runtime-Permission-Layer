<!-- smerc-pr-guardian:v1 -->
## SMERC PR Guardian

**Posture:** `THROTTLE`  
**Risk score:** `0.581`  
**Confidence score:** `0.527`  
**Replay ID:** `replay_AI_DEPLOY_PRODUCTION_CHANGE_1785202285892`

**Action:** AI coding agent proposes deploying a generated infrastructure change to production.

### Recommendation

Proceed only with the listed constraints before merge or deployment.

### Required Controls

- `limit_scope`
- `preview_before_execution`
- `log_replay`
- `rate_limit_external_effect`
- `require_recovery_path`

### Reason Codes

- `EXTERNAL_SIDE_EFFECT`
- `MODERATE_HARM_POTENTIAL`

### Decision Certificate

- Certificate digest: `a4d4d112738e58ab0b19c3f15369253ca6b02f01b3a47d425e2de61e040fb242`
- Integration status: `evaluated`
- Mode: `observe`

<sub>SMERC PR Guardian is pilot-grade evidence for review. It does not replace branch protection, code review, security review, deployment approvals, or human accountability.</sub>

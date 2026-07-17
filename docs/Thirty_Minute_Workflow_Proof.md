# SMERC 30-Minute Workflow Proof

## Purpose

This is the fastest serious way to evaluate whether SMERC is more than a concept.

It answers one narrow question:

> Can SMERC score one AI-assisted GitHub Actions workflow end-to-end, produce a replayable decision record, and show a useful difference from simple allow/deny review in under 30 minutes?

This is a technical proof path. It is not customer validation, not production certification, not compliance attestation, and not proof of incident reduction.

## Target Workflow

Use one GitHub Actions workflow where automation can create side effects:

- production canary deployment
- infrastructure change
- database migration
- privileged maintenance job
- AI-assisted pull-request workflow that can trigger deployment

The first workflow should already have some human review or approval expectation. SMERC should start in observe mode so the existing workflow remains unchanged.

## What The Reviewer Should See

The reviewer should see a concrete difference:

| Traditional allow/deny | SMERC posture | Why it matters |
| --- | --- | --- |
| Allowed because the workflow or actor has permission | `THROTTLE` | The action can proceed only with constraints such as canary size, cancel handle, rollback evidence, or human review. |
| Allowed because CI/CD credentials are valid | `FREEZE` | Missing evidence, anomaly pressure, weak rollback, or unclear impact pauses automated progression. |
| Blocked because action looks risky | `ESCALATE` | A higher-trust reviewer can decide instead of forcing a blanket deny. |
| Allowed by policy | `DENY` | The action is not recoverable enough for automated execution. |

The key test is not whether SMERC blocks more. The key test is whether SMERC creates a better review conversation by exposing recoverability, containment, rollback latency, evidence validity, anomaly pressure, and impact scope.

## 30-Minute Path

### Minutes 0-5: Choose One Action

Pick one candidate action from `examples/ciso_review_seed_actions.json`.

Recommended first example:

```text
CISO_REVIEW_DEPLOY_CANARY
```

This action is useful because a simple allow/deny system may allow it, while SMERC should produce a constrained posture because the action is production-facing but partially recoverable.

### Minutes 5-10: Run The Local Decision Seed

```bash
python -m reference_engine.ciso_review_seed \
  --audit-db ./smerc_ciso_review.sqlite3 \
  --json-output reports/ciso_evidence_walkthrough_seed.json \
  --markdown-output reports/CISO_Evidence_Walkthrough_Seed_Report.md \
  --pretty
```

Expected result:

- five stored decisions
- five stored decision-time ledgers
- security events for the seeded walkthrough
- a Markdown report a reviewer can inspect

### Minutes 10-20: Inspect The Decision

Open `reports/CISO_Evidence_Walkthrough_Seed_Report.md` and inspect:

- posture
- irreversible exposure score
- reversible capacity score
- confidence score
- reason codes
- recommended controls
- replay identifier
- Decision Lifecycle Ledger identifier

The reviewer should be able to explain why a production canary deployment is not simply "allowed" or "blocked." It can be constrained.

### Minutes 20-25: Compare Against Allow/Deny

Ask:

1. Would the existing workflow allow this action because credentials and branch rules are satisfied?
2. Would the existing workflow block this action because production deployment is too risky?
3. Does SMERC's posture give a more useful intermediate answer?
4. Are the recommended controls practical in this workflow?
5. What metadata is missing for a real pilot?

### Minutes 25-30: Decide Whether A Pilot Is Worth It

Proceed to a shadow-mode pilot only if the reviewer can name:

- one workflow where recoverability matters
- one accountable security or platform owner
- one reviewer group that can label decisions
- one safe metadata boundary
- one success metric worth measuring

Do not proceed if the organization cannot supply reviewer labels, cannot define action metadata safely, or does not have AI-agent or automation actions with meaningful side effects.

## Minimum Evidence Output

At the end of the 30-minute review, SMERC should produce or point to:

- seeded decision report
- replayable posture record
- reason codes and controls
- decision-time DLL record
- evidence boundary statement
- next-step pilot decision

## What Would Invalidate The Pilot

The pilot should stop or narrow if reviewers conclude:

- recoverability is already handled well enough by existing controls
- SMERC's posture does not change review quality
- reason codes are not understandable
- recommended controls cannot be implemented in the workflow
- action metadata is too difficult or sensitive to provide
- approval latency or operational complexity outweighs signal value
- the workflow has no meaningful side effects

## Success Definition

The 30-minute proof is successful only if a reviewer can say:

> I understand where SMERC would sit, what it would score, what it would record, and why a constrained posture can be more useful than simple allow/deny for at least one real workflow.

That statement is not a purchase decision. It is permission to test.

## Next Step

If the 30-minute proof is credible, use `pilot_package/First_Pilot_Path.md` to run a 30-day GitHub Actions shadow-mode pilot.

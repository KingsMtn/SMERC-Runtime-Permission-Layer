# SPARTa Router Operations

## What This Adds

SPARTa turns a SMERC decision into a practical execution route.

Before this layer, SMERC could say `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`. SPARTa answers the next operational question:

> Given that posture, what should the execution system do with this specific tool plan?

That matters for CISOs and platform teams because many tools can execute an action, but not every tool can safely constrain, pause, rollback, or escalate the action.

## First Pilot Use

The first intended use is GitHub Actions and deployment workflow review.

Example:

1. An AI-assisted workflow proposes a production deployment.
2. SMERC evaluates recoverability and returns `THROTTLE`.
3. SPARTa checks whether the execution plan supports dry run, scope limiting, checkpoint, rollback, and human approval.
4. If the plan supports the required controls, SPARTa returns `CONSTRAINED_EXECUTE`.
5. If the plan cannot enforce the constraints, SPARTa returns `REVIEW_REQUIRED`.

This makes the difference between a policy opinion and an executable governance route.

## Local Run

```bash
python -m reference_engine.sparta_router \
  --decision examples/sparta/throttle_decision.json \
  --plan examples/sparta/github_actions_deploy_plan.json \
  --pretty
```

Try the freeze path:

```bash
python -m reference_engine.sparta_router \
  --decision examples/sparta/freeze_decision.json \
  --plan examples/sparta/destructive_tool_plan.json \
  --pretty
```

## How To Read A Route Report

Important fields:

- `source_posture`: the original SMERC posture.
- `route_state`: the execution route SPARTa selected.
- `executable`: whether automation can proceed.
- `effective_scope_units`: the allowed scope after routing.
- `applied_controls`: controls the route expects the adapter to apply.
- `blocked_controls`: controls or routes that are unavailable.
- `decision_digest`: digest binding the route to the relevant SMERC decision fields.

## Commercial Meaning

SPARTa makes SMERC easier to understand as runtime permission infrastructure:

- SMERC scores whether the action is defensible.
- Permits authorize narrow eligible execution.
- Control evidence records what enforcement actually happened.
- SPARTa routes posture into the right tool behavior.

The product claim should stay modest: SPARTa v1 is not a full workflow engine. It is a conservative posture-aware router that helps integrations fail closed when they cannot enforce the controls SMERC requires.

## Current Limits

- No adapter registry yet.
- No API endpoint yet.
- No signed route reports yet.
- No formal policy language binding yet.
- No live evidence that SPARTa routes reduce real-world incidents.

Those are the next build steps after v1 is reviewed.

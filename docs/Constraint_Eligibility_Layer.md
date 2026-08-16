# Constraint Eligibility Layer

SMERC uses recoverability as a permission modifier, not as a substitute for authority or hard policy.

The Constraint Eligibility Layer answers one question before recoverability scoring is allowed to soften a decision:

> Is this action eligible for constrained authorization at all?

Some actions should not become `THROTTLE` merely because rollback appears possible. If an action is unauthorized, categorically prohibited, legally held, identity-weak, or goal-inconsistent, the safer posture is `DENY`, `FREEZE`, or `ESCALATE`.

## Runtime Order

```text
action request
  -> authority and prohibited-action check
  -> constraint eligibility
  -> recoverability scoring
  -> SPARTa route selection
  -> control evidence
  -> Decision Lifecycle Ledger
```

## Eligibility Labels

| Label | Meaning |
| --- | --- |
| `categorically_prohibited` | The action matches a hard-deny pattern such as deleting audit logs, bypassing authentication, exporting secrets, deleting backups, or disabling security controls. |
| `requires_authority` | Actor authority or identity confidence is too weak for constrained execution. |
| `constraint_eligible` | The action is allowed in principle and may proceed to recoverability-aware runtime scoring. |
| `review_required` | The action may be legitimate, but needs accountable review before execution. |
| `recoverability_sensitive` | The action remains highly dependent on reversibility, containment, rollback latency, or cancellation reliability. |

## Why This Matters

Without this layer, recoverability can be misunderstood as a way to convert too many risky actions into constrained actions.

The stricter rule is:

> A recoverable prohibited action is still prohibited.

This improves SMERC's credibility with CISOs because it preserves hard denies while adding useful middle states only where those states are appropriate.

## Reference Implementation

- `reference_engine/constraint_eligibility.py`
- `schemas/smerc-constraint-eligibility-v1.schema.json`
- `examples/constraint_eligibility/constraint_eligible_canary.json`
- `examples/constraint_eligibility/prohibited_audit_log_delete.json`
- `examples/constraint_eligibility/weak_authority_funds_transfer.json`
- `tests/test_constraint_eligibility.py`

Run:

```bash
python -m reference_engine.constraint_eligibility examples/constraint_eligibility/prohibited_audit_log_delete.json --pretty
```

Expected result: the action is not eligible for constrained authorization and receives a recommended runtime posture of `DENY`.

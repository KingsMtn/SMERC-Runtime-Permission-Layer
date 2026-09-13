# AWS Audit Delay And Irreversibility Map

## Purpose

This map records how SMERC should reason about AWS-style agent actions when audit evidence may arrive after the action, or when the proposed action can damage the evidence and recovery path itself.

It answers the question:

> How should SMERC handle AWS actions where waiting for CloudTrail-style evidence is too slow, incomplete, or already at risk of being blinded?

## Short Answer

SMERC should not wait for delayed cloud audit evidence before making a pre-execution recoverability decision.

For AWS-style agent actions, SMERC needs two layers:

1. **Pending state cache:** a short-lived local record of permitted or attempted cloud mutations while CloudTrail-, CloudWatch-, Security Lake-, EventBridge-, or adapter-shaped evidence catches up.
2. **Structural irreversibility rules:** hard pre-execution rules for actions that can destroy evidence, break decryption, weaken identity boundaries, or create broad remediation blast radius.

This is a design and metadata map, not a live AWS integration.

## Why This Matters

CloudTrail-style evidence is essential for later review, but it is not always immediate enough for the next agent action.

An agent may request:

- a KMS change that makes historical data or logs unrecoverable
- a CloudTrail change that weakens or removes the audit path
- an IAM boundary change that expands delegated authority
- a broad S3 or repository remediation action with collateral impact
- a second cloud mutation before the first mutation is reconciled

In those cases, SMERC should use the pending state it already saw at the gateway or adapter boundary, not wait for a delayed audit record before constraining the next action.

## Pending State Cache Shape

The cache is a short-lived operational memory of actions SMERC has permitted, held, denied, escalated, or observed but not yet reconciled against cloud evidence.

Example file:

- `examples/aws_audit_delay_irreversibility_map.json`

Core fields:

- `permit_id`
- `agent_id`
- `issued_at`
- `expires_at`
- `reconciliation_status`
- `pending_mutations`
- `unreconciled_risk`
- `required_evidence`
- `next_action_effect`

The cache should expire quickly, but long enough to cover the audit visibility gap for a normal pilot. The example uses a bounded `ttl_minutes` field and does not prescribe Redis, ElastiCache, DynamoDB, or any particular production store.

## Structural Irreversibility Rules

These AWS-style actions should be treated as structural recoverability hazards before execution.

| Rule | Action Family | Default SMERC Posture | Why |
| --- | --- | --- | --- |
| `AWS-IRR-001` | KMS key disable, deletion, or broad key-policy change | `DENY` | Cryptographic dead ends can make data, logs, backups, or recovery evidence unreadable. |
| `AWS-IRR-002` | CloudTrail stop, delete, or audit-integrity weakening | `FREEZE` | Audit-path changes can blind later review and make postcondition evidence unreliable. |
| `AWS-IRR-003` | IAM permission boundary or role-policy weakening by autonomous agent | `ESCALATE` | Identity-boundary changes alter who can act next and can widen blast radius across sessions. |
| `AWS-IRR-004` | S3 bucket policy changes that broaden sensitive data access | `FREEZE` | Data exposure may be irreversible once accessed or copied. |
| `AWS-IRR-005` | Broad remediation, takedown, cleanup, or delete action across many resources | `ESCALATE` | Remediation can create collateral damage if the affected-object set is not scoped and reviewable. |
| `AWS-IRR-006` | Second high-impact mutation while prior mutation is unreconciled | `THROTTLE` or `FREEZE` | Pending state should reduce autonomy until the earlier action is reconciled. |

## Mapping To SMERC Signals

| AWS Signal | SMERC Field Or Concept |
| --- | --- |
| delayed audit visibility | `postcondition_evidence_expected`, `evidence_validity`, `POSTCONDITION_EVIDENCE_MISSING` |
| unreconciled mutation count | pending state cache, autonomy budget, anomaly pressure |
| KMS dead-end risk | low `reversibility`, low `containment_strength`, high `rollback_latency`, `DENY` |
| audit blinding risk | low evidence validity, high impact scope, `FREEZE` |
| IAM boundary change | authority confidence, delegated authority, least-privilege gate, `ESCALATE` |
| broad remediation | scope units, dry-run affected count, reviewer approval, `ESCALATE` |
| repeated mutation velocity | autonomy budget, cost or blast-radius velocity, `THROTTLE` |

## Work / Result / Impact

Work: define how AWS-style delayed audit evidence and structural dead-end actions should map into SMERC decisions.

Result: reviewers can see that SMERC does not depend only on after-the-fact CloudTrail-style records. It also needs pre-execution hard rules and a short-lived pending-state view.

Impact: SMERC becomes more realistic for AWS-style agent governance because it accounts for audit lag, audit blinding, cryptographic dead ends, identity-boundary drift, broad remediation blast radius, and unreconciled mutation velocity.

## Evidence Boundary

This map does not call AWS APIs, read CloudTrail, assume roles, inspect live accounts, deploy Redis, deploy ElastiCache, create SCPs, change KMS keys, modify IAM, alter CloudTrail, or prove AWS production enforcement.

It is a design map for what a live AWS integration would need to prove later.

## Runnable Replay

The metadata-only replay runner is implemented and can be run locally:

```bash
python -m reference_engine.aws_audit_delay_irreversibility_replay examples/aws_audit_delay_irreversibility_map.json --pretty
```

It emits:

- normalized customer-evaluation actions at `examples/aws_audit_delay_irreversibility_normalized_customer_eval_actions.json`
- the replay report at `reports/aws_audit_delay_irreversibility_replay_report.json`
- the reviewer-readable report at `reports/AWS_Audit_Delay_And_Irreversibility_Replay_Report.md`
- the full customer-evaluation report under `reports/aws_audit_delay_irreversibility_customer_evaluation/`

This turns the map into a runnable local loop: an in-memory pending mutation cache records unreconciled AWS-style mutations, structural dead-end rules convert them into SMERC customer-evaluation actions, and SPARTa routing shows whether the result is executable, constrained, paused, escalated, or blocked.

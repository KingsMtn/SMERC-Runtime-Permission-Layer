# SMERC DLL Intelligence

## Purpose

DLL Intelligence analyzes many verified SMERC Decision Lifecycle Ledger records and turns them into governance signals.

The raw DLL answers:

> What happened in this governed decision?

DLL Intelligence answers:

> What are we learning across many governed decisions?

This is the layer that turns SMERC from a runtime permission check into a governance memory system.

## What It Measures

DLL Intelligence summarizes:

- posture distribution before and after review
- human review and override rate
- helpful and harmful overrides
- rollback attempts and rollback success
- judged-correct rate after outcome review
- unexpected consequence rate
- control sufficiency rate
- near-miss decisions
- recovery failures
- recurring reason codes
- recurring missing evidence
- recurring safeguards
- review-gated policy recommendations
- governance drift signals

## What Counts As A Near Miss

DLL Intelligence treats a decision as a near miss when SMERC selected a constrained, frozen, escalated, or denied posture and the outcome later suggests that the restraint was useful.

Examples:

- a risky deployment was throttled to canary and later completed safely
- a destructive database action was denied before execution
- an infrastructure change failed but rollback succeeded
- a key-management action was frozen because owner confirmation was missing

This does not prove an incident would have happened. It records where recoverability-aware governance appears to have preserved options.

## What Counts As A Recovery Failure

DLL Intelligence marks recovery failure when:

- rollback was attempted and failed, or
- unexpected consequences occurred and recovery time was greater than zero

Recovery failure is one of the clearest signals that an action class needs stronger containment, better rollback design, or stricter authorization posture.

## Policy Review Queue

DLL Intelligence does not silently update policy.

It creates a policy review queue when:

- a DLL learning recommendation exists
- the same missing evidence appears repeatedly
- the same reason code appears repeatedly

Every generated item has `activation_status: requires_review`.

This preserves the SMERC principle that learning should be reviewable and auditable before becoming active governance.

## Example

Generate a synthetic example portfolio and report:

```bash
python -m reference_engine.dll_intelligence \
  --example-bundle-output examples/decision_lifecycle_ledger_portfolio.json \
  --json-output reports/dll_intelligence_report.json \
  --markdown-output reports/DLL_Intelligence_Report.md \
  --pretty
```

Analyze existing DLL or pilot intake files:

```bash
python -m reference_engine.dll_intelligence \
  reports/decision_lifecycle_ledger_example.json \
  --json-output reports/dll_intelligence_report.json \
  --markdown-output reports/DLL_Intelligence_Report.md
```

## Product Role

DLL Intelligence gives SMERC a second-order value proposition:

```text
SMERC decides whether an action is recoverable enough to proceed.
SPARTa routes the action into controls.
DLL records the full lifecycle.
DLL Intelligence identifies what governance is learning across decisions.
```

This matters to CISOs because it creates evidence for questions existing policy tools often leave unanswered:

- Which constraints actually reduce risk?
- Which overrides improved or worsened outcomes?
- Which action types repeatedly lack evidence?
- Which controls fail under real execution?
- Which policies should be reviewed before enforcement expands?

## Evidence Boundary

DLL Intelligence is only as strong as the ledger records supplied to it.

Synthetic examples are useful for product testing. Analyst-assigned incident replays are useful for structured research. Customer-context pilot records are required before claiming operational risk reduction.

DLL Intelligence is not:

- a SIEM
- legal recordkeeping
- regulatory retention
- automatic policy training
- proof of incident prevention
- proof of customer demand

It is a pilot-grade governance intelligence layer for reviewing decision quality, recoverability, and policy improvement.

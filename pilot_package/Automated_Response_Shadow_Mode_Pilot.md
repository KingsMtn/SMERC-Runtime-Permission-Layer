# Automated Response Shadow-Mode Pilot

## Purpose

This pilot tests whether SMERC's recoverability checkpoint adds useful judgment before automated security, cloud, or DevOps response actions execute.

The pilot does not replace the customer's existing tools. It runs beside them in shadow mode.

## Best-Fit Workflows

Start with one workflow where automation already recommends or executes high-impact actions:

- endpoint isolation
- privileged session revocation
- cloud security group rollback
- firewall or domain blocking
- mailbox rule removal
- deployment rollback
- infrastructure change cancellation

## Required Customer Inputs

Use metadata only:

- event or workflow identifier
- existing workflow outcome
- proposed response action
- affected entity counts
- severity or priority
- current approval path
- rollback option
- containment option
- expected blast radius
- reviewer label

Do not include secrets, raw customer records, regulated data, private prompts, or confidential incident detail.

## Pilot Phases

### Phase 1: Map

Duration: 1 week

Goals:

- select one action stream
- map 25 to 100 historical events or workflow actions
- define reviewer labels and stop conditions
- confirm metadata boundary

Deliverables:

- metadata mapping table
- pilot success-metric agreement
- sample SMERC input set

### Phase 2: Replay

Duration: 2 to 3 weeks

Goals:

- replay historical or shadow-mode events through SMERC
- compare existing workflow outcome with SMERC posture
- record reason codes, controls, and latency

Deliverables:

- replay report
- posture distribution
- decision-difference analysis
- latency summary

### Phase 3: Review

Duration: 2 weeks

Goals:

- collect reviewer agreement
- identify false release risk
- identify false constraint rate
- decide whether enforce-mode testing is justified

Deliverables:

- reviewer agreement report
- false release and false constraint analysis
- go/no-go recommendation

## Success Metrics

| Metric | Question |
| --- | --- |
| decision difference rate | Does SMERC produce meaningfully different action posture? |
| reviewer agreement rate | Do customer reviewers agree with SMERC restraint or release decisions? |
| false release rate | Did SMERC allow an action reviewers believe should have been constrained, frozen, denied, or escalated? |
| false constraint rate | Did SMERC constrain actions reviewers believe should have run normally? |
| irreversible exposure reduction | Did SMERC identify actions with higher recoverability risk than the current workflow catches? |
| latency impact | Is the scoring path fast enough for the workflow class? |
| evidence usefulness | Do reason codes and controls help reviewers understand the decision? |

## Go / No-Go Gate

Continue only if:

- reviewers find the posture differences understandable,
- false release risk is acceptably low,
- latency fits the workflow,
- the customer can name at least one workflow where shadow-mode scoring would continue,
- the customer can identify who would own enforcement if the pilot succeeds.

Stop if:

- existing controls already answer recoverability well enough,
- reviewers cannot understand or use the outputs,
- metadata mapping is too expensive,
- the customer cannot identify an owner,
- SMERC creates review burden without reducing action risk.

## Evidence Boundary

This pilot proves only whether SMERC is useful for the tested workflow and metadata boundary. It does not prove production incident reduction, regulatory compliance, Microsoft validation, or broad enterprise readiness.

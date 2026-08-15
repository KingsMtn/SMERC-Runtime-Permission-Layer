# SMERC Evidence And Unknowns Program

## Purpose

SMERC cannot eliminate unknowns. This program makes important unknowns explicit, falsifiable, owned, and capable of limiting deployment. It prevents implementation volume, synthetic examples, or persuasive language from being mistaken for proof.

The executable registry is `examples/evidence_program/core_assumptions.json`. The evaluator is `reference_engine/evidence_program.py`.

## Unknown Classes

| Class | Question |
| --- | --- |
| Epistemic | Does the scoring mechanism correspond to real outcomes? |
| Adversarial | Can an agent manipulate the evidence or action envelope? |
| Operational | Can the integration enforce decisions reliably and quickly? |
| Normative | Do accountable reviewers agree with the encoded restraint? |
| Commercial | Will a qualified organization pay after measuring the result? |
| Regulatory | Is authority provenance sufficient for the governed workflow? |

## Evidence Rules

Every claim states its failure consequence, accountable role, risk level, and measurable criteria. An observation qualifies only when it:

- references an existing claim and criterion
- uses the criterion's exact metric
- meets the minimum sample size
- meets the minimum source-quality floor
- includes every required segment
- carries a dataset identifier, source type, and collection timestamp

Evidence below those requirements remains `INSUFFICIENT`; it does not partially satisfy the threshold. Synthetic observations demonstrate the evaluator but do not validate the product thesis.

Qualified observations are not overwritten by a newer convenient result. If qualified datasets disagree about a criterion, its status becomes `CONFLICTED` and the applicable deployment restriction remains in force.

## Deployment Ceiling

| Evidence condition | Maximum mode |
| --- | --- |
| Critical claim challenged | `STOP` |
| Critical claim unresolved | `OBSERVE` |
| High-risk claim challenged | `OBSERVE` |
| High-risk claim unresolved | `RECOMMEND` |
| Only moderate claims unresolved | `LIMITED_ENFORCE` |
| All registered claims supported | `CALIBRATED_ENFORCE` |

The ceiling is not a production certification. It is the most permissive mode the current evidence registry permits. Security review, legal review, integration controls, change approval, and domain-specific requirements remain separate gates.

## Core Claims

The first registry tests whether:

- irreversible exposure correlates with incident severity
- false releases remain within an approved tolerance
- descriptive metadata cannot routinely evade restraint
- qualified reviewers agree with recommendations
- adapters faithfully enforce returned controls
- high-impact actions carry verified authority provenance
- evaluation latency remains tolerable
- qualified pilots convert into paid continuation

## Running The Program

Baseline with no observations:

```bash
python -m reference_engine.evidence_program \
  examples/evidence_program/core_assumptions.json \
  examples/evidence_program/no_observations.json \
  --json-output reports/evidence_readiness_baseline.json \
  --markdown-output reports/SMERC_Evidence_Readiness_Baseline.md
```

Demonstrate contradiction handling with explicitly synthetic observations:

```bash
python -m reference_engine.evidence_program \
  examples/evidence_program/core_assumptions.json \
  examples/evidence_program/synthetic_observations.json
```

## Pilot Use

Before a pilot, the customer and SMERC team approve claim definitions, thresholds, sample requirements, reviewer qualifications, source-quality scoring, and segmentation. During the pilot, observations are appended without rewriting the criteria to fit outcomes. Any criterion change requires a new program version and written rationale.

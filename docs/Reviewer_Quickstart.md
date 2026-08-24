# Reviewer Quickstart

## Purpose

This is the shortest product-facing proof path in the repository.

It gives a security, platform, accelerator, or design-partner reviewer one command that generates a local review package connecting:

- PR Guardian posture output
- SPARTa routing
- Decision Lifecycle Ledger
- DLL Intelligence
- CISO seeded review decisions
- runtime benchmark comparison
- Ref-gated runtime proof showing hard evidence gates before recoverability scoring

## Run

From the repository root:

```bash
python -m reference_engine.reviewer_quickstart --pretty
```

Generated files are written to:

```text
reports/reviewer_quickstart/
```

Start with:

```text
reports/reviewer_quickstart/Reviewer_Quickstart_Report.md
```

## What To Look For

A reviewer should be able to answer:

1. What action was proposed?
2. What posture did SMERC return?
3. How did SPARTa route that posture?
4. What evidence was preserved?
5. Where does the benchmark differ from simple allow/deny?
6. Did hard evidence gates run before recoverability scoring?
7. What would a first shadow-mode pilot measure?

## Evidence Boundary

This quickstart proves local coherence. It does not prove production safety, customer demand, compliance readiness, or incident reduction.

Move from quickstart to pilot only when a real reviewer can name one side-effecting workflow, one review owner, and one measurable success criterion.

## Next Step: Customer Action Intake

If the reviewer understands the quickstart and wants to test fit, use:

```bash
python -m reference_engine.customer_action_intake examples/customer_action_intake_sample.json --pretty
```

Then replace the sample file with metadata-only examples from the prospect. Use `docs/Customer_Action_Intake.md` for the data boundary and review process.

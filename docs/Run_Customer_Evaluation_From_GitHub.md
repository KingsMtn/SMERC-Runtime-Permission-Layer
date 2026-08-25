# Run SMERC Runtime Evaluation From GitHub

## Purpose

This is the fastest public proof path for a reviewer who wants to see SMERC generate evaluation evidence without installing anything locally.

The workflow runs the repository's metadata-only sample actions through the customer-evaluation runner and uploads review artifacts from GitHub Actions.

## What To Click

1. Open the repository workflow:
   `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/customer-evaluations.yml`
2. Select **Run workflow**.
3. Set `evaluation_set` to `both`.
4. Start the run.
5. Open the completed run.
6. Download the artifact named `smerc-customer-evaluations`.

## What The Artifact Contains

The artifact includes generated JSON and Markdown reports for:

- the general customer-evaluation action set
- the financial runtime customer-evaluation action set, internally called SMERC-F
- a compact summary showing action counts, posture counts, route-state counts, Ref-gate counts, ledger validity, autonomy state, and pilot-fit result

## What This Proves

This proves that the public repository can execute a repeatable evaluation path and produce reviewable evidence from structured action metadata.

It demonstrates:

- metadata-only action intake
- Ref-gate checks
- SMERC posture evaluation
- execution-routing behavior, internally called SPARTa
- Decision Lifecycle Ledger evidence
- autonomy-budget impact
- generated reviewer reports

## What This Does Not Prove

This does not prove production safety, regulatory compliance, live incident reduction, customer demand, prompt-injection defense, or readiness to enforce inside a production workflow.

It is a public technical review path. A real customer pilot still needs one workflow owner, metadata-only customer examples, reviewer labels, success metrics, and a shadow-mode operating boundary.

## Flow

```text
Metadata-only action examples
  -> Ref-gate validation
  -> SMERC recoverability posture
  -> SPARTa execution route
  -> Decision Lifecycle Ledger evidence
  -> downloadable review artifact
```

## Recommended Reviewer Next Step

If the public workflow looks useful, replace the sample action set with 5 to 25 metadata-only actions from one customer workflow and run the same evaluation before discussing a shadow-mode pilot.

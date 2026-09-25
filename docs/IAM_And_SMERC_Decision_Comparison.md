# IAM and SMERC Runtime Assurance Decision Comparison

This report tests a narrow product claim:

> After an AWS identity is authorized for an action, SMERC Runtime Assurance adds a separate pre-execution judgment about whether current recovery evidence supports executing that action now and under what constraints.

The deterministic comparison holds the synthetic IAM result constant at `allowed` and changes only recovery evidence:

| Recovery evidence | IAM result | SMERC result |
| --- | --- | --- |
| Missing | `allowed` | `DENY` before normal governance |
| Stale | `allowed` | `FREEZE` before normal governance |
| Verified and scoped | `allowed` | `THROTTLE` / constrained execution after normal governance |

Run locally:

```powershell
python -c "from reference_engine.iam_smerc_decision_comparison import build_comparison, render_markdown; print(render_markdown(build_comparison()))"
```

## Interpretation

IAM authorization and SMERC runtime posture answer different questions. SMERC does not replace IAM, weaken an IAM denial, or claim that IAM cannot express contextual conditions. Its narrower role is to make recovery capability, freshness, scope, mutation limits, and rollback latency explicit at the execution boundary.

## Evidence Boundary

This is zero-spend, synthetic, metadata-only evidence. The IAM result is supplied policy-evaluation metadata, not a live AWS IAM Policy Simulator response or AWS attestation. The SMERC outcomes are deterministic local reference-engine results, not production validation.

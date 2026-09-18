# AWS Execution-Boundary Contrast

This validation asks whether SMERC treats the same action differently when its recoverability signals are unchanged but its execution boundary changes.

Two public-source-informed AWS action families are each evaluated twice:

- a bounded variant with restricted tools, hardened-container isolation, scoped private networking, and no known escape surface
- a broad variant with privileged automation, process-only isolation, production-network reachability, and cloud-metadata plus production-credential exposure

The action, tool, reversibility, containment score, rollback latency, evidence quality, impact scope, cancellation reliability, and authorization confidence remain identical within each pair. Boundary descriptions are controlled SMERC fixtures and are not observed AWS configurations.

## Run

```bash
python -m reference_engine.aws_boundary_contrast
```

The run writes a concise comparison plus the complete adapter and customer-evaluation evidence to `reports/aws_boundary_contrast/`.

## Required Result

For each pair, the broad-production variant must receive a strictly more restrictive posture than the bounded variant. The bounded path must not report incomplete execution-boundary evidence. The broad path must identify production-network and sandbox/credential exposure.

This is a differential regression test. It demonstrates that the current engine uses supplied boundary facts consistently; it does not prove those facts are true, that AWS enforcement exists, or that the posture thresholds are calibrated against customer outcomes.

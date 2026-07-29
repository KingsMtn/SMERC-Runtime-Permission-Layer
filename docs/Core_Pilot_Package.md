# Core Pilot Package

## Purpose

The core pilot package is the shortest complete path from interested prospect to pilot decision materials.

It runs the core review sequence in one command:

- prospect routing
- customer action intake
- pilot handoff checklist
- pilot evidence summary

## Run

```bash
python -m reference_engine.core_pilot_package --pretty
```

With reviewer-labeled sample metrics:

```bash
python -m reference_engine.core_pilot_package \
  --pilot-metrics examples/pilot_metrics_summary_sample.json \
  --pretty
```

Generated folder:

```text
reports/core_pilot_package/
```

Start with:

```text
reports/core_pilot_package/README.md
```

## Boundary

This package helps decide whether to start observe mode, continue observe mode, narrow, stop, or move to recommend mode.

It is not production certification, compliance attestation, proof of customer demand, proof of incident reduction, or approval for enforcement.

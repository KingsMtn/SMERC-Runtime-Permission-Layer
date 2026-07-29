# Pilot Evidence Summary

## Purpose

The pilot evidence summary is the executive wrapper around SMERC pilot materials.

It combines:

- prospect routing
- customer action intake
- pilot handoff checklist
- optional reviewer-labeled pilot metrics

The output is a single go/no-go style package that says whether the next step should be:

- `review_only`
- `start_observe`
- `continue_observe`
- `narrow`
- `move_to_recommend`
- `stop`

## Run

Before reviewer-labeled metrics exist:

```bash
python -m reference_engine.pilot_evidence_summary \
  --prospect-route reports/prospect_route_report.json \
  --customer-intake reports/customer_action_intake_report.json \
  --pilot-handoff examples/pilot_handoff_checklist.json \
  --pretty
```

With reviewer-labeled sample metrics:

```bash
python -m reference_engine.pilot_evidence_summary \
  --prospect-route reports/prospect_route_report.json \
  --customer-intake reports/customer_action_intake_report.json \
  --pilot-handoff examples/pilot_handoff_checklist.json \
  --pilot-metrics examples/pilot_metrics_summary_sample.json \
  --pretty
```

Generated outputs:

```text
reports/Pilot_Evidence_Summary.md
reports/pilot_evidence_summary.json
```

## Boundary

This is a pilot evidence summary, not production certification, compliance attestation, proof of customer demand, proof of incident reduction, or approval for enforcement.

It should be used to decide the next pilot mode, not to claim that SMERC is production-proven.

# Authorization-Afterlife Pilot Runner

The pilot runner connects the strict evidence intake to consequence-time reconciliation. A company can supply 1 to 25 metadata-only observations and receive deterministic `SETTLE`, `QUARANTINE`, `COMPENSATE`, or `DENY` decisions while preserving the declared evidence class, source digest, limitations, reasons, and required actions.

Run:

```text
python -m reference_engine.authorization_afterlife_pilot_runner examples/authorization_afterlife_evidence_manifest.json
```

The included example produces one current-authority settlement, one authority-epoch quarantine, and one revoked partial-effect compensation decision.

This is a self-run evaluation path, not a production enforcement agent. It evaluates supplied metadata and does not verify upstream truth, AWS attestation, customer production safety, or complete mediation of execution paths.

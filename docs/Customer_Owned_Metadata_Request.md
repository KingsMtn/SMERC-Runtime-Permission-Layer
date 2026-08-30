# Customer-Owned Metadata Request

This is the clean handoff from public proof to real reviewer evidence.

SMERC should ask external reviewers to replace the public examples with 5 to 25 safe metadata-only actions from one real workflow. The goal is to learn whether recoverability before execution changes reviewer judgment without asking for secrets, customer data, production logs, regulated payloads, or execution authority.

Run:

```bash
python -m reference_engine.customer_owned_metadata_request --workflow-family general --requested-actions 10 --pretty
```

Outputs:

- `reports/Customer_Owned_Metadata_Request.md`
- `reports/customer_owned_metadata_request.json`

## Work / Result / Impact

Work: ask a reviewer for safe metadata-only actions from one real workflow family.

Result: SMERC can compare customer-owned action metadata against its public examples, posture logic, SPARTa routes, postcondition evidence expectations, and local performance metrics.

Impact: this moves the project from synthetic proof toward reviewer-owned evidence without requesting production access, sensitive data, or enforcement authority.

## What To Ask For

Ask for 5 to 25 actions from one workflow family:

- AI-assisted code or deployment
- MCP tool calls
- cloud administration
- security-response automation
- support or customer operations automation
- payment, refund, treasury, stablecoin, tokenized-collateral, wallet-policy, or transaction-limit actions

For each action, request only metadata:

- action description
- actor or agent role
- tool family
- environment
- requested scope
- current reviewer or control outcome
- recoverability, containment, rollback, evidence, anomaly, impact, cancellation, and authorization scores
- hard-gate results for identity, attestation, least privilege, typed contract, and object shape

## Do Not Ask For

- secrets, keys, tokens, passwords, private keys, or wallet keys
- source code bodies, private prompts, or proprietary policies
- raw customer records, regulated transaction payloads, AML case files, or sanctions-screening records
- production logs, incident details, account numbers, or confidential infrastructure diagrams
- live credentials or authorization to execute production actions

## Where Performance Fits

Run the Serious Report Performance harness alongside the customer-owned metadata review:

```bash
python -m reference_engine.serious_report_performance --iterations 5 --pretty
```

This gives local p50, p95, and maximum timing for serious proof paths. Customer pilots still need their own production-environment timing, workflow-overhead, and reviewer-burden measurements.

## Reviewer Question

Does recoverability before execution change judgment enough on your own metadata to justify a bounded shadow-mode pilot?

## Evidence Boundary

Customer-owned metadata review is still pre-production and shadow-mode. It does not prove customer demand, incident reduction, compliance, production safety, or enforce-mode readiness.

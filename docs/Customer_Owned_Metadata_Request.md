# Customer-Owned Metadata Request

This is the clean handoff from public proof to real reviewer evidence.

SMERC should ask external reviewers to replace the public examples with 5 to 25 safe metadata-only actions from one real workflow. The goal is to learn whether recoverability before execution changes reviewer judgment without asking for secrets, customer data, production logs, regulated payloads, or execution authority.

Run:

```bash
python -m reference_engine.customer_owned_metadata_request --workflow-family general --requested-actions 10 --pretty
```

For AWS-style platform review:

```bash
python -m reference_engine.customer_owned_metadata_request --workflow-family aws --requested-actions 12 --pretty
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
- AWS AgentCore Runtime or Gateway tool calls, IAM execution-role changes, CloudFormation change sets, drift remediation, S3 policies, Secrets Manager rotation, RDS operations, cost-velocity actions, or cross-account delegation

For each action, request only metadata:

- action description
- actor or agent role
- tool family
- environment
- requested scope
- current reviewer or control outcome
- recoverability, containment, rollback, evidence, anomaly, impact, cancellation, and authorization scores
- hard-gate results for identity, attestation, least privilege, typed contract, and object shape

For AWS-style workflows, reviewers can also provide safe summary fields such as:

- source format
- AWS surface
- service family
- resource class
- region scope count
- identity scope summary
- permission-boundary presence
- dry-run, preview, change-set, checkpoint, and rollback-plan availability
- gateway-path enforcement and direct-runtime-path block status
- gateway-only path, gateway bypass, delegated on-behalf-of authority, principal type, session mode, tool discovery method, approval mode, and temporal policy context
- server-initiated elicitation, server-initiated sampling, progress notification, and message notification summaries
- expected CloudTrail, CloudWatch, AgentCore trace, runtime usage log, and tool-result metadata evidence
- cost-velocity and cost-anomaly signal summaries

## Do Not Ask For

- secrets, keys, tokens, passwords, private keys, or wallet keys
- source code bodies, private prompts, or proprietary policies
- raw customer records, regulated transaction payloads, AML case files, or sanctions-screening records
- production logs, incident details, account numbers, or confidential infrastructure diagrams
- live credentials or authorization to execute production actions
- AWS account IDs, ARNs, raw CloudTrail events, raw CloudWatch logs, raw trace bodies, private topology, or production commands
- permission to assume roles, inspect live accounts, execute change sets, modify IAM, access S3, rotate secrets, or change cross-account trust

## Where Performance Fits

Run the Serious Report Performance harness alongside the customer-owned metadata review:

```bash
python -m reference_engine.serious_report_performance --iterations 5 --pretty
```

This gives local p50, p95, and maximum timing for serious proof paths. Customer pilots still need their own production-environment timing, workflow-overhead, and reviewer-burden measurements.

## Reviewer Question

Does recoverability before execution change judgment enough on your own metadata to justify a bounded shadow-mode pilot?

AWS reviewer question:

Can one AWS-style workflow export safe action summaries and safe postcondition observations that prove preview, scope limit, checkpoint, rollback plan, gateway enforcement, block, replay, cost-velocity, and trace evidence without exposing secrets or raw customer logs?

## Evidence Boundary

Customer-owned metadata review is still pre-production and shadow-mode. It does not prove customer demand, incident reduction, compliance, production safety, or enforce-mode readiness.

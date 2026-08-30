# Cloud Admin Proof Pack

## Purpose

The Cloud Admin Proof Pack shows how SMERC evaluates AI/devops cloud-administration actions before they change infrastructure, permissions, routing, data, or recovery posture.

This is the clearest infrastructure proof path for cloud platforms, SRE teams, DevOps teams, CI/CD platform owners, and AI-agent platform teams.

The core question is:

> Can a team let autonomous agents move faster while still throttling, freezing, denying, or escalating actions that are not recoverable enough to execute?

## What It Runs

The proof pack expands the existing Cloud Admin Customer Evaluation into 24 metadata-only scenarios:

- base scenario
- degraded evidence scenario
- expanded scope scenario

It covers:

- IAM permission expansion
- network-boundary changes
- database-cluster deletion
- Kubernetes rollout
- DNS cutover
- service authentication rotation
- capacity reduction
- backup-retention changes

## What The Report Adds

The report adds cloud-specific reason codes:

- `IAM_SCOPE_EXPANSION`
- `NETWORK_BOUNDARY_WIDENING`
- `DATA_PLANE_DESTRUCTIVE_ACTION`
- `KUBERNETES_ROLLOUT_UNDER_PRESSURE`
- `DNS_TRAFFIC_CUTOVER`
- `SECRET_OR_AUTH_ROTATION`
- `BACKUP_RETENTION_RECOVERY_RISK`
- `PRODUCTION_BLAST_RADIUS_WIDE`
- `ROLLBACK_UNCERTAIN`
- `EVIDENCE_INCOMPLETE`
- `CANCEL_RELIABILITY_WEAK`
- `AUTONOMY_SCOPE_PRESSURE`

Each record includes:

- Ref-gate result
- SMERC posture
- SPARTa route
- irreversible exposure score
- cloud reason codes
- Decision Lifecycle Ledger validity
- Work / Result / Impact explanation

## Run

```bash
python -m reference_engine.cloud_admin_proof_pack --pretty
```

Outputs:

```text
reports/cloud_admin_proof_pack/Cloud_Admin_Proof_Pack.md
reports/cloud_admin_proof_pack/cloud_admin_proof_pack.json
```

## What A Reviewer Should Look For

Useful signals:

- existing authorization would permit broad cloud action, but SMERC constrains it
- rollback is weak or slow, so SMERC freezes or denies the action
- Ref-gate evidence fails before scoring can support execution
- SPARTa translates posture into a concrete route such as block or constrained execute
- the Decision Lifecycle Ledger preserves the decision path for audit review

## Boundary

This is metadata-only proof. It does not connect to AWS, Azure, Google Cloud, Cloudflare, Kubernetes, Terraform state, DNS providers, databases, secrets managers, production logs, or customer infrastructure.

It does not prove cloud-provider certification, production enforcement readiness, incident reduction, compliance, or replacement for IAM, OPA, Terraform policy, Kubernetes RBAC, CI approvals, SIEM, or human accountability.

## Customer Next Step

If the generated report is useful, the next test is:

```text
one cloud workflow family -> 10 to 25 metadata-only customer actions -> SMERC shadow-mode scoring -> reviewer labels -> pilot-fit decision
```

Good first workflow families:

- production IAM changes
- infrastructure-as-code applies
- Kubernetes rollouts
- DNS or traffic routing
- database administration
- network-policy updates
- secret or service-auth rotation
- backup and recovery policy changes

# Policy Calibration And Evidence Provenance

## Purpose

SMERC decisions must identify both the policy that produced them and the evidence permitted to justify deployment. This layer addresses two risks:

1. Treating one global threshold set as correct for every tenant and workflow.
2. Allowing untraceable or mutable observations to advance enforcement readiness.

## Runtime Policy Bundles

`smerc.policy.v1` binds a tenant to:

- policy ID and revision
- operating mode: `OBSERVE`, `RECOMMEND`, or `ENFORCE`
- evidence program and current evidence ceiling
- unavailable-service behavior
- approving role and effective timestamp
- all thresholds used to select runtime posture

Every decision and replay record includes the policy ID, revision, mode, evidence ceiling, and deterministic SHA-256 policy hash. This lets a reviewer reproduce which policy configuration governed an action.

The registry selects the latest policy revision whose effective timestamp has passed. A configured tenant with only future-dated policies fails startup rather than silently falling back to the reference policy. Tenants without a configured policy use the clearly identified reference policy in `OBSERVE` mode.

## Calibration Safeguards

- `ENFORCE` requires an evidence ceiling of at least `LIMITED_ENFORCE`.
- `ENFORCE` requires fail-closed service behavior.
- Denial thresholds cannot be less restrictive than related throttle or freeze boundaries.
- Unknown fields and incomplete threshold sets are rejected.
- Policies are selected from authenticated tenant identity, not request-supplied policy IDs.
- Future revisions do not activate early.

These checks establish configuration coherence. They do not prove that the chosen thresholds are empirically correct.

## Evidence Provenance Ledger

`smerc.evidence-ledger.v1` creates one record per observation containing:

- exact observation SHA-256 digest
- source-artifact SHA-256 digest
- collector identity and collection method
- timezone-qualified record timestamp
- previous-record hash
- record hash and authentication method

The verifier requires an exact one-to-one relationship between observations and ledger records. It rejects missing observations, duplicates, reordered sequences, altered observations, broken chains, invalid head hashes, mixed authentication methods, and incorrect HMAC keys.

## Provenance Strength

| Provenance state | Maximum evidence-supported deployment |
| --- | --- |
| Unverified observations | `OBSERVE` |
| SHA-256 chain verified | `RECOMMEND` |
| HMAC-SHA-256 chain authenticated | Evidence-derived ceiling |

A hash chain detects later mutation when a trusted head hash is retained elsewhere. By itself, it does not establish who created the ledger. HMAC authentication adds shared-key authenticity, but it is not public-key nonrepudiation and does not prove that the source artifact was accurate. Enterprise deployments still require managed secrets, collector identity, source-system controls, and independent artifact retention.

## Commands

Evaluate an action under a tenant policy:

```bash
python -m reference_engine.recoverability_engine \
  examples/recoverability_single_action.json \
  --policy examples/policies/alpha_conservative.json \
  --pretty
```

Build and verify a hash-chain demonstration:

```bash
python -m reference_engine.evidence_provenance build \
  examples/evidence_program/synthetic_observations.json \
  examples/evidence_program/synthetic_artifact_digests.json \
  reports/synthetic_evidence_ledger.json \
  --program-id smerc-core-validation-v1 \
  --collector-id synthetic-collector \
  --collection-method synthetic-demonstration

python -m reference_engine.evidence_provenance verify \
  examples/evidence_program/synthetic_observations.json \
  reports/synthetic_evidence_ledger.json
```

For HMAC authentication, add `--hmac-key-env SMERC_EVIDENCE_HMAC_KEY` to both commands. The environment value must contain at least 32 characters and must never be committed.

Run the evidence report with provenance admission:

```bash
python -m reference_engine.evidence_program \
  examples/evidence_program/core_assumptions.json \
  examples/evidence_program/synthetic_observations.json \
  --ledger reports/synthetic_evidence_ledger.json
```

## API Deployment

Set `SMERC_POLICY_DIR` to a directory containing one or more validated JSON policy revisions. The API resolves policies by the tenant attached to the bearer key. Policy files are loaded at startup; operational policy changes require controlled replacement and service restart in this reference implementation.

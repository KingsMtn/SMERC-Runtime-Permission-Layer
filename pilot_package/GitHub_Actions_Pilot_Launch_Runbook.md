# SMERC GitHub Actions Pilot Launch Runbook

## Purpose

This runbook turns the SMERC pilot package into a concrete first deployment path for a design partner. It is written for security architects, platform engineering leaders, DevSecOps teams, and AI governance owners who want to test whether recoverability-aware runtime scoring is useful before AI-assisted workflows create side effects.

The first launch path is GitHub Actions shadow-mode scoring. SMERC observes proposed workflow actions, returns a posture, stores replayable evidence when the remote API is used, and allows the customer to compare SMERC recommendations with existing reviewer judgment.

This runbook is not production certification. It is a bounded pilot procedure for collecting evidence.

## Pilot Boundary

Use the pilot only for metadata about proposed actions:

- workflow name
- repository or service identifier
- action type
- environment
- actor or automation class
- impact scope
- reversibility
- rollback latency
- containment strength
- evidence validity
- anomaly pressure

Do not send production secrets, raw customer records, proprietary source code, private prompts, credentials, or regulated data into the first pilot unless the customer has separately approved storage, access control, retention, and legal handling.

## Launch Modes

| Mode | Customer effect | Recommended use |
| --- | --- | --- |
| `observe` | SMERC scores and reports only. It does not fail the workflow. | Start here. |
| `recommend` | SMERC surfaces posture, controls, and reviewer guidance. It still should not block production until the customer approves. | Use after initial reviewer agreement exists. |
| `enforce` | SMERC fails selected postures. | Use only after calibration, security review, rollback proof, and written approval. |

The first customer pilot should begin in `observe`.

## Recommended First Workflow

Start with one workflow where recoverability matters and existing review already exists:

- production deployment workflow
- infrastructure change workflow
- privileged automation workflow
- database migration workflow
- AI-assisted code generation or pull-request automation workflow

Do not start with the highest-risk production workflow. Start where the customer can compare SMERC output against human judgment without introducing a new blocking dependency.

## Minimum Customer Setup

The customer should identify:

- one GitHub organization or repository
- one workflow to observe
- one security owner
- one platform engineering owner
- one reviewer group
- one pilot tenant name
- whether the pilot uses local scoring, remote API scoring with static credentials, or remote API scoring with GitHub OIDC
- retention period for decision artifacts
- reviewer meeting cadence
- stop conditions

## Option A: Local Shadow Mode

Local mode is the easiest way to see SMERC output without deploying the API. It does not persist tenant-scoped audit records in the SMERC API.

```yaml
name: SMERC Local Shadow Mode

on:
  workflow_dispatch:
  pull_request:

jobs:
  smerc-local-shadow:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Evaluate proposed action
        id: smerc
        uses: KingsMtn/SMERC-Runtime-Permission-Layer/integrations/github_actions@COMMIT_SHA
        with:
          action-file: integrations/github_actions/sample_action_request.json
          source: local
          mode: observe
          output-file: smerc-decision.json

      - name: Upload SMERC decision report
        uses: actions/upload-artifact@v4
        with:
          name: smerc-decision
          path: smerc-decision.json
          retention-days: 14
```

For a real customer repository, replace the sample action file with a generated metadata file describing the proposed workflow action. Pin `COMMIT_SHA` to a reviewed SMERC commit before use.

## Option B: Remote Shadow Mode With Static Credential

Remote mode calls the SMERC Pilot API, persists tenant-scoped decisions, and supports review metrics. Use scoped principals instead of legacy all-scope keys.

GitHub repository configuration:

| Type | Name | Purpose |
| --- | --- | --- |
| Secret | `SMERC_API_KEY` | Scoped `actions.evaluate` credential for this workflow. |
| Variable | `SMERC_API_URL` | HTTPS URL of the deployed SMERC Pilot API. |

```yaml
name: SMERC Remote Shadow Mode

on:
  workflow_dispatch:

jobs:
  smerc-remote-shadow:
    runs-on: ubuntu-latest
    environment: production
    permissions:
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Evaluate through SMERC API
        id: smerc
        uses: KingsMtn/SMERC-Runtime-Permission-Layer/integrations/github_actions@COMMIT_SHA
        env:
          SMERC_API_KEY: ${{ secrets.SMERC_API_KEY }}
        with:
          action-file: examples/recoverability_single_action.json
          source: remote
          api-url: ${{ vars.SMERC_API_URL }}
          tenant: platform-team
          mode: observe
          api-failure-policy: report
          output-file: smerc-decision.json

      - name: Upload SMERC decision evidence
        uses: actions/upload-artifact@v4
        with:
          name: smerc-decision
          path: smerc-decision.json
          retention-days: 14
```

## Option C: Remote Shadow Mode With GitHub OIDC

OIDC removes the stored SMERC API key from the evaluated workflow. It requires a deployed SMERC API with an exact `SMERC_GITHUB_OIDC_TRUST` policy and a configured `SMERC_ACCESS_TOKEN_KEY`.

```yaml
name: SMERC OIDC Shadow Mode

on:
  workflow_dispatch:

jobs:
  smerc-oidc-shadow:
    runs-on: ubuntu-latest
    environment: production
    permissions:
      contents: read
      id-token: write
    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Evaluate through GitHub OIDC-authenticated SMERC API
        id: smerc
        uses: KingsMtn/SMERC-Runtime-Permission-Layer/integrations/github_actions@COMMIT_SHA
        with:
          action-file: examples/recoverability_single_action.json
          source: remote
          api-url: ${{ vars.SMERC_API_URL }}
          auth-mode: github-oidc
          tenant: platform-team
          mode: observe
          api-failure-policy: report
          output-file: smerc-decision.json
```

OIDC proves signed GitHub workload identity claims for the configured workflow. It does not prove the workflow is safe, the runner is uncompromised, or the proposed action is desirable.

## Required Evidence Collection

Each week, collect:

- number of scored actions
- posture distribution
- unavailable evaluation count
- reviewer agreement rate
- override rate
- false release candidates
- false constraint candidates
- approval latency impact
- action categories with highest irreversible exposure
- controls most often recommended
- examples where SMERC changed the discussion

Use `pilot_package/Weekly_Review_Template.md` to record the weekly review.

## Stop Conditions

Pause or stop the pilot if:

- the workflow sends sensitive payloads outside the approved metadata boundary
- SMERC produces confusing recommendations that reviewers cannot evaluate
- unavailable evaluations are frequent enough to make the pilot noisy
- reviewers do not agree on what false release and false constraint mean
- pilot artifacts are retained outside the approved period
- customer security owners decide the control point adds unacceptable operational risk

## Go/No-Go Decision

At the end of the first phase, the customer should decide one of four outcomes:

- **Stop**: recoverability scoring did not add useful signal.
- **Narrow**: continue on a smaller or different workflow.
- **Continue observe**: collect more evidence before recommendation mode.
- **Move to recommend**: show SMERC controls to reviewers during normal approval.

Do not move to enforcement because a synthetic report looks promising. Enforcement requires customer pilot evidence, calibrated thresholds, rollback proof, and approval from the customer's security and platform owners.

## Evidence Package To Produce

The pilot should produce:

- launch scope and data boundary
- workflow configuration used during the pilot
- sample decision reports
- weekly review notes
- decision distribution
- reviewer agreement and override metrics
- false release and false constraint analysis
- latency observations
- recommended next mode
- unresolved security, privacy, legal, and operational questions

The evidence package should clearly distinguish customer-observed data from synthetic examples and illustrative values.


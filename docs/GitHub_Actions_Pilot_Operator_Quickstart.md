# GitHub Actions Pilot Operator Quickstart

## Purpose

This is the shortest operator path for a company that wants to test SMERC against one GitHub Actions workflow.

The pilot question is:

> Can SMERC run in observe mode against one workflow, score recoverability-aware action posture, and produce evidence reviewers can compare with existing judgment?

This is not a production rollout, compliance attestation, or enforcement approval.

## Who This Is For

- CISO or deputy CISO deciding whether a shadow-mode pilot is worth approving
- security architect defining the metadata boundary
- platform engineering owner installing the GitHub Actions workflow
- DevSecOps reviewer comparing SMERC output with existing review
- AI governance lead evaluating whether recoverability is a useful runtime signal

## Week-Zero Checklist

Before installing anything, confirm:

- one selected repository or workflow family
- one accountable security owner
- one accountable platform owner
- one reviewer group
- metadata-only action descriptions
- no production secrets, raw customer records, private prompts, full proprietary source code, or regulated payloads
- observe mode only
- decision artifact retention period
- weekly review cadence
- stop conditions
- day-30 go/no-go criteria

Generate the machine-readable readiness report:

```bash
python -m reference_engine.github_actions_pilot_readiness --pretty
```

Expected outputs:

- `reports/github_actions_pilot_readiness.json`
- `reports/GitHub_Actions_Pilot_Readiness.md`

## Install Path

Start with local shadow mode when the team only wants to inspect output shape:

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

Use remote API mode when the team wants tenant-scoped audit records, review metrics, and API-backed evidence. Prefer GitHub OIDC when the SMERC Pilot API has an exact trust policy configured.

Do not use enforcement mode in the first pilot.

## What The Action File Should Contain

The action file should describe the proposed workflow action, not the underlying secret, prompt, source code, or customer payload.

Minimum useful fields:

- action description
- action category
- environment
- impact scope
- reversibility
- rollback latency
- containment strength
- evidence validity
- anomaly pressure

Use `integrations/github_actions/sample_action_request.json` for local mode and `examples/recoverability_single_action.json` for remote API mode.

## What To Collect Weekly

- scored action count
- posture distribution
- unavailable evaluation count
- reviewer agreement rate
- override rate
- false release candidates
- false constraint candidates
- latency observations
- top reason codes
- top recommended controls
- examples where SMERC changed the review discussion

Use `pilot_package/Weekly_Review_Template.md` for the weekly review.

## Summarize Artifacts

After downloading `smerc-decision.json` artifacts into one directory:

```bash
python -m reference_engine.github_actions_pilot_summary downloaded-smerc-decisions \
  --json-output reports/github_actions_pilot_artifact_summary.json \
  --markdown-output reports/GitHub_Actions_Pilot_Artifact_Summary.md
```

This summary reports artifact distribution. It does not measure false release, false constraint, reviewer agreement, or incident reduction unless the customer separately supplies reviewer labels and outcome evidence.

## Day-30 Decision

Choose one:

| Outcome | Meaning |
| --- | --- |
| Stop | Recoverability scoring did not add useful signal. |
| Narrow | Continue on a smaller or different workflow. |
| Continue observe | More evidence is needed before showing recommendations in normal review. |
| Move to recommend | Show SMERC posture and controls to reviewers during normal approval. |

Do not move to enforcement without customer-specific calibration, rollback proof, security review, and written approval from accountable owners.

## Related Files

- `pilot_package/GitHub_Actions_Pilot_Launch_Runbook.md`
- `pilot_package/First_Pilot_Path.md`
- `integrations/github_actions/README.md`
- `docs/GitHub_OIDC_Operations.md`
- `docs/API_Deployment_Guide.md`
- `pilot_package/Go_No_Go_Criteria.md`

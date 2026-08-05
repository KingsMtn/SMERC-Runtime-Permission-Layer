# SMERC GitHub PR Guardian

## Purpose

SMERC GitHub PR Guardian is the developer-facing wedge for SMERC.

It turns recoverability-aware runtime permission scoring into a visible pull-request artifact:

> Before an AI-assisted change is merged or deployed, SMERC comments on the PR with posture, risk, confidence, reason codes, controls, replay ID, and a decision certificate digest.

## Why This Matters

AI coding agents can now propose code, deployment, configuration, secret, permission, and infrastructure changes faster than traditional review workflows can reason about side effects.

Existing controls usually ask:

- Is the actor allowed?
- Did tests pass?
- Is branch protection satisfied?
- Did a reviewer approve?

SMERC PR Guardian adds:

- Is this action recoverable enough to proceed?
- What controls should apply before merge or deployment?
- Is the decision replayable?
- Did the workflow preserve a certificate that reviewers can inspect later?

## What It Produces

The PR Guardian renderer creates:

- `smerc-pr-comment.md`
- `smerc-pr-certificate.json`

The comment is designed to be posted on a pull request. The certificate is a hash-bound pilot artifact with:

- posture
- mode and source
- integration status
- replay ID
- risk and confidence scores
- reason codes
- controls
- action metadata
- GitHub event metadata
- boundary language
- deterministic certificate digest

## Example

```bash
python integrations/github_actions/run_smerc_gate.py \
  --action-file integrations/github_actions/sample_action_request.json \
  --mode observe \
  --output-file smerc-decision.json

python integrations/github_pr_guardian/pr_guardian.py \
  --decision-report smerc-decision.json \
  --action-file integrations/github_actions/sample_action_request.json \
  --comment-output smerc-pr-comment.md \
  --certificate-output smerc-pr-certificate.json
```

## GitHub Workflow

See:

- `examples/github_pr_guardian/pr_guardian_workflow.yml`

## End-To-End Demo

To see PR Guardian in the full SMERC loop, run:

```bash
python -m reference_engine.end_to_end_pr_guardian_demo --pretty
```

That creates `reports/End_To_End_PR_Guardian_Demo.md` plus JSON artifacts for the runtime decision, PR certificate, SPARTa route, Decision Lifecycle Ledger, and DLL Intelligence summary.

That example evaluates a PR action, renders the comment and certificate, uploads artifacts, and posts or updates a sticky PR comment using `GITHUB_TOKEN`.

## First Pilot Use

Use PR Guardian in observe mode for:

- AI-generated pull requests
- production-impacting code changes
- auth and permission changes
- Terraform or infrastructure changes
- deployment workflow edits
- secret-management changes
- database migration proposals

The first pilot should compare SMERC comments against existing reviewer judgment. Enforcement should come only after enough customer-context decisions are reviewed.

## Boundary

SMERC PR Guardian is pilot-grade evidence for review. It does not replace:

- branch protection
- human code review
- security review
- deployment approvals
- IAM
- policy engines
- SIEM or audit retention
- human accountability

It is a visible review surface for recoverability-aware governance, not a production certification claim.

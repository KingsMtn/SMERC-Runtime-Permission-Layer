# SMERC GitHub PR Guardian

SMERC GitHub PR Guardian turns a runtime permission decision into a pull-request review artifact.

It is designed for AI-assisted coding, deployment, and infrastructure workflows where a reviewer needs a clear answer:

> Is this automated change recoverable enough to proceed?

## Outputs

PR Guardian produces:

- a Markdown PR comment body
- a hash-bound `smerc.github-pr-guardian-certificate.v1` JSON artifact
- GitHub Action outputs for posture, certificate digest, comment path, and certificate path

The PR comment includes:

- SMERC posture
- risk and confidence scores
- replay ID
- proposed action
- recommendation
- required controls
- reason codes
- certificate digest
- evidence boundary

## Generate A Comment Locally

```bash
python integrations/github_actions/run_smerc_gate.py \
  --action-file integrations/github_actions/sample_action_request.json \
  --mode observe \
  --output-file smerc-decision.json

python integrations/github_pr_guardian/pr_guardian.py \
  --decision-report smerc-decision.json \
  --action-file integrations/github_actions/sample_action_request.json \
  --comment-output smerc-pr-comment.md \
  --certificate-output smerc-pr-certificate.json \
  --pretty
```

## GitHub Actions Example

See `examples/github_pr_guardian/pr_guardian_workflow.yml`.

The example:

1. evaluates the proposed action with SMERC
2. renders the PR Guardian comment and certificate
3. uploads both as workflow artifacts
4. optionally posts or updates a sticky PR comment using `GITHUB_TOKEN`

## Boundary

PR Guardian is pilot-grade review evidence. It does not replace branch protection, code review, security review, deployment approvals, SIEM, IAM, or human accountability.

Use it first in observe mode, then compare the comments against existing reviewer judgment before enforcement.

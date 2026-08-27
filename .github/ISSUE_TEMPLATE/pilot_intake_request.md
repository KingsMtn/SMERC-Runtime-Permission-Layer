---
name: Pilot intake request
about: Submit metadata-only action examples for a SMERC pilot intake review
title: "Pilot intake: "
labels: ["pilot-intake", "customer-evaluation"]
---

## Data Boundary

Do not include secrets, credentials, API keys, wallet keys, source code, private prompts, customer records, regulated payloads, production logs, or confidential incident details.

Use safe metadata only.

## Reviewer Perspective

Examples: CISO, security architect, platform engineer, AI governance lead, DevSecOps, financial risk reviewer, cloud workflow owner.

## Organization Type

Examples: enterprise SaaS, financial services, cloud platform, healthcare technology, security operations, internal platform team.

## Workflow Family

Choose one:

- GitHub Actions / CI-CD
- MCP tool calls
- cloud administration
- security response
- financial operations
- customer support automation
- other

## Current Governance Approach

Examples: manual approval, IAM plus ticket approval, allow/block policy, AI gateway, OPA/policy-as-code, CI/CD approval, security playbook, mixed controls, not clearly defined.

## Action Examples

Provide 5 to 25 metadata-only actions. For each action, include:

- action description
- actor or automated system
- tool/workflow/system
- current outcome: `ALLOW`, `BLOCK`, `REVIEW`, or `UNKNOWN`
- why current controls produce that outcome
- possible consequence if the action is wrong
- rollback or recovery path

Example:

```text
Action 1:
Description: AI release assistant requests a production canary deploy for a customer-facing API.
Actor/system: release_agent via GitHub Actions
Current outcome: ALLOW
Current reason: branch protection and deployment approval are satisfied
Possible consequence: limited customer-facing outage if the canary is bad
Rollback path: revert artifact and disable feature flag within 15 minutes
```

## Main Concern

What could go wrong if this workflow acts too quickly, too broadly, or without a reliable recovery path?

## What Would Make This Worth A Pilot?

Examples:

- SMERC identifies actions current controls allow but reviewers would want constrained.
- SMERC creates a useful middle state between allow and block.
- SMERC gives clearer reason codes, controls, and escalation paths.
- SMERC finds missing evidence before recoverability scoring.
- SMERC produces useful reviewer disagreement that can be measured in shadow mode.

## Preferred Next Step

Choose one:

- public GitHub discussion
- private follow-up outside GitHub
- run the sample intake locally first
- technical review only
- shadow-mode pilot discussion

## Relevant Links

- Pilot intake guide: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Pilot_Intake_Template.md
- Filled example input: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/examples/pilot_intake_filled_examples.json
- Filled example report: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/reports/pilot_intake/Filled_Pilot_Intake_Report.md
- Public intake page: https://admirable-sorbet-9986d5.netlify.app/pilot-intake

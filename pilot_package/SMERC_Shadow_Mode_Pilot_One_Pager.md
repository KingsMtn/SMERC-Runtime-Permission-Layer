# SMERC Shadow-Mode Pilot One-Pager

## Offer

SMERC provides a controlled shadow-mode assessment for AI-agent actions in GitHub Actions workflows.

## Buyer

Chief Information Security Officer, security engineering leader, platform engineering leader, AppSec leader, DevSecOps leader, or AI governance owner.

## Problem

AI agents and automation are moving closer to high-impact workflows: code changes, deployments, infrastructure updates, sensitive-data access, and operational process triggers. Existing controls often decide whether an identity or policy allows an action. They may not explicitly evaluate whether the action is recoverable, constrainable, or defensible under uncertainty.

## First Use Case

GitHub Actions shadow-mode scoring for AI-assisted code, deployment, and infrastructure workflows.

## What SMERC Does

Before a proposed action executes, SMERC returns a replayable posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

Decision reports include risk score, confidence score, reason codes, recommended constraints, and replay ID.

## Pilot Packages

| Package | Price | Scope |
| --- | ---: | --- |
| Technical Review | `$0-$2,500` | Repo review, integration walkthrough, feedback call, fit assessment. |
| 30-Day Shadow-Mode Pilot | `$7,500` | One GitHub Actions workflow, observe mode, weekly review, final findings report. |
| 90-Day Design Partner Pilot | `$25,000+` | Multiple workflows, observe/recommend/enforce-readiness, calibration support, executive report. |

## What Is Included

- GitHub Actions shadow-mode setup guidance
- action metadata review
- posture reports
- reason-code review
- weekly review for paid pilots
- final findings and enforcement-readiness recommendation

## What Is Not Included

- production enforcement before calibration
- compliance certification
- replacement of IAM, OPA, code review, branch protection, or existing approvals
- handling production secrets or raw customer data
- custom enterprise integrations outside agreed scope

## Success Metrics

- reviewer agreement rate
- false release rate
- false throttle/freeze/deny rate
- override rate
- approval latency impact
- useful constraint rate
- workflow improvements discovered

## Deployment Posture

SMERC should start in `observe` mode:

```text
workflow event -> action metadata -> SMERC score -> decision artifact -> reviewer comparison
```

Existing approvals remain authoritative during the first phase.

## Review Links

- CISO page: `https://admirable-sorbet-9986d5.netlify.app/ciso.html`
- Pilot page: `https://admirable-sorbet-9986d5.netlify.app/pilot.html`
- GitHub Actions page: `https://admirable-sorbet-9986d5.netlify.app/github-action.html`
- Repository: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer`

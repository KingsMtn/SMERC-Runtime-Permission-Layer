# Self-Service Pilot Hand-Off Email

## Purpose

Use this when a company shows interest but should not require the founder to explain or operate the entire pilot.

## Email

Subject:

```text
SMERC self-service GitHub Actions pilot path
```

Body:

```text
Hi [Name],

Thank you for taking a look at SMERC.

The lowest-friction way to evaluate it is a 30-day GitHub Actions shadow-mode pilot against one workflow. SMERC does not block execution during this phase. It scores proposed automated actions and produces recoverability posture, reason codes, controls, and replay evidence so your security and platform reviewers can compare SMERC output with existing judgment.

Start here:
https://admirable-sorbet-9986d5.netlify.app/self-service-pilot.html

GitHub repo:
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer

GitHub Actions pilot path:
https://admirable-sorbet-9986d5.netlify.app/github-action.html

External benchmark replay:
https://admirable-sorbet-9986d5.netlify.app/ilion-benchmark.html

The pilot should use metadata only. Please do not send secrets, credentials, raw source code, customer records, private prompts, regulated payloads, or full incident logs.

The first decision point is simple:

Can SMERC run in observe mode on one real workflow and produce recoverability evidence your reviewers find useful?

If yes, the next step is to complete the intake packet and identify one security owner, one platform owner, and one reviewer group.

Best,
[Name]
```

## Boundary

This email invites technical evaluation only. It is not a contract, legal approval, production enforcement authorization, compliance claim, or incident-reduction claim.

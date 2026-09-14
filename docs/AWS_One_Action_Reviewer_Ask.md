# AWS One-Action Reviewer Ask

## Purpose

Use this when asking an AWS-style platform, cloud-security, SRE, DevSecOps, FinOps, or AI-agent infrastructure reviewer for the smallest useful critique.

The goal is not adoption. The goal is to learn whether SMERC's recoverability posture matches how a real reviewer would handle one authorized-but-risky action before execution.

## Short Outbound Message

```text
Hi [Name], I am looking for a quick peer review of one AWS-style runtime action, not a sales conversation.

I am building SMERC, a metadata-only recoverability gate for AI-agent and cloud-automation actions. The narrow question is:

If an action is already authorized, should it still be allowed, throttled, frozen, denied, or escalated based on rollback path, blast radius, evidence quality, cost velocity, and containment?

Here is the one-action demo:
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/reports/aws_one_action_reviewer_demo/AWS_One_Action_Reviewer_Demo.md

The easiest sample is `AWS_ONE_RDS_CLUSTER_DELETE`, where SMERC returns `DENY`.

If you have 2 minutes, I am only looking for your gut check:

1. Would your team allow, throttle, freeze, deny, or escalate this kind of action?
2. What evidence would change your mind?
3. What field is missing from the review?

No account IDs, ARNs, logs, credentials, customer data, production commands, or live AWS access wanted.
```

## Slack Or Forum Version

```text
I am looking for a quick technical critique from AWS/cloud/security/SRE folks.

SMERC is a pre-execution recoverability gate. It asks whether an already-authorized AI-agent or cloud-automation action is recoverable enough to execute now.

The smallest review path is one metadata-only AWS-style action:
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/reports/aws_one_action_reviewer_demo/AWS_One_Action_Reviewer_Demo.md

Question: for `AWS_ONE_RDS_CLUSTER_DELETE`, would you allow, throttle, freeze, deny, or escalate it? What evidence would change that answer?

I am not asking for sensitive data or production access. I am trying to learn whether recoverability-before-execution is a real control gap or already covered well enough by existing cloud controls.
```

## Two-Minute Response Template

```text
Reviewer role:
Closest sample action:
My expected handling: ALLOW / THROTTLE / FREEZE / DENY / ESCALATE
SMERC output seems: useful / too strict / too loose / irrelevant / unclear
Evidence that would change my mind:
Missing field or signal:
Current tool or control that already handles this:
One action in my world that worries me:
```

## GitHub Issue Path

If the reviewer is willing to leave public feedback, ask them to use:

```text
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/issues/new?template=workflow-intake-template.md
```

If the reviewer is AWS-specific and willing to provide 5 to 25 safe metadata-only actions, use:

```text
https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/issues/new?template=aws_metadata_pilot_request.md
```

## What Not To Ask For

Do not ask for:

- account IDs
- ARNs
- credentials
- secrets
- raw logs
- packet payloads
- customer records
- private topology
- screenshots with identifiers
- production commands
- live AWS access

## How To Interpret Replies

| Reply Type | Meaning | Next Move |
| --- | --- | --- |
| "We would also deny this" | SMERC matches reviewer instinct on hard-stop risk. | Ask what evidence would move it from `DENY` to `FREEZE` or `THROTTLE`. |
| "Too strict" | Scoring may be overweighting irreversibility or weak evidence. | Ask which field should lower the posture. |
| "Too loose" | Scoring may underweight blast radius, identity, data sensitivity, or audit delay. | Ask which field should force `FREEZE`, `DENY`, or `ESCALATE`. |
| "Already handled" | Category may overlap with existing control systems. | Ask which control handles recoverability and whether it produces pre-execution evidence. |
| "Interesting but needs real metadata" | Reviewer sees the gap but wants owned examples. | Send the AWS metadata pilot request link. |

## Fallback If No One Responds

If there is no useful response after 7 to 10 days, do not wait. Continue using:

- `examples/aws_one_action_reviewer_samples.json`
- `reports/aws_one_action_reviewer_demo/AWS_One_Action_Reviewer_Demo.md`
- `docs/AWS_Cloud_Action_Replay.md`
- `docs/AWS_Audit_Delay_And_Irreversibility_Map.md`
- `docs/Public_Agent_Runtime_Incident_Learning.md`

Then treat outside metadata as a bonus, not a blocker.

## Evidence Boundary

This ask is for review signal only. It does not prove AWS endorsement, AWS certification, customer demand, production readiness, incident reduction, compliance readiness, or willingness to pay.

# Why This Matters Now

## The Short Version

AI agents are moving from suggestion to execution.

They can call tools, deploy code, change infrastructure, modify permissions, trigger remediation, rotate credentials, scale compute, move data, and start financial or operational workflows.

Most existing systems answer important but incomplete questions:

| Existing Layer | Primary Question |
| --- | --- |
| IAM / identity | Who or what is allowed to act? |
| Policy engines | Does this request match policy? |
| Guardrails | Is the content or model output acceptable? |
| Sandboxes | Can the action be isolated? |
| Approval workflows | Did a person or process approve it? |
| Audit logs | What happened after execution? |

SMERC adds one missing pre-execution question:

> If this action is already authorized, is it recoverable enough to execute right now?

## Why Recoverability Is The Wedge

Authorization alone does not answer:

- Can this be rolled back?
- How wide is the blast radius?
- Is the evidence fresh enough?
- Can execution be paused or cancelled?
- Is cost velocity rising faster than task confidence?
- Does the route preserve postcondition evidence?
- Should the action slow down, narrow scope, pause, block, or escalate?

SMERC converts those questions into a runtime posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

## Why AWS-Style Cloud Automation Is First

AWS-style cloud automation is the clearest first wedge because the risk is visible:

- IAM changes can expand future authority.
- S3 policy changes can widen data exposure.
- CloudFormation changes can replace stateful resources.
- RDS cleanup can destroy data-plane assets.
- remediation loops can restart or mutate production systems.
- compute scaling can create financial velocity before humans notice.
- agent runtimes and gateways can move from model output to real side effects.

SMERC does not replace AWS controls. It complements them by asking whether the action is recoverable before execution and whether the route produced evidence after execution.

## The Reviewer Proof Path

Start small:

```bash
python -m reference_engine.aws_one_action_reviewer_demo --action-id AWS_ONE_RDS_CLUSTER_DELETE --pretty
```

Then inspect:

- `reports/aws_one_action_reviewer_demo/AWS_One_Action_Reviewer_Demo.md`
- `docs/AWS_One_Action_Reviewer_Ask.md`

If the one-action review is useful, move to:

- `docs/Tier2_AWS_Reviewer_Front_Door.md`
- `docs/AWS_Cloud_Action_Replay.md`
- `docs/AWS_Metadata_Intake_Contract.md`
- `docs/AWS_Postcondition_Evidence.md`

## What Would Make This More Valuable

The next useful evidence is not more founder explanation. It is reviewer judgment.

Useful outside signals:

- a platform reviewer says SMERC posture matches their instinct
- a reviewer says SMERC is too strict and names which field is overweighted
- a reviewer says SMERC is too loose and names the missing evidence
- a reviewer provides 5 to 25 metadata-only actions from one workflow
- a reviewer identifies an existing system that already handles recoverability better

## What This Does Not Prove

This brief does not prove production readiness, AWS endorsement, compliance, incident reduction, customer demand, willingness to pay, acquisition value, or that SMERC should replace existing cloud controls.

It explains why recoverability-before-execution is the current control question SMERC is built to test.

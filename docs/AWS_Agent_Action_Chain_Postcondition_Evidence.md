# AWS Agent Action Chain Postcondition Evidence

## Purpose

This proof extends the AWS Agent Action Chain from placement to verification.

The chain proof asks where SMERC fits:

`AI Agent Action -> Bedrock-style Guardrail -> SMERC Recoverability Gate -> Dynamic IAM / Systems Manager / Cloud Execution -> Postcondition Evidence`

This postcondition proof asks whether the required controls actually happened after SMERC routed the action.

## Evidence Boundary

This is AWS-style metadata-only proof. It does not connect to AWS, invoke Amazon Bedrock, modify Bedrock Guardrails, call IAM, run Systems Manager, apply CloudFormation, read CloudTrail, read CloudWatch, create infrastructure, change permissions, or prove AWS endorsement.

It models safe observation summaries that a reviewer could export without exposing account IDs, ARNs, raw logs, credentials, private topology, customer records, or production commands.

## Run It

```bash
python -m reference_engine.aws_agent_action_chain_postcondition --pretty
```

Generated outputs:

- `reports/aws_agent_action_chain_postcondition/AWS_Agent_Action_Chain_Postcondition_Evidence.md`
- `reports/aws_agent_action_chain_postcondition/aws_agent_action_chain_postcondition.json`

## What It Checks

- Whether blocked AWS-style actions stayed unexecuted
- Whether constrained actions recorded checkpoint, scope, preview, replay, execution report, and rollback-plan evidence
- Whether expected AWS-style evidence sources were present
- Whether missing evidence sources create a gap instead of a false pass
- Whether Decision Lifecycle Ledger evidence remains valid across the action chain

## Why It Matters

Guardrails and IAM can say an action appears acceptable or authorized. SMERC adds recoverability judgment. Postcondition evidence closes the loop by showing whether the required route controls were actually observed after the decision.

## Recommended Next Step

Ask an AWS-style platform reviewer for 5 to 25 safe action-chain examples and matching observation summaries so SMERC can compare guardrail status, IAM authorization, route controls, and postcondition evidence without live AWS access.

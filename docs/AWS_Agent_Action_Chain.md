# AWS Agent Action Chain

## Purpose

This proof makes the AWS-style SMERC placement explicit:

`AI Agent Action -> Bedrock-style Guardrail -> SMERC Recoverability Gate -> Dynamic IAM / Systems Manager / Cloud Execution -> Postcondition Evidence`

Bedrock-style guardrails can evaluate content, model behavior, prompts, responses, and tool intent. IAM can evaluate whether the caller is authorized. SMERC adds the pre-execution recoverability question before the cloud action executes: is this specific authorized action recoverable, bounded, evidenced, and safe to execute right now?

## Evidence Boundary

This is AWS-style metadata-only proof. It does not connect to AWS, invoke Amazon Bedrock, modify Bedrock Guardrails, call IAM, run Systems Manager, apply CloudFormation, read CloudTrail, read CloudWatch, create infrastructure, change permissions, or prove AWS endorsement.

It is designed to show where SMERC could sit as a recoverability-aware gate after content/model guardrails and before cloud execution.

## Run It

```bash
python -m reference_engine.aws_agent_action_chain --pretty
```

Generated outputs:

- `reports/aws_agent_action_chain/AWS_Agent_Action_Chain.md`
- `reports/aws_agent_action_chain/aws_agent_action_chain.json`

## What It Tests

- Agent action metadata after a Bedrock-style guardrail result
- IAM authorization state
- Dynamic IAM or Systems Manager execution context
- Rollback checkpoint state
- Expected postcondition evidence from CloudTrail-, CloudWatch-, change-set-, runtime-, or tool-result-shaped summaries
- SMERC posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- Governance Routing Workbench route state
- Decision Lifecycle Ledger validity

## Reviewer Question

If the content is acceptable and IAM says the agent is authorized, should the action still execute immediately?

SMERC helps answer that narrower question by checking recoverability before side effects occur.

## Recommended Next Step

Ask an AWS-style platform reviewer for 5 to 25 safe metadata-only action-chain examples that include guardrail status, authorization state, rollback checkpoint state, expected evidence, and whether the action created an irreversible or cost-sensitive side effect.

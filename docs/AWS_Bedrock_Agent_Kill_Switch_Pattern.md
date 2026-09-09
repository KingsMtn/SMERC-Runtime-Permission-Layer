# AWS Bedrock Agent Kill Switch Pattern

## Purpose

This pattern shows the cleanest AWS-style placement for SMERC:

`Bedrock-style Agent Action -> Action Group / Lambda-shaped Handler -> SMERC Recoverability Decision -> Route Control`

The goal is not to claim native AWS integration, AWS endorsement, AWS certification, or production readiness. The goal is to make the control point concrete enough that an AWS-style reviewer can see how recoverability-before-execution could sit between an authorized agent and a side-effecting tool call.

## Run The Local Handler

From the repository root:

```bash
python - <<'PY'
import json
from pathlib import Path
from reference_engine.aws_lambda_decision_handler import lambda_handler

event = json.loads(Path("examples/aws_lambda_decision_event.json").read_text())
print(json.dumps(lambda_handler(event), indent=2, sort_keys=True))
PY
```

Expected shape:

- `posture`: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- `route_state`: the Governance Routing Workbench route
- `required_controls`: the controls the action must satisfy before proceeding
- `ledger_valid`: whether Decision Lifecycle Ledger evidence was produced
- `evidence_boundary`: the no-live-AWS and no-endorsement boundary

## Work / Result / Impact

Work:

Evaluate a Lambda-backed action request with SMERC before the action creates cloud, data, customer-facing, or financial side effects.

Result:

The handler returns a compact decision envelope that a Bedrock Agent Action Group, gateway, or local reviewer could inspect before allowing a tool call to continue.

Impact:

This makes SMERC easier to evaluate as an agentic kill switch or action governor: content guardrails and IAM may permit the call, while SMERC can still slow, pause, block, or escalate it when recoverability is weak.

## What The Handler Accepts

The handler accepts either:

- a complete `smerc.customer-evaluation.v1` payload, or
- a single `action` object wrapped in an AWS-style event.

Use:

- `reference_engine/aws_lambda_decision_handler.py`
- `examples/aws_lambda_decision_event.json`

## What This Proves

- SMERC can be exposed through a Lambda-compatible entry point.
- SMERC can return a posture and route before a side-effecting action proceeds.
- SMERC can preserve a Decision Lifecycle Ledger ID and verification result.
- The proof can run locally with metadata only.

## What This Does Not Prove

- AWS endorsement
- AWS certification
- native Bedrock interception
- production enforcement
- live AWS account safety
- customer-validated incident reduction
- replacement for IAM, Bedrock Guardrails, AgentCore Gateway, CloudTrail, CloudWatch, AWS Config, or human accountability

## Best Next Reviewer Question

Can one AWS-style platform reviewer replace the example event with 5 to 25 safe action-group requests from one owned workflow and say whether the returned SMERC posture would have changed execution judgment?


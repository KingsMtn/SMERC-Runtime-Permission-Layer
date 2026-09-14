# AWS Decision API Surface

## Purpose

This is the next AWS proof step after the AWS ecosystem entry path.

It turns the SMERC AWS story into a small reviewable API surface:

- one metadata-only request
- one compact decision response
- one OpenAPI operation ID
- one Lambda-compatible handler
- one local report that proves the request and response work

This is not an AWS deployment, AWS Marketplace listing, AWS certification, AWS partnership claim, or production safety claim.

## Run It

```bash
python -m reference_engine.aws_decision_api_surface --pretty
```

The command writes:

- `reports/aws_decision_api_surface/aws_decision_api_surface.json`
- `reports/aws_decision_api_surface/AWS_Decision_API_Surface.md`
- `reports/aws_decision_api_surface/sample_decision_request.json`
- `reports/aws_decision_api_surface/sample_decision_response.json`

## Inspect These Files

- `reference_engine/aws_lambda_decision_handler.py`
- `schemas/smerc-aws-decision-api-openapi-v1.json`
- `examples/aws_lambda_decision_event.json`
- `reports/aws_decision_api_surface/AWS_Decision_API_Surface.md`

## API Shape

The OpenAPI contract exposes:

```text
POST /smerc/decision
operationId: evaluateAwsActionRecoverability
```

The request carries metadata-only action fields such as:

- actor
- tool
- action type
- base action risk
- reversibility
- containment strength
- rollback latency
- evidence validity
- anomaly pressure
- impact scope
- cancel reliability
- authorization confidence
- external side effect
- sensitive data flag

The response returns:

- posture
- route state
- executable flag
- required controls
- blocked controls
- scores
- ledger ID
- ledger head hash
- ledger verification result
- recommended next action
- explicit evidence boundary

## AWS Fit

This surface is intentionally narrow. It is meant to be legible to reviewers who understand:

- Lambda handlers
- API Gateway or Function URL JSON bodies
- Bedrock Agent Action Group pre-execution checks
- AgentCore Gateway-style OpenAPI tools
- metadata-only shadow-mode review

SMERC still does not call AWS from this proof path. The handler evaluates a supplied metadata object and returns a recoverability decision.

## Evidence Boundary

This proof does not:

- call AWS
- invoke Amazon Bedrock
- read CloudTrail or CloudWatch
- assume roles
- inspect secrets
- process raw logs
- modify IAM
- deploy infrastructure
- configure AgentCore
- list on AWS Marketplace
- prove AWS endorsement
- prove AWS certification
- prove production safety

## Work / Result / Impact

Work:

Convert the AWS lane from a strategy document into a reviewable Lambda/OpenAPI decision surface.

Result:

A reviewer can inspect a stable operation ID, run one local example, and see SMERC return posture, route controls, scores, and ledger evidence for a proposed AWS-style agent action.

Impact:

SMERC becomes easier to evaluate as a future Bedrock Action Group, AgentCore Gateway, or AWS-adjacent decision tool while preserving honest boundaries and avoiding premature cloud claims.

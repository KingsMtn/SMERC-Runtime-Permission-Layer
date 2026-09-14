# AWS Decision API Surface

Generated: `2026-09-14T01:23:39+00:00`
Version: `smerc.aws-decision-api-surface.v1`
Status: `reviewable_aws_decision_surface`
Handler version: `smerc.aws-lambda-decision-handler.v1`

## Purpose

This report packages SMERC as a small AWS-style decision API surface: one metadata-only request, one compact decision response, and one OpenAPI operation a reviewer can inspect before any live AWS integration exists.

## Contract

- OpenAPI: `schemas/smerc-aws-decision-api-openapi-v1.json`
- Operation ID: `evaluateAwsActionRecoverability`
- Sample request: `examples/aws_lambda_decision_event.json`
- Sample request ID: `AWS_BEDROCK_ACTION_GROUP_LAMBDA_001`

## Sample Decision

- Posture: `THROTTLE`
- Route state: `CONSTRAINED_EXECUTE`
- Executable: `True`
- Ledger valid: `True`
- Required controls: `6`
- Blocked controls: `0`

## Compatibility Targets

- AWS Lambda-compatible handler
- API Gateway or Function URL JSON body
- Bedrock Agent Action Group pre-execution decision check
- AgentCore Gateway-style OpenAPI tool surface
- local reviewer CLI proof without live AWS access

## Reviewer Runbook

1. Inspect schemas/smerc-aws-decision-api-openapi-v1.json.
2. Inspect examples/aws_lambda_decision_event.json.
3. Run python -m reference_engine.aws_decision_api_surface --pretty.
4. Confirm the response returns posture, route controls, scores, and ledger evidence.
5. Replace the sample with 5 to 25 metadata-only actions from one workflow when safe.

## Evidence Boundary

This Lambda-shaped handler is a local, metadata-only adapter. It does not call AWS, invoke Amazon Bedrock, read CloudTrail or CloudWatch, assume roles, modify IAM, execute CloudFormation, access S3, change RDS, rotate secrets, deploy infrastructure, or prove AWS endorsement, AWS certification, production safety, or incident reduction.

## Work / Result / Impact

- Work: Convert the AWS lane from a strategy document into a reviewable Lambda/OpenAPI decision surface.
- Result: A reviewer can inspect one request, one response, one operation ID, route controls, scores, and ledger evidence without live AWS access.
- Impact: SMERC becomes easier to evaluate as a future Bedrock Action Group, AgentCore Gateway, or AWS-adjacent decision tool while preserving honest boundaries.

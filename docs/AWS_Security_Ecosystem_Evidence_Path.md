# AWS Security Ecosystem Evidence Path

## Purpose

SMERC should speak the language AWS-style security and platform reviewers already use. This path describes how SMERC decision evidence could be exported into AWS-native review surfaces without claiming live integration today.

The useful direction is evidence export, not tool replacement.

## Candidate Evidence Destinations

SMERC decision records can be shaped for:

- Security Lake-style normalized security evidence
- EventBridge-style decision events
- Macie-style data exposure findings
- CloudTrail-style action summaries
- CloudWatch-style route and latency metrics
- Security Hub-style posture findings
- AWS Config-style change context
- ticketing or incident-review systems used by platform teams

## Suggested Event Shape

```json
{
  "source": "smerc.recoverability",
  "detail_type": "SMERCRecoverabilityDecision",
  "detail": {
    "action_id": "AWS_BEDROCK_ACTION_GROUP_LAMBDA_001",
    "posture": "THROTTLE",
    "route_state": "constrained",
    "required_controls": ["dry_run", "scope_limit", "checkpoint"],
    "aws_surface": "bedrock_agent_action_group",
    "environment": "production",
    "reason_codes": ["AGENTCORE_TOOL_SIDE_EFFECT", "ROLLBACK_UNCERTAIN"],
    "ledger_valid": true,
    "evidence_boundary": "metadata_only_no_live_aws_access"
  }
}
```

## Work / Result / Impact

Work:

Map SMERC posture, route, reason codes, required controls, and ledger verification into AWS-style security evidence streams.

Result:

An AWS-style reviewer can understand how SMERC output would coexist with CloudTrail, CloudWatch, Security Lake, EventBridge, Macie, AWS Config, Security Hub, IAM, and Bedrock-style guardrails.

Impact:

SMERC becomes easier to evaluate as a complementary recoverability signal: it does not replace security telemetry, but it can add pre-execution judgment and postcondition evidence to existing review workflows.

## What To Build Later

- JSON schema for SMERC security events
- local emitter that writes normalized event files
- optional EventBridge-compatible envelope
- optional Security Lake / OCSF-style mapping
- report showing which SMERC fields map cleanly and which need customer-owned metadata

## Current Boundary

This is an evidence-design path. It does not call AWS APIs, write to Security Lake, create EventBridge rules, inspect Macie findings, read CloudTrail, read CloudWatch, or prove AWS endorsement.


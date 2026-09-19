# AWS Postcondition Evidence

## Purpose

AWS Postcondition Evidence shows how SMERC could verify that required AWS-style controls actually happened after a route decision.

The AWS metadata adapter answers:

> What action is being proposed?

AWS postcondition evidence answers:

> After SMERC routed the action, can safe AWS-style observation metadata prove preview, scope limit, checkpoint, rollback plan, gateway enforcement, block, replay, cost velocity, and execution evidence actually existed?

## What It Uses

The checked-in example is metadata-only. It is modeled on public AWS documentation for observable surfaces such as:

- Amazon Bedrock AgentCore Gateway CloudTrail management events
- Amazon Bedrock AgentCore Gateway CloudTrail data events for `InvokeGateway` when explicitly enabled
- Amazon Bedrock AgentCore Runtime and Gateway CloudWatch logs, metrics, and spans
- AgentCore runtime usage logs with one-second CPU and memory usage fields
- AgentCore tool result metadata stream entries
- AgentCore Gateway MCP logging notifications
- native AWS change records such as IAM, CloudFormation, S3, Secrets Manager, and cost anomaly summaries
- gateway/session context such as gateway-only path, bypass detection, delegated on-behalf-of authority, temporal policy context, server-initiated elicitation, and MCP progress/message notifications

It does not read live AWS accounts, call AWS APIs, collect raw CloudTrail, collect raw CloudWatch logs, expose account IDs, expose ARNs, or prove AWS production enforcement.

The report separates **route satisfaction** from **evidence assurance**. A sample or reviewer-supplied observation may satisfy every expected route control while still being `modeled_unverified`. Such a row is not proof-eligible until a trusted adapter or native-record verifier authenticates the evidence and binds it to the governed action.

An authenticated SMERC evidence-provenance ledger can promote matching rows to `authenticated_provenance`. The ledger must hash-bind every normalized observation and pass HMAC verification; changing an observation after collection invalidates the chain.

## Run It

```bash
python -m reference_engine.aws_postcondition_evidence --pretty
```

To verify an authenticated observation ledger before reporting:

```bash
export SMERC_AWS_EVIDENCE_HMAC="replace-with-a-secret-of-at-least-32-characters"
python -m reference_engine.aws_postcondition_evidence \
  --provenance-ledger path/to/aws-postcondition-ledger.json \
  --hmac-key-env SMERC_AWS_EVIDENCE_HMAC \
  --pretty
```

Generated outputs:

- `reports/aws_postcondition_evidence/AWS_Postcondition_Evidence_Report.md`
- `reports/aws_postcondition_evidence/aws_postcondition_evidence_report.json`

## Work / Result / Impact

Work: compare SMERC/SPARTa route controls for AWS-style actions against safe postcondition observations modeled on CloudTrail, CloudWatch, AgentCore Gateway, AgentCore Runtime, MCP gateway logs, and native AWS change records.

Result: the report identifies pass and gap statuses where controls or expected AWS evidence sources are missing.

Impact: SMERC can show how an AWS-style governed action bot would prove that controls were actually applied after a decision, not only that recoverability scoring recommended them.

## Why This Matters

Cloud platforms already have many useful logs, metrics, traces, event streams, and policy records. The gap SMERC is targeting is the connection between:

1. the action requested by an agent or automation,
2. the recoverability decision before execution,
3. the controls required by the route,
4. the postcondition evidence that proves those controls happened, and
5. the replayable report a platform team can review later.

That is especially relevant for AWS-style agentic cloud automation because an authorized agent can still create expensive, destructive, or difficult-to-reverse side effects if preview, scope, rollback, gateway routing, and cost-velocity evidence are weak.

## Reviewer Question

For one AWS-style workflow, can the platform export safe observation metadata that proves preview, scope limit, checkpoint, rollback plan, gateway enforcement, execution block, replay, cost-velocity, and trace evidence without exposing secrets or raw customer logs?

# AWS Marketplace Validation Path

## Purpose

AWS Marketplace packaging is a later validation path, not the immediate build priority.

The current priority is to prove SMERC can evaluate AWS-style action metadata, return useful posture decisions, preserve evidence, and help reviewers replace examples with safe customer-owned metadata. Marketplace packaging only matters after that proof is credible.

For the broader AWS ecosystem route from GitHub proof to practitioner review to future AgentCore Gateway, AgentCore Runtime, Marketplace, or Partner path, read `docs/AWS_Ecosystem_Entry_Path.md`.

## Future Package Shape

A future AWS-style package could include:

- Lambda-compatible SMERC decision handler
- CloudFormation or Terraform deployment example
- metadata-only shadow-mode configuration
- sample Bedrock Agent Action Group contract
- EventBridge-compatible decision event envelope
- no-credentials local review mode
- commercial-use license boundary

If shaped for an AgentCore Runtime-style package, the future package would also need:

- containerized runtime surface
- health endpoint such as `/ping`
- invocation endpoint such as `/invocations`
- clear non-secret logging policy
- cold-start and timeout notes
- concurrency and fallback behavior
- support/contact information
- pricing and commercial-use terms
- documentation that explains exactly what metadata SMERC consumes and what it refuses

If shaped for an AgentCore Gateway-style tool, the future package would need:

- OpenAPI 3.0 or 3.1 description with operation IDs
- HTTPS server endpoint
- simple JSON request and response bodies
- no complex security schemes embedded in the OpenAPI document
- clear MCP/tool-call metadata boundary
- explicit statement that SMERC is a decision and evidence layer, not the cloud control plane itself

These are packaging targets, not current claims.

## Validation Sequence

1. Run the local AWS reviewer bundle.
2. Run the Lambda-shaped decision handler with metadata-only examples.
3. Replace examples with 5 to 25 safe customer-owned action summaries.
4. Confirm whether SMERC changes reviewer judgment.
5. Add matching postcondition observations for the same workflow.
6. Measure local and pilot latency.
7. Only then consider Marketplace-style packaging or a cloud-native deployment example.

## Trigger To Start Packaging

Do not start Marketplace packaging because the idea is exciting.

Start packaging only when at least one outside reviewer can say:

- the AWS reviewer bundle was understandable in under 10 minutes
- the metadata replacement path was safe enough to try
- SMERC produced at least one useful difference from existing controls
- the postcondition evidence model was understandable
- the commercial boundary was clear

Until then, the better use of effort is proof, reviewer-owned metadata, and outreach.

## Work / Result / Impact

Work:

Define what a future AWS Marketplace-ready SMERC package would need to include without pretending the current repo is already a commercial AWS product.

Result:

Reviewers can see the path from local proof to customer-owned metadata review to shadow-mode pilot to packaging.

Impact:

The project stays honest while still showing a credible route toward AWS-style customer adoption, commercial validation, or strategic review.

## Non-Claims

This document does not claim:

- Marketplace listing
- AWS partnership
- AWS endorsement
- AWS certification
- production deployment
- commercial customer validation
- usage-based pricing readiness
- acquisition interest

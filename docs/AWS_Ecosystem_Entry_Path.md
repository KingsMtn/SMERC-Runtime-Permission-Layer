# AWS Ecosystem Entry Path

## Purpose

AWS has opened a clearer ecosystem lane for agent tools, AgentCore-compatible runtimes, AgentCore Gateway integrations, and Marketplace-distributed AI agent products.

This document explains how SMERC should use that lane without overstating current readiness.

## Short Answer

Yes, AWS has created a more direct path for projects like SMERC to become legible.

The path is not acquisition outreach first. The path is:

1. Prove the local AWS-style reviewer bundle.
2. Get one AWS-style practitioner to replace examples with safe metadata from one workflow.
3. Turn the useful parts into a Lambda/OpenAPI decision surface.
4. Shape that surface toward AgentCore Gateway or AgentCore Runtime requirements.
5. Consider AWS Marketplace, Partner Network, or Partner Agent Factory only after external review signal exists.

## Why The Lane Exists

AWS now has public surfaces for:

- AI agents and tools in AWS Marketplace
- AgentCore Runtime-compatible agent, MCP, and A2A packages
- AgentCore Gateway integration for SaaS API tools, OpenAPI-described tools, and MCP servers
- Partner Agent Factory and agent solution co-innovation paths

That means AWS-style buyers already have language for:

- agent tools
- MCP servers
- guardrails
- runtime hosting
- gateway integration
- Marketplace procurement
- support, pricing, and packaging

SMERC should fit into that conversation as a recoverability and evidence layer for consequential agent actions.

## SMERC Fit

SMERC is not an agent that answers prompts.

SMERC is a pre-execution decision and evidence layer that can sit near:

- AgentCore Gateway
- AgentCore Runtime
- IAM and scoped authorization
- Cedar-style policy decisions
- CloudTrail and CloudWatch evidence
- EventBridge-style decision events
- Security Lake-style downstream evidence
- human approval and change-management workflows

The AWS-style reviewer frame is:

```text
Guardrails check content.
IAM and gateway policy check authority.
SMERC checks recoverability before execution.
Postcondition evidence checks whether the required route happened.
```

## Current Proof Assets

Run:

```bash
python -m reference_engine.aws_reviewer_bundle --requested-actions 12 --pretty
```

Start with:

- `docs/AWS_Reviewer_Quickstart.md`
- `reports/aws_reviewer_bundle/AWS_Reviewer_Bundle.md`
- `reports/aws_reviewer_bundle/AWS_Postcondition_Evidence_Report.md`
- `reports/aws_metadata_adapter/AWS_Metadata_Adapter_Report.md`
- `docs/AWS_Marketplace_Validation_Path.md`

The current proof is metadata-only. It does not connect to AWS, invoke Bedrock, call IAM, inspect CloudTrail, read CloudWatch, deploy infrastructure, configure AgentCore, or list on AWS Marketplace.

## Entry Routes

### Route 1: Practitioner Review

Best next route.

Ask one AWS-style platform, SRE, cloud-security, FinOps, DevSecOps, or AI-infrastructure reviewer to run the 10-minute path and answer:

```text
Would 5 to 25 metadata-only actions from one workflow be safe and useful enough for a shadow-mode review?
```

### Route 2: Lambda/OpenAPI Decision Surface

Next build after the reviewer path is understandable.

Shape SMERC as a small decision endpoint:

- accepts metadata-only action summaries
- returns posture, route controls, reason codes, and evidence expectations
- refuses secrets, account IDs, ARNs, raw logs, and production commands
- exposes an OpenAPI contract with simple JSON request and response bodies

### Route 3: AgentCore Gateway-Compatible Tool

Later packaging route.

SMERC could be shaped as a Gateway-callable decision/evidence tool if the OpenAPI surface is simple, HTTPS-ready, operation-ID complete, and cleanly separated from AWS control-plane execution.

### Route 4: AgentCore Runtime-Compatible Package

Later packaging route.

SMERC could be shaped as a containerized decision service only after the local proof, external metadata review, and endpoint contract are credible. See `docs/AWS_Marketplace_Validation_Path.md`.

### Route 5: AWS Marketplace / Partner Path

Last route, not first.

Marketplace or Partner Agent Factory-style packaging should wait until SMERC has evidence that outside reviewers can understand the proof and see useful decision differences on safe workflow metadata.

These are ecosystem entry routes, not current claims.

## Readiness Gap

Before pursuing AWS ecosystem packaging, SMERC still needs:

- external reviewer-owned metadata
- reviewer labels for useful, too strict, too loose, or irrelevant decisions
- a stable OpenAPI decision endpoint shape
- a support and commercial-use model
- latency and operational overhead observations
- a clear deployment boundary for observe-only versus enforce-mode use

## What To Do Now

Do this now:

1. Keep the GitHub proof current.
2. Use `docs/AWS_Reviewer_Quickstart.md` as the first learning path.
3. Ask for 5 to 25 safe metadata-only rows from one workflow.
4. Record whether SMERC changed reviewer judgment.
5. Build the Lambda/OpenAPI endpoint only after the ask is understandable.

Do not do this yet:

- claim AWS partnership
- claim AWS certification
- claim Marketplace readiness
- build a complex cloud deployment before external metadata review
- request live AWS access
- ask reviewers for secrets, account IDs, ARNs, raw logs, private topology, or production commands

## Work / Result / Impact

Work:

Map the new AWS agent ecosystem lane into SMERC's current proof path.

Result:

SMERC has a practical sequence from GitHub proof to AWS-style practitioner review to future Gateway, Runtime, or Marketplace packaging.

Impact:

The project can aim at a real AWS-adjacent distribution path while staying honest about current evidence and avoiding premature product claims.

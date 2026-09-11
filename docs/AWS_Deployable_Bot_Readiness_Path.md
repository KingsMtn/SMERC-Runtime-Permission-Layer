# AWS Deployable Bot Readiness Path

## Purpose

This path defines what SMERC should prove if the long-term target is an AWS-style platform team deploying SMERC as a governed action bot for agentic cloud automation.

The goal is not to claim AWS partnership, AWS endorsement, AWS certification, or AWS production integration. The goal is to make SMERC credible enough that an AWS-style reviewer can see exactly where it would fit, what it would need to consume, what it would return, and what evidence it would preserve.

## Target Shape

SMERC should behave like a recoverability-aware action bot that sits between agentic automation and consequential cloud actions.

Input:

- proposed agent action
- actor and workload identity
- tool or API target
- requested scope
- trusted evidence
- rollback and cancellation facts
- blast-radius estimate
- cost-velocity estimate
- current autonomy budget
- postcondition evidence expectations

Output:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`
- reason codes
- required controls
- Governance Routing Workbench route
- Decision Lifecycle Ledger evidence
- reviewer-ready Work / Result / Impact report

## Work / Result / Impact

Work:

Build SMERC toward an AWS-style deployable bot shape by proving safe metadata ingestion, hard evidence gates, recoverability scoring, route generation, control evidence, autonomy budgeting, and audit replay for cloud and agent actions.

Result:

A reviewer can run public examples first, then replace them with 5 to 25 metadata-only actions from one real AWS-style workflow.

Impact:

The project becomes easier to evaluate as infrastructure that could complement cloud identity, gateway, guardrail, logging, monitoring, change-management, and approval systems rather than a loose security idea.

## Valuation Link

The AWS deployable bot path is the Tier 2 proof path in `docs/Two_Tier_Valuation_Path.md`.

Tier 1 makes SMERC visible and reusable through public decision-language contracts. Tier 2 makes SMERC strategically interesting by showing how those contracts become enterprise cloud-action governance with metadata intake, recoverability posture, route controls, postcondition evidence, timing metrics, and customer-owned shadow-mode review.

This path should therefore prioritize evidence that an AWS-style platform reviewer can inspect without live credentials:

- safe metadata input
- `smerc.decision.v1` posture output
- required controls
- route state
- postcondition observations
- performance overhead
- commercial-use boundary
- customer-owned metadata replacement path
- sanitized shadow-mirror metadata path without packet payloads

## Readiness Milestones

### 1. Public AWS-Style Replay

Status: started.

Current artifact:

```bash
python -m reference_engine.aws_cloud_action_replay --pretty
```

This proves AWS-style metadata can move through the SMERC customer-evaluation contract with reason codes, posture counts, route evidence, autonomy budget impact, and DLL validity.

### 1A. Lambda-Shaped Decision Handler

Status: implemented as a local metadata-only handler.

Current artifact:

```bash
python - <<'PY'
import json
from pathlib import Path
from reference_engine.aws_lambda_decision_handler import lambda_handler

event = json.loads(Path("examples/aws_lambda_decision_event.json").read_text())
print(json.dumps(lambda_handler(event), indent=2, sort_keys=True))
PY
```

The handler accepts a single AWS-style action event or a full `smerc.customer-evaluation.v1` payload and returns posture, route state, required controls, scores, ledger verification, and an explicit no-live-AWS evidence boundary.

This is the cleanest local proof for the Bedrock Agent Action Group / Lambda action-governor idea. It is not native Bedrock interception or production enforcement.

### 2. AWS Metadata Intake Contract

Status: implemented as a metadata-only contract.

Current artifact:

```bash
python -m reference_engine.aws_metadata_adapter examples/aws_metadata_adapter_source_exports.json --pretty
```

Contract:

- `docs/AWS_Metadata_Intake_Contract.md`
- `examples/aws_metadata_adapter_source_exports.json`
- `reference_engine/aws_metadata_adapter.py`

The contract accepts AWS-style evidence:

- agent runtime target
- gateway or direct-runtime path
- IAM role or policy change summary
- CloudFormation change-set summary
- drift-detection summary
- CloudTrail-style action summary
- CloudWatch alarm/remediation summary
- RDS snapshot or deletion summary
- S3 policy exposure summary
- cost-velocity estimate
- Secrets Manager rotation summary
- cross-account trust summary

Boundary:

No live AWS credentials, account IDs, ARNs, secrets, private topology, production logs, or customer records should be required for public review.

### 3. AWS Adapter Stub

Status: implemented as a non-executing adapter stub.

It should not call AWS APIs by default.

It should produce:

- accepted rows
- skipped rows
- skipped reasons
- SMERC action metadata
- source version
- evidence boundary

The current adapter accepts safe rows, skips unsafe rows, records skipped reasons, normalizes accepted rows into `smerc.customer-evaluation.v1`, and produces a customer-evaluation report.

### 4. Postcondition Evidence For Cloud Controls

Extend postcondition evidence to AWS-style controls:

- dry-run or preview observed
- scope limit applied
- checkpoint recorded
- rollback plan attached
- approval route created
- gateway path enforced
- direct runtime path rejected
- execution blocked
- replay preserved

This matters because reviewers need to see whether SMERC only recommended a control or whether an adapter supplied evidence that the control happened.

Current proof path:

```bash
python -m reference_engine.aws_postcondition_evidence --pretty
```

Work: compare SMERC/SPARTa route controls for AWS-style actions against safe postcondition observations modeled on CloudTrail, CloudWatch, AgentCore Gateway, AgentCore Runtime, MCP gateway logs, and native AWS change records.

Result: `reports/aws_postcondition_evidence/AWS_Postcondition_Evidence_Report.md` shows 6 AWS-style routed actions, observed controls, expected AWS evidence sources, missing sources, and route-control gaps.

Impact: SMERC can now show how an AWS-style governed action bot would prove that controls were actually applied after a decision, not only that recoverability scoring recommended them.

### 5. Performance And Overhead Report

Add AWS replay timing to serious performance reports.

Measure:

- local decision latency
- route-generation latency
- report-generation latency
- p50
- p95
- maximum observed time
- evidence boundary

Do not claim production SLA until tested inside a real environment.

### 6. Customer-Owned AWS Metadata Request

Create a reviewer ask:

```text
Please replace the public examples with 5 to 25 metadata-only actions from one AWS-style workflow.
Do not include secrets, credentials, account IDs, ARNs, raw logs, customer records, private topology, or production commands.
```

Good first workflows:

- agent runtime tool calls
- gateway-controlled tool invocation
- IAM execution-role changes
- CloudFormation change-set execution
- drift remediation
- RDS cleanup or restore path
- S3 access-policy changes
- CloudWatch automated remediation
- cloud cost automation
- cross-account delegation

### 7. Shadow-Mode Pilot Shape

If metadata review is useful, the next stage is shadow mode:

- SMERC observes proposed actions.
- Existing AWS/customer controls remain authoritative.
- SMERC records the posture it would have returned.
- Reviewers label whether the posture was useful, too strict, too loose, or irrelevant.
- No production enforcement happens without a separate written agreement.

### 8. AWS Security Evidence Export Shape

Status: documented as an evidence-design path.

Current artifact:

- `docs/AWS_Security_Ecosystem_Evidence_Path.md`

This path explains how SMERC posture and route facts could be shaped for Security Lake-style normalized evidence, EventBridge-style decision events, Macie-style exposure findings, CloudTrail-style action summaries, CloudWatch-style metrics, Security Hub-style findings, and AWS Config-style change context.

### 9. Marketplace Validation Path

Status: parked as later packaging.

Current artifact:

- `docs/AWS_Marketplace_Validation_Path.md`

Marketplace or CloudFormation/Terraform packaging should come after local proof, customer-owned metadata review, and shadow-mode validation.

### 10. AWS Shadow Mirror Metadata Path

Status: implemented as a metadata-only shadow-mode adapter.

Current artifact:

```bash
python -m reference_engine.aws_shadow_mirror_adapter examples/aws_shadow_mirror_source_exports.json --pretty
```

Contract:

- `docs/AWS_Shadow_Mirror_Metadata_Path.md`
- `examples/aws_shadow_mirror_source_exports.json`
- `reference_engine/aws_shadow_mirror_adapter.py`

The path accepts sanitized summaries shaped like VPC Traffic Mirroring, Network Load Balancer fan-out, or Gateway Load Balancer endpoint observations. It rejects raw packet payloads, retained payload content, account IDs, ARNs, raw logs, credentials, customer records, private topology, production commands, and live AWS access.

Work: convert mirror-derived flow summaries into SMERC customer-evaluation actions.

Result: the generated report shows posture, route, skipped unsafe rows, high-velocity flow counts, sensitive-pattern flow counts, and evidence boundaries.

Impact: an AWS-style reviewer can test SMERC against realistic operational behavior in shadow mode without making SMERC a packet firewall or granting live cloud access.

## Success Criteria

SMERC is closer to an AWS-deployable bot when it can show:

- one-command public replay
- clean metadata intake
- no secrets required
- clear AWS-style reason codes
- useful posture differences
- postcondition evidence
- performance overhead
- customer-owned metadata path
- bounded shadow-mode pilot plan
- clear commercial-use boundary
- safe shadow mirror evidence path

## Non-Claims

This path does not claim:

- AWS partnership
- AWS endorsement
- AWS certification
- live AWS integration
- production safety
- compliance support
- incident reduction
- customer willingness to pay
- replacement for IAM, AgentCore Gateway, Bedrock Guardrails, CloudFormation, CloudTrail, CloudWatch, AWS Config, or human accountability

## Commercial Boundary

Public review, research, non-production evaluation, and metadata-only pilot testing are governed by the `SMERC Public Review License v1.0`.

Production deployment, commercial embedding, hosted use, resale, revenue-generating use, or integration into a commercial product, internal enterprise platform, cloud service, agent framework, financial workflow, security product, or managed service requires a separate written commercial license or agreement.

Organizations evaluating acquisition, strategic partnership, or production use should contact the project owner before implementation.

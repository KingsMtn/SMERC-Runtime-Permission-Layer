# AWS Reviewer Quickstart

## Purpose

This is the fastest AWS-style review path for SMERC.

It answers one question:

If Bedrock-style guardrails approve the content and IAM permits the actor, can SMERC still decide whether the action is recoverable enough to execute before side effects occur?

Put differently: can SMERC reduce systemic liability and operational downtime risk for autonomous cloud execution by checking recoverability before the agent or tool call acts?

## Run The Proof

From the repository root:

```bash
python -m reference_engine.aws_reviewer_bundle --requested-actions 12 --pretty
```

To inspect the Lambda-shaped action-gate proof directly:

```bash
python - <<'PY'
import json
from pathlib import Path
from reference_engine.aws_lambda_decision_handler import lambda_handler

event = json.loads(Path("examples/aws_lambda_decision_event.json").read_text())
print(json.dumps(lambda_handler(event), indent=2, sort_keys=True))
PY
```

To test the customer-owned metadata handoff with the bundled safe sample:

```bash
python -m reference_engine.aws_reviewer_bundle \
  --customer-aws-source-exports examples/aws_customer_metadata_filled_sample.json \
  --customer-aws-observations examples/aws_customer_postcondition_observations_sample.json \
  --output-dir reports/aws_customer_mini_pack \
  --iterations 1 \
  --pretty
```

## Inspect These Three Outputs

1. `reports/aws_reviewer_bundle/AWS_Reviewer_Bundle.md`

   Start here. It summarizes the full AWS-style proof path, readiness status, evidence gaps, performance, and next action.

2. `reports/aws_reviewer_bundle/AWS_Agent_Action_Chain.md`

   Review the eight AWS-style action-chain examples. They show where SMERC fits after Bedrock-style guardrails and before IAM, Systems Manager, CloudFormation, CloudWatch remediation, S3 policy changes, cross-account delegation, retry-loop pressure, cost-sensitive scaling, or cloud execution.

3. `reports/aws_metadata_adapter/AWS_Metadata_Adapter_Report.md`

   Review the safe metadata intake path. It shows how SMERC can preserve AgentCore/Cedar-style policy context, gateway-session context, derived-output governance context, and route evidence without live AWS access.

Also inspect:

- `docs/AWS_Bedrock_Agent_Kill_Switch_Pattern.md`
- `docs/AWS_Customer_Metadata_Mini_Pack.md`
- `docs/AWS_Shadow_Mirror_Metadata_Path.md`
- `docs/AWS_Shadow_Mirror_Customer_Metadata_Request.md`
- `docs/AWS_Security_Ecosystem_Evidence_Path.md`
- `docs/AWS_Marketplace_Validation_Path.md`
- `docs/SMERC_Defensible_Moat_And_Commercial_Boundary.md`

## Sample Reviewer Interpretation

An AWS-style policy engine may say an action is allowed because the principal, tool, target, and session policy are valid.

SMERC can still return `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE` when the action is not recoverable enough right now.

Example:

- Work: an agent proposes widening an S3 policy after a guardrail pass and valid authority.
- Result: SMERC returns `DENY` because least-privilege evidence, containment, and rollback confidence are not strong enough.
- Impact: the reviewer sees the distinction between authorization and recoverability before the data-access side effect happens.

## Customer-Owned Metadata Template

Use this file when replacing the public examples:

```text
examples/aws_customer_metadata_template.json
```

Copy the shape into `customer_working/aws_source_exports.json`, replace placeholder values with 5 to 25 safe metadata-only rows from one workflow, then run:

```bash
python -m reference_engine.aws_metadata_adapter customer_working/aws_source_exports.json --normalized-output reports/customer_working/aws_normalized_customer_actions.json --json-output reports/customer_working/aws_metadata_adapter_report.json --markdown-output reports/customer_working/AWS_Metadata_Adapter_Report.md --customer-json-output reports/customer_working/aws_customer_evaluation_report.json --customer-markdown-output reports/customer_working/AWS_Customer_Evaluation_Report.md --pretty
```

For mirror-derived operational summaries, use:

```text
examples/aws_shadow_mirror_customer_template.json
```

Copy the shape into `customer_working/aws_shadow_mirror_rows.json`, replace placeholder values with 5 to 25 sanitized mirror-derived rows from one workflow, then run:

```bash
python -m reference_engine.aws_shadow_mirror_adapter customer_working/aws_shadow_mirror_rows.json --normalized-output reports/customer_working/aws_shadow_mirror_normalized_customer_actions.json --json-output reports/customer_working/aws_shadow_mirror_adapter_report.json --markdown-output reports/customer_working/AWS_Shadow_Mirror_Adapter_Report.md --customer-json-output reports/customer_working/aws_shadow_mirror_customer_evaluation_report.json --customer-markdown-output reports/customer_working/AWS_Shadow_Mirror_Customer_Evaluation_Report.md --pretty
```

## What This Proves

- SMERC can evaluate AWS-style action metadata before execution.
- SMERC can be exposed through a Lambda-compatible handler shape for Bedrock-style Action Group or gateway review.
- SMERC can distinguish content approval, authority approval, recoverability posture, and postcondition evidence.
- SMERC can produce a reviewer-ready report without account IDs, ARNs, raw logs, credentials, production commands, or live AWS access.

## What This Does Not Prove

- AWS endorsement
- AWS certification
- native AWS integration
- live Bedrock or AgentCore interception
- AWS Marketplace listing
- production enforcement
- customer-validated incident reduction
- compliance attestation

## Best Next Reviewer Question

Can one AWS-style platform, cloud-security, SRE, FinOps, or agent-infrastructure reviewer replace the examples with 5 to 25 safe metadata-only actions from one owned workflow and say whether SMERC changed their judgment?

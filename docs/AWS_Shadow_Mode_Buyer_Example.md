# AWS Shadow-Mode Buyer Example

## Buyer question

Can SMERC identify useful recoverability gaps in AWS-style automation metadata without receiving credentials, production access, raw logs, ARNs, customer data, or executable commands?

## Input

The worked metadata-only source is:

```bash
examples/aws_customer_metadata_filled_sample.json
```

It contains five synthetic AWS-style actions from one cloud-automation review lane:

- Amazon Bedrock action-group invocation
- IAM execution-role expansion
- AWS CloudFormation change-set execution
- Amazon S3 bucket-policy expansion
- compute-capacity increase during a retry loop

The rows describe proposed action, current control, scope, side-effect class, recoverability signals, admission evidence, and tool capabilities. They do not contain live AWS data.

## Run

```bash
python -m reference_engine.aws_metadata_adapter examples/aws_customer_metadata_filled_sample.json \
  --normalized-output reports/aws_shadow_mode_buyer_example/normalized_customer_actions.json \
  --json-output reports/aws_shadow_mode_buyer_example/aws_metadata_adapter_report.json \
  --markdown-output reports/aws_shadow_mode_buyer_example/AWS_Metadata_Adapter_Report.md \
  --customer-json-output reports/aws_shadow_mode_buyer_example/customer_evaluation_report.json \
  --customer-markdown-output reports/aws_shadow_mode_buyer_example/Customer_Evaluation_Report.md \
  --pretty
```

## Review

Start with:

```bash
reports/aws_shadow_mode_buyer_example/AWS_Metadata_Adapter_Report.md
```

Then inspect the action-level posture and replay evidence in:

```bash
reports/aws_shadow_mode_buyer_example/Customer_Evaluation_Report.md
```

The useful result is a reviewable difference between the current control and SMERC, a missing-evidence finding, or a constrained execution path that preserves useful automation. The useful result is not a high score or a claim that AWS endorses SMERC.

## Safety evidence

Before treating the example as pilot evidence, run:

```bash
python -m unittest tests.test_cross_path_safety_invariants -v
```

That suite verifies fail-closed admission defaults, strictest-posture preservation, missing-evidence behavior across four entry paths, and rejection of unknown structured fields.

## Boundary

This is synthetic, metadata-only, shadow-mode evidence. It can demonstrate the review flow and expose questions worth testing with a workflow owner. It cannot demonstrate deployed AWS enforcement, production safety, incident reduction, customer demand, compliance, AWS approval, or acquisition readiness.

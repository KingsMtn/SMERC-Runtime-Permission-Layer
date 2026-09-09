# AWS-Style Reviewer Bundle

Generated: `2026-09-09T22:00:04+00:00`
Version: `smerc.aws-reviewer-bundle.v1`
Bundle status: `ready_for_limited_aws_review`

## One-Line Reviewer Frame

Guardrails check content. IAM checks authority. SMERC checks recoverability. Postcondition evidence checks whether the route happened.

## AWS Reviewer Path

1. Bedrock-style guardrails check content and model behavior.
2. IAM and change systems check identity, authority, session, and allowed path.
3. SMERC checks recoverability, blast radius, rollback, cost velocity, fallback, and evidence before execution.
4. Postcondition evidence checks whether the required route controls actually happened after the decision.

## Work / Result / Impact

- Work: Assemble the AWS-style reviewer path into one local package: action-chain proof, route-control postcondition evidence, AWS postcondition evidence, performance metrics, and customer-owned AWS metadata request.
- Result: Generated an AWS reviewer bundle with 8 action-chain examples, chain postcondition statuses {'gap': 1, 'pass': 7}, AWS postcondition statuses {'gap': 2, 'pass': 4}, and slowest local p95 4.973 ms.
- Impact: An AWS-style platform reviewer can inspect where SMERC fits, what it decides, what evidence would prove the route, and what safe customer-owned metadata is needed next without granting live AWS access.

## Readiness

- Status: `ready_for_limited_aws_review`
- Slowest local p95 ms: `4.973`
- Chain postcondition gaps: `1`
- Chain postcondition violations: `0`
- AWS postcondition gaps: `2`
- AWS postcondition violations: `0`

## Reviewer Takeaways

- The AWS path is now one command instead of separate documents.
- The bundle explains the difference between content guardrails, authority controls, recoverability control, and postcondition evidence.
- The proof remains metadata-only and does not need live AWS access.
- The next real proof is reviewer-owned AWS-style metadata from one workflow.
- Customer AWS metadata supplied: 5 accepted rows and 0 skipped rows.
- Customer AWS postcondition statuses: {'gap': 4, 'pass': 1}.
- Warnings: AWS chain postcondition evidence includes expected evidence gaps, AWS postcondition evidence includes expected evidence gaps.

## Included Reports

| Report | Main Result |
| --- | --- |
| AWS agent action chain | scenarios=`8`, postures=`{'DENY': 5, 'THROTTLE': 3}` |
| AWS chain postcondition evidence | statuses=`{'gap': 1, 'pass': 7}` |
| AWS postcondition evidence | statuses=`{'gap': 2, 'pass': 4}` |
| Performance | status=`ready_for_local_review`, slowest_p95_ms=`4.973` |
| AWS customer-owned metadata request | requested_actions=`12` |
| Customer AWS metadata review | accepted_rows=`5`, skipped_rows=`0` |
| Customer AWS postcondition evidence | statuses=`{'gap': 4, 'pass': 1}` |

## Evidence Boundary

This is a local, metadata-only AWS-style review package. It does not connect to AWS, invoke Amazon Bedrock, call IAM, run Systems Manager, apply CloudFormation, read CloudTrail or CloudWatch, modify infrastructure, process secrets, prove AWS endorsement, prove AWS certification, or establish production safety.

## Next Action

Use the gaps as reviewer questions and ask for 5 to 25 safe AWS-style action and observation summaries.

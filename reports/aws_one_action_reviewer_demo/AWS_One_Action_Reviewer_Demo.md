# AWS One-Action Reviewer Demo

Generated: `2026-09-14T11:27:55+00:00`
Version: `smerc.aws-one-action-reviewer-demo.v1`

## Purpose

This is the quickest AWS-style review path for SMERC: choose one safe metadata-only action, run it locally, and inspect posture, route, reason codes, scores, and transition guidance.

## Evidence Boundary

This is a metadata-only AWS-style one-action reviewer demo. It does not connect to AWS, inspect CloudTrail, invoke Lambda, modify IAM, change S3, execute CloudFormation, scale compute, delete databases, rotate secrets, spend money, read customer systems, or prove production safety.

## Summary

- Actions evaluated: `8`
- Posture counts: `{'ALLOW': 1, 'DENY': 1, 'THROTTLE': 6}`
- Route state counts: `{'BLOCK': 1, 'CONSTRAINED_EXECUTE': 6, 'EXECUTE': 1}`
- AWS surface counts: `{'cloudformation': 1, 'cost_management': 1, 'ecs': 1, 'iam': 1, 'lambda': 1, 'rds': 1, 's3': 1, 'secrets_manager': 1}`
- Non-executable routes: `1`
- Highest exposure action: `AWS_ONE_RDS_CLUSTER_DELETE`

## Results

| Action | Surface | Posture | Route | Executable | Exposure | Recovery | Reason codes |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `AWS_ONE_LAMBDA_CONFIG_UPDATE` | `lambda` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | 0.45 | 0.683 | `EXTERNAL_SIDE_EFFECT` |
| `AWS_ONE_IAM_ROLE_EXPANSION` | `iam` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | 0.792 | 0.428 | `IRREVERSIBLE_EXPOSURE_HIGH`, `CONTAINMENT_WEAK`, `IMPACT_SCOPE_WIDE`, `EXTERNAL_SIDE_EFFECT`, `SENSITIVE_DATA` |
| `AWS_ONE_S3_POLICY_WIDENING` | `s3` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | 0.759 | 0.459 | `IRREVERSIBLE_EXPOSURE_HIGH`, `CONTAINMENT_WEAK`, `ANOMALY_PRESSURE_HIGH`, `IMPACT_SCOPE_WIDE`, `EXTERNAL_SIDE_EFFECT` |
| `AWS_ONE_CFN_CHANGESET_REPLACE` | `cloudformation` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | 0.763 | 0.441 | `IRREVERSIBLE_EXPOSURE_HIGH`, `IMPACT_SCOPE_WIDE`, `EXTERNAL_SIDE_EFFECT`, `SENSITIVE_DATA` |
| `AWS_ONE_ECS_SCALE_SHIFT` | `ecs` | `ALLOW` | `EXECUTE` | `True` | 0.31 | 0.729 | `RECOVERABILITY_ACCEPTABLE` |
| `AWS_ONE_RDS_CLUSTER_DELETE` | `rds` | `DENY` | `BLOCK` | `False` | 0.968 | 0.204 | `IRREVERSIBLE_EXPOSURE_HIGH`, `RECOVERY_CAPACITY_LOW`, `ROLLBACK_LATENCY_HIGH`, `CANCEL_RELIABILITY_WEAK`, `CONTAINMENT_WEAK` |
| `AWS_ONE_COST_VELOCITY_SCALE_OUT` | `cost_management` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | 0.551 | 0.561 | `IRREVERSIBLE_EXPOSURE_ELEVATED`, `ANOMALY_PRESSURE_HIGH`, `EXTERNAL_SIDE_EFFECT` |
| `AWS_ONE_SECRETS_ROTATION` | `secrets_manager` | `THROTTLE` | `CONSTRAINED_EXECUTE` | `True` | 0.481 | 0.734 | `IRREVERSIBLE_EXPOSURE_ELEVATED`, `EXTERNAL_SIDE_EFFECT`, `SENSITIVE_DATA` |

## Why It Judged That Way

### AWS_ONE_LAMBDA_CONFIG_UPDATE

- Work: Evaluate AWS-style `aws.lambda_config` action `AWS_ONE_LAMBDA_CONFIG_UPDATE` before execution.
- Result: Returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, exposure `0.45`, recovery capacity `0.683`, confidence `0.776`.
- Impact: SMERC found the action potentially useful, but only safe through reduced scope, preview, checkpointing, or rollback controls.
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect']`
- Route controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- Transition guidance: `{'current_posture': 'THROTTLE', 'target_posture': 'THROTTLE', 'release_conditions': {'irreversible_exposure_below': 0.45, 'authorization_score_at_or_above': 0.62, 'confidence_score_target': 0.7, 'reversible_capacity_target': 0.6}, 'blocking_factors': ['irreversible_exposure_above_release_threshold'], 'evidence_needed': [], 'control_improvements': ['increase_containment', 'limit_scope', 'narrow_impact_scope', 'preview_before_execution', 'prove_rollback_path', 'rate limit or stage external side effect', 'rate_limit_external_side_effect', 'record_replay']}`

### AWS_ONE_IAM_ROLE_EXPANSION

- Work: Evaluate AWS-style `aws.iam_policy` action `AWS_ONE_IAM_ROLE_EXPANSION` before execution.
- Result: Returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, exposure `0.792`, recovery capacity `0.428`, confidence `0.577`.
- Impact: SMERC found the action potentially useful, but only safe through reduced scope, preview, checkpointing, or rollback controls.
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Route controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- Transition guidance: `{'current_posture': 'THROTTLE', 'target_posture': 'THROTTLE', 'release_conditions': {'irreversible_exposure_below': 0.45, 'authorization_score_at_or_above': 0.62, 'confidence_score_target': 0.7, 'reversible_capacity_target': 0.6}, 'blocking_factors': ['confidence_below_release_target', 'irreversible_exposure_above_release_threshold', 'reversible_capacity_incomplete'], 'evidence_needed': ['rollback test or recovery evidence', 'stronger authorization and evidence validity'], 'control_improvements': ['checkpoint_before_execution', 'data minimization or scoped export proof', 'increase_containment', 'limit_scope', 'narrow_impact_scope', 'preview_before_execution', 'prove_rollback_path', 'rate limit or stage external side effect', 'rate_limit_external_side_effect', 'record_replay', 'reliable cancellation handle', 'require_rollback_plan']}`

### AWS_ONE_S3_POLICY_WIDENING

- Work: Evaluate AWS-style `aws.s3_bucket_policy` action `AWS_ONE_S3_POLICY_WIDENING` before execution.
- Result: Returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, exposure `0.759`, recovery capacity `0.459`, confidence `0.494`.
- Impact: SMERC found the action potentially useful, but only safe through reduced scope, preview, checkpointing, or rollback controls.
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Route controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- Transition guidance: `{'current_posture': 'THROTTLE', 'target_posture': 'THROTTLE', 'release_conditions': {'irreversible_exposure_below': 0.45, 'authorization_score_at_or_above': 0.62, 'confidence_score_target': 0.7, 'reversible_capacity_target': 0.6}, 'blocking_factors': ['confidence_below_release_target', 'irreversible_exposure_above_release_threshold', 'reversible_capacity_incomplete'], 'evidence_needed': ['rollback test or recovery evidence', 'stronger authorization and evidence validity'], 'control_improvements': ['checkpoint_before_execution', 'data minimization or scoped export proof', 'increase_containment', 'limit_scope', 'narrow_impact_scope', 'preview_before_execution', 'prove_rollback_path', 'rate limit or stage external side effect', 'rate_limit_external_side_effect', 'record_replay', 'reliable cancellation handle']}`

### AWS_ONE_CFN_CHANGESET_REPLACE

- Work: Evaluate AWS-style `aws.cloudformation_changeset` action `AWS_ONE_CFN_CHANGESET_REPLACE` before execution.
- Result: Returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, exposure `0.763`, recovery capacity `0.441`, confidence `0.647`.
- Impact: SMERC found the action potentially useful, but only safe through reduced scope, preview, checkpointing, or rollback controls.
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'require_rollback_plan', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Route controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- Transition guidance: `{'current_posture': 'THROTTLE', 'target_posture': 'THROTTLE', 'release_conditions': {'irreversible_exposure_below': 0.45, 'authorization_score_at_or_above': 0.62, 'confidence_score_target': 0.7, 'reversible_capacity_target': 0.6}, 'blocking_factors': ['confidence_below_release_target', 'irreversible_exposure_above_release_threshold', 'reversible_capacity_incomplete'], 'evidence_needed': ['rollback test or recovery evidence', 'stronger authorization and evidence validity'], 'control_improvements': ['checkpoint_before_execution', 'data minimization or scoped export proof', 'increase_containment', 'limit_scope', 'narrow_impact_scope', 'preview_before_execution', 'prove_rollback_path', 'rate limit or stage external side effect', 'rate_limit_external_side_effect', 'record_replay', 'reliable cancellation handle', 'require_rollback_plan']}`

### AWS_ONE_ECS_SCALE_SHIFT

- Work: Evaluate AWS-style `aws.ecs_service_scaling` action `AWS_ONE_ECS_SCALE_SHIFT` before execution.
- Result: Returned `ALLOW`, routed `EXECUTE`, exposure `0.31`, recovery capacity `0.729`, confidence `0.665`.
- Impact: SMERC found enough recovery capacity, confidence, and containment to allow execution with replay evidence.
- Controls: `['execute', 'record_replay', 'retain_cancel_handle']`
- Route controls: `['execute', 'record_execution_report']`
- Transition guidance: `{'current_posture': 'ALLOW', 'target_posture': 'ALLOW', 'release_conditions': {'irreversible_exposure_below': 0.45, 'authorization_score_at_or_above': 0.62, 'confidence_score_target': 0.7, 'reversible_capacity_target': 0.6}, 'blocking_factors': ['confidence_below_release_target'], 'evidence_needed': ['stronger authorization and evidence validity'], 'control_improvements': ['execute', 'record_replay', 'retain_cancel_handle']}`

### AWS_ONE_RDS_CLUSTER_DELETE

- Work: Evaluate AWS-style `aws.rds_admin` action `AWS_ONE_RDS_CLUSTER_DELETE` before execution.
- Result: Returned `DENY`, routed `BLOCK`, exposure `0.968`, recovery capacity `0.204`, confidence `0.44`.
- Impact: SMERC found the action structurally unsafe in this form, so execution is blocked until a materially safer request is submitted.
- Controls: `['block_execution', 'explain_denial', 'preserve_replay', 'require_new_request']`
- Route controls: `['block_execution', 'preserve_replay', 'explain_denial']`
- Transition guidance: `{'current_posture': 'DENY', 'target_posture': 'THROTTLE', 'release_conditions': {'irreversible_exposure_below': 0.45, 'authorization_score_at_or_above': 0.62, 'confidence_score_target': 0.7, 'reversible_capacity_target': 0.6}, 'blocking_factors': ['confidence_below_release_target', 'irreversible_exposure_above_release_threshold', 'reversible_capacity_incomplete'], 'evidence_needed': ['rollback test or recovery evidence', 'stronger authorization and evidence validity'], 'control_improvements': ['block_execution', 'data minimization or scoped export proof', 'explain_denial', 'increase_containment', 'narrow_impact_scope', 'preserve_replay', 'prove_rollback_path', 'rate limit or stage external side effect', 'reliable cancellation handle', 'require_new_request']}`

### AWS_ONE_COST_VELOCITY_SCALE_OUT

- Work: Evaluate AWS-style `aws.compute_capacity` action `AWS_ONE_COST_VELOCITY_SCALE_OUT` before execution.
- Result: Returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, exposure `0.551`, recovery capacity `0.561`, confidence `0.473`.
- Impact: SMERC found the action potentially useful, but only safe through reduced scope, preview, checkpointing, or rollback controls.
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect', 'checkpoint_before_execution']`
- Route controls: `['limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- Transition guidance: `{'current_posture': 'THROTTLE', 'target_posture': 'THROTTLE', 'release_conditions': {'irreversible_exposure_below': 0.45, 'authorization_score_at_or_above': 0.62, 'confidence_score_target': 0.7, 'reversible_capacity_target': 0.6}, 'blocking_factors': ['confidence_below_release_target', 'irreversible_exposure_above_release_threshold', 'reversible_capacity_incomplete'], 'evidence_needed': ['rollback test or recovery evidence', 'stronger authorization and evidence validity'], 'control_improvements': ['checkpoint_before_execution', 'increase_containment', 'limit_scope', 'narrow_impact_scope', 'preview_before_execution', 'prove_rollback_path', 'rate limit or stage external side effect', 'rate_limit_external_side_effect', 'record_replay', 'reliable cancellation handle']}`

### AWS_ONE_SECRETS_ROTATION

- Work: Evaluate AWS-style `aws.secrets_manager_rotation` action `AWS_ONE_SECRETS_ROTATION` before execution.
- Result: Returned `THROTTLE`, routed `CONSTRAINED_EXECUTE`, exposure `0.481`, recovery capacity `0.734`, confidence `0.836`.
- Impact: SMERC found the action potentially useful, but only safe through reduced scope, preview, checkpointing, or rollback controls.
- Controls: `['limit_scope', 'preview_before_execution', 'record_replay', 'rate_limit_external_side_effect']`
- Route controls: `['checkpoint_before_execution', 'limit_scope', 'preserve_replay', 'preview_before_execution', 'record_execution_report', 'require_rollback_plan']`
- Transition guidance: `{'current_posture': 'THROTTLE', 'target_posture': 'THROTTLE', 'release_conditions': {'irreversible_exposure_below': 0.45, 'authorization_score_at_or_above': 0.62, 'confidence_score_target': 0.7, 'reversible_capacity_target': 0.6}, 'blocking_factors': ['irreversible_exposure_above_release_threshold'], 'evidence_needed': [], 'control_improvements': ['data minimization or scoped export proof', 'increase_containment', 'limit_scope', 'narrow_impact_scope', 'preview_before_execution', 'prove_rollback_path', 'rate limit or stage external side effect', 'rate_limit_external_side_effect', 'record_replay']}`

## Recommended Reviewer Ask

Pick the closest sample, replace only safe metadata with one real action from your workflow, and tell us whether the posture and route match how your team would handle the action.

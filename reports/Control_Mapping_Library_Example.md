# SMERC Control Mapping Report

This report maps abstract SMERC controls to declared native mechanisms for one tool path.
It is pilot evidence, not proof that a production environment is certified or continuously enforced.

- Library: `github-actions-control-library-v1`
- Posture: `THROTTLE`
- Tool: `github_actions`
- Capability: `deploy_production`
- Executable: `true`

## Mapped Controls

| Control | Native mechanism | Evidence required |
| --- | --- | --- |
| `limit_scope` | Run canary, single-environment, or scoped path workflow with least-privilege permissions. | `effective_scope`, `permissions_summary`, `target_environment` |
| `preserve_replay` | Store route report, action request, and workflow run URL as artifacts. | `route_report_ref`, `action_request_ref`, `workflow_run_url` |
| `preview_before_execution` | Run a dry-run, plan, diff, or validation job before the deployment job. | `dry_run_status`, `preview_artifact_ref` |
| `require_rollback_plan` | Require rollback workflow, rollback command, or previous deployment redeploy target. | `rollback_ref`, `rollback_owner` |

## Missing Controls

No required controls are missing for this mapping.

## Recommendation

Proceed only through an adapter that applies the mapped native controls and records evidence.

SMERC posture THROTTLE maps to 4 native control(s) for github_actions; execution should remain evidence-bound.

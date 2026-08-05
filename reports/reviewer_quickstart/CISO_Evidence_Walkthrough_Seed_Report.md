# SMERC CISO Evidence Walkthrough Seed Report

Version: `smerc.ciso-review-seed.v1`
Generated at: `2026-07-28T02:25:21+00:00`
Tenant: `pilot-team`
Audit database: `./smerc_reviewer_quickstart.sqlite3`

## Evidence Boundary

This walkthrough seeds synthetic but realistic review data. It proves the local product flow, not customer validation, production safety, or incident reduction.

## Seeded Decisions

| Action | Posture | Replay ID | DLL decision ID |
| --- | --- | --- | --- |
| `CISO_REVIEW_RUN_TESTS` | `ALLOW` | `replay_CISO_REVIEW_RUN_TESTS_1785205521523_9370188fdf9e` | `dll:ciso-review:ciso_review_run_tests` |
| `CISO_REVIEW_DEPLOY_CANARY` | `THROTTLE` | `replay_CISO_REVIEW_DEPLOY_CANARY_1785205521523_3cfef05cdd52` | `dll:ciso-review:ciso_review_deploy_canary` |
| `CISO_REVIEW_ROTATE_SECRET` | `THROTTLE` | `replay_CISO_REVIEW_ROTATE_SECRET_1785205521539_82839170422d` | `dll:ciso-review:ciso_review_rotate_secret` |
| `CISO_REVIEW_DELETE_AUDIT_LOGS` | `ESCALATE` | `replay_CISO_REVIEW_DELETE_AUDIT_LOGS_1785205521539_8e19a005daa7` | `dll:ciso-review:ciso_review_delete_audit_logs` |
| `CISO_REVIEW_EXPORT_CUSTOMER_DATA` | `DENY` | `replay_CISO_REVIEW_EXPORT_CUSTOMER_DATA_1785205521544_e14ec322cd0d` | `dll:ciso-review:ciso_review_export_customer_data` |

## Reviewer Flow

1. Start the authenticated API against the same audit database.
2. Open the pilot console and connect with a principal that has decisions.read, reviews.read, reviews.write, metrics.read, and audit.read.
3. Review the seeded decisions in the queue.
4. Generate a stored DLL evidence package using one of the listed dll_decision_id values.

## What This Demonstrates

- SMERC can evaluate realistic AI-agent actions into reviewable postures.
- The pilot API can expose those decisions through the review queue.
- Stored DLL records can be used to generate CISO evidence packages.
- The flow is replayable without claiming production validation.


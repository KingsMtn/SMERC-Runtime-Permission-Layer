# SMERC Local Shadow Intake Report

Generated: `2026-09-13T11:26:23+00:00`
Version: `smerc.local-shadow-intake.v1`

## Work / Result / Impact

- Work: Screen local structured action summaries before they become SMERC reviewer-owned metadata.
- Result: Accepted 5 of 7 action summaries and rejected or flagged the rest.
- Impact: Reviewers can prepare 5 to 25 metadata-only actions without sending raw logs, secrets, account identifiers, private prompts, customer records, ARNs, or production commands into the public repo.

## Summary

- Input actions: `7`
- Accepted actions: `5`
- Classification counts: `{'ACCEPTED_METADATA_ONLY': 5, 'REJECTED_RAW_LOG': 1, 'SKIPPED_PROHIBITED_FIELD': 1}`
- Share status: `HUMAN_REVIEW_REQUIRED`

## Evidence Boundary

This utility is reject-first intake, not guaranteed anonymization. Hashing is not treated as proof of privacy. A human must inspect the output before sharing, and raw logs should not be submitted.

## Decisions

| Source row | Classification | Reasons |
| --- | --- | --- |
| `1` | `ACCEPTED_METADATA_ONLY` | `['METADATA_ONLY_DRAFT']` |
| `2` | `ACCEPTED_METADATA_ONLY` | `['METADATA_ONLY_DRAFT']` |
| `3` | `ACCEPTED_METADATA_ONLY` | `['METADATA_ONLY_DRAFT']` |
| `4` | `ACCEPTED_METADATA_ONLY` | `['METADATA_ONLY_DRAFT']` |
| `5` | `ACCEPTED_METADATA_ONLY` | `['METADATA_ONLY_DRAFT']` |
| `6` | `SKIPPED_PROHIBITED_FIELD` | `['PROHIBITED_KEY:account_id']` |
| `7` | `REJECTED_RAW_LOG` | `['RAW_LOG_SHAPED_RECORD']` |

## Recommended Next Action

Manually inspect the sanitized draft, then use accepted records for a shadow-mode posture gap matrix.

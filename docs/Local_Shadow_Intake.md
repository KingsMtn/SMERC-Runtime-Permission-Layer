# Local Shadow Intake

## Purpose

Local Shadow Intake is the safer version of a sanitizer script.

It does not promise anonymization. It rejects risky records first, produces a metadata-only draft from accepted rows, and requires human review before sharing.

## Run

```bash
python -m reference_engine.local_shadow_intake examples/local_shadow_intake_examples.json --pretty
```

Generated outputs:

- `reports/smerc_anonymous_contribution.json`
- `reports/local_shadow_intake_report.json`
- `reports/Local_Shadow_Intake_Report.md`

## What It Accepts

Structured action summaries with fields such as:

- `action_type`
- `tool_system`
- `external_side_effects`
- `reversibility`
- `rollback_latency_seconds`
- `containment_strength`
- `evidence_available`
- `blast_radius_scope`
- `human_approval_existed`
- `schema_contract_match`
- `current_system_handling`

## What It Rejects Or Flags

- prohibited keys such as secrets, tokens, passwords, credentials, account IDs, ARNs, emails, raw logs, prompts, or source code
- identifier-shaped values such as AWS account IDs, ARNs, emails, or IP addresses
- raw-log-shaped records
- missing required metadata
- unknown current-control outcomes

## Classifications

- `ACCEPTED_METADATA_ONLY`
- `SKIPPED_PROHIBITED_FIELD`
- `NEEDS_MANUAL_REVIEW`
- `REJECTED_RAW_LOG`
- `REJECTED_IDENTIFIER_RISK`

## Evidence Boundary

This utility is reject-first intake, not guaranteed anonymization. Hashing is not treated as proof of privacy. A human must inspect the output before sharing, and raw logs should not be submitted.

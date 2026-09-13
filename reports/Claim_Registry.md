# SMERC Claim Registry

Generated: `2026-09-13T13:10:26+00:00`
Version: `smerc.claim-registry.v1`

## Work / Result / Impact

- Work: Separate supported SMERC claims from partial or unsupported claims.
- Result: Reviewers can inspect the exact evidence and boundary for each major public claim.
- Impact: SMERC can keep moving aggressively without overstating customer validation, AWS readiness, or incident-reduction proof.

## Status Counts

`{'not_supported': 3, 'supported': 4}`

## Claims

| Claim ID | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `local_end_to_end_reviewer_flow_runs` | `supported` | `docs/End_To_End_Reviewer_Flow.md`<br>`reports/End_To_End_Reviewer_Flow.md`<br>`reference_engine/end_to_end_reviewer_flow.py`<br>`tests/test_end_to_end_reviewer_flow.py` | Local proof only; no live AWS, MCP server, customer data, or production execution. |
| `reject_first_metadata_intake_exists` | `supported` | `docs/Local_Shadow_Intake.md`<br>`reports/Local_Shadow_Intake_Report.md`<br>`reference_engine/local_shadow_intake.py`<br>`tests/test_local_shadow_intake.py` | Reject-first intake is not guaranteed anonymization and still requires human review before sharing. |
| `public_pattern_fallback_adapter_runs` | `supported` | `docs/Public_Fallback_Adapter.md`<br>`reports/Public_Fallback_Adapter_Report.md`<br>`reference_engine/public_fallback_adapter.py`<br>`tests/test_public_fallback_adapter.py` | This is adapter readiness on benchmark-shaped metadata, not an official benchmark score or customer validation. |
| `public_evidence_fallback_plan_exists` | `supported` | `docs/Public_Evidence_Fallback_Plan.md`<br>`reports/Public_Evidence_Fallback_Plan.md`<br>`reference_engine/public_evidence_fallback.py`<br>`tests/test_public_evidence_fallback.py` | Public-pattern evidence improves technical proof but is not customer validation. |
| `customer_owned_metadata_received` | `not_supported` | `docs/External_Metadata_Reviewer_Request.md`<br>`.github/ISSUE_TEMPLATE/workflow-intake-template.md` | The repo has the ask and templates, but no sufficient customer-owned response is recorded here. |
| `production_aws_connector_ready` | `not_supported` | `docs/AWS_Deployable_Bot_Readiness_Path.md`<br>`docs/AWS_Metadata_Intake_Contract.md`<br>`docs/AWS_Reviewer_Bundle.md` | AWS proof is metadata-only and local; no AWS endorsement, production certification, or live-account control is claimed. |
| `incident_reduction_proven` | `not_supported` | `docs/SMERC_Premortem.md`<br>`docs/Public_Evidence_Fallback_Plan.md` | No production deployment or incident-reduction study is present. |

## Evidence Boundary

The registry is a claims-control artifact. It does not create validation by itself; it records what the repository evidence currently supports.

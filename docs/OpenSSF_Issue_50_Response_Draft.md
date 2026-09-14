# OpenSSF Issue #50 Response Draft

Thanks again. This feedback was specific enough to turn into code, not just wording.

I agreed with your ordering: static classification first, then hard admission checks, then recoverability evidence, then posture and controls. Two concrete gaps came out of your comment and I patched both:

1. Missing recoverability fields are now treated as unavailable evidence.

   If a caller omits a supported recoverability signal such as `rollback_latency`, SMERC now auto-records that field in `context.unavailable_recoverability_signals` instead of forcing the caller to invent a placeholder value. The engine still validates the rest of the action contract, but omitted recoverability evidence is handled as uncertainty, not permission.

   The decision output now carries `RECOVERABILITY_EVIDENCE_UNAVAILABLE` plus signal-specific reason codes such as `ROLLBACK_LATENCY_UNAVAILABLE`. Low-impact missing evidence caps to `THROTTLE`; high-impact or external-side-effect missing evidence caps to `FREEZE`.

2. `/v1/evaluate` can now honor the runtime admission gate when the caller includes an inline `admission` block.

   The separate `/v1/admission/evaluate` endpoint still exists, but a combined `/v1/evaluate` request can no longer produce an uncapped recoverability decision when inline admission fails. If admission returns `REJECT`, the final posture is capped to `DENY`; if admission returns an escalation-style result, the final posture is capped to `FREEZE`. The response keeps the `runtime_admission` result and marks `admission_capped_recoverability_scoring`.

Tests added:

- `tests/test_recoverability_engine.py::test_omitted_recoverability_signal_is_marked_unavailable`
- `tests/test_api_server.py::test_evaluate_with_inline_failed_admission_is_capped_before_execution`

I also re-ran the relevant API, recoverability, admission, OpenAPI, and findability suites locally: 95 tests passing.

On reviewer labels: your point is right that labels collected after seeing posture measure agreement or usefulness, not blind ground truth. I am keeping that distinction in the pilot language.

On contribution terms: SMERC is available for public review and non-production evaluation, but production deployment, commercial embedding, hosted use, resale, revenue-generating use, or integration into a commercial product requires a separate written agreement. I will keep that boundary visible so contributors can decide what they are comfortable sharing.

Relevant project notes:

- `docs/Ref_Gated_Runtime_Proof_Loop.md`
- `docs/Runtime_Evidence_Trust_Gate.md`
- `docs/External_Metadata_Reviewer_Request.md`
- `COMMERCIAL_USE.md`

This is still pilot-grade. It does not claim production enforcement, compliance, or incident reduction. The narrower claim is that failed hard admission and missing recoverability evidence should not quietly become permission to execute.

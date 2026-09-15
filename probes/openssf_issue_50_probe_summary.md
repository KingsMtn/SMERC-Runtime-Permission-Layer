# OpenSSF Issue 50 Probe Summary

Source: OpenSSF `ossf/ai-ml-security` issue 50 public feedback.

Date captured: 2026-09-15.

Commit range addressed: `a5e3057` feedback addressed through `c210e36` and follow-up hardening.

## Probe 1: Omitted Recoverability Signal

Minimal behavior tested:

- omit a supported recoverability field such as `rollback_latency`
- do not require the caller to invent a placeholder value
- treat omission as unavailable evidence

Expected behavior:

- request remains parseable if required core action fields are present
- omitted supported signal is recorded in `context.unavailable_recoverability_signals`
- final posture cannot quietly resolve to `ALLOW` only because the signal was absent

Regression test:

- `tests/test_recoverability_engine.py::test_omitted_recoverability_signal_is_marked_unavailable`

## Probe 2: Admission Rejection Versus `/v1/evaluate`

Minimal behavior tested:

- include an inline admission block in a `/v1/evaluate` request
- set a required hard-admission check to fail

Expected behavior:

- final decision is capped by admission
- failed hard admission cannot be rescued by recoverability scoring
- response keeps `runtime_admission` and marks `admission_capped_recoverability_scoring`

Regression test:

- `tests/test_api_server.py::test_evaluate_with_inline_failed_admission_is_capped_before_execution`

## Probe 3: Unknown Rollback Path In Pilot Intake

Minimal behavior tested:

- set pilot intake `rollback_path` to `unknown`

Expected behavior:

- pilot intake should not treat unknown rollback text as inert context
- compiled customer-evaluation action should mark rollback/evidence signals as unavailable
- downstream decision should carry unavailable-evidence reason codes

Regression test:

- `tests/test_pilot_intake_report.py::test_unknown_rollback_path_becomes_unavailable_recoverability_evidence`

## Boundary

These probes are public-pattern, metadata-only regression probes. They do not prove production enforcement, customer demand, compliance, security certification, or incident reduction.

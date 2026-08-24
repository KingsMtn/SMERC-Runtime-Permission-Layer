# SMERC Reviewer Quickstart Report

Version: `smerc.reviewer-quickstart.v1`
Generated at: `2026-08-24T21:53:41+00:00`

## Review Question

Is SMERC credible enough to test in a bounded shadow-mode pilot?

## Evidence Boundary

- not production certification
- not compliance attestation
- not customer validation
- not proof of incident reduction

## One Command

```bash
python -m reference_engine.reviewer_quickstart --pretty
```

## Proof Highlights

- PR Guardian posture: `ESCALATE`
- PR Guardian replay ID: `replay_AI_AUTH_MIDDLEWARE_PR_1787608420912`
- SPARTa route state: `REVIEW_REQUIRED`
- SPARTa executable: `False`
- DLL record count: `7`
- DLL verification valid: `True`
- CISO seeded decisions: `5`
- CISO stored ledgers: `5`
- Benchmark scenarios: `84`
- Benchmark decision difference rate: `0.786`
- Ref-gated requests: `4`
- Ref-gate failures: `1`
- Ref-gated scoring capped: `1`
- Ref-gated autonomy state: `SUSPEND_AUTONOMY`

## Generated Artifacts

- summary_markdown: `reports/reviewer_quickstart/Reviewer_Quickstart_Report.md`
- summary_json: `reports/reviewer_quickstart/reviewer_quickstart.json`
- pr_guardian_demo: `reports/reviewer_quickstart/End_To_End_PR_Guardian_Demo.md`
- pr_guardian_json: `reports/reviewer_quickstart/end_to_end_pr_guardian_demo.json`
- pr_guardian_comment: `reports/reviewer_quickstart/end_to_end_pr_guardian_comment.md`
- pr_guardian_certificate: `reports/reviewer_quickstart/end_to_end_pr_guardian_certificate.json`
- sparta_route: `reports/reviewer_quickstart/end_to_end_pr_guardian_sparta_route.json`
- decision_lifecycle_ledger: `reports/reviewer_quickstart/end_to_end_pr_guardian_dll.json`
- dll_intelligence: `reports/reviewer_quickstart/end_to_end_pr_guardian_dll_intelligence.json`
- ciso_seed_report: `reports/reviewer_quickstart/CISO_Evidence_Walkthrough_Seed_Report.md`
- ciso_seed_json: `reports/reviewer_quickstart/ciso_evidence_walkthrough_seed.json`
- runtime_benchmark: `reports/reviewer_quickstart/Runtime_Governance_Benchmark.md`
- runtime_benchmark_json: `reports/reviewer_quickstart/runtime_governance_benchmark.json`
- ref_gated_runtime_proof: `reports/reviewer_quickstart/Ref_Gated_Runtime_Proof.md`
- ref_gated_runtime_proof_json: `reports/reviewer_quickstart/ref_gated_runtime_proof.json`
- audit_database: `./smerc_reviewer_quickstart.sqlite3`

## Reviewer Path

1. Read the summary report.
2. Open the PR Guardian demo and confirm the action, posture, route, DLL, and DLL Intelligence are linked.
3. Open the CISO seed report and confirm the review queue has replayable seeded decisions.
4. Open the runtime benchmark and inspect where SMERC differs from simple allow/deny.
5. Open the Ref-gated runtime proof and confirm hard evidence gates run before recoverability scoring.
6. Decide whether one real GitHub Actions workflow is worth testing in observe mode.

## Pilot Gate

- Proceed only if a reviewer can name one side-effecting workflow.
- Proceed only if reviewer labels can be collected.
- Proceed only if the organization accepts observe mode before enforcement.
- Do not proceed if current controls already cover recoverability scoring and replay well enough.

## What This Proves

This proves that SMERC can generate a coherent local review package connecting a proposed AI-agent action, runtime posture, visible PR review artifact, hard Ref-gated tool-call screening, SPARTa route, Decision Lifecycle Ledger, DLL Intelligence, seeded CISO review evidence, and benchmark comparison.

## What This Does Not Prove

This does not prove customer demand, production safety, compliance readiness, or incident reduction. Those require external review, shadow-mode pilot evidence, and customer-specific calibration.

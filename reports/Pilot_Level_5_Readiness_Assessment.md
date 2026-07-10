# SMERC Runtime Permission Layer Pilot Readiness Assessment

Target: Level 5: Pilot-ready
Assessment date: 2026-07-09

Assess whether SMERC is ready for an outside technical team to run a bounded shadow-mode pilot.

## Result

Level 5 shadow-mode ready: yes
Required gates met: 7 of 7
Optional gates met: 0 of 3

## Required Failures

- None.

## Gate Results

### Working deterministic engine

- Gate ID: `working_engine`
- Required: yes
- Status: `met`
- Evidence paths present: yes
- Notes: Engine and action language are implemented and covered by unit tests.
- Evidence:
  - `reference_engine/recoverability_engine.py`
  - `reference_engine/action_language.py`
  - `tests/test_recoverability_engine.py`
  - `tests/test_action_language.py`

### Authenticated pilot API

- Gate ID: `api_and_auth`
- Required: yes
- Status: `met`
- Evidence paths present: yes
- Notes: API supports scoped principals, tenant decisions, replay, reviews, permits, route API, and audit/security events.
- Evidence:
  - `api_server.py`
  - `reference_engine/api_identity.py`
  - `docs/API_Deployment_Guide.md`
  - `tests/test_api_server.py`
  - `tests/test_api_identity.py`

### Posture-aware route layer

- Gate ID: `sparta_routing`
- Required: yes
- Status: `met`
- Evidence paths present: yes
- Notes: SPARTa converts stored SMERC decisions into executable, constrained, paused, blocked, or review-required routes.
- Evidence:
  - `reference_engine/sparta_router.py`
  - `reference_engine/sparta_registry.py`
  - `specification/SMERC_SPARTa_Router_v1.md`
  - `docs/SPARTa_Router_Operations.md`
  - `tests/test_sparta_router.py`
  - `tests/test_sparta_registry.py`

### First shadow-mode integration path

- Gate ID: `shadow_mode_integration`
- Required: yes
- Status: `met`
- Evidence paths present: yes
- Notes: GitHub Actions shadow-mode path exists for AI-assisted code, deployment, and infrastructure workflows.
- Evidence:
  - `integrations/github_actions/README.md`
  - `integrations/github_actions/action.yml`
  - `integrations/github_actions/example_workflow.yml`
  - `examples/github_actions_shadow_mode_scenarios.json`
  - `reports/GitHub_Actions_Shadow_Mode_Pilot_Report.md`
  - `tests/test_github_actions_integration.py`

### Pilot review and metrics loop

- Gate ID: `review_metrics`
- Required: yes
- Status: `met`
- Evidence paths present: yes
- Notes: Pilot reviewers can record agreement, overrides, false release, false constraint, useful constraint, and latency.
- Evidence:
  - `reference_engine/audit_store.py`
  - `reference_engine/pilot_metrics_report.py`
  - `docs/Pilot_Review_Metrics.md`
  - `pilot_console/README.md`
  - `tests/test_pilot_metrics_report.py`
  - `tests/test_pilot_console_contract.py`

### Documented local and hosted deployment path

- Gate ID: `deployment_path`
- Required: yes
- Status: `met`
- Evidence paths present: yes
- Notes: Local, Docker, and Render deployment paths are documented for pilot review.
- Evidence:
  - `Dockerfile`
  - `docker-compose.yml`
  - `render.yaml`
  - `docs/API_Deployment_Guide.md`
  - `docs/Deployment_Model.md`

### Explicit limitations and stop conditions

- Gate ID: `limits_and_stop_conditions`
- Required: yes
- Status: `met`
- Evidence paths present: yes
- Notes: Repository states that SMERC is not production-certified and names unresolved validation areas.
- Evidence:
  - `SECURITY.md`
  - `docs/Pilot_Readiness.md`
  - `docs/Evidence_And_Unknowns_Program.md`
  - `docs/Public_Review_And_Feedback.md`

### External pilot data

- Gate ID: `external_pilot_data`
- Required: no
- Status: `not_met`
- Evidence paths present: yes
- Notes: No outside design-partner pilot data has been recorded yet. This is not required to start Level 5 shadow-mode outreach, but it is required to move toward Level 6.

### Independent production security review

- Gate ID: `production_security_review`
- Required: no
- Status: `not_met`
- Evidence paths present: yes
- Notes: No independent security assessment, compliance attestation, or production approval exists.

### Signed SPARTa route artifacts

- Gate ID: `signed_sparta_routes`
- Required: no
- Status: `partial`
- Evidence paths present: yes
- Notes: SPARTa route reports exist, but route reports are not signed yet.
- Evidence:
  - `reference_engine/sparta_router.py`
  - `docs/SPARTa_Router_Operations.md`

## Interpretation

This assessment supports a shadow-mode pilot discussion only. It does not assert production readiness, customer validation, compliance certification, or incident-reduction proof.

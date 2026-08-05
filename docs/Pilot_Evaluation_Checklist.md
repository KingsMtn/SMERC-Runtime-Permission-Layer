# SMERC Pilot Evaluation Checklist

## Purpose

This checklist gives a CISO, security architect, platform engineer, or AI governance lead a practical way to decide whether SMERC is worth a controlled pilot.

It is intentionally skeptical. A pilot should proceed only if the organization can test whether recoverability-aware authorization improves real governance decisions.

## Minimum Pilot Fit

Proceed only if at least three are true:

- AI agents, copilots, scripts, or automations can propose or trigger meaningful side effects.
- GitHub Actions, CI/CD, infrastructure workflows, security automation, or agent tool calls are in scope.
- Existing approval controls are difficult to replay or explain after the fact.
- Allow/block decisions are too blunt for some workflows.
- Rollback, containment, or blast radius are recurring concerns.
- Reviewers can spend time calibrating decisions during a shadow-mode period.

## Technical Review Checklist

### Action Contract

- Confirm proposed actions can be expressed as `smerc.action.v1`.
- Confirm action metadata avoids raw secrets, credentials, customer PII, and unnecessary source-code contents.
- Confirm action hashes are deterministic for replay.
- Confirm posture outputs include reason codes and controls.

Primary files:

- `specification/SMERC_Action_Language_v1.md`
- `schemas/smerc-action-language-v1.schema.json`
- `reference_engine/action_language.py`

### Runtime Decision Behavior

- Run representative actions through the recoverability engine.
- Confirm high-reversibility actions do not receive unnecessary blocking.
- Confirm high-exposure, low-recovery actions do not receive `ALLOW`.
- Inspect reason codes for reviewer usefulness.

Primary files:

- `reference_engine/recoverability_engine.py`
- `specification/SMERC_SPL_v0.md`
- `examples/recoverability_action_requests.json`
- `examples/policies/github_actions_shadow_spl.json`
- `reports/Recoverability_Engine_Report.md`

### API And Audit

- Confirm API authentication is enabled for any shared environment.
- Confirm idempotency is used for workflow retries.
- Confirm replay IDs and decision records are retrievable by tenant.
- Confirm reviews are immutable and denominator-aware metrics are available.

Primary files:

- `api_server.py`
- `reference_engine/audit_store.py`
- `docs/API_Deployment_Guide.md`
- `docs/Pilot_Review_Metrics.md`

### Permit And Evidence Path

- Confirm eligible enforcement decisions can issue action-bound permits.
- Confirm permit preparation occurs before native controls run.
- Confirm signed control evidence is required for configured executor audiences.
- Confirm permit consumption is atomic and single use.

Primary files:

- `reference_engine/authorization_permit.py`
- `reference_engine/control_evidence.py`
- `docs/Action_Bound_Permit_Operations.md`
- `docs/Control_Evidence_Operations.md`

### GitHub Deployment Adapter

- Validate an execution plan in `validate` mode.
- Confirm the adapter uses argument arrays rather than shell strings.
- Confirm report artifacts exclude raw command output and secrets.
- Confirm timeout, cancellation, and rollback behavior are understood.

Primary files:

- `integrations/github_deployment/deployment_adapter.py`
- `docs/GitHub_Deployment_Adapter_Operations.md`
- `examples/github_deployment/execution_plan.json`
- `schemas/smerc-execution-plan-v1.schema.json`
- `schemas/smerc-execution-report-v1.schema.json`
- `schemas/smerc-sparta-execution-evidence-v1.schema.json`

## Shadow-Mode Success Metrics

Measure these before any enforcement claim:

- decision volume by posture
- reviewer agreement rate
- false release rate
- false constraint rate
- useful constraint rate
- override rate
- review latency
- approval latency impact
- number of workflow changes recommended because of recoverability findings

Do not claim production risk reduction from synthetic examples alone.

## Pilot Stop Conditions

Stop or narrow the pilot if:

- reviewers cannot understand posture reasons
- SMERC frequently constrains low-risk reversible work
- SMERC releases actions reviewers consider obviously dangerous
- metadata collection requires sensitive payloads
- workflow latency becomes unacceptable
- existing controls already produce the same decision quality with less complexity
- no design partner is willing to allocate reviewer time

## Decision Output

At the end of the pilot, produce:

- a decision-distribution report
- reviewer agreement and disagreement analysis
- examples where `THROTTLE`, `FREEZE`, or `ESCALATE` mattered
- false release and false constraint cases
- recommended calibration changes
- a go/no-go recommendation for limited enforcement

# SMERC CISO 30-Minute Review Package

## Purpose

This package gives a Chief Information Security Officer or delegated security architect a fast, evidence-based way to review SMERC without a live founder walkthrough.

The review question is narrow:

> Is SMERC credible enough to test in a bounded shadow-mode pilot for AI-agent or automation actions?

The review question is not:

> Is SMERC already a production-certified security platform?

## One-Sentence Positioning

SMERC is runtime permission infrastructure that evaluates whether AI-agent and automation actions are recoverable enough to allow, throttle, freeze, deny, or escalate before execution.

## What To Review In 30 Minutes

| Time | Action | Evidence |
| --- | --- | --- |
| 0-5 min | Understand the claim and limits. | `docs/Plain_English_Product_Overview.md`, `docs/Maturity_Model.md` |
| 5-10 min | Inspect the action boundary. | `reference_engine/action_language.py`, `specification/SMERC_Action_Language_v1.md` |
| 10-15 min | Inspect recoverability scoring and posture output. | `reference_engine/recoverability_engine.py`, `reports/Recoverability_Engine_Report.md` |
| 15-20 min | Inspect route, controls, and execution evidence. | `docs/SPARTa_Router_Operations.md`, `docs/Control_Mapping_Library.md`, `docs/Control_Evidence_Operations.md` |
| 20-25 min | Inspect replayability and auditability. | `docs/Governance_Report_Generator.md`, `reports/Governance_Report_Example.md`, `docs/Decision_Lifecycle_Ledger.md` |
| 25-30 min | Decide whether a shadow-mode pilot is justified. | `pilot_package/Level_5_Shadow_Mode_Pilot_Packet.md`, `docs/Pilot_Evaluation_Checklist.md` |

For a local product-flow demonstration, run `docs/CISO_Evidence_Walkthrough.md` after the timed review. It seeds realistic decisions, opens them through the pilot console, and generates stored DLL evidence packages.

## The System Flow To Verify

```text
agent or automation proposes action
        |
        v
SMERC evaluates structured action signals
        |
        v
posture: ALLOW / THROTTLE / FREEZE / DENY / ESCALATE
        |
        v
SPARTa routes posture into execution behavior
        |
        v
control mapping checks native mechanisms and evidence
        |
        v
permit, control evidence, audit record, and governance report
```

## What Exists Today

SMERC currently includes:

- deterministic Python reference engine
- structured action language and decision language
- recoverability-aware scoring
- runtime policy contract
- authenticated pilot API
- SQLite pilot audit store
- GitHub Actions observe-mode integration
- action-bound permit contract
- scoped workload identity
- GitHub Actions OIDC trust profile
- signed control-evidence receipts
- SPARTa posture-aware route layer
- control mapping library
- Decision Lifecycle Ledger
- replayable governance report generator
- Python and JavaScript SDKs
- test suite and generated evidence reports

## What A CISO Should Look For

Look for evidence that SMERC:

- evaluates proposed actions before side effects occur
- treats uncertainty and low recoverability as reasons for restraint
- returns intermediate postures rather than simple allow/block
- maps postures to controls that a tool can actually enforce
- records why a decision was made and what happened afterward
- fails closed when required evidence or controls are missing
- states limits plainly instead of claiming production proof

## What A CISO Should Challenge

Challenge these areas before any enforcement pilot:

- Does the action metadata reflect the real workflow risk?
- Are the thresholds calibrated against internal reviewer judgment?
- Are native controls actually enforced or merely declared?
- Can workflow owners tolerate added review latency?
- Does SMERC duplicate existing policy-as-code or approval gates?
- Are secrets, tokens, and audit records handled according to internal standards?
- Is there a clear owner for overrides and disputed decisions?

## Run-And-Inspect Commands

From the repository root:

```bash
python -m reference_engine.agent_permission_layer examples/agent_permission_actions.json --pretty
python -m reference_engine.recoverability_engine examples/recoverability_single_action.json --pretty
python -m reference_engine.sparta_router --decision examples/sparta/throttle_decision.json --plan examples/sparta/github_actions_deploy_plan.json --pretty
python -m reference_engine.control_mapping examples/control_mapping/github_actions_controls.json --posture THROTTLE --tool github_actions --capability deploy_production --controls limit_scope preview_before_execution require_rollback_plan preserve_replay --pretty
python -m reference_engine.governance_report examples/governance_report/github_actions_governance_bundle.json --pretty
python -m unittest discover -s tests
```

## Pilot Decision

Consider a shadow-mode pilot if:

- AI agents or automation can trigger deployments, infrastructure changes, data movement, or privileged workflows.
- Existing tools answer who is allowed but not whether the action is recoverable enough right now.
- Security or platform reviewers are willing to label SMERC decisions for agreement, false release, false constraint, and useful constraint.
- The pilot can start in observe mode without blocking production.

Reject or defer if:

- there are no meaningful side-effecting agent or automation workflows
- current controls already provide adequate recoverability scoring and replay
- the organization expects a certified production product immediately
- there is no reviewer capacity for calibration
- the integration cannot produce reliable action metadata

## Recommended First Pilot

Start with a GitHub Actions shadow-mode pilot:

1. Select one repository or workflow family.
2. Run SMERC in observe mode.
3. Record posture, reason codes, controls, route state, and replay ID.
4. Ask reviewers to label agreement and overrides.
5. Generate pilot metrics and governance reports.
6. Decide whether to stop, narrow, expand, or test limited enforcement.

## Evidence Needed Before Production Claims

SMERC should not claim enterprise production readiness until external pilots provide:

- decision volume across real workflows
- reviewer agreement rate
- false release rate
- false constraint rate
- useful constraint rate
- approval latency impact
- override analysis
- integration burden
- security review notes
- operational incident or near-miss correlation where available

## Bottom Line

SMERC is ready for serious technical review and bounded shadow-mode pilot discussion.

This package is not production certification.

SMERC is not yet ready to be described as production-certified, compliance-attested, or proven to reduce incidents in live environments.

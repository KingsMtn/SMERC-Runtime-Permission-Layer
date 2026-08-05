# SMERC Governance Pattern Atlas

Generated at: `2026-07-31T02:57:05+00:00`

## Purpose

This atlas consolidates the enterprise operating models SMERC has been tested against in the repository.

The point is not to claim SMERC replaces those systems. The point is to show a coherent product pattern: established governance disciplines all leave a gap at the moment an automated action is about to execute.

## Core Claim

SMERC is runtime permission infrastructure that scores whether automated actions are recoverable enough to execute before they create real side effects.

## Evidence Boundary

Unified synthetic/proxy benchmark summary only. It is not customer validation, product-market fit, production certification, compliance attestation, incident-reduction proof, or proof that any buyer will purchase SMERC.

## Unified Benchmark Summary

- Pattern count: `5`
- Total scenarios: `40`
- Total deltas: `24`
- Weighted delta rate: `0.6`
- Primary wedge: `GitHub Actions and AI-assisted software delivery shadow-mode pilot`

| Discipline | Scenarios | Deltas | Delta Rate | What SMERC Adds | Does Not Replace |
| --- | ---: | ---: | ---: | --- | --- |
| AML-inspired financial governance | 8 | 2 | 0.25 | Pre-execution recoverability scoring for financial actions without claiming AML compliance. | AML, sanctions screening, KYC, suspicious-activity reporting, custody, settlement, or payment execution. |
| Change-management-inspired production governance | 8 | 7 | 0.875 | Runtime recoverability scoring after ticket approval but before automation executes. | ITIL, ServiceNow, Jira, CABs, production approval, compliance attestation, or change-management software. |
| Security-response-inspired automation governance | 8 | 4 | 0.5 | Recoverability checkpoint before security automation isolates, disables, deletes, notifies, or alters controls. | SOAR, SIEM, EDR, threat intelligence, malware classification, or incident-response services. |
| Model-risk-inspired AI governance | 8 | 6 | 0.75 | Execution-time permission boundary between approved models, agents, tools, data, and real-world actions. | Model validation, model approval, SR 11-7 programs, model monitoring, bias testing, or AI governance systems of record. |
| SRE/incident-management-inspired reliability governance | 8 | 5 | 0.625 | Runtime recoverability checkpoint before reliability automation changes production state. | Observability, incident management, SLO tooling, pager routing, incident command, or post-incident review. |

## Strongest Examples

### AML-inspired financial governance

- Benchmark: `reports/AML_Inspired_Financial_Governance_Benchmark.md`
- Scenario: `AML_CRYPTO_WITHDRAWAL_NEW_DEVICE`
- Category: `digital_asset_withdrawal`
- SMERC posture: `FREEZE`
- Delta type: `AML_ALERT_SMERC_RESTRAINT`
- Irreversible exposure: `0.684`
- Reversible capacity: `0.251`
- Interpretation: Both lenses indicate review or restraint, but for different reasons: suspiciousness versus recoverability and execution risk.

### Change-management-inspired production governance

- Benchmark: `reports/Change_Management_Governance_Benchmark.md`
- Scenario: `CM_DATABASE_MIGRATION_WEAK_ROLLBACK`
- Category: `database_change`
- SMERC posture: `DENY`
- Delta type: `CHANGE_APPROVED_SMERC_RESTRAINT`
- Irreversible exposure: `0.813`
- Reversible capacity: `0.343`
- Interpretation: Traditional change review approves or emergency-approves the change, but SMERC restrains runtime execution because current recoverability, containment, rollback, evidence, or scope is weak.

### Security-response-inspired automation governance

- Benchmark: `reports/Security_Response_Governance_Benchmark.md`
- Scenario: `SR_SEND_CUSTOMER_BREACH_NOTICE`
- Category: `external_communications`
- SMERC posture: `DENY`
- Delta type: `BOTH_RESTRAIN`
- Irreversible exposure: `0.932`
- Reversible capacity: `0.179`
- Interpretation: Both lenses require restraint, but SMERC records recoverability scores, reason codes, and controls.

### Model-risk-inspired AI governance

- Benchmark: `reports/Model_Risk_Governance_Benchmark.md`
- Scenario: `MR_PROHIBITED_MODEL_EMAIL_SEND`
- Category: `customer_communications`
- SMERC posture: `DENY`
- Delta type: `BOTH_RESTRAIN`
- Irreversible exposure: `0.966`
- Reversible capacity: `0.17`
- Interpretation: Both lenses require restraint, but SMERC preserves runtime recoverability evidence and controls.

### SRE/incident-management-inspired reliability governance

- Benchmark: `reports/SRE_Incident_Governance_Benchmark.md`
- Scenario: `SRE_DELETE_QUEUE_BACKLOG`
- Category: `data_loss_risk`
- SMERC posture: `DENY`
- Delta type: `SRE_AUTO_SMERC_RESTRAINT`
- Irreversible exposure: `0.923`
- Reversible capacity: `0.231`
- Interpretation: The SRE playbook would auto-mitigate, but SMERC restrains the action because rollback, containment, evidence, impact scope, or recovery capacity is not strong enough.

## Why This Makes SMERC One System

Across AML, change management, security response, model risk, and SRE, the recurring enterprise question is not whether a tool can detect risk or open a ticket. The recurring gap is whether a specific automated action should proceed at the moment of execution.

SMERC's common mechanism is recoverability-weighted authorization: irreversible exposure, reversible capacity, confidence, operational stress, reason codes, controls, and replay evidence.

## Credibility Partner Readiness

Find a security, platform, reliability, or AI-governance team willing to review the evidence package and test SMERC in shadow mode against their own metadata-only workflow examples.

A credibility partner should be asked to challenge three things:

- whether the scenarios resemble real workflow actions
- whether the SMERC deltas are useful or noisy
- whether shadow-mode scoring would be worth testing against their own metadata-only examples

## Next Action

Use this atlas as the front-door evidence artifact before asking for a design-partner or credibility-partner review.

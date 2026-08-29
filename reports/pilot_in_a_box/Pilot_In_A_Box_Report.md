# SMERC Pilot-In-A-Box Report

Generated: `2026-08-29T00:35:32+00:00`

## What This Is

This is a one-command, metadata-only pilot preview. It runs SMERC across general AI-agent, cloud-admin, and financial-runtime action packs, then produces reviewer-ready evidence.

## Evidence Boundary

This package uses synthetic or reviewer-supplied metadata only. It demonstrates runtime coherence, report generation, recoverability postures, SPARTa routes, Decision Lifecycle Ledger evidence, and pilot-fit signals. It does not prove production safety, compliance, incident reduction, customer demand, or enforce-mode readiness.

## Result

- Evaluation packs: `3`
- Actions evaluated: `21`
- Non-executable routes: `9`
- Valid DLL ledgers: `21`
- Strong pilot-fit packs: `3`
- Moderate pilot-fit packs: `0`
- Posture counts: `{'ALLOW': 2, 'DENY': 9, 'THROTTLE': 10}`
- Route state counts: `{'BLOCK': 9, 'CONSTRAINED_EXECUTE': 10, 'EXECUTE': 2}`
- Actions constrained instead of simply allowed or blocked: `10`
- Binary-equivalent allow count: `12`
- Binary-equivalent block/review count: `9`

## SMERC Versus Binary Allow/Block

A traditional binary control usually has to choose between allowing useful automation and blocking it. SMERC adds middle states when an action is technically possible but needs scope limits, checkpoints, rollback evidence, or human review before execution.

| Signal | Count | Why It Matters |
| --- | ---: | --- |
| `ALLOW` | 2 | Low-risk actions can keep moving. |
| `THROTTLE` | 10 | Useful actions are constrained instead of treated as all-or-nothing. |
| `FREEZE/ESCALATE/DENY` | 9 | Poorly recoverable or poorly evidenced actions stop before execution. |
| `DLL_VALID` | 21 | Decisions produce replayable governance evidence. |

## Evaluation Packs

| Pack | Source | Pilot Fit | Actions | Non-Executable | Markdown Report |
| --- | --- | --- | ---: | ---: | --- |
| `general_ai_agent` | `examples/customer_eval_actions.json` | `strong` | 5 | 3 | `reports/pilot_in_a_box/general_ai_agent/Customer_Evaluation_Report.md` |
| `cloud_admin` | `examples/cloud_admin_customer_eval_actions.json` | `strong` | 8 | 3 | `reports/pilot_in_a_box/cloud_admin/Customer_Evaluation_Report.md` |
| `financial_runtime` | `examples/smerc_f_customer_eval_actions.json` | `strong` | 8 | 3 | `reports/pilot_in_a_box/financial_runtime/Customer_Evaluation_Report.md` |

## Single-Action Proof Loop

- Source: `examples/customer_proof_action.json`
- Markdown report: `reports/pilot_in_a_box/single_action_proof_loop/Customer_Proof_Loop_Report.md`
- Overall status: `PASS`

## Recommended Reviewer Flow

1. Read Pilot_In_A_Box_Report.md.
2. Open the strongest-fit evaluation report.
3. Replace one example pack with 5 to 25 metadata-only actions from one owned workflow.
4. Compare SMERC posture against current reviewer judgment.
5. Move to shadow mode only if reviewers find a useful difference.

## Work, Result, Impact

- Work: SMERC evaluates metadata-only action packs through hard evidence gates, recoverability scoring, SPARTa routing, autonomy impact, and Decision Lifecycle Ledger evidence.
- Result: A reviewer receives concrete reports instead of a slide-only explanation.
- Impact: A company can decide whether a shadow-mode pilot is worth time before sharing sensitive data or granting execution authority.

# SMERC First Pilot Path

## Purpose

This is the shortest practical path from interested prospect to useful pilot evidence.

The first SMERC pilot should answer one question:

> Does recoverability-aware runtime scoring give a security or platform team useful signal before AI-assisted or automated GitHub Actions workflows create side effects?

This pilot path is intentionally narrow. It is not a production rollout, compliance certification, or proof that SMERC reduces incidents. It is a controlled evidence-gathering exercise.

## Recommended Starting Point

Start with one GitHub Actions workflow in `observe` mode.

Good first workflows:

- production deployment workflow with existing human review
- infrastructure change workflow
- privileged automation workflow
- database migration workflow
- AI-assisted pull-request or code-generation workflow

Avoid the most dangerous workflow first. The first pilot should compare SMERC's recommendations against existing reviewer judgment without adding a new blocking dependency.

## What The Customer Provides

The customer should provide:

- one repository or workflow family
- one security owner
- one platform engineering owner
- one reviewer group
- a metadata-only action description for each evaluated workflow action
- existing approval or review outcome when available
- weekly reviewer labels for sampled decisions
- agreed artifact retention period
- stop conditions

The first pilot should not require production secrets, raw customer data, proprietary source code, private prompts, credentials, or regulated records.

## What SMERC Provides

SMERC provides:

- GitHub Actions observe-mode setup guidance
- action metadata schema and examples
- recoverability-aware posture scoring
- reason codes and recommended controls
- decision artifacts with replay identifiers
- optional API-backed tenant-scoped audit records
- reviewer comparison workflow
- pilot artifact summary
- final evidence report and go/no-go recommendation

SMERC does not provide production certification, compliance attestation, guaranteed incident reduction, managed enterprise SSO, customer legal approval, or replacement for IAM, OPA, code review, branch protection, SIEM, EDR, or existing change-management controls.

## Week Zero: Qualification

Before starting implementation, run the design-partner fit screen:

```bash
python -m reference_engine.design_partner_fit examples/design_partner_fit_example.json --pretty
python -m reference_engine.first_pilot_packet \
  --manifest examples/github_actions_pilot_manifest.json \
  --fit examples/design_partner_fit_example.json \
  --markdown-output reports/First_Pilot_Packet.md
```

Proceed only if:

- the workflow has real side effects or meaningful operational risk
- reviewers can label decisions during the pilot
- the metadata boundary is acceptable
- a security or platform owner is accountable
- success metrics can be measured

Do not sell a paid pilot when there is no reviewer capacity, no safe data boundary, no accountable owner, or no measurable success path.

## Week One: Observe

Goal: install the lightest scoring path and collect first evidence without blocking workflow execution.

Steps:

1. Select one workflow.
2. Generate action metadata for the proposed workflow action.
3. Run SMERC in `observe` mode through the local GitHub Action or remote API.
4. Upload `smerc-decision.json` as an artifact.
5. Confirm that decision artifacts contain no secrets or sensitive payloads.
6. Review the first ten decisions with security and platform owners.

Exit criteria:

- SMERC can score the workflow without breaking execution.
- Reviewers understand the posture, reason codes, and controls.
- The customer agrees that the artifact format is safe enough for the pilot.

## Weeks Two Through Four: Compare

Goal: determine whether SMERC changes the review conversation in a useful way.

Collect:

- decision volume
- posture distribution
- reviewer agreement rate
- override rate
- false release candidates
- false constraint candidates
- useful constraint examples
- approval latency impact
- unavailable evaluation count
- top reason codes
- top recommended controls

Weekly review should answer:

- Which decisions did reviewers agree with?
- Which decisions looked too permissive?
- Which decisions looked too restrictive?
- Which constraints would be useful in the existing workflow?
- Which metadata fields were missing or unreliable?
- Did SMERC identify risk the current process does not explicitly capture?

## 30-Day Decision

At the end of the first 30 days, choose one outcome:

| Outcome | Meaning |
| --- | --- |
| Stop | Recoverability scoring did not add useful signal. |
| Narrow | Continue on a smaller or different workflow. |
| Continue observe | More evidence is needed before recommending controls. |
| Move to recommend | Show SMERC posture and controls to reviewers during normal approval. |

Do not move directly to production enforcement because a synthetic benchmark or early pilot result looks promising. Enforcement requires customer-specific calibration, rollback proof, security review, and written approval from the customer's accountable owners.

## Success Metrics

The pilot is useful if it can measure:

- reviewer agreement rate
- false release rate
- false constraint rate
- useful constraint rate
- override rate
- approval latency impact
- action categories with highest irreversible exposure
- recommended controls that are practical in the workflow
- unresolved metadata, privacy, security, or operational blockers

## Evidence Package

The pilot should produce:

- scope and data-boundary record
- workflow configuration used for scoring
- sample decision artifacts
- weekly review notes
- decision distribution
- reviewer agreement and override metrics
- false release and false constraint analysis
- latency observations
- recommended next mode
- unresolved questions

The evidence package must clearly distinguish customer-observed data from synthetic examples, proxy benchmarks, and illustrative values.

## Commercial Boundary

The first paid offer should be a 30-day GitHub Actions shadow-mode pilot:

- one workflow
- metadata-only
- observe mode
- weekly review
- final evidence report
- price range: `$7,500-$15,000`

A 90-day design-partner pilot should be offered only when the first workflow has clear fit, reviewer capacity, safe metadata handling, and accountable ownership.

## Bottom Line

The first pilot is not about proving that SMERC is universally correct.

It is about proving whether recoverability-aware scoring produces useful, measurable governance signal in one real workflow before automated systems create side effects.

# SMERC Self-Service Pilot Start Here

## Purpose

This is the founder-light path for a company that wants to evaluate SMERC without turning the founder into the implementation team.

The first pilot question is:

> Can SMERC score one real automation workflow in observe mode and produce recoverability evidence that security and platform reviewers find useful?

This is not production enforcement, certification, incident-reduction proof, compliance approval, or a managed-service commitment.

## Recommended Pilot Shape

Start with one GitHub Actions workflow in shadow mode.

Best first workflow:

- production deployment with existing human approval
- infrastructure change workflow
- database migration workflow
- privileged automation workflow
- AI-assisted pull-request workflow

Avoid the most dangerous workflow first. The first pilot should measure reviewer agreement and useful constraint signal without changing the customer's current approvals.

## What The Customer Does

The customer owns these tasks:

1. Select one repository or workflow family.
2. Name one security owner.
3. Name one platform engineering owner.
4. Name one reviewer group.
5. Confirm a metadata-only boundary.
6. Provide 10 to 25 plain-language sample action descriptions.
7. Run SMERC in observe mode.
8. Review sampled decisions weekly.
9. Decide at day 30 whether to stop, narrow, continue observe, or move to recommend mode.

The customer should not send production secrets, credentials, raw source code, customer records, private prompts, regulated payloads, or full incident logs.

## What SMERC Provides

SMERC provides:

- public review site
- GitHub repository
- local recoverability engine
- REST API option
- Docker/Render deployment material
- GitHub Actions observe-mode workflow examples
- customer intake checker
- pilot readiness checker
- decision artifacts
- reason codes and controls
- pilot review metrics
- evidence summary generator
- benchmark context, including ILION-Bench v2 external replay and Microsoft-style security replay

SMERC does not provide customer-specific legal approval, production authorization, compliance attestation, SSO integration, managed incident response, branch protection replacement, IAM replacement, OPA replacement, SIEM replacement, EDR replacement, or human review replacement.

## 30-Minute Self-Service Path

### 1. Read The Public Pages

- CISO review: `https://admirable-sorbet-9986d5.netlify.app/ciso.html`
- Self-service pilot: `https://admirable-sorbet-9986d5.netlify.app/self-service-pilot.html`
- GitHub Actions pilot: `https://admirable-sorbet-9986d5.netlify.app/github-action.html`
- ILION external replay: `https://admirable-sorbet-9986d5.netlify.app/ilion-benchmark.html`
- Repository: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer`

### 2. Complete Intake

Start from:

```text
examples/github_actions_customer_pilot_intake_packet.json
```

Replace only metadata-safe fields.

Run:

```bash
python -m reference_engine.github_actions_customer_pilot_intake \
  examples/github_actions_customer_pilot_intake_packet.json \
  --pretty
```

Continue only if the output is ready for a review call or week-zero qualification.

### 3. Check Pilot Readiness

Run:

```bash
python -m reference_engine.github_actions_pilot_readiness --pretty
```

Review:

```text
reports/GitHub_Actions_Pilot_Readiness.md
```

### 4. Run Observe Mode

Use the GitHub Actions pilot operator path:

```text
docs/GitHub_Actions_Pilot_Operator_Quickstart.md
```

The first workflow should write `smerc-decision.json` as an artifact and must not block execution.

### 5. Review Weekly

Use:

```text
pilot_package/Weekly_Review_Template.md
```

Track:

- reviewer agreement rate
- false release candidates
- false constraint candidates
- useful constraint rate
- override rate
- unavailable evaluation count
- latency observations
- top reason codes
- top recommended controls

### 6. Generate Evidence Summary

After reviewer labels exist, run:

```bash
python -m reference_engine.core_pilot_package \
  --pilot-metrics examples/pilot_metrics_summary_sample.json \
  --pretty
```

Start with:

```text
reports/core_pilot_package/README.md
```

## Day-30 Decision

Choose one:

| Decision | Meaning |
| --- | --- |
| Stop | Recoverability scoring did not add useful signal. |
| Narrow | Try a smaller or different workflow. |
| Continue observe | More data is needed before showing recommendations in normal review. |
| Move to recommend | Show SMERC posture and controls to reviewers while existing approvals remain authoritative. |

Do not move to enforcement unless the customer has completed calibration, rollback proof, security review, written approval, and stop-condition agreement.

## Founder Involvement Boundary

The founder should not be required for:

- first-pass product review
- intake packet completion
- local demo review
- GitHub Actions observe-mode setup by a technical team
- weekly reviewer labeling
- day-30 evidence packet generation

Founder or maintainer involvement may still be needed for:

- commercial terms
- legal paperwork
- unusual deployment environments
- customer-specific integration bugs
- production enforcement decisions
- security review answers not covered by public docs

## Minimum Useful Customer Commitment

Do not start a pilot unless the customer can provide:

- one real workflow
- accountable owners
- metadata-only boundary
- 10 to 25 sample actions
- weekly reviewer time
- explicit day-30 decision criteria
- agreement that observe mode does not replace existing approvals

## Evidence Boundary

Self-service materials reduce explanation burden. This package does not prove demand, product-market fit, production safety, incident reduction, compliance, or customer willingness to pay.

# SMERC Public Review Snapshot

## Purpose

This snapshot is for a reviewer who lands on the repository and wants to know what SMERC is, what exists, what changed recently, and what should not be believed yet.

## One-Line Positioning

SMERC, short for Structural Momentum Entropy Range Confidence, is runtime permission infrastructure for AI agents.

Tagline:

> Recoverability scoring before automated actions execute.

## Current Maturity

SMERC is a Level 5 candidate:

> Pilot-ready for bounded shadow-mode evaluation.

It is not Level 6 or Level 7. There is no external design-partner pilot data, independent production security review, compliance attestation, or live incident-reduction proof in this repository.

## What Exists Now

The repository contains working product artifacts, not only concept documents:

- Python recoverability and runtime permission engine
- versioned action and decision language
- authenticated tenant-scoped REST API
- scoped workload identity and short-lived sessions
- GitHub Actions OIDC trust path
- audit store, decision replay, review queue, and pilot metrics
- pilot review console
- GitHub Actions shadow-mode integration
- action-bound permits
- signed control evidence
- GitHub deployment adapter with cancellation, rollback attempt, and non-secret execution reports
- SPARTa posture-aware routing
- control mapping library
- governance report generator
- Decision Lifecycle Ledger
- Model and Agent Fitness Layer
- Agent Handshake Protocol
- public discovery files, beacon, `llms.txt`, sitemap, and discovery audit
- Python and JavaScript SDK helpers
- Docker and Render deployment materials
- tests for the major engine, API, SDK, audit, permit, routing, control, discovery, and pilot paths

## What Recently Improved

Recent external-review improvements:

- first-pilot path for 30-day GitHub Actions shadow-mode evidence
- design-partner fit scorer
- first-pilot packet generator
- naming and search style guide
- public discovery audit tool and generated report
- AI-agent-governance landing page on the public site
- clearer brand/category/search labels using `SMERC | Runtime Permission Infrastructure for AI Agents`

## Best First Review Path

For a 10-minute review:

1. Read `docs/Plain_English_Product_Overview.md`.
2. Read `docs/CISO_Quick_Review.md`.
3. Read `docs/Public_Review_Snapshot.md`.
4. Read `docs/Release_Notes_v0_14_Public_Review.md`.
5. Inspect `reference_engine/recoverability_engine.py`.
6. Review `reports/Public_Discovery_Audit.md`.

For a 30-minute technical review:

1. Read `docs/CISO_30_Minute_Review_Package.md`.
2. Run `docs/CISO_Evidence_Walkthrough.md`.
3. Run `python -m unittest discover -s tests`.
4. Inspect `api_server.py`.
5. Inspect `integrations/github_actions/`.
6. Inspect `integrations/github_deployment/`.
7. Inspect `reference_engine/sparta_router.py`.
8. Inspect `reference_engine/decision_lifecycle_ledger.py`.

## Best First Pilot Path

The recommended first pilot is GitHub Actions shadow-mode scoring:

- one workflow
- metadata-only action descriptions
- observe mode first
- weekly reviewer comparison
- final evidence report
- explicit go/no-go decision after 30 days

Start with:

- `pilot_package/First_Pilot_Path.md`
- `pilot_package/GitHub_Actions_Pilot_Launch_Runbook.md`
- `pilot_package/Design_Partner_Qualification_Checklist.md`
- `python -m reference_engine.design_partner_fit examples/design_partner_fit_example.json --pretty`
- `python -m reference_engine.first_pilot_packet --pretty`

## What Not To Claim

Do not claim SMERC is:

- production-certified
- compliance-attested
- proven to reduce incidents
- customer-validated
- a replacement for IAM, OPA, AI gateways, SIEM, EDR, code review, approval systems, or human accountability
- a general AI firewall
- a model-safety system

## What Evidence Is Still Missing

To move toward enterprise beta, SMERC needs:

- external design-partner pilot data
- reviewer agreement and override data from real workflows
- false release and false constraint analysis
- approval latency impact
- practical constraint usefulness
- independent security review
- production key-management and tenancy hardening
- customer willingness-to-pay evidence

## Bottom Line

SMERC is not just a collection of documents. It has working engine, API, integration, audit, routing, permit, evidence, and pilot-review components.

The honest status is:

> Ready for external technical review and bounded shadow-mode pilot discussion, not ready to claim production-certified security platform.

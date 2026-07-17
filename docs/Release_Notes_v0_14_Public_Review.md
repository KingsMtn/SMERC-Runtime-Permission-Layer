# SMERC v0.14 Public Review Release Notes

## Release Purpose

This release package is intended for public technical review and bounded design-partner pilot discussion.

SMERC, short for Structural Momentum Entropy Range Confidence, is runtime permission infrastructure for AI-agent actions. It evaluates proposed actions before execution and returns replayable postures:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

Tagline:

> Recoverability scoring before automated actions execute.

## Current Maturity

Status:

> Level 5 candidate: pilot-ready for bounded shadow-mode evaluation.

This is not a production-certified release. It is not compliance-attested, not customer-validated, and not proven to reduce incidents in live environments.

## What This Release Contains

Core technical artifacts:

- recoverability-aware runtime permission engine
- strict action and decision language
- authenticated tenant-scoped REST API
- scoped workload identity and short-lived sessions
- GitHub Actions OIDC trust path
- pilot audit store, review queue, and denominator-aware metrics
- browser-based pilot review console
- GitHub Actions shadow-mode integration
- action-bound permits
- signed control evidence
- GitHub deployment adapter
- SPARTa posture-aware routing
- control mapping library
- governance report generator
- Decision Lifecycle Ledger
- Model and Agent Fitness Layer
- Agent Handshake Protocol
- Python and JavaScript SDK helpers
- Docker and Render deployment materials

External-review and pilot artifacts:

- public review snapshot
- CISO 30-minute review package
- first-pilot path
- design-partner fit scorer
- first-pilot packet generator
- public discovery audit tool and generated report
- naming and search style guide
- public Netlify discovery files, `llms.txt`, beacon, and structured project profile

## Best First Review Path

Read:

- `docs/Public_Review_Snapshot.md`
- `docs/External_Review_Start_Here.md`
- `docs/CISO_30_Minute_Review_Package.md`
- `docs/Developer_Quickstart.md`
- `docs/Security_Model.md`
- `docs/Maturity_Model.md`

Run:

```bash
python -m unittest tests.test_public_review_snapshot tests.test_public_discovery_audit tests.test_findability_docs -v
python -m reference_engine.public_discovery_audit ../SMERC-Macro-Language-Model/site --pretty
python -m reference_engine.design_partner_fit examples/design_partner_fit_example.json --pretty
python -m reference_engine.first_pilot_packet --pretty
```

For deeper local validation:

```bash
python -m unittest discover -s tests -v
```

On the managed Windows workspace, some localhost API tests may occasionally hit host-level `ConnectionAbortedError` flakiness. Those tests should be rerun directly if they fail in aggregate.

## Recommended First Pilot

Start with:

> GitHub Actions shadow-mode scoring for AI-assisted code, deployment, and infrastructure workflows.

Pilot shape:

- one workflow
- metadata-only action descriptions
- observe mode first
- no production blocking during initial phase
- weekly reviewer comparison
- final 30-day go/no-go decision

Useful files:

- `pilot_package/First_Pilot_Path.md`
- `pilot_package/GitHub_Actions_Pilot_Launch_Runbook.md`
- `pilot_package/Design_Partner_Qualification_Checklist.md`
- `examples/github_actions_pilot_manifest.json`

## What Not To Claim

Do not claim this release is:

- production-ready
- production-certified
- compliance-attested
- customer-validated
- proven to reduce incidents
- a replacement for IAM, OPA, AI gateways, SIEM, EDR, code review, approval systems, or human accountability
- a general AI firewall

## Evidence Still Needed

To move toward enterprise beta, SMERC needs:

- external design-partner pilot evidence
- reviewer agreement and override rates from real workflows
- false release and false constraint analysis
- approval latency measurements
- evidence of practical constraint usefulness
- security review of deployment and tenancy hardening
- customer willingness-to-pay evidence

## Release Summary

This release is a coherent public-review artifact: working code, tests, integration paths, pilot package, public discovery assets, and claim boundaries are present.

The right buyer-facing claim is:

> Ready for technical review and bounded shadow-mode pilot discussion.

The wrong buyer-facing claim is:

> Production-certified AI governance platform.

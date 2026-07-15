# SMERC CISO Evidence Walkthrough

## Purpose

This walkthrough gives a CISO, security architect, platform engineer, or design partner a fast way to experience the SMERC review flow locally.

It seeds a local audit database with realistic AI-agent action decisions, opens those decisions through the pilot review console, and lets the reviewer generate a stored Decision Lifecycle Ledger evidence package.

This is a product-flow demonstration. It is not customer evidence, production validation, compliance certification, or proof of incident reduction.

## What The Walkthrough Demonstrates

- SMERC evaluates structured AI-agent action requests before execution.
- Decisions become reviewable records in the tenant-scoped audit store.
- The pilot console can show review queue, posture, scores, reason codes, controls, and metrics.
- Stored Decision Lifecycle Ledger records can produce CISO evidence packages.
- Evidence packages can be downloaded as JSON or Markdown.

## Step 1: Seed The Review Database

From the repository root:

```bash
python -m reference_engine.ciso_review_seed \
  --audit-db ./smerc_ciso_review.sqlite3 \
  --json-output reports/ciso_evidence_walkthrough_seed.json \
  --markdown-output reports/CISO_Evidence_Walkthrough_Seed_Report.md \
  --pretty
```

The command uses `examples/ciso_review_seed_actions.json` and creates:

- five stored decisions
- five stored DLL decision-time ledgers
- security events marking the seeded walkthrough records
- JSON and Markdown seed reports

The seeded action set includes:

- routine test execution
- canary production deployment
- production secret rotation
- audit-log deletion
- customer-data export

## Step 2: Start The Authenticated API

Use the same audit database:

```bash
export SMERC_API_PRINCIPALS="pilot-team:pilot-console:decisions.read+reviews.read+reviews.write+metrics.read+audit.read=development-console-secret-2026-rotate"
export SMERC_AUDIT_DB="./smerc_ciso_review.sqlite3"
export SMERC_CORS_ORIGINS="http://127.0.0.1:8790"
python api_server.py --host 127.0.0.1 --port 8788
```

On Windows PowerShell:

```powershell
$env:SMERC_API_PRINCIPALS="pilot-team:pilot-console:decisions.read+reviews.read+reviews.write+metrics.read+audit.read=development-console-secret-2026-rotate"
$env:SMERC_AUDIT_DB="./smerc_ciso_review.sqlite3"
$env:SMERC_CORS_ORIGINS="http://127.0.0.1:8790"
python api_server.py --host 127.0.0.1 --port 8788
```

## Step 3: Start The Pilot Console

In another terminal:

```bash
python -m http.server 8790 --bind 127.0.0.1 --directory pilot_console
```

Open:

```text
http://127.0.0.1:8790
```

Connect with:

- API URL: `http://127.0.0.1:8788`
- Bearer key: `development-console-secret-2026-rotate`

## Step 4: Review The Queue

The queue should show the five seeded decisions. A reviewer should inspect:

- posture
- irreversible exposure score
- reversible capacity score
- confidence score
- reason codes
- controls
- plain-English summary

The seeded records are designed to show why a runtime permission layer needs more than simple allow/block:

| Example | Expected Learning |
| --- | --- |
| Routine tests | Low-risk recoverable actions can be allowed. |
| Canary deploy | Recoverable production action can be constrained rather than blocked. |
| Secret rotation | Sensitive action may require constraints or escalation. |
| Audit-log deletion | Weak recoverability and evidence should stop automated progression. |
| Customer-data export | Irreversible exposure can justify denial. |

## Step 5: Generate A Stored DLL Evidence Package

Use one `dll_decision_id` from `reports/CISO_Evidence_Walkthrough_Seed_Report.md`, for example:

```text
dll:ciso-review:ciso_review_deploy_canary
```

In the console's Stored DLL evidence package panel:

- paste the DLL decision ID
- set issuer to `pilot-console-reviewer`
- keep security event limit at `50`
- click `Generate package`

Download both:

- JSON
- Markdown

## What A Reviewer Should Look For

The evidence package should make these questions answerable:

- What action was proposed?
- What evidence existed at decision time?
- Why did SMERC choose the posture?
- Which reason codes and controls were attached?
- What record hash anchors the DLL?
- Was the generated decision certificate valid?
- Which security events were included?
- What evidence is still missing before production claims?

## What This Does Not Prove

This walkthrough does not prove:

- customer demand
- live incident reduction
- production safety
- compliance readiness
- threshold correctness for a specific enterprise
- downstream native control truth

It proves that the current repository contains a working local flow for reviewable runtime permission decisions and evidence-package generation.

## Recommended Follow-Up

After the walkthrough, a design partner should decide whether to run a shadow-mode pilot on a real workflow family. The first pilot should measure:

- reviewer agreement rate
- false release rate
- false constraint rate
- useful constraint rate
- approval latency impact
- override rate
- integration burden
- whether recoverability scoring changes the team's understanding of action risk

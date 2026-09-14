# Known Data Fallback Brief

## Purpose

This brief is for the day outside reviewers do not provide metadata.

The plan is simple:

> Do not wait forever. Do not fake customer validation. Keep building from known public patterns, generated stress cases, benchmark-shaped metadata, and safe AWS-style examples while clearly labeling the evidence.

## Current Ask

SMERC is asking reviewers for 5 to 25 metadata-only actions from one workflow, or a two-minute judgment on one AWS-style action.

Useful paths:

- `docs/AWS_One_Action_Reviewer_Ask.md`
- `docs/External_Metadata_Reviewer_Request.md`
- `docs/Tier2_AWS_Reviewer_Front_Door.md`
- `.github/ISSUE_TEMPLATE/workflow-intake-template.md`
- `.github/ISSUE_TEMPLATE/aws_metadata_pilot_request.md`

## If No One Responds

After 7 to 10 days without useful response, continue with known data:

1. public incident-pattern lessons
2. public benchmark-shaped categories
3. generated AWS-style cloud action samples
4. small deterministic stress corpus
5. public fallback adapters
6. metadata-only postcondition evidence

This keeps SMERC moving technically without pretending those artifacts are market proof.

## Existing Fallback Assets

| Asset | What It Provides |
| --- | --- |
| `docs/Public_Evidence_Fallback_Plan.md` | provenance rules and source labels |
| `docs/Public_Fallback_Adapter.md` | focused adapter for public-pattern examples |
| `docs/Small_Generated_Stress_Corpus.md` | deterministic stress corpus for cloud, MCP, CI/CD, finance, and incident pressure |
| `docs/Public_Agent_Runtime_Incident_Learning.md` | safe learning from public reporting without leaked proprietary code |
| `docs/Public_Benchmark_Ingestion.md` | benchmark-shaped metadata conversion boundary |
| `docs/AWS_Cloud_Action_Replay.md` | AWS-style metadata-only cloud action replay |
| `docs/AWS_Audit_Delay_And_Irreversibility_Map.md` | delayed evidence and structural dead-end patterns |
| `docs/AWS_One_Action_Reviewer_Ask.md` | smallest outside sanity-check loop |

## Evidence Labels

Use these labels consistently:

- `customer-owned`: supplied by an outside reviewer from one workflow
- `reviewer-labeled`: a reviewer judged whether SMERC posture was useful, too strict, too loose, irrelevant, or unclear
- `public-pattern`: derived from public reporting, advisories, docs, or benchmark descriptions
- `synthetic`: generated to test a boundary
- `emulated`: produced in a controlled local or lab environment
- `benchmark-shaped`: representative of an upstream benchmark category but not an official score
- `official-benchmark`: only when the source license, version, and runner are documented

## What To Build While Waiting

Build only things that improve the next reviewer conversation:

- clearer one-action reviewer paths
- stronger reason-code explanations
- better postcondition evidence
- public-pattern replay coverage
- compact reports that expose `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, and `ESCALATE`
- small workflow-specific examples for AWS, MCP, CI/CD, and SMERC-F

Avoid building vague enterprise features until an outside reviewer names the workflow pain.

## Decision Rule

Use customer-owned metadata when available.

Use known data when customer-owned metadata is unavailable.

Never describe known-data fallback as customer validation, production proof, incident-reduction proof, willingness-to-pay proof, compliance proof, or AWS endorsement.

## Evidence Boundary

Known-data fallback can strengthen technical proof and reviewer clarity. It cannot prove market demand, production safety, buyer urgency, acquisition value, or live customer impact.

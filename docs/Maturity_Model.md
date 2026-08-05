# SMERC Maturity Model

## Purpose

This scale keeps SMERC claims grounded. It separates idea quality, prototype quality, pilot readiness, and production readiness.

## Levels

| Level | Name | Meaning |
| --- | --- | --- |
| 1 | Idea | Concept, thesis, or language only. No working system. |
| 2 | Hobby page | Website or documents exist, but little or no runnable product behavior. |
| 3 | Prototype | Working local code exists. Tests and integration paths may be limited. |
| 4 | Serious technical prototype | Engine, API, tests, docs, examples, and coherent architecture are available for technical review. |
| 5 | Pilot-ready | An outside team can run a bounded shadow-mode pilot with setup guidance, metrics, logs, stop conditions, and clear non-production limits. |
| 6 | Enterprise beta | Multiple pilots or strong external evidence exist, with hardened deployment, monitoring, operational support, and security review in progress. |
| 7 | Production product | Real customers rely on the system with operational reliability, support, incident response, versioning, and security/compliance posture. |
| 8 | Enterprise platform scale | Broad integrations, certifications, commercial support, ecosystem trust, procurement maturity, and large-customer operating history. |

## Current Classification

SMERC is classified as:

> Level 5 candidate: pilot-ready for bounded shadow-mode review.

The repository has enough implementation, testing, and documentation for an outside technical team to evaluate SMERC in shadow mode. It is not Level 6 because no external pilot data, independent security review, or production operating record exists.

## Evidence For Level 5 Candidate Status

The generated readiness report is in:

- `reports/Pilot_Level_5_Readiness_Assessment.md`
- `reports/pilot_level5_readiness.json`

Required Level 5 gates currently met:

- working deterministic engine
- authenticated pilot API
- SPARTa posture-aware route layer
- control mapping library for native tool mechanisms and evidence requirements
- replayable governance report generator for decision, route, control, and lifecycle evidence
- GitHub Actions shadow-mode integration path
- pilot review and metrics loop
- documented local and hosted deployment path
- explicit limitations and stop conditions

Optional gaps that remain:

- no external design-partner pilot data
- no independent production security review
- signed SPARTa route reports are pilot-grade HMAC artifacts, not production key-management infrastructure
- control mappings are declared pilot contracts and require adapter validation before they should be treated as production enforcement
- governance reports assemble existing evidence; they do not create external proof of operational impact

## Language Rules

Use this language:

- "Pilot-ready for bounded shadow-mode evaluation."
- "Technical prototype with executable readiness evidence."
- "Seeking design partners to validate recoverability-weighted authorization."

Do not use this language:

- "Production-ready security platform."
- "Certified AI governance system."
- "Do not claim proven incident reduction."
- "Enterprise-grade replacement for OPA, Permit.io, Microsoft, or Cloudflare."

## Next Maturity Step

To move from Level 5 candidate toward Level 6, SMERC needs at least one external design-partner pilot that records:

- decision volume
- reviewer agreement rate
- false release rate
- false constraint rate
- useful constraint rate
- approval latency impact
- route-state distribution
- qualitative reviewer feedback
- stop-condition outcomes

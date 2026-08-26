# SMERC Content Evidence Adapter

## Purpose

SMERC should not claim to understand every email, code diff, SQL query, prompt, document, or API payload by itself.

The Content Evidence Adapter lets SMERC consume trusted content-risk signals from systems that already inspect content:

- SAST and code scanners
- SQL analyzers
- DLP systems
- email security tools
- secrets scanners
- malware scanners
- prompt-injection detectors
- policy engines
- AI evaluation platforms
- human review records

SMERC then uses those signals as runtime evidence before an action executes.

## What It Answers

> Do trusted content-risk signals show that this proposed action should be capped, constrained, escalated, frozen, or denied before execution?

This is different from the core recoverability engine. Recoverability asks whether the organization can recover from the action. Content evidence asks whether the actual content or payload appears risky enough to change the action posture.

## What It Does Not Do

This module does not:

- classify raw source code, raw customer records, private prompts, regulated payloads, or emails directly
- replace DLP, SAST, malware scanning, policy engines, or AI eval platforms
- prove production safety
- prove compliance
- prove incident reduction

It normalizes signals from those systems into a SMERC-compatible decision input.

## Input Shape

Each input uses `smerc.content-evidence-input.v1` and includes:

- `action_id`
- `content_target`
- `content_available`
- `assessments`

Each assessment includes:

- scanner source
- scanner type
- status
- finding type
- severity
- confidence
- authentication and signature status
- whether the evidence was agent-supplied
- freshness

## Output Shape

The adapter returns:

- `content_risk_score`
- `evidence_reliability_score`
- `content_trust_level`
- `max_recommended_posture`
- high-risk findings
- unavailable assessments
- reason codes
- required controls

## Runtime Rule

Content evidence can cap release, but it should not rescue weak recoverability.

Examples:

- Low-risk content with weak rollback remains constrained, frozen, denied, or escalated by recoverability.
- High-risk content can cap an otherwise recoverable action.
- Unavailable scanners can force freeze when the action is high impact.
- Agent-supplied content claims should not support autonomous release for high-impact actions.

## Run

```bash
python -m reference_engine.content_evidence --pretty
```

Generated outputs:

```text
reports/content_evidence_report.json
reports/Content_Evidence_Adapter_Report.md
```

## Evidence Boundary

Synthetic examples demonstrate content-evidence ingestion. A real pilot should use customer-approved scanner or reviewer signals and should not send raw source code, secrets, raw customer records, private prompts, production logs, or regulated payloads.


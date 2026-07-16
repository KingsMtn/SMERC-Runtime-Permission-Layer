# SMERC Pilot Data Handling And Security Boundary

## Purpose

This document defines the preferred data boundary for a SMERC pilot. The goal is to collect enough action metadata to evaluate recoverability without receiving unnecessary sensitive data.

## Preferred Data

SMERC should receive structured action metadata such as:

- action ID
- workflow or tool name
- actor or automation identity label
- action type
- environment label
- risk scores from 0.0 to 1.0
- reversibility and rollback estimates
- containment and evidence scores
- external side-effect flag
- sensitive-data flag
- reason-code context

## Data To Avoid In A First Pilot

Do not send:

- production secrets
- API keys
- raw private source code
- raw customer data
- regulated records
- full private prompts
- credential material
- payment instructions
- private keys
- personal health, financial, or identity data
- large logs that contain sensitive payloads

## Recommended Pattern

Use metadata instead of payloads.

Example:

```json
{
  "action_id": "deploy-prod-config-1021",
  "actor": "github-deployment-agent",
  "tool": "github_actions",
  "action_type": "deployment_change",
  "environment": "production",
  "reversibility": 0.42,
  "rollback_latency": 0.58,
  "external_side_effect": true,
  "sensitive_data": false
}
```

Avoid sending the actual production config contents unless the customer approves a stronger security and legal boundary.

## Storage Boundary

Pilot records may include:

- posture decisions
- replay IDs
- reason codes
- controls
- reviewer labels
- timestamps
- selected workflow metadata
- generated reports

Pilot records should not be treated as a compliance archive unless the customer separately approves retention, storage, access control, and legal hold requirements.

## Access Control

Recommended pilot roles:

- action proposer: can call evaluation endpoints
- reviewer: can read decisions and submit reviews
- auditor: can read metrics, evidence packages, and security events
- permit issuer or executor: only used in enforcement-readiness testing

Use scoped principals where possible. Avoid all-scope pilot keys except for local compatibility testing.

## Hosting Options

Local-only:

- simplest for technical evaluation
- data remains inside the customer's workstation or environment
- limited availability and durability

Customer-hosted:

- preferred for sensitive pilots
- customer controls network, storage, credentials, and retention
- requires customer infrastructure support

Hosted pilot:

- easier for demos and lower-sensitivity metadata
- should use non-sensitive metadata only
- requires explicit customer approval

## Security Limits

The current reference build uses pilot-grade controls. It does not provide:

- managed enterprise identity
- production-grade key management
- immutable external audit storage
- SIEM integration by default
- compliance certification
- multi-region availability
- formal penetration-test attestation

## Approval Requirement

Before any pilot begins, customer stakeholders should confirm:

- what data may be sent
- where records may be stored
- who may access reports
- how long records may be retained
- whether the pilot is observe-only, recommend-only, or enforcement-readiness

# External Metadata Reviewer Request

## Purpose

This page is for public reviewers, message-board readers, cloud engineers, security architects, SREs, FinOps teams, and AI-infrastructure builders who want to critique SMERC without sharing secrets or granting access.

The question is narrow:

> Does recoverability before execution belong as its own control layer for AI agents and cloud automation?

SMERC is not asking reviewers to adopt a product. It is asking whether safe metadata from one real workflow would change pre-execution judgment.

## What To Share

Share 5 to 25 metadata-only examples from one workflow.

If that is too much for a first reaction, start with the smaller example shape in `docs/Five_Row_Metadata_Example.md`.

Good examples include:

- an AI agent proposing a cloud change
- an automation worker modifying infrastructure
- a CI/CD workflow preparing a deployment
- an agent calling a tool or API
- a FinOps automation changing spend or scale
- a security remediation workflow acting on production resources
- a sanitized mirror-derived flow summary from an owned AWS workflow

For each example, include:

- short action or flow description
- actor or automated system
- target workflow family
- current outcome: `ALLOW`, `BLOCK`, `REVIEW`, `ALERT`, or `UNKNOWN`
- why current controls produce that outcome
- possible consequence if the action is wrong
- rollback or recovery path, if known
- whether a route control or postcondition observation exists, if known
- reviewer label after seeing SMERC posture: useful, too strict, too loose, irrelevant, or unclear

## What Not To Share

Do not share:

- account IDs
- ARNs
- credentials
- access keys
- session tokens
- raw logs
- packet payloads
- retained payload content
- customer records
- regulated data
- private topology
- screenshots with identifiers
- incident-sensitive details
- production commands
- live AWS access

## Best GitHub Paths

Use the path that matches your evidence:

- AWS action metadata request: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/issues/new?template=aws_metadata_pilot_request.md`
- AWS shadow mirror metadata request: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/issues/new?template=aws_shadow_mirror_metadata_request.md`
- General public review feedback: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/issues/new?template=public_review_feedback.md`

## What SMERC Returns

SMERC should return:

- accepted rows
- skipped unsafe rows
- recoverability posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- route controls
- evidence gaps
- highest exposure actions or flows
- postcondition evidence status, if observations are supplied
- performance observations
- pilot-fit next step

## Why This Matters

Work:

Replace public examples with safe metadata from one real workflow.

Result:

A reviewer can compare current allow/block/review behavior against SMERC recoverability posture without exposing secrets.

Impact:

SMERC gets closer to external proof only if real reviewers can say whether the posture was useful, too strict, too loose, irrelevant, or operationally unclear.

## Boundaries

SMERC is pilot-grade. It is not production-certified, AWS-endorsed, compliance-attested, independently security-audited, or proven to reduce incidents.

Existing identity, authorization, policy, guardrail, SIEM, SOAR, change-management, approval, and human-accountability controls remain authoritative.

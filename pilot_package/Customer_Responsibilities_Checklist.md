# SMERC Customer Responsibilities Checklist

## Purpose

This checklist prevents pilot confusion by defining what the customer must provide and decide.

## Before Pilot

Customer should:

- identify the pilot owner
- select one workflow or workflow family
- confirm the pilot mode: observe, recommend, or enforcement-readiness
- approve data boundary
- identify reviewers
- define stop conditions
- define success metrics
- approve where SMERC runs
- approve where audit records are stored
- confirm that existing approvals remain authoritative

## Technical Responsibilities

Customer should provide:

- workflow sample
- action metadata source
- expected event volume
- current approval process
- repository or workflow owner
- network path for API calls if using remote mode
- scoped credential plan
- CORS origin if using browser console
- retention preference

## Security Responsibilities

Customer should decide:

- whether action metadata can leave the customer environment
- whether SMERC must run customer-hosted
- who can access decisions and reports
- whether any fields must be redacted
- whether audit records may persist
- whether pilot reports may be shared internally
- whether enforcement testing is prohibited

## Reviewer Responsibilities

Reviewers should:

- label representative decisions
- identify false release candidates
- identify false constraint candidates
- mark useful constraints
- flag confusing reason codes
- attend weekly review or provide asynchronous notes

## Business Responsibilities

Customer sponsor should:

- confirm pilot value question
- protect team time for weekly review
- decide at day 30, 60, or 90 whether to stop, narrow, continue, or expand
- avoid treating pilot results as compliance certification

## SMERC Responsibilities

SMERC provides:

- technical setup guidance
- API, SDK, and integration documentation
- sample reports
- weekly review structure
- final findings template
- evidence-boundary language

SMERC does not provide without separate agreement:

- production managed service
- compliance certification
- legal advice
- full enterprise identity integration
- custom workflow buildout beyond agreed scope
- production enforcement approval

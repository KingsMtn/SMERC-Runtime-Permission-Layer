# SMERC Pilot Kickoff Packet

## Purpose

This packet defines how a customer can run a controlled SMERC pilot without replacing existing approvals or trusting SMERC as a production enforcement system on day one.

The recommended first pilot is GitHub Actions shadow-mode scoring for AI-assisted code, deployment, and infrastructure workflows.

## Pilot Objective

Determine whether SMERC provides useful recoverability-aware governance signals before automated actions create side effects.

The pilot should answer:

- Does SMERC identify actions that are technically authorized but hard to recover?
- Do reviewers agree with SMERC posture recommendations?
- Are `THROTTLE`, `FREEZE`, and `ESCALATE` decisions useful, or do they create noise?
- Can action metadata be generated reliably from the customer workflow?
- Is the integration burden justified by the governance value?

## Kickoff Participants

Required customer participants:

- security owner or CISO delegate
- platform engineering owner
- DevSecOps or GitHub Actions owner
- pilot reviewer group
- data/security boundary approver

SMERC-side responsibilities:

- explain pilot scope and limitations
- provide repository, API, SDK, and integration guidance
- review proposed action metadata
- help interpret pilot reports
- produce final findings package

## Human/AI Operating Model

The pilot should be human-owned and automation-assisted. AI agents, bots, scripts, and GitHub Actions may propose actions and generate metadata. SMERC may score those actions. Customer humans remain accountable for pilot scope, data boundary, reviewer labels, false release and false constraint judgments, and go/no-go decisions.

Use `pilot_package/Human_AI_Pilot_Operating_Model.md` as the operating model before the first workflow is connected.

## Pilot Boundary

Recommended scope:

- one repository or workflow family
- GitHub Actions or similar CI/CD automation
- observe mode during initial phase
- action metadata only, not raw secrets, source code bodies, private prompts, or production credentials

Out of scope unless separately approved:

- production blocking
- money movement
- customer-data export
- raw private prompts
- privileged secrets
- replacement of existing approval workflows
- compliance certification

## Required Inputs Before Start

The customer should provide:

- target workflow name and business owner
- sample workflow events or representative action descriptions
- current approval path
- existing policy outcome for each sampled action where available
- reviewer list
- environment boundary: dev, staging, or production-shadow
- data handling constraints
- stop conditions

## SMERC Setup Path

1. Confirm pilot scope and data boundary.
2. Select observe-mode integration path.
3. Generate action metadata from the workflow.
4. Call SMERC API or local engine.
5. Store replayable decisions.
6. Review posture distribution weekly.
7. Record reviewer agreement and overrides.
8. Produce final pilot report.

## Expected Deliverables

Customer receives:

- kickoff scope record
- integration notes
- weekly review notes
- posture distribution
- reviewer agreement metrics
- false release and false constraint analysis
- evidence package or final pilot report
- go/no-go recommendation

## Initial Success Definition

A pilot is useful if it produces enough evidence to decide whether SMERC should be stopped, narrowed, expanded, or tested in limited enforcement.

It is not required that SMERC be "right" on every decision. It must be understandable, measurable, and useful compared with the customer's current process.

## Boundary Statement

SMERC is pilot-grade software for controlled technical evaluation. It is not production-certified, compliance-attested, or a replacement for IAM, OPA, code review, approval workflows, SIEM, EDR, legal review, or human accountability.

# SMERC Buyer-Facing Proof Packet

## Purpose

This packet is the short version of why SMERC is worth a pilot.

It is for a security, platform, cloud, DevSecOps, AI governance, or infrastructure leader who wants to know whether SMERC solves a real operational gap without granting production access.

## The Problem

Most existing controls ask:

> Is this action allowed?

SMERC asks the missing runtime question:

> If this automated action goes wrong, can the organization contain and recover from the failure before damage spreads?

That matters for AI agents, CI/CD systems, MCP tool calls, cloud automation, financial workflows, and other high-impact actions where permission alone is not enough.

## The Product Claim

SMERC is a pilot-grade product candidate for metadata-only shadow-mode recoverability review.

It evaluates proposed automated actions before execution and returns a replayable posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

The decision is based on recoverability evidence, hard admission gates, rollback latency, containment strength, external side effects, authorization scope, anomaly pressure, and execution-boundary risk.

## The Pilot Input

Use the shadow-mode product lane:

```bash
docs/Shadow_Mode_Product_Lane.md
```

The reviewer supplies 5 to 25 metadata-only actions from one owned workflow.

Do not include secrets, raw logs, account IDs, ARNs, production commands, source code, private prompts, customer records, regulated payloads, live credentials, or live access.

Each action should answer:

- what action is proposed
- who or what initiates it
- where it will execute
- whether the execution boundary can contain failure
- what current controls would do
- what rollback would require
- what evidence is missing

## The Pilot Command

```bash
python -m reference_engine.pilot_intake_report examples/pilot_intake_template.json \
  --json-output reports/pilot_intake/pilot_intake_report.json \
  --markdown-output reports/pilot_intake/Pilot_Intake_Report.md \
  --pretty
```

## The Pilot Output

The primary output is:

```bash
reports/pilot_intake/Pilot_Intake_Report.md
```

The report shows:

- where current controls and SMERC agree
- where current controls and SMERC disagree
- which actions SMERC would constrain rather than fully block
- which actions lack recoverability evidence
- which actions fail hard admission gates
- which actions have weak execution-boundary evidence
- whether a shadow-mode pilot is justified

## The Buyer Question

The useful buyer question is not:

> Do you like the idea?

The useful buyer question is:

> Did SMERC find at least one meaningful decision gap in a real workflow that current controls do not explain clearly enough?

If yes, the next step is a bounded shadow-mode pilot.

If no, the next step is calibration or a different workflow.

## What This Can Prove

This can prove:

- SMERC can process reviewer-owned workflow metadata
- SMERC can produce a readable posture gap report
- SMERC can identify missing recoverability evidence
- SMERC can ask where an action will execute and whether failure is contained
- SMERC can help decide whether a workflow deserves shadow-mode testing

## What This Does Not Prove

This does not prove:

- production safety
- incident reduction
- regulatory compliance
- AWS endorsement
- enterprise readiness
- acquisition readiness
- replacement of IAM, OPA, SIEM, CI/CD approvals, GRC, code review, or human accountability

## Buyer Fit

The strongest first buyer fit is a team that has:

- AI-assisted coding or deployment workflows
- CI/CD automation with high-impact actions
- cloud actions with rollback or containment concerns
- MCP or tool-call automation touching real systems
- security reviewers who need clearer action-level evidence

AWS-style cloud automation is the preferred first vertical, but SMERC should stay field-of-use separable so the same recoverability logic can later support finance, insurance, crypto, and other domains.

## Next Action

Ask one reviewer for 5 to 25 metadata-only actions from one workflow.

Run the shadow-mode product lane.

Do not move to enforcement until the report produces useful reviewer disagreement and the workflow owner confirms the output is worth deeper pilot time.

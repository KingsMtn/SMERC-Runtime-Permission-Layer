# SMERC Shadow-Mode Product Lane

## Purpose

This is the preferred product path for SMERC right now.

It turns the existing project pieces into one reviewer flow:

1. one input
2. one command
3. one report
4. one reviewer ask

Use this before asking for production access, live AWS credentials, customer records, raw logs, source code, private prompts, or enforcement authority.

## One Input

Start with the general pilot intake file:

```bash
examples/pilot_intake_template.json
```

For an AWS-focused review, use the AWS metadata examples only as a shape reference:

```bash
examples/aws_customer_metadata_template.json
examples/aws_metadata_adapter_source_exports.json
```

The reviewer should replace sample rows with 5 to 25 metadata-only actions from one owned workflow.

## One Command

Run the shadow-mode pilot intake report:

```bash
python -m reference_engine.pilot_intake_report examples/pilot_intake_template.json \
  --json-output reports/pilot_intake/pilot_intake_report.json \
  --markdown-output reports/pilot_intake/Pilot_Intake_Report.md \
  --pretty
```

For AWS metadata adapter review:

```bash
python -m reference_engine.aws_metadata_adapter examples/aws_metadata_adapter_source_exports.json --pretty
```

## One Report

The primary report is:

```bash
reports/pilot_intake/Pilot_Intake_Report.md
```

For AWS adapter evidence, the companion report is:

```bash
reports/aws_metadata_adapter/AWS_Metadata_Adapter_Report.md
```

The report should show where current controls and SMERC disagree, which actions are constrained rather than blocked, which rows lack recoverability evidence, and whether a shadow-mode pilot is worth reviewer time.

## One Reviewer Ask

Ask for this, and only this:

> Replace the sample file with 5 to 25 metadata-only actions from one workflow. Do not include secrets, raw logs, account IDs, ARNs, production commands, customer records, private prompts, regulated payloads, live credentials, or live access.

Each row should answer:

- what action is proposed
- who or what initiates it
- where it will execute
- whether the execution environment boundary can contain failure
- what the current control would do
- what rollback would require
- how long rollback or containment would take
- what evidence is missing

## Decision Checklist

A result is useful when at least one of these happens:

- current controls allow an action SMERC would `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- current controls block an action SMERC can constrain with explicit controls
- SMERC identifies missing recoverability evidence
- SMERC detects a failed hard admission gate
- the reviewer can name the workflow owner and current reviewer path
- latency, rollback time, or review burden can be measured
- no production behavior changes are required

## Product Boundary

This lane is metadata-only and shadow-mode.

It does not prove production safety, incident reduction, regulatory compliance, customer demand, AWS endorsement, or readiness to enforce.

It does prove a narrower and more valuable thing: whether SMERC can turn one real workflow's safe metadata into a decision report that a platform, security, or cloud reviewer finds useful enough to continue.

## Product Rule

Do not build new broad surfaces until this lane works for a reviewer.

If nobody supplies external metadata, use public incident-pattern data and generated stress cases as fallback evidence, but keep the ask the same: 5 to 25 metadata-only actions, one workflow, one report, no live access.

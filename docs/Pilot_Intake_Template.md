# SMERC Pilot Intake Template

## Purpose

The pilot intake template is the simplest way for a company to test SMERC without a live integration.

It answers:

> If we give SMERC 5 to 25 metadata-only examples from one workflow, does it produce useful differences from our current allow, block, or review process?

Use it before asking for production access, customer data, source code, secrets, wallet keys, regulated transaction payloads, or enforcement authority.

## Input File

Start with:

```bash
examples/pilot_intake_template.json
```

The file uses the `smerc.pilot-intake.v1` format. It is friendlier than the lower-level customer-evaluation contract because it asks reviewers to state:

- what the action is
- who or what initiates it
- which system or tool would execute it
- what the current control would do: `ALLOW`, `BLOCK`, `REVIEW`, or `UNKNOWN`
- why current controls would treat it that way
- what could go wrong
- how rollback would work
- whether hard evidence gates pass
- whether the tool supports dry run, scope limit, checkpoint, rollback, and human approval
- recoverability, evidence, anomaly, scope, and authorization scores from `0.0` to `1.0`

For a completed synthetic example, start with:

```bash
examples/pilot_intake_filled_examples.json
```

The filled example includes five metadata-only actions:

- GitHub Actions production canary deploy
- MCP customer-record deletion request
- cloud IAM permission expansion
- security response endpoint isolation
- financial/stablecoin liquidity transfer

## Data Boundary

Do not include:

- secrets
- credentials
- API keys
- wallet keys
- source code
- private prompts
- raw customer records
- regulated transaction payloads
- production logs
- confidential incident details

Use metadata only. A good action description is enough for a first review.

## Run

```bash
python -m reference_engine.pilot_intake_report examples/pilot_intake_template.json \
  --json-output reports/pilot_intake/pilot_intake_report.json \
  --markdown-output reports/pilot_intake/Pilot_Intake_Report.md \
  --pretty
```

Run the filled example:

```bash
python -m reference_engine.pilot_intake_report examples/pilot_intake_filled_examples.json \
  --json-output reports/pilot_intake/filled_pilot_intake_report.json \
  --markdown-output reports/pilot_intake/Filled_Pilot_Intake_Report.md \
  --pretty
```

## Output

The generated report includes:

- current control outcome counts
- SMERC posture counts
- decision difference rate
- constrained-rather-than-blocked rate
- highest irreversible exposure actions
- current-control versus SMERC comparison table
- reason codes
- recommended controls
- SPARTa route state
- embedded lower-level customer evaluation evidence
- pilot-fit recommendation

## What A Useful Result Looks Like

A useful intake result usually shows at least one of these:

- current controls allow an action that SMERC would throttle, freeze, deny, or escalate
- current controls block an action that SMERC would throttle with explicit controls
- current controls route to generic review while SMERC identifies a specific missing evidence or recoverability issue
- hard evidence gates cap a decision before recoverability can support execution
- reviewers disagree with SMERC in a way that reveals calibration requirements

If every action is obviously safe or obviously forbidden, the workflow may not be a strong SMERC pilot candidate.

## What This Proves

This proves that SMERC can turn company-supplied metadata into a coherent review artifact.

It does not prove:

- production safety
- incident reduction
- regulatory compliance
- customer demand
- correct threshold calibration
- readiness to enforce
- replacement of IAM, OPA, AI gateways, CI/CD approval, SIEM, GRC, or human accountability

## Pilot Decision

Move from intake to shadow-mode pilot only when:

- reviewers see useful differences from current controls
- a workflow owner is available
- reviewer labels can be collected
- latency and review burden can be measured
- SMERC can run without changing production behavior

Do not move to enforcement from intake alone.

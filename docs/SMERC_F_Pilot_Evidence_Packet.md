# SMERC-F Pilot Evidence Packet

## Purpose

The SMERC-F Pilot Evidence Packet is the financial-services review wrapper around the current SMERC-F artifacts.

It connects:

```text
source export
-> normalized SMERC-F metadata
-> regulatory-context overlay
-> replay posture
-> state-change explanation
-> reviewer questions
-> pilot go/no-go criteria
```

The packet is designed for CISOs, financial-services security teams, payments risk owners, treasury reviewers, stablecoin or tokenized-finance infrastructure teams, and AI governance leaders.

## Run

```bash
python -m reference_engine.smerc_f_pilot_evidence_packet --pretty
```

Outputs:

```text
reports/SMERC_F_Pilot_Evidence_Packet.md
reports/smerc_f_pilot_evidence_packet.json
```

## What It Combines

The packet summarizes:

- `reports/SMERC_F_Source_Ingestion_Report.md`
- `reports/SMERC_F_Regulatory_Context_Report.md`
- `reports/SMERC_F_Public_Data_Replay_Report.md`
- `pilot_package/Fortune_500_Financial_Services_Review_Checklist.md`

It is meant to make the review path obvious without asking a prospect to assemble scattered artifacts.

## What It Is Not

The packet is not:

- AML compliance
- legal compliance
- fraud detection
- sanctions screening
- custody software
- settlement infrastructure
- payment execution
- production certification
- proof of customer demand
- proof of incident reduction

## First Review Boundary

The first customer-facing version should remain:

```text
30-day metadata-only shadow-mode review for one financial workflow family
```

No live funds, customer records, wallet keys, raw regulated transaction payloads, private suspicious-activity records, production credentials, or live execution instructions should be used in the first review.

## Value Hypothesis

The packet is useful only if a reviewer can say:

> This recoverability posture would have changed how we reviewed at least some automated financial actions.

If reviewers cannot say that, SMERC-F should stop or narrow instead of moving toward enforcement.

# End-to-End Reviewer Flow

This is the clean reviewer path that ties the existing SMERC pieces together:

```text
metadata intake -> schema validation -> policy evaluation -> posture output -> evidence report
```

It is meant for contributors and reviewers who want to map AWS-like or tool-call actions into SMERC without sending raw logs, credentials, account identifiers, ARNs, customer data, private prompts, or source code.

## Run

```bash
python -m reference_engine.end_to_end_reviewer_flow --pretty
```

Generated outputs:

- `reports/end_to_end_reviewer_flow.json`
- `reports/End_To_End_Reviewer_Flow.md`

## What It Proves

- Local Shadow Intake can reject unsafe or raw-log-shaped rows before public sharing.
- Dynamic Schema Gate can evaluate MCP/JSON-RPC-style tool-call shapes locally before network execution.
- SPL policy identity can be compiled and attached to the posture evidence.
- Accepted action summaries can produce posture and route hints.
- A reviewer can inspect one packet instead of stitching together scattered outputs.

## What It Does Not Prove

- no live AWS connection
- no Bedrock, CloudTrail, IAM, Lambda, or Marketplace integration
- no MCP server connection
- no production execution
- no guaranteed anonymization
- no incident reduction claim
- no replacement for IAM, policy engines, scanners, approvals, SIEM, SOAR, or human accountability

## Reviewer Use

Use this when asking for external feedback:

> Can you replace these examples with 5 to 25 metadata-only actions from one real workflow and tell us whether the SMERC posture would be useful, too strict, too loose, or irrelevant compared with your current controls?

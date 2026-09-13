---
name: Workflow intake template
about: Share 5 to 25 metadata-only workflow actions for SMERC posture review
title: "Workflow intake: "
labels: ["workflow-intake", "metadata-only", "public-review"]
---

## Before You Paste

Do not include secrets, credentials, API keys, account IDs, ARNs, IP addresses, emails, customer records, raw logs, source code, private prompts, confidential incidents, regulated payloads, or production commands.

Use metadata only. If you are unsure, keep the example generic.

## Quick Ask

Can you replace the sample rows below with 5 to 25 actions from one workflow and tell us whether the SMERC posture would be useful, too strict, too loose, or irrelevant compared with your current controls?

## Workflow Context

- Workflow family:
- Reviewer role:
- Current control style:
- Existing approval or review step:
- Main thing that could go wrong:

## Copy-Paste Table

| action_id | action_type | tool_system | current_handling | reversibility | rollback_latency_seconds | containment_strength | external_side_effects | evidence_available | blast_radius_scope | human_approval_existed | schema_contract_match |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| ACT-001 | Identity Modification | AWS IAM | allow | Reversible | 5 | High | true | policy diff summary | one role or permission set | false | true |
| ACT-002 | Credential Rotation | Secrets Manager | allow | Hard to reverse | -1 | Low | true | target secret class summary | one service credential class | false | true |
| ACT-003 | Dynamic Tool Invocation | MCP Server | log only | Unknown | -1 | None | unknown | mismatched schema summary | unknown tool side effects | false | false |
| ACT-004 | Database Change | PostgreSQL | block | Irreversible | 3600 | Low | true | DDL command class summary | production data plane | true | true |
| ACT-005 | Compute Scaling | AWS ECS | allow | Reversible | 120 | High | true | desired count summary | one service or workload group | false | true |

## JSON Option

```json
{
  "schema_version": "smerc.local-shadow-intake.v1",
  "actions": [
    {
      "action_id": "ACT-001",
      "action_type": "Identity Modification",
      "tool_system": "AWS IAM",
      "external_side_effects": true,
      "reversibility": "Reversible",
      "rollback_latency_seconds": 5,
      "containment_strength": "High",
      "evidence_available": "policy diff summary",
      "blast_radius_scope": "one role or permission set",
      "human_approval_existed": false,
      "schema_contract_match": true,
      "current_system_handling": "allow"
    }
  ]
}
```

## Your Read On The Result

After filling the rows, please add a quick reviewer label:

- useful
- too strict
- too loose
- irrelevant
- not enough information

## Boundary Confirmation

- [ ] I removed secrets, credentials, account IDs, ARNs, IP addresses, emails, customer records, raw logs, source code, private prompts, confidential incidents, regulated payloads, and production commands.
- [ ] These are metadata-only summaries from one workflow or realistic public examples.
- [ ] I understand this public issue is for review signal only, not production certification or incident-response handling.

## Relevant Links

- End-to-end reviewer flow: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/End_To_End_Reviewer_Flow.md
- Local shadow intake: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Local_Shadow_Intake.md
- Five-row example: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Five_Row_Metadata_Example.md
- Claim Registry: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Claim_Registry.md
- Evidence Bundle: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Evidence_Bundle.md

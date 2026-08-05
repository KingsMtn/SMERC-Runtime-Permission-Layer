# Microsoft Ecosystem Positioning

## Position

SMERC is recoverability-aware runtime permission infrastructure for AI agents, MCP-style tool calls, deployment automation, and high-impact workflows.

It sits after identity and policy checks, but before execution. The core question is:

> Even if an action is technically authorized, is it recoverable enough to execute right now?

## Why This Matters In The Microsoft Ecosystem

Microsoft-oriented teams are moving toward agentic workflows across developer tools, cloud operations, productivity systems, security operations, and enterprise automation. Those systems often already have identity, access control, logging, and approval mechanisms.

SMERC is not trying to replace those controls. It adds a runtime recoverability decision before a tool call, workflow, deployment, or agent action creates side effects.

## Relevant Surfaces

| Surface | Existing Controls | SMERC Addition |
| --- | --- | --- |
| MCP-style tool calls | tool discovery, tool schema, client/server transport, identity integration | pre-execution recoverability scoring and SPARTa route decision |
| GitHub Actions and DevOps workflows | branch protection, approvals, secrets, environments, audit logs | shadow-mode or enforce-mode posture before deployment, rollback, secret, or infrastructure action |
| AI agents and copilots | model safety, tool permissions, prompt defenses, enterprise policy | action-level recoverability decision with reason codes and controls |
| Security operations automation | SOAR playbooks, incident tools, escalation policies | pause, constrain, deny, or escalate high-blast-radius response actions |
| Enterprise governance review | GRC, audit evidence, ticketing records | replayable decision evidence and Decision Lifecycle Ledger records |

## What SMERC Does Not Replace

SMERC does not replace:

- Microsoft Entra ID or enterprise identity systems
- Microsoft Defender, Sentinel, Purview, or security operations tooling
- GitHub Advanced Security, branch protection, or deployment approvals
- MCP clients, MCP servers, OAuth, IAM, or tool registries
- OPA, Permit.io, policy-as-code, or enterprise access-control systems
- human accountability, legal review, compliance review, or production certification

## Proof Path For Microsoft-Oriented Reviewers

1. Read `docs/MCP_Tool_Governance.md` for the current MCP-style tool governance adapter.
2. Run the adapter against the included examples:

```bash
python -m reference_engine.mcp_tool_governance \
  --request examples/mcp/tool_call_delete_customer_records.json \
  --pretty
```

3. Review `docs/GitHub_Actions_Pilot_Operator_Quickstart.md` for the GitHub Actions pilot path.
4. Review `docs/Operator_Status_And_OPA_Log_Export.md` to see how SMERC evidence can be exported beside existing policy and audit pipelines.
5. Review `docs/Decision_Lifecycle_Ledger.md` to see how request, evidence, evaluation, review, execution, outcome, and learning records are preserved.

## Public Discovery Language

Use this phrasing in Microsoft community or MCP ecosystem discussion:

> SMERC is a recoverability-aware runtime permission layer for AI agents and MCP-style tool calls. It does not replace identity, MCP, OPA, or AI gateways. It adds a pre-execution question: if this authorized tool call goes wrong, can the organization contain, reverse, explain, and learn from it?

## Evidence Boundary

The current repository is suitable for technical review and shadow-mode pilot discussion. It is not Microsoft-certified, marketplace-listed, production-attested, or proven in a live customer environment.

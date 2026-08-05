# Draft: Recoverability-Aware Runtime Permission For MCP-Style Tool Calls

## Suggested Title

Recoverability-Aware Runtime Permission For AI Agents And MCP-Style Tool Calls

## Draft Post

AI agents are beginning to call tools, trigger workflows, modify code, update infrastructure, and interact with enterprise systems. Many teams already have identity, policy, access control, logging, and approval systems. Those controls remain necessary.

The gap I am exploring is narrower:

> When an agent is technically allowed to call a tool, should that specific action execute right now if the organization may not be able to recover from a bad outcome?

SMERC, short for Structural Momentum Entropy Range Confidence, is a pilot-grade runtime permission layer for AI-agent and automation actions. It evaluates proposed actions before execution and returns one of five replayable postures:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

The current project focuses on recoverability. It scores signals such as reversibility, containment strength, rollback latency, evidence validity, anomaly pressure, and impact scope. The goal is not to replace MCP, OAuth, IAM, OPA, AI gateways, Microsoft security tools, or human review. The goal is to add a recoverability-aware decision point between "the tool is allowed" and "the action executes."

For MCP-style workflows, the current reference adapter maps tool-call metadata into:

- a SMERC recoverability evaluation,
- a SPARTa route decision,
- a recommended client/proxy behavior such as `call_tool`, `call_tool_with_constraints`, `require_approval_before_tool_call`, `pause_tool_call`, or `block_tool_call`,
- a replayable evidence record.

The most important distinction is that SMERC is not asking only whether an action is permitted by policy. It asks whether the action is recoverable enough to execute now, and what controls should apply before side effects occur.

Public review links:

- GitHub repository: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer
- Public review site: https://admirable-sorbet-9986d5.netlify.app/
- MCP governance documentation: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/MCP_Tool_Governance.md
- Microsoft ecosystem positioning: https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Microsoft_Ecosystem_Positioning.md

I am looking for technical feedback from security architects, platform engineers, AI governance teams, and agent-framework builders:

1. Is recoverability a useful runtime signal for AI-agent tool calls?
2. Would shadow-mode scoring be a safe first evaluation path?
3. Where should this sit: agent runner, MCP proxy, workflow engine, CI/CD gate, API gateway, or approval queue?
4. What existing Microsoft, GitHub, security, or platform controls should this integrate with first?
5. What would make this unnecessary because existing controls already solve the problem?

Current evidence boundary: SMERC is suitable for technical review and shadow-mode pilot discussion. It is not production-certified, Microsoft-certified, marketplace-listed, or proven to reduce incidents in live customer environments.

## Posting Notes

Use this as a discussion post, not a sales announcement.

Do not imply Microsoft partnership, certification, endorsement, marketplace listing, or customer validation unless those facts exist.

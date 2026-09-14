# Public Runtime Pain Points To SMERC

Last updated: 2026-09-13

## Purpose

This note maps current public AWS AgentCore and MCP security pain points into SMERC proof work.

It is not customer validation, vendor endorsement, production certification, or evidence that any named company needs SMERC.

## Short Finding

Public runtime guidance is converging on a practical gap:

> Identity, authorization, isolation, gateway policy, and audit logs are necessary, but they do not by themselves answer whether a proposed action is recoverable enough to execute now.

SMERC should leverage that gap by staying focused on pre-execution recoverability:

- rollback latency
- containment strength
- blast radius
- external side effects
- session and principal binding
- gateway bypass
- schema and tool metadata drift
- postcondition evidence
- replayable posture decisions

## Source-Backed Pain Point Map

| Public pain point | Why it matters | SMERC leverage | Current artifact | Next proof move |
| --- | --- | --- | --- | --- |
| AgentCore Gateway bypass | Gateway policies, guardrails, and interceptors only protect traffic that actually flows through the gateway. | Treat gateway-only path as a recoverability and evidence precondition before execution. | `docs/AWS_Metadata_Intake_Contract.md`, `docs/AWS_Security_Ecosystem_Evidence_Path.md` | Add explicit gateway-bypass rows to the small stress corpus and AWS metadata examples. |
| Session-to-user binding | AWS notes that AgentCore validates session ID format but customer backends must enforce user/session ownership. | Score weak session binding as evidence weakness and possible cross-principal blast-radius expansion. | `docs/AWS_Agent_Action_Chain.md`, `docs/AWS_Shadow_Mirror_Metadata_Path.md` | Add session-binding fields to AWS customer metadata requests. |
| Execution role credential exposure | Any code running inside an AgentCore runtime can access the execution role credentials available to that runtime. | Raise posture when broad execution credentials combine with weak rollback, weak containment, or external side effects. | `docs/AWS_Audit_Delay_And_Irreversibility_Map.md`, `docs/Runtime_Evidence_Trust_Gate.md` | Add credential-exposure pressure to AWS action-chain scoring examples. |
| Command execution authority | Command APIs and shell sessions can run within the runtime boundary and need restricted caller access. | Treat command execution as a high-impact action family requiring recoverability metadata and postcondition evidence. | `docs/Recoverability_Metadata_Contract.md`, `docs/Small_Generated_Stress_Corpus.md` | Add command execution examples to recoverability metadata hints. |
| Audit delay and correlation gaps | CloudTrail, CloudWatch, request IDs, and VPC Flow Logs help investigate, but delayed observation is not the same as pre-execution recovery. | Keep pending mutation state and postcondition evidence separate from authorization. | `docs/AWS_Audit_Delay_And_Irreversibility_Map.md`, `docs/AWS_Postcondition_Evidence.md` | Keep proving controls happened, not only that SMERC recommended them. |
| MCP token passthrough and confused deputy | MCP servers must validate audience and avoid forwarding received tokens downstream. | Treat resource/audience mismatch and token passthrough as hard pre-recoverability gates. | `docs/MCP_Governance_Gateway.md`, `docs/MCP_Adversarial_Metadata_Replay.md` | Add recoverability metadata examples for token audience and delegated authority hints. |
| MCP tool metadata poisoning | Tool descriptions and server-provided instructions can redirect agents before tool execution. | Pair schema validation with recoverability hints so runtime gates know whether the requested call is bounded and recoverable. | `docs/Dynamic_Schema_Gate.md`, `docs/Recoverability_Metadata_Contract.md` | Add hidden-instruction normalization checks before schema and posture decisions. |

## What This Changes

Near-term build order:

1. Keep the Recoverability Metadata Contract small and easy for MCP, GitHub Actions, and AWS-style tool calls to emit.
2. Add AgentCore-style fields to AWS metadata intake: gateway path, session binding, credential exposure class, command execution class, and audit correlation evidence.
3. Add MCP delegated authority and token audience fields to MCP governance examples.
4. Add hidden-instruction and unusual character normalization to the Dynamic Schema Gate.
5. Keep the Claim Registry updated so these are recorded as source-backed technical signals, not customer proof.

## Source Notes

- AWS AgentCore Runtime security guidance: `https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-security-best-practices.html`
- AWS AgentCore Runtime Instances security model: `https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-instances-security.html`
- MCP authorization specification: `https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization`
- OWASP MCP Tool Poisoning overview: `https://owasp.org/www-community/attacks/MCP_Tool_Poisoning`

## Boundary

This document is a market and technical signal map.

It does not prove:

- customer demand
- willingness to pay
- production safety
- AWS endorsement
- MCP standard adoption
- incident reduction
- benchmark superiority

It helps SMERC decide what to build next from public, non-private runtime security guidance.

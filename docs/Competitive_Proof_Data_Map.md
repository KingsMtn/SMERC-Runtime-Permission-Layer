# Competitive Proof Data Map

## Purpose

This document maps the public proof patterns used by adjacent runtime governance, MCP gateway, policy, and AI-agent security products against the proof SMERC can legitimately reproduce.

It does not copy competitor data, private telemetry, customer claims, screenshots, or proprietary benchmarks. It identifies proof categories that are publicly observable and translates them into SMERC-compatible evidence work.

## Executive Summary

The adjacent market proves value with recurring evidence types:

1. **Catalog evidence**: inventory tools, agents, permissions, risk annotations, and missing metadata.
2. **Runtime decision evidence**: show policy or governance decisions before tool execution.
3. **Proxy/enforcement evidence**: demonstrate monitor/shadow/enforce behavior at a gateway or proxy.
4. **Audit evidence**: preserve logs, decision records, traces, approvals, overrides, and replay artifacts.
5. **Benchmark evidence**: run public or synthetic scenarios through deterministic tests.
6. **Operational evidence**: show latency, throughput, reliability, integration paths, and deployment instructions.
7. **Rollback/replay evidence**: show whether high-impact actions can be undone, replayed, or compared against prior decisions.
8. **Autonomy and budget evidence**: show how much independence, spend, tool scope, and delegation an agent can use before additional review.

SMERC can reproduce parts of all six with public data and synthetic metadata. SMERC cannot legitimately reproduce competitor customer telemetry, production adoption claims, internal incident outcomes, or non-public benchmark data.

## Competitor Proof Pattern Table

| Adjacent product type | Public proof commonly shown | Available public data SMERC can use | SMERC artifact to compare |
|---|---|---|---|
| MCP gateways | Tool-call proxy behavior, auth boundary, routing, tool-call logs, policy checks | Public MCP tool definitions, JSON-RPC-shaped `tools/call` examples, synthetic tool catalogs | `docs/MCP_Tool_Risk_Scanner.md`, `docs/MCP_Tool_Governance.md`, `docs/MCP_Proxy_Runner.md`, `docs/MCP_Transport_Proxy.md` |
| Policy-as-code systems | Policy examples, allow/deny decisions, decision logs, unit tests | Public OPA/Rego-style policy examples, GitHub Actions scenarios, cloud/IAM change scenarios | `specification/SMERC_SPL_v0.md`, `docs/Operator_Status_And_OPA_Log_Export.md`, `reports/Runtime_Governance_Benchmark.md` |
| AI gateways | Request logging, guardrails, provider routing, latency, usage analytics | Synthetic LLM/action requests, public prompt/tool-call scenarios, latency harnesses | `docs/Runtime_Health_Metrics.md`, `reports/End_To_End_PR_Guardian_Demo.md`, `docs/Timing_Evidence.md` |
| Agent security platforms | Prompt/tool risk categories, tool permissions, monitor/enforce modes, alerts | Public agent-action benchmark rows, MCP tool-risk examples, public incident writeups | `docs/ILION_Bench_Replay.md`, `docs/MCP_Tool_Risk_Scanner.md`, `docs/Real_Public_Incident_Replay.md` |
| Runtime governance platforms | Agent inventory, approval workflows, policy UI, audit trails, reviewer queues | Synthetic pilot reviews, reviewer labels, GitHub PR/action metadata | `docs/Pilot_Review_Metrics.md`, `docs/CISO_Evidence_Walkthrough.md`, `pilot_console/` |
| Enterprise access-control systems | Identity, roles, scopes, tokens, audit events, access decisions | Static pilot principals, scoped sessions, GitHub OIDC metadata | `docs/Scoped_Workload_Identity.md`, `docs/GitHub_Actions_OIDC.md`, `docs/API_Deployment_Guide.md` |
| Security approval workflows | Ticket payloads, human approval states, override logs, escalation records | Synthetic human-review requests and response evidence | `integrations/human_review/README.md`, `docs/Pilot_Ledger_Intake.md`, `docs/Decision_Lifecycle_Ledger.md` |
| Risk / GRC platforms | Reports, control mapping, audit packages, evidence exports | Synthetic control evidence, benchmark ledger bundles, decision certificates | `docs/Control_Mapping_Library.md`, `docs/Governance_Report_Generator.md`, `docs/Decision_Certificate.md` |
| Developer-agent runtime firewalls | Concrete blocked commands, local enforcement, hold/block/pass decisions, no-LLM critical path | Synthetic shell, git, database, Kubernetes, and Terraform action metadata | `examples/proxy_incident_replay_scenarios.json`, `reports/Runtime_Governance_Benchmark.md` |
| Agent observability and replay platforms | Historical replay, changed-decision counts, regression checks, traces, cost and latency evidence | Synthetic replay/regression rows and timing evidence | `docs/Benchmark_Decision_Time_Ledgers.md`, `docs/Serious_Report_Performance.md` |
| Agent control planes | Agent inventory, agent identity, token spend, delegation, budget limits, and fleet visibility | Synthetic identity, unregistered-agent, agent-spawn, and cost-pressure metadata | `docs/Autonomy_Budgeting_Framework.md`, `docs/Earned_Autonomy_Framework.md`, `docs/Runtime_Health_Metrics.md` |

## What SMERC Should Use Immediately

### 1. MCP Tool Catalog Data

Use public MCP-style tool definitions and synthetic tool definitions shaped like real MCP tools.

SMERC should measure:

- percentage of tools with missing governance metadata
- percentage of tools that create external side effects
- destructive or high-impact tool classes
- tools that should require human approval, scope limits, dry runs, rollback plans, or blocking
- mismatch between `readOnlyHint`, `destructiveHint`, and inferred risk

Current implementation:

- MCP Tool Risk Scanner
- `reference_engine/mcp_tool_risk_scanner.py`
- `examples/mcp/tool_definition_risk_examples.json`
- `reports/MCP_Tool_Risk_Scanner_Report.md`

### 2. MCP Runtime Tool-Call Data

Use JSON-RPC-shaped `tools/call` requests and metadata-only tool-call examples.

SMERC should measure:

- posture distribution across tool calls
- allowed vs constrained vs paused vs blocked calls
- route decisions through the proxy
- reason codes and controls emitted before execution
- shadow-mode vs enforce-mode differences

Current implementation:

- `reference_engine/mcp_tool_governance.py`
- `reference_engine/mcp_proxy_runner.py`
- `reference_engine/mcp_transport_proxy.py`

### 3. Public Agent-Action Benchmarks

Use public benchmark datasets only when their license and terms permit local replay. If raw data cannot be committed, download it on demand into an ignored folder and keep only SMERC-generated summary reports in the repository.

SMERC should measure:

- difference between binary labels and SMERC posture
- when `THROTTLE`, `FREEZE`, or `ESCALATE` is more informative than `ALLOW` or `BLOCK`
- false-release candidates
- false-constraint candidates
- recoverability score distribution by scenario family

Current implementation:

- `docs/ILION_Bench_Replay.md`
- `reference_engine/ilion_replay.py`
- `examples/proxy_incident_replay_scenarios.json`
- `reference_engine/runtime_benchmark_suite.py`

### 4. Competitor-Inspired Synthetic Action Patterns

Use public product-positioning patterns without copying private data, screenshots, customer telemetry, or proprietary benchmark inputs.

The current benchmark now includes metadata-only scenarios shaped around common public examples:

- destructive developer-agent commands such as infrastructure teardown
- harmless developer-agent PR creation after passing validation
- prompt-injection-driven external data transfer
- token spend, agent spawning, loop, and autonomy-budget pressure
- approval-memory reuse after material conditions changed
- model or policy replay regression before release
- unregistered agent identity and inventory gaps
- MCP tool calls with valid tool names but overbroad arguments

SMERC should measure:

- whether recoverability creates a useful middle posture before execution
- whether a traditional allow/block decision misses rollback, evidence, or scope problems
- whether replay and prior approvals are safe to reuse under changed conditions
- whether budget, delegation, and identity pressure should reduce autonomy
- whether a registered tool is still unsafe because arguments or object scope changed

### 5. Public Incident Writeups

Use public incident reports only for source facts. Analyst-assigned SMERC signals must be clearly labeled as assumptions.

SMERC should measure:

- whether known failure modes would have elevated irreversible exposure
- whether rollback difficulty aligns with exposure/capacity scores
- which evidence would have been missing before the action
- which controls would have been recommended before execution

Current implementation:

- `docs/Real_Public_Incident_Replay.md`
- `reference_engine/real_incident_replay.py`

### 6. Synthetic Production-Like Workflow Data

Use fake-customer environments to prove product mechanics without pretending to have customer validation.

SMERC should measure:

- whether the full flow works end to end
- whether action intake, SMERC evaluation, SPARTa routing, permits, control evidence, DLL, DLL Intelligence, and reports connect without manual stitching
- latency and unavailable-evaluation behavior

Current implementation:

- `docs/Fake_Customer_Production_Like_Test.md`
- `reference_engine/fake_customer_pilot.py`
- `docs/Timing_Evidence.md`

## Proof SMERC Should Not Claim From Public Data

Public and synthetic proof cannot establish:

- incident reduction
- outage prevention
- compliance certification
- production security certification
- customer willingness to pay
- enterprise deployment readiness
- superiority over a named competitor in that competitor's own environment
- validity of customer-specific thresholds

Those claims require external pilot data, customer labels, customer-owned outcomes, independent security review, or formal certification.

## Recommended Next Evidence Build

The next best build is a **competitive proof parity harness**:

1. Load a mixed public/synthetic input bundle:
   - MCP tool definitions
   - MCP tool calls
   - GitHub Actions metadata
   - public incident replay assumptions
   - public benchmark rows when licensing allows
2. Run the bundle through SMERC.
3. Produce one report with the same proof categories competitors use:
   - catalog risk
   - runtime decisions
   - proxy actions
   - audit/replay evidence
   - benchmark deltas
   - operational latency
4. Keep the report explicit about source boundaries.

This would let SMERC say:

> We evaluated SMERC against the same public proof categories used by adjacent MCP gateway, AI gateway, policy, and runtime governance products. The current evidence shows mechanical fit and recoverability-specific decision differences, not customer-validated risk reduction.

## Commercial Interpretation

The useful sales line is not "SMERC is better than all competitors."

The useful sales line is:

> Existing systems can prove authorization, routing, policy, and logging. SMERC adds a recoverability proof layer: before an agent tool executes, SMERC estimates irreversible exposure, reversible capacity, required controls, replay evidence, and whether prior approvals or rollback assumptions still apply.

That is the lane to validate.

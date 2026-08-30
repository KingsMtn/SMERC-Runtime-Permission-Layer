# Market Signal To Proof Map

Last updated: 2026-08-30

## Purpose

This map connects public market and technical-community signals to concrete SMERC proof artifacts.

It answers one question:

> What are people already worried about, what public data or benchmark shape can we learn from, what has SMERC already built, and what should be proven next?

This is not customer validation, demand proof, pricing proof, or a claim that SMERC is better than adjacent products.

## Short Finding

The strongest public signal is not that buyers are searching for "SMERC."

The strongest signal is that technical communities and vendors are converging on the same operational problem:

> AI agents are gaining tool access, cloud access, financial workflow access, and execution authority faster than organizations can prove the action is bounded, recoverable, attributable, and reviewable.

SMERC should keep using market language people already search for:

- AI agent governance
- MCP security
- runtime authorization
- tool-call governance
- action-boundary drift
- pre-execution governance
- cloud automation guardrails
- recoverability scoring
- Decision Lifecycle Ledger

Use SPARK, SPARTa, and other internal names as internal architecture terms after the plain category is clear.

## Signal Map

| Public signal | What it suggests buyers worry about | Public data or benchmark shape | Current SMERC proof | Next useful proof |
| --- | --- | --- | --- | --- |
| Agent governance discussions | Agents can act with unclear identity, authority, and accountability. | AgentGovBench-style identity, policy, observability, and isolation scenarios. | `docs/Public_Benchmark_Ingestion.md`, `docs/Scoped_Workload_Identity.md`, `docs/Agent_Identity_Gate.md` | Add an AgentGovBench-compatible runner or mapping when licensing and runner interfaces allow it. |
| MCP security work | Tool descriptions, outputs, and tool chains can poison or redirect agent behavior. | MCP tool poisoning, MCP safety, JSON-RPC `tools/call`, and tool catalog examples. | `docs/MCP_Tool_Risk_Scanner.md`, `docs/MCP_Governance_Gateway.md`, `docs/MCP_Transport_Proxy.md`, `docs/Public_Benchmark_Ingestion.md` | Add a larger license-compatible MCP corpus replay and report unsupported fields explicitly. |
| Action-boundary benchmarks | The approved action and executed action can drift before side effects happen. | Approved-action vs executed-action records, drift classes, execution evidence. | `docs/Public_Benchmark_Ingestion.md`, `docs/Complete_Lifecycle_Proof.md`, `docs/Action_Bound_Permit_Operations.md` | Add action-boundary object comparison before SPARTa route execution. |
| Agent egress and exfiltration tests | External destinations, secrets, and outbound actions create risk even when a model sounds compliant. | Egress attack cases, secret exfiltration examples, external webhook or network destinations. | `docs/MCP_Tool_Risk_Scanner.md`, `docs/Runtime_Evidence_Trust_Gate.md`, `docs/Content_Evidence_Adapter.md` | Add destination and egress metadata as first-class fields in customer action intake. |
| Cloud and infrastructure governance | AI/devops agents can change IAM, network, Kubernetes, DNS, databases, capacity, and backup posture. | Cloud change metadata, Terraform-like plans, audit summaries, rollout plans. | Cloud Admin Proof Pack: `docs/Cloud_Admin_Proof_Pack.md`; Cloud Metadata Connector: `docs/Cloud_Metadata_Connector.md` | Add cloud postcondition evidence: did scope limit, rollback, or checkpoint actually occur? |
| Financial automation and stablecoin operations | Future finance workflows need action control before settlement, liquidity, collateral, or tokenized actions move. | Public-data-shaped financial stress and metadata-only transaction-control examples. | `docs/SMERC_F_Fortune_500_Financial_Services_Review.md`, `docs/SMERC_F_Financial_Public_Data_Replay.md`, `docs/SMERC_F_Financial_Source_Ingestion.md` | Add institution-style threshold profiles for treasury, payment, stablecoin, and tokenized-collateral action families. |
| Runtime performance claims | Governance that slows teams too much will be bypassed. | Latency benchmarks, proxy overhead, workflow duration, review burden. | `docs/Timing_Evidence.md`, `docs/Runtime_Health_Metrics.md`, `reports/Competitive_Proof_Parity_Report.md` | Report median and p95 decision latency in every customer-evaluation proof path. |
| Auditability and replay | A log of what happened is weaker than a replayable record of why action was allowed, constrained, or blocked. | Decision logs, signed tickets, approval records, replay artifacts. | `docs/Decision_Lifecycle_Ledger.md`, `docs/DLL_Intelligence.md`, `docs/Complete_Lifecycle_Proof.md` | Add optional tamper-evident packaging for customer-facing DLL exports. |

## What This Changes

SMERC should keep building in this order:

1. Make the public proof path easier to run.
2. Add public benchmark-compatible adapters where the license and methodology are clean.
3. Add postcondition evidence so SMERC can prove controls happened, not only that it recommended controls.
4. Add performance metrics to every serious report.
5. Ask external reviewers to replace examples with 5 to 25 metadata-only actions from one real workflow.

## Buyer-Readable Interpretation

Work: observe public technical concerns, translate them into safe metadata, and run them through SMERC.

Result: SMERC shows where it allows low-risk actions, adds restraint to baseline-allowed actions, blocks weak-evidence actions, and preserves decision lifecycle evidence.

Impact: a company can decide whether recoverability-before-execution changes judgment before sharing secrets, granting production access, or replacing existing controls.

## Useful Public Sources To Revisit

- AgentGovBench: `https://github.com/agentic-control-plane/agentgovbench`
- Agent Action Boundary Benchmark: `https://github.com/OndCo/Agent-Action-Boundary-Benchmark`
- AgentDefense-Bench: `https://github.com/arunsanna/AgentDefense-Bench`
- MCPTox / MCP tool poisoning benchmark: `https://ojs.aaai.org/index.php/AAAI/article/view/40895`
- MCP-SafetyBench: `https://xjzzzzzzzz.github.io/mcpsafety.github.io/`
- Microsoft MCP control-plane article: `https://developer.microsoft.com/blog/securing-mcp-a-control-plane-for-agent-tool-execution/`
- PipeLab agent egress corpus: `https://pipelab.org/blog/agent-egress-bench-benchmark-corpus/`

## Boundary

This map validates the problem space and helps prioritize proof work.

It does not prove:

- customer demand
- willingness to pay
- production safety
- compliance readiness
- superiority over named competitors
- benchmark performance on official upstream datasets
- acquisition value

Those require customer-owned metadata, formal pilots, independent review, and measured operational outcomes.

# Runtime Data Source Map

## Purpose

This map identifies current public runtime, MCP, AI-agent, cloud-action, and financial-action data sources that can strengthen SMERC proof without copying private data, secrets, proprietary benchmark rows, or customer telemetry.

It answers the practical reviewer question:

> Which external datasets or benchmark families should SMERC test next, and what would each prove?

## Short Finding

SMERC should prioritize public data that contains tool calls, action attempts, runtime traces, authorization context, attack objectives, latency, or financial-action evidence.

The best near-term sources are:

1. Agent Security Benchmark
2. CrossMCP-Bench
3. AgentShield-Bench
4. SyFI TraceLab
5. Toolathlon
6. Blackstable stablecoin blacklisting dataset

These do not prove customer value by themselves. They can prove that SMERC can map current public runtime problems into pre-execution recoverability decisions, Governance Routing Workbench routes, postcondition expectations, and Decision Lifecycle Ledger evidence.

## Data Source Table

| Source | What It Contains | SMERC Use | Best Proof Outcome | Boundary |
| --- | --- | --- | --- | --- |
| Agent Security Benchmark | Tool-access attack prompts, tool-call transcripts, raw results, MCPGuard comparison, attack categories such as exfiltration, stored prompt injection, privilege escalation, social engineering, multi-step escalation, and inconsistency probing. | Convert attack attempts and captured tool calls into metadata-only SMERC action requests. | Show where SMERC would add `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE` around tool-use attacks before execution. | Use only license-compatible rows and cite source/version. Do not claim official benchmark performance unless the documented runner is used. |
| CrossMCP-Bench | Authorization-conditioned MCP scenarios across multi-server MCP architectures, including attack and benign scenarios. | Map scenario policy category, server/tool context, requested action, and benign/attack label into MCP Governance Gateway inputs. | Show SMERC fit for MCP runtime authorization and multi-server tool-call governance. | Hugging Face dataset terms and version must be recorded before local replay. |
| AgentShield-Bench | Structured tool-calling/MCP scenarios with trusted instructions, untrusted content, tools, canary secrets, expected safe behavior, and attack success conditions. | Extract non-secret metadata about trusted/untrusted boundary, tool family, content risk, and expected safe behavior. | Test content evidence, fallback policy, hard gates, and unavailable evidence handling. | Do not commit canary secrets or raw prompt content if unnecessary; prefer derived metadata. |
| SyFI TraceLab | Real-world coding-agent traces, tool calls, latency distributions, cache behavior, human waits, and workload characteristics from Claude Code and Codex sessions. | Use trace metadata to calibrate autonomy budgets, tool-call pressure, latency reporting, and consequence horizon. | Move SMERC from synthetic action examples toward real agent runtime shape and operational overhead evidence. | Use documented public-access terms. Avoid personal, prompt, or session content unless explicitly permitted and needed. |
| Toolathlon | Long-horizon tool-use tasks, many tool categories, trajectories, evaluators, and public evaluation service paths. | Use task/tool trajectories to identify where a recoverability checkpoint should intervene without breaking legitimate task completion. | Test SMERC against long-horizon agent workflows instead of isolated one-step actions. | Treat task success as upstream benchmark evidence, not SMERC safety proof, unless SMERC-specific replay is documented. |
| Blackstable | Stablecoin freeze and unfreeze actions across chains with transaction metadata, public triggers, entities, incidents, and source links. | Feed SMERC-F with public financial-action metadata around freeze/unfreeze authority, reversibility, evidence validity, and policy/timing context. | Strengthen Financial Runtime proof for stablecoin, wallet-policy, reserve, freeze, unfreeze, and recoverability evidence. | Public on-chain and cited event data only. Do not claim AML, sanctions, fraud, custody, settlement, or compliance certification. |

## What To Build Next

### 1. Runtime Data Adapter Registry

Create a small registry of external source profiles:

- source name
- source URL
- license or terms status
- allowed local use
- raw-data commit policy
- normalized SMERC target contract
- unsupported fields
- evidence boundary

This gives reviewers a clear answer before any external row is ingested.

The first implemented source-specific replay is `docs/Agent_Security_Benchmark_Replay.md`.

The first implemented MCP adversarial replay is `docs/MCP_Adversarial_Metadata_Replay.md`, which converts public MCP security pain points into safe metadata-only records for tool metadata, schema, server-instruction, cache, argument, encoded-instruction, and missing-evidence failure shapes.

Public incident learning should follow `docs/Public_Agent_Runtime_Incident_Learning.md`: use public reporting, public advisories, public research, and public benchmark descriptions to improve threat models and metadata-only replay packs, but do not use leaked proprietary source, copied private architecture, credentials, raw logs, private prompts, or customer data.

### 2. Metadata-Only Normalizers

Build source-specific normalizers that output `smerc.customer-evaluation.v1` actions or MCP Governance Gateway inputs.

Priority order:

1. Agent Security Benchmark normalizer
2. CrossMCP-Bench normalizer
3. AgentShield-Bench normalizer
4. SyFI TraceLab metadata normalizer
5. Blackstable financial runtime normalizer
6. Toolathlon long-horizon tool-use normalizer

Public agent-runtime incident lessons should become metadata-only records only after the source boundary is clean. Useful derived fields include agent family, tool family, delegated authority mode, rollback path status, credential exposure pressure, postcondition evidence status, and reviewer label.

### 3. Benchmark Boundary Reports

Every run should report:

- source URL
- source version or commit
- row count
- inclusion criteria
- skipped rows and why
- SMERC policy version
- posture distribution
- Governance Routing Workbench route distribution
- latency and overhead
- decision deltas against any upstream labels
- non-claims

### 4. Customer Bridge

Use the public runtime-data report to ask reviewers for replacement data:

> Here is how SMERC handled public runtime/tool-use data. Can you replace these examples with 5 to 25 metadata-only actions from one real workflow?

That is the bridge from public benchmark proof to customer-owned metadata.

## Work / Result / Impact

Work: identify license-compatible public runtime data, map it into SMERC-compatible metadata, and preserve source boundaries.

Result: reviewers can see that SMERC is being tested against current public agent/tool-call/security/financial runtime problems, not only founder-created examples.

Impact: SMERC becomes easier to evaluate as a serious pre-execution recoverability control because its proof path follows the same external data shapes that AI-agent, MCP, cloud, and financial-runtime teams already recognize.

## Evidence Boundary

This map is not benchmark certification, customer validation, production readiness, incident-reduction evidence, or proof that a named company needs SMERC.

It is an evidence roadmap. Named public datasets should be replayed only when license-compatible, versioned, and reported with clear inclusion criteria.

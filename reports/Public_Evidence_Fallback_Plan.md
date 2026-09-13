# Public Evidence Fallback Plan

Generated: `2026-09-13T12:54:46+00:00`
Version: `smerc.public-evidence-fallback.v1`

## Work / Result / Impact

- Work: Inspect public agent-failure, action-boundary, MCP-security, reliability, and incident benchmarks for metadata provenance.
- Result: SMERC has a fallback evidence map showing where adjacent projects obtained useful metadata and how SMERC can safely learn from their shapes.
- Impact: If outside reviewers do not provide 5 to 25 workflow actions, SMERC can keep building from public-pattern evidence while stating clearly that it is not customer validation.

## Short Finding

Adjacent projects are moving forward by building structured public, synthetic, generated, emulated, or benchmark-shaped datasets with explicit provenance. SMERC should do the same if no reviewer provides private metadata.

## Source Provenance

| Source | Metadata origin | What SMERC can learn | Priority |
| --- | --- | --- | ---: |
| [Lakmus Agent Failures](https://github.com/lakmus-ai/agent-failures) | realistic generated tasks run across multiple LLM APIs, then labeled with failure taxonomy and judge evidence | Map failure labels into missing evidence, wrong-tool selection, goal drift, unsupported claim, or constraint violation pressure before execution. | 2 |
| [Agent Action Boundary Benchmark](https://github.com/OndCo/Agent-Action-Boundary-Benchmark) | synthetic runtime-boundary corpus with approved_action, executed_action, policy, drift class, expected control outcome, runtime surface, and scenario family | Map approval-execution drift into SMERC posture, route, rollback-path, and evidence-boundary decisions. | 1 |
| [AgentShield-Bench](https://huggingface.co/datasets/alirezaaminzadeh/agentshield-bench) | structured adversarial and benign tool-calling/MCP scenarios with trusted instructions, untrusted content, tools, canary secrets, expected safe behaviors, and attack success conditions | Derive metadata-only tool risk, trusted/untrusted evidence, expected safe behavior, and hard-deny conditions for Dynamic Schema Gate and MCP governance. | 1 |
| [CrossMCP-Bench](https://huggingface.co/datasets/MLZoo/CrossMCP-Bench) | authorization-conditioned MCP scenarios across multi-server MCP architectures with attack and benign cases | Map multi-server MCP authorization conditions into pre-execution posture and gateway route behavior. | 2 |
| [WeTriedAI Failure-Repair Corpus](https://wetriedai.com/dataset) | selected synthetic failures with prompt, first failed result, one correction, checks, scores, evidence notes, and limitations | Borrow the failure-to-correction audit shape for SMERC calibration reports and transition guidance. | 3 |
| [Agent Reliability Lab](https://github.com/Hai-qq/agent-reliability-lab) | project-owned synthetic states in deterministic local environments with fault injection, state evaluators, runtime comparisons, and evidence bundles | Use fault-injected state transitions to test rollback evidence, cancellation reliability, and postcondition proof. | 3 |
| [NIKA Network Incidents Benchmark](https://sands-lab.github.io/nika/) | curated network incidents from emulated network scenarios with injectable root causes, telemetry, CLI interaction, traces, ground truth, and submissions | Map incident-remediation actions into recoverability posture, rollback evidence, and escalation when live network state is uncertain. | 4 |
| [MCP-AttackBench](https://www.emergentmind.com/topics/mcp-attackbench) | MCP-specific samples from public data, real-world metadata, and GPT-augmented content for LLM-tool interactions | Map MCP attack metadata into schema, content-evidence, and tool-call route controls without importing operational exploit payloads. | 4 |

## Build Order

1. Implement source registry and provenance report before importing any upstream rows.
2. Map Agent Action Boundary Benchmark and AgentShield-Bench first because their metadata directly matches action boundary and tool-call governance.
3. Use Lakmus Agent Failures for calibration language and failure taxonomy, not direct cloud-action proof.
4. Use NIKA later for infrastructure remediation and rollback evidence once SMERC has a stronger live/sandbox story.
5. Keep asking for customer-owned metadata, but do not block public-pattern progress on silence.

## Evidence Boundary

This report is source-provenance planning, not an official benchmark run, endorsement, customer validation, production proof, or permission to copy upstream data. Each source needs license and version checks before any row-level replay. SMERC should prefer derived metadata and cite source boundaries.

## Outreach Bridge

Public-pattern evidence should end with the same ask: replace these examples with 5 to 25 metadata-only actions from one real workflow.

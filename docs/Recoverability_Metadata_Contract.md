# Recoverability Metadata Contract

## Purpose

The Recoverability Metadata Contract is the smallest practical SMERC-adjacent idea: a tiny machine-readable hint attached to one tool call, CI/CD step, cloud action, or automation proposal before execution.

It lets smaller systems answer:

> What do we know about rollback, side effects, blast radius, available evidence, and the safest posture hint before this action runs?

## Run

```bash
python -m reference_engine.recoverability_metadata_contract --pretty
```

This validates `examples/recoverability_metadata_examples.json` and writes:

- `reports/recoverability_metadata_contract_report.json`
- `reports/Recoverability_Metadata_Contract_Report.md`

## Minimal Shape

```json
{
  "version": "smerc.recoverability-metadata.v0",
  "action_id": "RMC-MCP-001",
  "action_type": "tool_call",
  "tool_system": "mcp.repo.write_file",
  "reversible": true,
  "rollback_latency_seconds": 30,
  "external_side_effect": true,
  "blast_radius_scope": "single repository file",
  "evidence_available": "proposed diff and pinned schema id",
  "tooling_isolation": "restricted_tools",
  "host_isolation": "process",
  "network_isolation": "none",
  "sandbox_escape_surface": ["none_known"],
  "execution_environment_boundary": "mcp_server",
  "recommended_posture": "THROTTLE"
}
```

## Optional Environment Boundary Evidence

Public sandboxing and agent-evaluation work increasingly treats the execution environment as part of the safety question. SMERC should do the same without forcing every contributor to expose infrastructure details.

The optional fields are:

| Field | Why it matters |
| --- | --- |
| `tooling_isolation` | Shows whether the action is limited to restricted tools or can reach shell, browser, code execution, or privileged automation. |
| `host_isolation` | Shows whether the executor is a process, container, hardened container, VM, dedicated account, production host, or unknown. |
| `network_isolation` | Shows whether the action can reach the internet, a scoped private network, or production network paths. |
| `sandbox_escape_surface` | Names known risk surfaces such as Docker sockets, privileged containers, host mounts, cloud metadata access, or production credentials. |
| `execution_environment_boundary` | Names where the action would run, such as an MCP server, CI runner, cloud function, Bedrock action group, Kubernetes workload, or production host. |

These are evidence fields, not automatic permission. Weak isolation should generally raise the required evidence before SMERC returns `ALLOW`.

## Why This Is Smaller Than SMERC

This contract does not score the action, route execution, preserve a Decision Lifecycle Ledger, or replace authorization.

It creates better inputs for larger systems. MCP servers, GitHub Actions, AWS-style action groups, cloud automation, and internal tools can emit this small hint so SMERC or another runtime does not have to infer recoverability from incomplete logs after the action already ran.

## Boundary

Recoverability metadata is not execution permission, customer validation, production certification, compliance evidence, or proof that an action is safe.

It is a small ecosystem hook that makes recoverability visible at the action boundary.

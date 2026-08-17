# MCP Tool Risk Scanner

## Purpose

The MCP Tool Risk Scanner is a public-facing front door for SMERC MCP governance.

It answers a smaller question than the full MCP governance adapter:

> If this tool is made available to an AI agent, what recoverability and autonomy risks should a reviewer inspect before the tool is called?

The scanner accepts an MCP-style tool definition, derives recoverability risk signals from tool name, description, input schema, and annotations, then returns:

- likely SMERC posture
- irreversible exposure score
- reversible capacity score
- risk-adjusted authorization score
- reason codes
- recommended controls
- missing governance metadata
- a starter `smerc.mcp-tool-governance.v1` request skeleton

## Command

```bash
python -m reference_engine.mcp_tool_risk_scanner \
  --tool examples/mcp/tool_definition_risk_examples.json \
  --select delete_customer_records \
  --pretty
```

Outputs:

```text
reports/mcp_tool_risk_scanner_report.json
reports/MCP_Tool_Risk_Scanner_Report.md
```

## Why This Exists

Many teams will not start by wiring SMERC into a live proxy. They will start by asking whether their agent tool catalog contains tools that are too powerful, too hard to undo, or too poorly described for autonomous use.

The scanner helps with that first review without requiring a live agent, production credentials, customer data, or a running MCP server.

## Evidence Boundary

This is deterministic triage, not production enforcement.

The scanner does not prove that a tool call is safe or unsafe. It does not replace MCP authorization, OAuth, IAM, OPA, prompt-injection defenses, sandboxing, runtime monitoring, or human approval.

It is designed to help reviewers identify tools that need stronger metadata, scope limits, dry runs, rollback plans, approval checks, and Decision Lifecycle Ledger evidence before autonomous execution.

## Relationship To The MCP Governance Adapter

Use this sequence:

1. Scan tool definitions with `reference_engine.mcp_tool_risk_scanner`.
2. Add missing governance metadata and tool annotations.
3. Convert the scanner's request skeleton into a real `smerc.mcp-tool-governance.v1` tool-call request.
4. Evaluate live or replayed tool calls with `reference_engine.mcp_tool_governance`.
5. Run shadow/enforce proxy behavior with `reference_engine.mcp_proxy_runner` or `reference_engine.mcp_transport_proxy`.

The scanner is the catalog review lane. The MCP governance adapter is the pre-execution decision lane.

# Dynamic Schema Gate

## Purpose

The Dynamic Schema Gate is SMERC's lower-pain proof path for MCP, JSON-RPC, and agent tool-call payloads.

It answers a narrow question:

> Before a tool call touches an external network or side-effecting adapter, can SMERC locally determine whether the schema is known, valid, drifted, unsafe, or under-specified?

## Run

```bash
python -m reference_engine.dynamic_schema_gate examples/dynamic_schema_gate_examples.json --pretty
```

Generated outputs:

- `reports/Dynamic_Schema_Gate_Report.md`
- `reports/dynamic_schema_gate_report.json`

## What It Checks

- known tool and schema version
- pinned schema hash versus observed schema hash
- required argument presence
- unexpected fields when `additionalProperties` is false
- basic JSON type matches
- unsafe schema text
- unsafe argument text
- under-specified or draft schema status

## Work / Result / Impact

Work: evaluate dynamic tool-call schemas entirely inside the SMERC gateway before execution.

Result: known-good calls can continue, while unknown schemas, schema drift, structural mismatch, unsafe schema text, unsafe argument values, and under-specified schemas receive `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE` posture hints before touching an external tool.

Impact: this proves that dynamic schemas are a localized gateway control problem by comparison with AWS audit-delay risk. The gateway can decide before network execution instead of waiting for delayed cloud logs or distributed enterprise state.

## Evidence Boundary

This is deterministic, local, and metadata-only. It is not a full JSON Schema implementation, live MCP proxy, external benchmark score, exploit detector, production certification, or replacement for MCP clients and servers.

## How It Fits

The gate should run before recoverability scoring:

1. Dynamic Schema Gate checks whether the tool-call contract is locally trustworthy.
2. Runtime Admission Gate applies hard identity, attestation, least-privilege, and object-shape facts.
3. SMERC recoverability scoring decides `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`.
4. SPARTa translates that posture into execution routing.

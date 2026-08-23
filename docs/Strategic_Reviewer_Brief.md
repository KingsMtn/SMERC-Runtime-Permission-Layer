# Strategic Reviewer Brief

## What SMERC Is

SMERC is recoverability-aware runtime permission infrastructure for AI agents, MCP tool calls, GitHub Actions, cloud automation, financial-action workflows, and other high-impact automated systems.

It sits after identity, policy, model output, and action proposal, but before execution.

SMERC returns a replayable posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

## Why It Exists

Most access and policy systems answer:

> Is this actor allowed to access this tool?

SMERC asks a different execution-time question:

> Given the evidence, recoverability, consequence horizon, authority, intent, and current autonomy state, should this action continue right now?

## What Is Real Now

The public repository contains:

- recoverability-aware runtime scoring
- Runtime Evidence Trust Gate
- SPARTa execution routing
- Decision Lifecycle Ledger
- autonomy health, autonomy budgeting, earned autonomy, and right-to-continue logic
- GitHub Actions pilot path
- MCP tool-call governance path
- SMERC-F financial-action review profile
- REST API, OpenAPI contract, SDKs, Docker support, examples, reports, and tests

## What Is Not Proven

SMERC is not production-certified, compliance-attested, independently security-audited, or proven to reduce incidents in live customer environments.

The next proof is external:

- one real or realistic workflow
- shadow-mode scoring
- reviewer agreement
- false release / false constraint analysis
- latency and workflow-burden measurement
- go/no-go decision from an accountable reviewer

## Why A Platform Company Might Care

AI agents and automation are becoming action-taking systems. They can edit code, deploy software, change infrastructure, call tools, move data, trigger workflows, and initiate financial operations.

SMERC may be valuable if the platform needs a reusable checkpoint between access policy and side-effecting execution.

## Fast Review Path

1. Read `docs/Strategic_Acquisition_Positioning.md`.
2. Read `docs/Technical_Diligence_Index.md`.
3. Run:

```bash
python -m reference_engine.strategic_reviewer_packet --pretty
```

4. Open:

```text
reports/strategic_reviewer_packet/Strategic_Reviewer_Evidence_Packet.md
```

5. Decide whether one shadow-mode workflow review is justified.

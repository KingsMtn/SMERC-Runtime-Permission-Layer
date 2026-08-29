# SMERC Pilot-In-A-Box

The pilot-in-a-box runner is the fastest way for a company reviewer to see SMERC operate across multiple workflow families without connecting production systems.

Run:

```bash
python -m reference_engine.pilot_in_a_box --pretty
```

The command writes a review package under `reports/pilot_in_a_box/`:

- `Pilot_In_A_Box_Report.md`
- `pilot_in_a_box_manifest.json`
- per-pack customer evaluation reports
- one single-action proof-loop report

## What It Runs

The default package evaluates:

- general AI-agent and automation actions
- cloud administration actions
- financial runtime actions
- one end-to-end customer proof-loop action

Each evaluation runs through existing SMERC reference components:

- hard evidence and Ref-gate checks
- agent identity gate when agent metadata is provided
- recoverability scoring
- SPARTa route generation
- Decision Lifecycle Ledger evidence
- autonomy-budget impact where applicable
- pilot-fit recommendation

## What It Proves

Work: SMERC can process structured action metadata and produce repeatable reviewer artifacts across multiple workflow families.

Result: reviewers get posture counts, route states, high-exposure action lists, DLL validity, and pilot-fit signals.

Impact: a company can decide whether to replace the example packs with 5 to 25 metadata-only actions from one real workflow before committing time to a shadow-mode pilot.

## Boundary

This is a metadata-only pilot preview. It does not execute customer workflows, inspect production logs, handle secrets, prove compliance, reduce incidents, or certify enforce-mode readiness.

The next step after a useful pilot-in-a-box review is a bounded observe-mode pilot using one owned workflow, usually GitHub Actions, MCP tool calls, cloud-admin automation, or financial-runtime workflow metadata.

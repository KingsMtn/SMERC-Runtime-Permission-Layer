# SPARK Signal Intake And Timing Evidence

## Purpose

SPARK is the proposed signal intake layer for SMERC.

Its job is not to decide. Its job is to collect, normalize, and label the evidence SMERC needs before scoring a proposed action.

Timing Evidence is the proposed coordination layer around execution and recovery. Its job is to measure whether governance adds unacceptable friction and whether rollback, cancellation, and recovery actually work.

Together:

```text
SPARK senses -> SMERC decides -> SPARTa routes -> adapters execute or pause -> DLL records -> Timing Evidence measures recovery
```

## Why This Matters

SMERC decisions are only as good as the evidence supplied to them.

If an integration sends incomplete, stale, or misleading action metadata, SMERC can still produce a posture, but the posture is less defensible. SPARK makes that evidence problem explicit.

Timing Evidence matters because enterprise reviewers will ask:

- How much latency does SMERC add?
- Can the action be cancelled after it starts?
- How long does rollback actually take?
- Did the required controls slow the workflow beyond an acceptable threshold?
- Did constrained execution reduce blast radius?

## SPARK Inputs

SPARK should normalize metadata from:

| Source | Example Signals |
| --- | --- |
| Agent request | actor, tool, proposed operation, declared intent |
| Identity system | principal, role, workload identity, token scope |
| Policy engine | allowed capability, denied capability, approval requirement |
| CI/CD workflow | repository, branch, environment, deployment target, rollback plan |
| Cloud platform | resource scope, region, production flag, permission breadth |
| Security tooling | anomaly pressure, incident state, suspicious sequence |
| Data system | sensitive data flag, record volume, export destination |
| Human review | approver, override reason, review status |

SPARK should not require raw secrets, full proprietary source code, private prompts, regulated payloads, or customer records for the first pilot.

## SPARK Output Contract

SPARK should hand SMERC a strict action evidence envelope:

```json
{
  "version": "smerc.spark-evidence.v1",
  "evidence_id": "spark-evt-001",
  "collected_at": "2026-08-15T00:00:00Z",
  "source_systems": ["github_actions", "policy", "identity"],
  "action_metadata": {
    "actor": "deployment_agent",
    "tool": "github_actions",
    "operation": "deploy_to_production",
    "environment": "production"
  },
  "recoverability_signals": {
    "reversibility": 0.62,
    "containment_strength": 0.71,
    "rollback_latency": 0.34,
    "evidence_validity": 0.82,
    "anomaly_pressure": 0.18,
    "impact_scope": 0.46,
    "cancel_reliability": 0.68
  },
  "evidence_gaps": [],
  "non_secret_boundary": true
}
```

This contract is proposed. It should not be treated as a production schema until implemented and tested.

## Timing Evidence Outputs

Timing Evidence should record:

| Metric | Meaning |
| --- | --- |
| decision_latency_ms | Time to score the action. |
| route_latency_ms | Time to generate SPARTa route and controls. |
| workflow_overhead_ms | Added workflow time from SMERC evaluation and artifacts. |
| cancellation_window_ms | Time available to cancel after initiation. |
| cancel_success | Whether cancellation succeeded when attempted. |
| rollback_latency_observed_ms | Actual rollback time when rollback happened. |
| rollback_success | Whether rollback restored acceptable state. |
| review_latency_ms | Time added by human review or escalation. |
| unavailable_evaluation | Whether SMERC could not evaluate and had to fail according to policy. |

## Pilot Interpretation

Timing Evidence should be interpreted conservatively:

- Low latency does not prove safety.
- High latency does not prove failure if the action is high impact.
- Rollback success in a synthetic test does not prove rollback success in production.
- Cancellation success depends on downstream systems, not only SMERC.

## Best First Implementation

The first practical build should stay narrow:

1. Add SPARK evidence fields to GitHub Actions metadata examples.
2. Record local decision latency and report-generation latency.
3. Add optional workflow overhead fields to pilot summaries.
4. Add rollback and cancellation fields to execution reports when adapters can supply them.
5. Keep all raw customer secrets and payloads out of SPARK evidence.

## Boundary

SPARK is a signal-intake concept and contract direction. Timing Evidence is a measurement direction.

They do not prove production safety, customer demand, incident reduction, or downstream system truthfulness. They make the evidence boundary clearer before SMERC decisions are trusted.

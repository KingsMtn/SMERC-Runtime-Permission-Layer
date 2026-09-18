# AWS Metadata Adapter Review SMERC Customer Evaluation Report

Version: `smerc.customer-evaluation.v1`
Generated: `2026-09-18T01:22:16+00:00`
Contact role: `aws_platform_security_reviewer`

## Evidence Boundary

This is a metadata-only customer evaluation. It proves local runtime coherence on supplied action metadata; it does not prove production safety, compliance, incident reduction, customer demand, or readiness to enforce in a live environment.

## Workflow Context

Non-executing AWS-style metadata adapter normalizing safe summaries into SMERC customer-evaluation actions for shadow-mode review.

## Summary

- Actions evaluated: `4`
- Ref-gate counts: `{'pass': 4}`
- Agent identity-gate counts: `{'WATCH': 4}`
- Posture counts: `{'FREEZE': 2, 'THROTTLE': 2}`
- Route state counts: `{'PAUSE': 2, 'REVIEW_REQUIRED': 2}`
- Non-executable routes: `4`
- Valid DLL ledgers: `4`
- Autonomy state: `SUSPEND_AUTONOMY`
- Pilot fit: `moderate`
- Fit reason: The evaluation shows at least one meaningful action where SMERC changes execution posture.

## Highest Exposure Actions

| Action | Posture | Route | Exposure |
| --- | --- | --- | ---: |
| `AWS_ADAPTER_002_create_a_billable_agentcore_runtime` | `FREEZE` | `PAUSE` | 0.487 |
| `AWS_ADAPTER_001_create_a_billable_agentcore_runtime` | `THROTTLE` | `REVIEW_REQUIRED` | 0.459 |
| `AWS_ADAPTER_004_invoke_a_bedrock_model_with_bounded_input` | `FREEZE` | `PAUSE` | 0.428 |
| `AWS_ADAPTER_003_invoke_a_bedrock_model_with_bounded_input` | `THROTTLE` | `REVIEW_REQUIRED` | 0.401 |

## Decision Path

| # | Action | Ref Gate | Scoring | Posture | SPARTa Route | Executable | DLL Valid |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | `AWS_ADAPTER_001_create_a_billable_agentcore_runtime` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `REVIEW_REQUIRED` | `False` | `True` |
| 2 | `AWS_ADAPTER_002_create_a_billable_agentcore_runtime` | `pass` | `admitted_with_agent_identity_watch` | `FREEZE` | `PAUSE` | `False` | `True` |
| 3 | `AWS_ADAPTER_003_invoke_a_bedrock_model_with_bounded_input` | `pass` | `admitted_with_agent_identity_watch` | `THROTTLE` | `REVIEW_REQUIRED` | `False` | `True` |
| 4 | `AWS_ADAPTER_004_invoke_a_bedrock_model_with_bounded_input` | `pass` | `admitted_with_agent_identity_watch` | `FREEZE` | `PAUSE` | `False` | `True` |

## Action Details

### AWS_ADAPTER_001_create_a_billable_agentcore_runtime

- Description: Non-executing AWS metadata adapter summary for agentcore_runtime_invocation_summary: create a billable AgentCore runtime in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.459, 'reversible_capacity_score': 0.654, 'confidence_score': 0.714, 'operational_stress_score': 0.427, 'risk_adjusted_authorization_score': 0.643, 'cancel_reliability_score': 0.7}`
- Reason codes: `['EXTERNAL_SIDE_EFFECT']`
- SPARTa route: `REVIEW_REQUIRED`
- Executable: `False`
- Applied controls: `['record_execution_report', 'preserve_replay']`
- DLL valid: `True`

### AWS_ADAPTER_002_create_a_billable_agentcore_runtime

- Description: Non-executing AWS metadata adapter summary for agentcore_runtime_invocation_summary: create a billable AgentCore runtime in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `FREEZE`
- Scores: `{'irreversible_exposure_score': 0.487, 'reversible_capacity_score': 0.654, 'confidence_score': 0.714, 'operational_stress_score': 0.456, 'risk_adjusted_authorization_score': 0.637, 'cancel_reliability_score': 0.7}`
- Reason codes: `['IRREVERSIBLE_EXPOSURE_ELEVATED', 'EXTERNAL_SIDE_EFFECT', 'HOST_ISOLATION_WEAK', 'PRODUCTION_NETWORK_REACHABLE', 'TOOLING_AUTHORITY_BROAD', 'SANDBOX_ESCAPE_OR_CREDENTIAL_SURFACE']`
- SPARTa route: `PAUSE`
- Executable: `False`
- Applied controls: `['pause_execution', 'preserve_replay', 'snapshot_current_state', 'checkpoint_before_execution']`
- DLL valid: `True`

### AWS_ADAPTER_003_invoke_a_bedrock_model_with_bounded_input

- Description: Non-executing AWS metadata adapter summary for agentcore_gateway_tool_call_summary: invoke a Bedrock model with bounded input in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `THROTTLE`
- Scores: `{'irreversible_exposure_score': 0.401, 'reversible_capacity_score': 0.684, 'confidence_score': 0.819, 'operational_stress_score': 0.274, 'risk_adjusted_authorization_score': 0.703, 'cancel_reliability_score': 0.78}`
- Reason codes: `['EXTERNAL_SIDE_EFFECT']`
- SPARTa route: `REVIEW_REQUIRED`
- Executable: `False`
- Applied controls: `['record_execution_report', 'preserve_replay']`
- DLL valid: `True`

### AWS_ADAPTER_004_invoke_a_bedrock_model_with_bounded_input

- Description: Non-executing AWS metadata adapter summary for agentcore_gateway_tool_call_summary: invoke a Bedrock model with bounded input in production.
- Ref gate: `pass`
- Ref failures: `[]`
- Agent identity gate: `WATCH`
- Agent identity reasons: `['AGENT_IDENTITY_MISSING']`
- Scoring admission: `admitted_with_agent_identity_watch`
- SMERC posture: `FREEZE`
- Scores: `{'irreversible_exposure_score': 0.428, 'reversible_capacity_score': 0.684, 'confidence_score': 0.819, 'operational_stress_score': 0.304, 'risk_adjusted_authorization_score': 0.696, 'cancel_reliability_score': 0.78}`
- Reason codes: `['EXTERNAL_SIDE_EFFECT', 'HOST_ISOLATION_WEAK', 'PRODUCTION_NETWORK_REACHABLE', 'TOOLING_AUTHORITY_BROAD', 'SANDBOX_ESCAPE_OR_CREDENTIAL_SURFACE']`
- SPARTa route: `PAUSE`
- Executable: `False`
- Applied controls: `['pause_execution', 'preserve_replay', 'snapshot_current_state', 'checkpoint_before_execution']`
- DLL valid: `True`

## Autonomy Budget

- State: `SUSPEND_AUTONOMY`
- Spent: `{'actions': 4, 'scope_units': 12.0, 'risk_spend': 1.055, 'ref_gate_failures': 0, 'blocked_or_held_attempts': 2}`
- Review triggers: `['repeated_blocked_or_held_attempts', 'autonomy_removed_until_review']`

## Recommended Next Action

Ask for more side-effecting actions from one workflow before proposing a pilot.

# SMERC Deployment Model

## Deployment Goal

Deploy SMERC where an AI agent, automation, or workflow is about to create a side effect.

The first practical deployment target is GitHub Actions because AI-assisted code and infrastructure changes are easy to observe, replay, and compare against existing approval flows.

## Deployment Patterns

### 1. Local Reference Engine

Use for development, demos, and internal review.

```bash
python -m reference_engine.agent_permission_layer examples/agent_permission_actions.json --pretty
```

### 2. GitHub Actions Shadow Mode

Use for first CISO/platform-team pilots.

```text
Pull request or workflow event
        |
        v
Build action metadata JSON
        |
        v
SMERC GitHub Action evaluates posture
        |
        v
Decision report uploaded as artifact
        |
        v
Existing workflow continues unchanged
```

### 3. GitHub Actions Recommend Mode

Use after shadow-mode calibration.

```text
SMERC decision appears in step summary
Reviewers compare posture against existing approval path
High-risk actions receive constraints or escalation guidance
```

### 4. GitHub Actions Enforce Mode

Use only after calibration and accountable approval.

```text
ALLOW / THROTTLE / ESCALATE -> workflow continues or routes to review
FREEZE / DENY -> workflow fails based on fail-on configuration
```

### 5. API Gateway / Tool Wrapper

Future production pattern:

```text
Agent plan
  -> tool-call wrapper
  -> SMERC API
  -> posture and constraints
  -> tool executes, delays, narrows scope, pauses, denies, or escalates
```

## Integration Inputs

Minimum action request:

```json
{
  "action_id": "AI_DEPLOY_PRODUCTION_CHANGE",
  "description": "AI coding agent proposes deploying a generated infrastructure change to production.",
  "tool": "github_actions.deploy",
  "actor": "coding_agent",
  "confidence": 0.64,
  "harm": 0.72,
  "consent": 0.58,
  "reversibility": 0.34,
  "external_effect": true,
  "sensitive_data": false
}
```

## Integration Outputs

SMERC returns:

- posture
- risk score
- confidence score
- reason codes
- constraints
- replay ID
- replay record

## First Pilot Recommendation

Start with `observe` mode for two to four weeks. Compare SMERC output against:

- existing code-review outcomes
- deployment approval outcomes
- security reviewer judgment
- rollback difficulty
- incident or near-miss signals

Only consider enforcement after reviewer agreement and false-positive/false-negative analysis.


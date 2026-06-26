# SMERC GitHub Actions Integration

This integration runs SMERC as a runtime permission gate in GitHub Actions.

It evaluates a proposed AI-agent or automation action and returns:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

The first deployment mode is intentionally narrow: AI-assisted code, deployment, and infrastructure workflows where a security or platform team wants a replayable decision before high-impact automation proceeds.

## Modes

| Mode | Behavior |
| --- | --- |
| `observe` | Score the action, write a report, never fail the workflow. |
| `recommend` | Score the action and surface constraints for reviewer use. |
| `enforce` | Fail the workflow when the posture matches `fail-on`. |

## Example

```yaml
- name: Evaluate proposed agent action
  id: smerc
  uses: ./integrations/github_actions
  with:
    action-file: integrations/github_actions/sample_action_request.json
    mode: observe
    output-file: smerc-decision.json
    fail-on: DENY,FREEZE
```

## Input Action Shape

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

## Output

The action writes:

- step outputs: `posture`, `risk-score`, `replay-id`
- JSON report at `output-file`
- GitHub step summary with posture, reasons, constraints, and replay ID

## Local Smoke Test

```bash
python integrations/github_actions/run_smerc_gate.py \
  --action-file integrations/github_actions/sample_action_request.json \
  --mode observe \
  --output-file smerc-decision.json
```

Expected behavior:

- exits successfully in `observe` mode
- writes `smerc-decision.json`
- prints the posture and replay ID

Use `denied_action_request.json` to test enforcement behavior:

```bash
python integrations/github_actions/run_smerc_gate.py \
  --action-file integrations/github_actions/denied_action_request.json \
  --mode enforce \
  --fail-on DENY,FREEZE \
  --output-file smerc-decision.json
```

## Shadow-Mode Pilot Report

The repository includes 10 realistic GitHub Actions scenarios for product review:

```bash
python -m reference_engine.pilot_report \
  examples/github_actions_shadow_mode_scenarios.json \
  --json-output reports/github_actions_shadow_mode_results.json \
  --markdown-output reports/GitHub_Actions_Shadow_Mode_Pilot_Report.md
```

The generated report shows posture distribution, risk/confidence averages, scenario-level reason codes, and the limits of synthetic evidence. It is intended to preview what a design partner would receive after scoring real workflows in shadow mode.

## CISO Review Notes

This is an MVP/reference integration. It is designed for shadow-mode review first. It is not a production-certified security control, does not replace branch protection, does not replace code review, and does not replace existing IAM or policy engines.

Use `observe` mode first to compare SMERC postures against existing approvals before any enforcement.

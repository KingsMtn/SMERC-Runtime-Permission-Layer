# SMERC Control Mapping Library

The SMERC Control Mapping Library turns abstract governance controls into declared native mechanisms for a specific tool path.

It answers a practical integration question:

> If SMERC returns `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`, what control must the execution system actually apply?

This is not a certification system. It is a pilot-grade control dictionary and report generator for technical review, adapter development, and shadow-mode evidence.

## Why It Exists

SMERC and SPARTa can produce controls such as:

- `limit_scope`
- `preview_before_execution`
- `require_rollback_plan`
- `pause_execution`
- `block_execution`
- `route_to_accountable_reviewer`
- `record_execution_report`

Those names are not enough for a CISO or platform engineer. A reviewer needs to know whether the target system has a native mechanism for each control, what evidence proves it was applied, and what should happen if the control is missing.

The control mapping library makes that explicit.

## Control Record

Each control declares:

- `control_id`
- description
- required SMERC postures
- supported tools
- native mechanism by tool
- evidence required
- failure behavior

Supported failure behaviors:

- `fail_closed`
- `route_to_review`
- `block_execution`
- `record_only`

## Example

```bash
python -m reference_engine.control_mapping examples/control_mapping/github_actions_controls.json --posture THROTTLE --tool github_actions --capability deploy_production --controls limit_scope preview_before_execution require_rollback_plan preserve_replay --pretty --json-output reports/control_mapping_example.json --markdown-output reports/Control_Mapping_Library_Example.md
```

Expected result:

- `executable: true` only when every required requested control maps to a native mechanism for the selected tool.
- `executable: false` when a required control is undeclared or unsupported by the selected tool.

## Relationship To SPARTa

SPARTa routes a SMERC posture into an execution route.

The control mapping library explains whether the route's controls can be enforced by a declared tool path.

In pilot terms:

1. SMERC decides posture.
2. SPARTa creates an execution route.
3. The control mapping library maps route controls to native mechanisms.
4. The execution adapter records control evidence.
5. The Decision Lifecycle Ledger preserves the decision history.

## Limits

This module does not prove that a production environment continuously enforces controls. It provides a strict, reviewable mapping contract and evidence requirements. Real deployment still requires adapter testing, identity scoping, secret handling review, production monitoring, and legal or compliance review where applicable.

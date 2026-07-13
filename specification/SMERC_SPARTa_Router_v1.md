# SMERC SPARTa Router v1

## Purpose

`smerc.sparta-route.v1` is the first SPARTa contract: Safe Posture-Aware Routing and Tooling Architecture.

SPARTa does not decide whether an action is acceptable. SMERC already makes that decision. SPARTa takes a SMERC posture and a declared tool plan, then determines the safest executable route:

- `EXECUTE`
- `CONSTRAINED_EXECUTE`
- `PAUSE`
- `BLOCK`
- `REVIEW_REQUIRED`
- `BLOCKED_ESCALATION_UNAVAILABLE`

This separates authorization from execution routing. A posture is not useful unless the next system knows what to do with it.

## Input: Tool Plan

A `smerc.sparta-plan.v1` plan declares what a tool can actually enforce.

Required fields:

| Field | Meaning |
|---|---|
| `version` | Fixed value `smerc.sparta-plan.v1`. |
| `plan_id` | Bounded identifier for the declared route candidate. |
| `tool` | Tool or execution surface, such as `github_actions`. |
| `action` | Tool action, such as `deploy_canary`. |
| `requested_capability` | Capability requested from the tool. |
| `supports_dry_run` | Whether the tool can preview before execution. |
| `supports_scope_limit` | Whether the tool can reduce blast radius natively. |
| `supports_checkpoint` | Whether the tool can checkpoint state before execution. |
| `supports_rollback` | Whether the tool can run a rollback plan. |
| `supports_human_approval` | Whether the tool can route to accountable review. |
| `max_scope_units` | Upper bound for the plan scope. |
| `requested_scope_units` | Scope requested for this execution. |
| `side_effect_level` | One of `none`, `internal`, `external`, `financial`, or `destructive`. |
| `metadata` | Bounded contextual object for audit and review. |

Unknown fields are rejected. `requested_scope_units` cannot exceed `max_scope_units`.

## Input: Adapter Registry

`smerc.sparta-adapter-registry.v1` lets the API derive a tool plan from a configured adapter instead of trusting each caller to send the whole plan.

An adapter declares:

- `adapter_id`
- `tool`
- `supported_actions`
- `supported_capabilities`
- native control support
- `max_scope_units`
- `allowed_side_effect_levels`
- bounded metadata

The API request supplies:

- `adapter_id`
- `action`
- `requested_capability`
- `requested_scope_units`
- `side_effect_level`
- optional metadata

The registry rejects unsupported actions, unsupported capabilities, side-effect levels outside the adapter boundary, and scope requests above the adapter maximum.

## Input: SMERC Decision

The router requires:

- `posture`
- `replay_id`

It also consumes:

- `controls`
- `reason_codes`
- `policy`

The router stores a SHA-256 digest over the decision fields it relies on. This binds the route report to the posture, replay, controls, reasons, and policy metadata without copying the entire decision into every route report.

## Routing Rules

### ALLOW

`ALLOW` routes to `EXECUTE`.

SPARTa still records an execution report requirement. For external, financial, or destructive side effects, a checkpoint is added when the tool supports one.

### THROTTLE

`THROTTLE` routes to `CONSTRAINED_EXECUTE` only when the tool can apply the required native controls.

Examples:

- `limit_scope` requires native scope limiting.
- `preview_before_execution` requires dry-run support.
- `require_rollback_plan` or `checkpoint_before_execution` requires checkpoint or rollback support.

If required features are missing, SPARTa routes to `REVIEW_REQUIRED` and marks the plan non-executable.

### FREEZE

`FREEZE` routes to `PAUSE`.

Automation does not execute. SPARTa preserves the replay, requests state snapshotting, and adds checkpointing if available.

### DENY

`DENY` routes to `BLOCK`.

Automation does not execute. The route report records denial explanation and replay preservation.

### ESCALATE

`ESCALATE` routes to `REVIEW_REQUIRED` only when a human approval route exists.

If no review route exists, SPARTa routes to `BLOCKED_ESCALATION_UNAVAILABLE`.

## Output: Route Report

The route report includes:

- route version and route ID
- route timestamp
- plan ID
- decision replay ID
- decision digest
- source posture
- route state
- executable boolean
- effective scope units
- applied controls
- blocked controls
- reason codes
- plain-English summary
- recommended next action
- sanitized tool plan
- optional signature object

When produced by the API, the route report also includes:

- `tenant_id`
- authenticated principal identity

## Optional Signature

When signed, the route report includes a `signature` object:

```json
{
  "version": "smerc.sparta-route-signature.v1",
  "algorithm": "HMAC-SHA256",
  "key_id": "development-sparta-key",
  "route_report_digest": "64 lowercase hex characters",
  "signature": "64 lowercase hex characters"
}
```

The `route_report_digest` is computed over canonical JSON for the route report excluding the `signature` field. The HMAC signature is computed over that digest. Verification fails if signed route content changes after signature generation.

## Security Boundaries

SPARTa v1 is a router, not a sandbox or executor.

It does not:

- run commands
- verify cloud IAM permissions
- prove a rollback succeeded
- replace signed permits
- replace control-evidence receipts
- replace the GitHub deployment adapter
- provide managed key custody or non-repudiation by itself

Its job is to fail closed when a tool plan cannot apply the constraints implied by the SMERC posture.

## Demonstration Command

```bash
python -m reference_engine.sparta_router \
  --decision examples/sparta/throttle_decision.json \
  --plan examples/sparta/github_actions_deploy_plan.json \
  --signing-key development-sparta-route-signing-key-rotate \
  --key-id development-sparta-key \
  --verify \
  --pretty
```

Expected result: `THROTTLE` becomes `CONSTRAINED_EXECUTE` with reduced effective scope and native controls.

## API Endpoint

`POST /v1/sparta/route` routes one stored tenant decision.

Required scope: `routes.write`.

Direct plan request:

```json
{
  "replay_id": "replay_example_throttle_001",
  "plan": {
    "version": "smerc.sparta-plan.v1",
    "plan_id": "github-prod-canary-deploy",
    "tool": "github_actions",
    "action": "deploy_canary",
    "requested_capability": "deployment",
    "supports_dry_run": true,
    "supports_scope_limit": true,
    "supports_checkpoint": true,
    "supports_rollback": true,
    "supports_human_approval": true,
    "max_scope_units": 100,
    "requested_scope_units": 80,
    "side_effect_level": "external",
    "metadata": {}
  }
}
```

Registry-backed request:

```json
{
  "replay_id": "replay_example_throttle_001",
  "adapter_id": "github-actions-deployer",
  "action": "deploy_canary",
  "requested_capability": "deployment",
  "requested_scope_units": 80,
  "side_effect_level": "external",
  "metadata": {
    "workflow_run": "1001"
  }
}
```

The API reads the stored decision by `replay_id`; callers cannot invent a posture inside the route request.

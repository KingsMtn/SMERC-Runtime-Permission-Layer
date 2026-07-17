# SPARTa Router Operations

## What This Adds

SPARTa, short for **Stateful Posture-Aware Routing and Tooling Adapter**, turns a SMERC decision into a practical execution route.

Before this layer, SMERC could say `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`. SPARTa answers the next operational question:

> Given that posture, what should the execution system do with this specific tool plan?

That matters for CISOs and platform teams because many tools can execute an action, but not every tool can safely constrain, pause, rollback, or escalate the action.

## First Pilot Use

The first intended use is GitHub Actions and deployment workflow review.

Example:

1. An AI-assisted workflow proposes a production deployment.
2. SMERC evaluates recoverability and returns `THROTTLE`.
3. SPARTa checks whether the execution plan or configured adapter supports dry run, scope limiting, checkpoint, rollback, and human approval.
4. If the plan supports the required controls, SPARTa returns `CONSTRAINED_EXECUTE`.
5. If the plan cannot enforce the constraints, SPARTa returns `REVIEW_REQUIRED`.

This makes the difference between a policy opinion and an executable governance route.

## Local Run

```bash
python -m reference_engine.sparta_router \
  --decision examples/sparta/throttle_decision.json \
  --plan examples/sparta/github_actions_deploy_plan.json \
  --pretty
```

Generate and verify a signed route report:

```bash
python -m reference_engine.sparta_router \
  --decision examples/sparta/throttle_decision.json \
  --plan examples/sparta/github_actions_deploy_plan.json \
  --signing-key development-sparta-route-signing-key-rotate \
  --key-id development-sparta-key \
  --verify \
  --pretty
```

Example output is stored in `reports/signed_sparta_route_example.json`.

Try the freeze path:

```bash
python -m reference_engine.sparta_router \
  --decision examples/sparta/freeze_decision.json \
  --plan examples/sparta/destructive_tool_plan.json \
  --pretty
```

## API Route Endpoint

Start the API with the example adapter registry:

```bash
python api_server.py \
  --host 127.0.0.1 \
  --port 8788 \
  --audit-db :memory: \
  --allow-unauthenticated \
  --sparta-adapter-registry examples/sparta/adapter_registry.json
```

Evaluate an action first, then route the returned `replay_id`:

```bash
curl -X POST http://127.0.0.1:8788/v1/sparta/route \
  -H "Content-Type: application/json" \
  --data '{"replay_id":"replay_...","adapter_id":"github-actions-deployer","action":"deploy_canary","requested_capability":"deployment","requested_scope_units":80,"side_effect_level":"external","metadata":{"workflow_run":"1001"}}'
```

Authenticated deployments require `routes.write`. The API records a `sparta.route.created` security event with the route state, replay ID, and plan ID.

## How To Read A Route Report

Important fields:

- `source_posture`: the original SMERC posture.
- `route_state`: the execution route SPARTa selected.
- `executable`: whether automation can proceed.
- `effective_scope_units`: the allowed scope after routing.
- `applied_controls`: controls the route expects the adapter to apply.
- `blocked_controls`: controls or routes that are unavailable.
- `decision_digest`: digest binding the route to the relevant SMERC decision fields.
- `signature`: optional HMAC signature over the canonical route report digest.

## Signed Route Reports

`smerc.sparta-route-signature.v1` signs the route report digest using HMAC-SHA256 when a signing key is supplied. The signature covers the route report except the `signature` field itself. Verification fails if the route state, source posture, applied controls, blocked controls, effective scope, decision digest, tool plan, or other signed route content changes after signing.

The signature fields are:

- `version`
- `algorithm`
- `key_id`
- `route_report_digest`
- `signature`

This is pilot-grade integrity evidence. It does not provide managed key custody, non-repudiation, hardware-backed signing, cross-service trust, revocation, rotation, or proof that the downstream adapter actually enforced the route. Production deployment would require managed KMS or HSM-backed signing, key rotation, tenant-specific key policy, durable storage, and independent security review.

## Commercial Meaning

SPARTa makes SMERC easier to understand as runtime permission infrastructure:

- SMERC scores whether the action is defensible.
- Permits authorize narrow eligible execution.
- Control evidence records what enforcement actually happened.
- SPARTa routes posture into the right tool behavior.

The product claim should stay modest: SPARTa v1 is not a full workflow engine. It is a conservative posture-aware router that helps integrations fail closed when they cannot enforce the controls SMERC requires.

## Current Limits

- Adapter registry exists, but adapters are static configuration loaded at process start.
- No dynamic adapter registration endpoint yet.
- No live third-party adapter marketplace or certification path yet.
- Signed route reports provide pilot-grade tamper detection only. They are not a production trust root.
- No formal policy language binding yet.
- No live evidence that SPARTa routes reduce real-world incidents.

Those are the next build steps after v1 is reviewed.

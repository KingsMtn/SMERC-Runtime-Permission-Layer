# SMERC Developer Quickstart

## Goal

This quickstart lets a technical reviewer run SMERC locally, evaluate one action, inspect the replayable decision, and understand the first pilot path without reading the whole repository.

SMERC is a pilot-grade runtime permission layer. The purpose of this quickstart is to prove mechanics, not production certification.

## 1. Run The Local Engine

Requires Python 3.10 or later. The reference path uses only the Python standard library.

```bash
python -m reference_engine.action_language examples/action_language/production_database_change.json
```

Expected result:

- a structured `smerc.decision.v1` response
- posture, scores, reason codes, controls, and replay metadata
- no external service dependency

## 2. Run The Recoverability Engine

```bash
python -m reference_engine.recoverability_engine examples/recoverability_single_action.json --pretty
```

This demonstrates the core recoverability signal:

```text
proposed action -> reversibility/containment/evidence/anomaly/scope -> posture
```

Run the same action with an explicit domain profile and inspect the decision trace:

```bash
python -m reference_engine.recoverability_engine \
  examples/recoverability_single_action.json \
  --domain-profile github_actions \
  --pretty
```

Read `docs/Engine_Profile_And_Trace.md` for available profiles, score contributions, threshold trace, and transition guidance.

Load a strict custom profile without changing engine code:

```bash
python -m reference_engine.recoverability_engine \
  examples/recoverability_single_action.json \
  --domain-profile-file examples/domain_profiles/github_actions_strict.json \
  --domain-profile github_actions_strict \
  --pretty
```

## 3. Run The Pilot API Locally

Start the API in explicit unauthenticated development mode:

```bash
python api_server.py --host 127.0.0.1 --port 8788 --audit-db :memory: --allow-unauthenticated
```

To test custom profile loading in the API, add `--domain-profile-dir examples/domain_profiles`.

Then evaluate one action:

```bash
curl -X POST http://127.0.0.1:8788/v1/evaluate \
  -H "Content-Type: application/json" \
  --data @examples/recoverability_single_action.json
```

For any shared, remote, or pilot deployment, use scoped authenticated principals instead. See `docs/API_Deployment_Guide.md`.

## 4. Compile A Starter SPL Policy

Compile the pilot-friendly SMERC Policy Language profile into the strict runtime policy contract:

```bash
python -m reference_engine.spl examples/policies/github_actions_shadow_spl.json --pretty
python -m reference_engine.spl examples/policies/github_actions_shadow_spl.json --hash
```

Read `specification/SMERC_SPL_v0.md` for the policy surface and its current limits.

## 5. Route A Posture Through SPARTa

Route a throttled SMERC decision into a concrete execution path for a declared GitHub Actions plan:

```bash
python -m reference_engine.sparta_router \
  --decision examples/sparta/throttle_decision.json \
  --plan examples/sparta/github_actions_deploy_plan.json \
  --pretty
```

Expected result:

- `source_posture` is `THROTTLE`
- `route_state` is `CONSTRAINED_EXECUTE`
- `effective_scope_units` is reduced
- native controls are listed for the adapter to enforce

Read `docs/SPARTa_Router_Operations.md` and `specification/SMERC_SPARTa_Router_v1.md`.

The API can route stored decisions when started with an adapter registry:

```bash
python api_server.py \
  --host 127.0.0.1 \
  --port 8788 \
  --audit-db :memory: \
  --allow-unauthenticated \
  --sparta-adapter-registry examples/sparta/adapter_registry.json
```

After evaluating an action, call `POST /v1/sparta/route` with the returned `replay_id`.

## 6. Validate A Deployment Plan

This validates the GitHub deployment adapter without issuing permission or running a deployment command:

```bash
python integrations/github_deployment/deployment_adapter.py \
  --action-file examples/action_language/production_canary_release.json \
  --plan-file examples/github_deployment/execution_plan.json \
  --mode validate
```

Expected result:

- strict execution-plan validation
- no permit consumption
- no native command execution

## 7. Understand The Enforce Path

The enforce path is intentionally stricter than the demo path:

```text
action proposal
  -> SMERC decision
  -> SPARTa route
  -> action-bound permit issuance
  -> permit preparation and reservation
  -> native controls
  -> signed control evidence
  -> single-use permit consumption
  -> bounded command execution
  -> execution report
```

Read:

- `docs/Action_Bound_Permit_Operations.md`
- `docs/Control_Evidence_Operations.md`
- `docs/GitHub_Deployment_Adapter_Operations.md`
- `specification/SMERC_Execution_Plan_v1.md`

## 8. Run Tests

```bash
python -m unittest discover -s tests -v
```

The GitHub CI suite also runs:

- Python unit tests on 3.10
- Python unit tests on 3.12
- console contract tests
- container smoke tests

## 9. Call The API From Python

Use the dependency-free SDK when a pilot needs a small service, notebook, or test harness to call SMERC without hand-written HTTP code.

```python
import json
from pathlib import Path

from smerc_sdk import SMERCClient

client = SMERCClient(
    "http://127.0.0.1:8788",
    token="development-console-secret-2026-rotate",
)
action = json.loads(Path("examples/recoverability_single_action.json").read_text())

decision = client.evaluate(action, idempotency_key="quickstart-1001")
replay = client.get_decision(decision["replay_id"])
metrics = client.pilot_metrics()
```

See `docs/Python_SDK_Quickstart.md` for review queue and Action Language examples.

## 10. Call The API From JavaScript

Use the dependency-free JavaScript SDK when a pilot needs a Node service, agent runner, GitHub tool, or browser-compatible utility to call SMERC.

```js
import { readFile } from 'node:fs/promises';
import { SMERCClient } from './smerc_js_sdk/index.mjs';

const client = new SMERCClient('http://127.0.0.1:8788', {
  token: 'development-console-secret-2026-rotate',
});
const action = JSON.parse(await readFile('examples/recoverability_single_action.json', 'utf8'));

const decision = await client.evaluate(action, { idempotencyKey: 'quickstart-1001' });
const replay = await client.getDecision(decision.replay_id);
const metrics = await client.pilotMetrics();
```

See `docs/JavaScript_SDK_Quickstart.md` for review queue and Action Language examples.

## 11. First Pilot Shape

The recommended first design-partner pilot is GitHub Actions shadow mode:

1. Choose several CI/CD, infrastructure, or AI-assisted workflow actions.
2. Generate or supply `smerc.action.v1` metadata for each proposed action.
3. Let SMERC score actions without blocking.
4. Have reviewers mark agreement, disagreement, override, false release, false constraint, and useful constraint.
5. Compare SMERC posture with existing approval behavior.
6. Decide whether any narrow non-production enforcement is justified.

Read:

- `docs/Pilot_Readiness.md`
- `docs/Pilot_Review_Metrics.md`
- `pilot_package/SMERC_Shadow_Mode_Pilot_One_Pager.md`
- `examples/pilot_evaluation_checklist.json`

## 12. Generate Proxy Evidence

Before a design partner supplies live workflow data, reviewers can inspect a proxy incident-replay benchmark:

```bash
python -m reference_engine.proxy_evidence_benchmark \
  examples/proxy_incident_replay_scenarios.json \
  --json-output reports/proxy_incident_replay_benchmark.json \
  --markdown-output reports/Proxy_Incident_Replay_Benchmark.md
```

Read `reports/Proxy_Incident_Replay_Benchmark.md`.

This is scenario-based proxy evidence, not production validation. It helps test whether recoverability scoring changes decisions in plausible incident patterns.

## 13. What To Inspect If You Have 30 Minutes

| Question | Inspect |
| --- | --- |
| What does SMERC decide? | `reference_engine/recoverability_engine.py` |
| What is the action contract? | `specification/SMERC_Action_Language_v1.md` |
| How are runtime thresholds configured? | `specification/SMERC_SPL_v0.md` |
| How do postures become tool routes? | `reference_engine/sparta_router.py` and `reference_engine/sparta_registry.py` |
| What proxy evidence exists? | `reports/Proxy_Incident_Replay_Benchmark.md` |
| How are decisions stored? | `reference_engine/audit_store.py` |
| How are permits bound to actions? | `reference_engine/authorization_permit.py` |
| How does GitHub identity enter? | `reference_engine/github_oidc.py` |
| How does deployment enforcement work? | `integrations/github_deployment/deployment_adapter.py` |
| What are the honest limits? | `SECURITY.md` |

## 14. What This Quickstart Does Not Prove

This quickstart does not prove:

- customer demand
- production-scale reliability
- production key management
- independent native-control attestation
- distributed replay prevention
- real-world reduction in incidents
- compliance certification

Those require design-partner pilots and production hardening.

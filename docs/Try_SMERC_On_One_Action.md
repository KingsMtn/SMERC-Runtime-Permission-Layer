# Try SMERC On One Action

## Purpose

This is the shortest path for a human reviewer, AI assistant, coding agent, or platform engineer to test SMERC without understanding the whole repository.

Use it when the question is:

> If this agent or automation action is already authorized, is it recoverable enough to execute right now?

## Run One Local Action

From the repository root:

```bash
python -m reference_engine.recoverability_engine examples/recoverability_single_action.json --pretty
```

The example action is:

- `examples/recoverability_single_action.json`

The result includes:

- posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- reason codes
- controls
- recoverability scores
- replay metadata
- transition guidance

## Change The Example

Copy `examples/recoverability_single_action.json` and change only safe metadata.

Useful fields to edit:

| Field | What It Means |
| --- | --- |
| `description` | Plain-English proposed action. |
| `actor` | Agent, workflow, bot, service, or human-delegated automation requesting the action. |
| `tool` | Tool family or integration the action would use. |
| `action_type` | General action category, such as deploy, delete, scale, rotate, refund, transfer, policy change, or data export. |
| `base_action_risk` | Baseline risk from `0.0` to `1.0`. |
| `reversibility` | How recoverable the action is if wrong. Higher means easier to recover. |
| `containment_strength` | How well the action is bounded. Higher means better containment. |
| `rollback_latency` | How slow rollback would be. Higher means slower or harder rollback. |
| `evidence_validity` | How trustworthy the supporting evidence is. |
| `anomaly_pressure` | How unusual or suspicious the action looks. |
| `impact_scope` | How wide the blast radius could be. |
| `cancel_reliability` | How reliably the action can be stopped. |
| `authorization_confidence` | How confident the system is that authority is valid. |
| `external_side_effect` | Whether the action creates side effects outside the runtime. |
| `sensitive_data` | Whether sensitive data, credentials, customer records, or regulated information may be touched. |

Do not include secrets, credentials, account IDs, ARNs, raw logs, packet payloads, customer records, private prompts, production commands, or live access.

## Call The Local API

Start the API:

```bash
python api_server.py --host 127.0.0.1 --port 8788 --audit-db :memory: --allow-unauthenticated
```

Evaluate the same action:

```bash
curl -X POST http://127.0.0.1:8788/v1/evaluate \
  -H "Content-Type: application/json" \
  --data @examples/recoverability_single_action.json
```

For shared, remote, or pilot use, do not use unauthenticated mode. Use scoped principals with `actions.evaluate` as described in `docs/API_Deployment_Guide.md`.

## Use The SDKs

Python:

```python
import json
from pathlib import Path

from smerc_sdk import SMERCClient

client = SMERCClient("http://127.0.0.1:8788")
action = json.loads(Path("examples/recoverability_single_action.json").read_text())
decision = client.evaluate(action, idempotency_key="one-action-test-001")
print(decision["posture"])
```

JavaScript:

```javascript
import fs from "node:fs";
import { SMERCClient } from "./sdk/js/smerc_client.mjs";

const client = new SMERCClient({ baseUrl: "http://127.0.0.1:8788" });
const action = JSON.parse(fs.readFileSync("examples/recoverability_single_action.json", "utf8"));
const decision = await client.evaluate(action, { idempotencyKey: "one-action-test-001" });
console.log(decision.posture);
```

## How To Interpret The Result

- `ALLOW`: the action appears recoverable enough to execute.
- `THROTTLE`: the action may proceed only with tighter speed, scope, or staged execution.
- `FREEZE`: pause until missing evidence, rollback, containment, or authority improves.
- `DENY`: do not execute this action in its current form.
- `ESCALATE`: send to accountable human or higher-authority review before execution.

Middle states matter. SMERC is not only an allow/block tool; it is designed to show when a technically authorized action should slow, pause, narrow scope, require evidence, or escalate.

## What This Proves

This proves the local mechanics of SMERC's recoverability decision path on one metadata-only action.

It does not prove production readiness, customer validation, incident reduction, compliance attestation, or that SMERC should replace IAM, policy engines, AI gateways, sandboxes, approval workflows, code review, SIEM, SOAR, or human accountability.

## Next Step

If one action is useful, move to `docs/Customer_Owned_Metadata_Request.md` and replace the examples with 5 to 25 safe metadata-only actions from one real workflow.

# Python SDK Quickstart

The `smerc_sdk` package is a dependency-free Python client for the SMERC Runtime Permission API. It is intended for pilots, tests, and lightweight service integration where teams want to call SMERC without hand-writing HTTP requests.

The SDK does not replace the policy engine. It wraps the authenticated API that persists replayable decisions, agent handshakes, reviews, pilot metrics, review queues, and security events.

## Start A Local API

```bash
python api_server.py --host 127.0.0.1 --port 8788 --audit-db :memory: --allow-unauthenticated
```

For authenticated pilot mode, start the API with scoped principals or legacy pilot keys as described in `docs/Developer_Quickstart.md`.

## Evaluate One Action

```python
import json
from pathlib import Path

from smerc_sdk import SMERCClient

client = SMERCClient("http://127.0.0.1:8788")
action = json.loads(Path("examples/recoverability_single_action.json").read_text())

decision = client.evaluate(action, idempotency_key="local-demo-1001")
print(decision["posture"])
print(decision["replay_id"])
```

## Authenticated Pilot Use

```python
from smerc_sdk import SMERCClient

client = SMERCClient(
    "http://127.0.0.1:8788",
    token="development-console-secret-2026-rotate",
)

decision = client.evaluate(action, idempotency_key="workflow-run-1001")
replay = client.get_decision(decision["replay_id"])
queue = client.review_queue(status="pending", limit=20)
metrics = client.pilot_metrics()
```

## Action Language Evaluation

```python
import json
from pathlib import Path

from smerc_sdk import SMERCClient

client = SMERCClient("http://127.0.0.1:8788", token="development-console-secret-2026-rotate")
payload = json.loads(Path("examples/action_language/production_database_change.json").read_text())

decision = client.evaluate_language_action(payload, idempotency_key="db-change-2041")
```

## Agent Handshake

Use this path when an agent or automation runner needs to discover SMERC, declare itself, propose a task and action, and receive a replayable posture before execution.

```python
import json
from pathlib import Path

from smerc_sdk import SMERCClient

client = SMERCClient("http://127.0.0.1:8788", token="development-console-secret-2026-rotate")
handshake_request = json.loads(Path("examples/agent_handshake_request.json").read_text())

handshake = client.agent_handshake(handshake_request)
print(handshake["handshake_posture"])
print(handshake["recommended_executor"])
print(handshake["replay"]["fitness_replay_id"])
```

## Reviews

```python
review = {
    "reviewer_id": "security-reviewer-1",
    "verdict": "agree",
    "review_latency_ms": 1800,
    "useful_constraint": decision["posture"] != "ALLOW",
}

client.review_decision(decision["replay_id"], review, idempotency_key="review-2041")
reviews = client.list_reviews(decision["replay_id"])
```

## Retained Pilot Evidence

Use this path when a pilot has produced a Decision Lifecycle Ledger and the security team needs a portable review package.

```python
import json
from pathlib import Path

ledger = json.loads(Path("reports/decision_lifecycle_ledger_example.json").read_text())

stored = client.store_pilot_dll_ledger(ledger)
decision_id = stored["stored_ledger"]["decision_id"]

certificate = client.issue_stored_pilot_dll_certificate(
    decision_id,
    issuer="smerc-api:pilot-reviewer",
)

evidence_package = client.pilot_evidence_package(
    decision_id,
    issuer="smerc-api:pilot-reviewer",
    security_event_limit=50,
)

print(certificate["certificate"]["certificate_digest"])
print(evidence_package["package"]["markdown_report"])
```

The evidence package is a pilot-review artifact. It does not provide immutable storage, legal retention, SIEM export, production assurance, or compliance certification by itself.

## Errors

Non-2xx API responses raise `SMERCAPIError` with the HTTP status, SMERC error code, message, and parsed JSON body.

```python
from smerc_sdk import SMERCAPIError

try:
    client.evaluate({"action_id": "bad"})
except SMERCAPIError as exc:
    print(exc.status, exc.code, exc.message)
```

## Scope

The first SDK version is intentionally narrow:

- standard library only
- JSON dictionaries in, JSON dictionaries out
- no background retry loop
- no hidden policy decisions on the client
- no automatic execution of approved actions

That keeps authority in the SMERC API and makes pilot behavior easier to inspect.

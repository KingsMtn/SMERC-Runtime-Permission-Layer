# JavaScript SDK Quickstart

The `smerc_js_sdk` package is a dependency-free ESM client for the SMERC Runtime Permission API. It is intended for Node services, agent runners, GitHub tooling, internal developer platforms, and browser-based pilot utilities that need to call SMERC without a generated client or npm dependency.

The SDK does not make local authorization decisions. It calls the authenticated SMERC API, which persists replayable decisions, agent handshakes, and audit records.

## Start A Local API

```bash
python api_server.py --host 127.0.0.1 --port 8788 --audit-db :memory: --allow-unauthenticated
```

For authenticated pilot mode, use scoped principals or pilot keys as described in `docs/Developer_Quickstart.md`.

## Evaluate One Action

```js
import { readFile } from 'node:fs/promises';
import { SMERCClient } from './smerc_js_sdk/index.mjs';

const client = new SMERCClient('http://127.0.0.1:8788');
const action = JSON.parse(await readFile('examples/recoverability_single_action.json', 'utf8'));

const decision = await client.evaluate(action, { idempotencyKey: 'node-demo-1001' });
console.log(decision.posture, decision.replay_id);
```

## Authenticated Pilot Use

```js
import { SMERCClient } from './smerc_js_sdk/index.mjs';

const client = new SMERCClient('http://127.0.0.1:8788', {
  token: 'development-console-secret-2026-rotate',
});

const decision = await client.evaluate(action, { idempotencyKey: 'workflow-run-1001' });
const replay = await client.getDecision(decision.replay_id);
const queue = await client.reviewQueue({ status: 'pending', limit: 20 });
const metrics = await client.pilotMetrics();
```

## Action Language Evaluation

```js
import { readFile } from 'node:fs/promises';
import { SMERCClient } from './smerc_js_sdk/index.mjs';

const client = new SMERCClient('http://127.0.0.1:8788', {
  token: 'development-console-secret-2026-rotate',
});
const payload = JSON.parse(await readFile('examples/action_language/production_database_change.json', 'utf8'));

const decision = await client.evaluateLanguageAction(payload, { idempotencyKey: 'db-change-2041' });
```

## Agent Handshake

Use this path when an agent or automation runner needs to discover SMERC, declare itself, propose a task and action, and receive a replayable posture before execution.

```js
import { readFile } from 'node:fs/promises';
import { SMERCClient } from './smerc_js_sdk/index.mjs';

const client = new SMERCClient('http://127.0.0.1:8788', {
  token: 'development-console-secret-2026-rotate',
});
const handshakeRequest = JSON.parse(await readFile('examples/agent_handshake_request.json', 'utf8'));

const handshake = await client.agentHandshake(handshakeRequest);
console.log(handshake.handshake_posture);
console.log(handshake.recommended_executor);
console.log(handshake.replay.fitness_replay_id);
```

## Reviews

```js
const review = {
  reviewer_id: 'security-reviewer-1',
  verdict: 'agree',
  review_latency_ms: 1800,
  useful_constraint: decision.posture !== 'ALLOW',
};

await client.reviewDecision(decision.replay_id, review, { idempotencyKey: 'review-2041' });
const reviews = await client.listReviews(decision.replay_id);
```

## Retained Pilot Evidence

Use this path when a pilot has produced a Decision Lifecycle Ledger and the security team needs a portable review package.

```js
import { readFile } from 'node:fs/promises';

const ledger = JSON.parse(await readFile('reports/decision_lifecycle_ledger_example.json', 'utf8'));

const stored = await client.storePilotDllLedger(ledger);
const decisionId = stored.stored_ledger.decision_id;

const certificate = await client.issueStoredPilotDllCertificate(decisionId, {
  issuer: 'smerc-api:pilot-reviewer',
});

const evidencePackage = await client.pilotEvidencePackage(decisionId, {
  issuer: 'smerc-api:pilot-reviewer',
  securityEventLimit: 50,
});

console.log(certificate.certificate.certificate_digest);
console.log(evidencePackage.package.markdown_report);
```

The evidence package is a pilot-review artifact. It does not provide immutable storage, legal retention, SIEM export, production assurance, or compliance certification by itself.

## Errors

Non-2xx API responses throw `SMERCAPIError` with `status`, `code`, and the parsed JSON `body`.

```js
import { SMERCAPIError } from './smerc_js_sdk/index.mjs';

try {
  await client.evaluate({ action_id: 'bad' });
} catch (error) {
  if (error instanceof SMERCAPIError) {
    console.log(error.status, error.code, error.body);
  }
}
```

## Scope

The first JavaScript SDK version is intentionally narrow:

- ESM only
- no npm dependencies
- no generated client code
- no hidden retries or local authorization shortcuts
- no automatic execution of approved actions

That keeps authority in the SMERC API and leaves pilot behavior inspectable.

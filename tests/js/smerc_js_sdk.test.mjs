import test from 'node:test';
import assert from 'node:assert/strict';

import { SMERCAPIError, SMERCClient } from '../../smerc_js_sdk/index.mjs';

function jsonResponse(body, init = {}) {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    statusText: init.statusText ?? 'OK',
    headers: { 'content-type': 'application/json' },
  });
}

test('client sends authenticated evaluation request with idempotency key', async () => {
  const calls = [];
  const client = new SMERCClient('https://smerc.example/api/', {
    token: 'pilot-secret',
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      return jsonResponse({ posture: 'THROTTLE', replay_id: 'replay_1' });
    },
  });

  const decision = await client.evaluate({ action_id: 'deploy-1' }, { idempotencyKey: 'run-1001' });

  assert.equal(decision.posture, 'THROTTLE');
  assert.equal(calls.length, 1);
  assert.equal(String(calls[0].url), 'https://smerc.example/api/v1/evaluate');
  assert.equal(calls[0].options.method, 'POST');
  assert.equal(calls[0].options.headers.get('Authorization'), 'Bearer pilot-secret');
  assert.equal(calls[0].options.headers.get('Idempotency-Key'), 'run-1001');
  assert.equal(calls[0].options.headers.get('Content-Type'), 'application/json');
  assert.deepEqual(JSON.parse(calls[0].options.body), { action_id: 'deploy-1' });
});

test('client builds query parameters for decision and review queue reads', async () => {
  const urls = [];
  const client = new SMERCClient('https://smerc.example', {
    fetchImpl: async (url) => {
      urls.push(String(url));
      return jsonResponse({ ok: true });
    },
  });

  await client.listDecisions({ limit: 10, posture: 'ALLOW' });
  await client.reviewQueue({ limit: 5, posture: 'THROTTLE', status: 'pending' });
  await client.securityEvents({ limit: 2 });

  assert.equal(urls[0], 'https://smerc.example/v1/decisions?limit=10&posture=ALLOW');
  assert.equal(urls[1], 'https://smerc.example/v1/review-queue?limit=5&posture=THROTTLE&status=pending');
  assert.equal(urls[2], 'https://smerc.example/v1/security-events?limit=2');
});

test('client exposes replay, review, language, batch, permit, and token endpoints', async () => {
  const calls = [];
  const client = new SMERCClient('https://smerc.example', {
    fetchImpl: async (url, options) => {
      calls.push({ url: String(url), method: options.method, body: options.body });
      return jsonResponse({ ok: true });
    },
  });

  await client.health();
  await client.ready();
  await client.schema();
  await client.getDecision('replay_1');
  await client.listReviews('replay_1');
  await client.reviewDecision('replay_1', { verdict: 'agree' });
  await client.evaluateLanguageAction({ language_version: 'smerc.action.v1' });
  await client.batch([{ action_id: 'a' }]);
  await client.issuePermit({ replay_id: 'replay_1' });
  await client.preparePermit({ permit_token: 'token' });
  await client.consumePermit({ permit_token: 'token' });
  await client.exchangeToken({ scopes: ['actions.evaluate'] });
  await client.storePilotDllLedger({ version: 'smerc.decision-lifecycle-ledger.v1' }, { decisionId: 'dll_1' });
  await client.listPilotDllLedgers({ limit: 3 });
  await client.getPilotDllLedger('dll_1');
  await client.issueStoredPilotDllCertificate('dll_1', { issuer: 'js-sdk-test' });
  await client.pilotEvidencePackage('dll_1', { issuer: 'js-sdk-test', securityEventLimit: 10 });

  assert.deepEqual(calls.map((call) => `${call.method} ${new URL(call.url).pathname}`), [
    'GET /v1/health',
    'GET /v1/ready',
    'GET /v1/schema',
    'GET /v1/decisions/replay_1',
    'GET /v1/decisions/replay_1/reviews',
    'POST /v1/decisions/replay_1/reviews',
    'POST /v1/language/evaluate',
    'POST /v1/batch',
    'POST /v1/permits/issue',
    'POST /v1/permits/prepare',
    'POST /v1/permits/consume',
    'POST /v1/auth/token',
    'POST /v1/pilot/dll/ledgers',
    'GET /v1/pilot/dll/ledgers',
    'GET /v1/pilot/dll/ledgers/dll_1',
    'POST /v1/pilot/dll/ledgers/dll_1/certificate',
    'POST /v1/pilot/evidence-packages',
  ]);
  assert.deepEqual(JSON.parse(calls.at(-1).body), {
    decision_id: 'dll_1',
    issuer: 'js-sdk-test',
    security_event_limit: 10,
  });
});

test('non-2xx responses throw structured SMERCAPIError', async () => {
  const client = new SMERCClient('https://smerc.example', {
    fetchImpl: async () => jsonResponse({
      error: 'authentication_required',
      message: 'Authentication is required.',
    }, { status: 401, statusText: 'Unauthorized' }),
  });

  await assert.rejects(
    () => client.evaluate({ action_id: 'deploy-1' }),
    (error) => {
      assert.ok(error instanceof SMERCAPIError);
      assert.equal(error.status, 401);
      assert.equal(error.code, 'authentication_required');
      assert.equal(error.body.message, 'Authentication is required.');
      return true;
    },
  );
});

test('invalid base URLs and path identifiers are rejected before request', async () => {
  assert.throws(() => new SMERCClient('file:///tmp/smerc'), /baseUrl/);

  const client = new SMERCClient('https://smerc.example', {
    fetchImpl: async () => jsonResponse({ ok: true }),
  });

  assert.throws(() => client.getDecision('../bad'), /path identifier/);
});

export class SMERCAPIError extends Error {
  constructor(status, code, message, body = {}) {
    super(`SMERC API error ${status} ${code}: ${message}`);
    this.name = 'SMERCAPIError';
    this.status = status;
    this.code = code;
    this.body = body;
  }
}

export class SMERCClient {
  constructor(baseUrl, options = {}) {
    if (typeof baseUrl !== 'string' || !/^https?:\/\//.test(baseUrl)) {
      throw new TypeError('baseUrl must start with http:// or https://');
    }
    const timeoutMs = options.timeoutMs ?? 10000;
    if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
      throw new TypeError('timeoutMs must be greater than zero');
    }
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.token = options.token ?? null;
    this.timeoutMs = timeoutMs;
    this.userAgent = options.userAgent ?? 'smerc-js-sdk/0.1';
    this.fetchImpl = options.fetchImpl ?? globalThis.fetch;
    if (typeof this.fetchImpl !== 'function') {
      throw new TypeError('SMERCClient requires fetch or an injected fetchImpl');
    }
  }

  health() {
    return this.request('GET', '/v1/health');
  }

  ready() {
    return this.request('GET', '/v1/ready');
  }

  schema() {
    return this.request('GET', '/v1/schema');
  }

  evaluate(action, options = {}) {
    return this.request('POST', '/v1/evaluate', { body: action, idempotencyKey: options.idempotencyKey });
  }

  evaluateLanguageAction(actionEnvelope, options = {}) {
    return this.request('POST', '/v1/language/evaluate', {
      body: actionEnvelope,
      idempotencyKey: options.idempotencyKey,
    });
  }

  batch(actions, options = {}) {
    return this.request('POST', '/v1/batch', { body: actions, idempotencyKey: options.idempotencyKey });
  }

  listDecisions(options = {}) {
    return this.request('GET', '/v1/decisions', {
      query: cleanQuery({ limit: options.limit, posture: options.posture }),
    });
  }

  getDecision(replayId) {
    return this.request('GET', `/v1/decisions/${pathToken(replayId)}`);
  }

  reviewDecision(replayId, review, options = {}) {
    return this.request('POST', `/v1/decisions/${pathToken(replayId)}/reviews`, {
      body: review,
      idempotencyKey: options.idempotencyKey,
    });
  }

  listReviews(replayId) {
    return this.request('GET', `/v1/decisions/${pathToken(replayId)}/reviews`);
  }

  pilotMetrics() {
    return this.request('GET', '/v1/pilot/metrics');
  }

  reviewQueue(options = {}) {
    return this.request('GET', '/v1/review-queue', {
      query: cleanQuery({ limit: options.limit, posture: options.posture, status: options.status }),
    });
  }

  securityEvents(options = {}) {
    return this.request('GET', '/v1/security-events', {
      query: cleanQuery({ limit: options.limit }),
    });
  }

  storePilotDllLedger(ledger, options = {}) {
    return this.request('POST', '/v1/pilot/dll/ledgers', {
      body: cleanBody({ ledger, decision_id: options.decisionId }),
    });
  }

  listPilotDllLedgers(options = {}) {
    return this.request('GET', '/v1/pilot/dll/ledgers', {
      query: cleanQuery({ limit: options.limit }),
    });
  }

  getPilotDllLedger(decisionId) {
    return this.request('GET', `/v1/pilot/dll/ledgers/${pathToken(decisionId)}`);
  }

  issueStoredPilotDllCertificate(decisionId, options = {}) {
    return this.request('POST', `/v1/pilot/dll/ledgers/${pathToken(decisionId)}/certificate`, {
      body: cleanBody({ issuer: options.issuer, route_report: options.routeReport }),
    });
  }

  pilotEvidencePackage(decisionId, options = {}) {
    return this.request('POST', '/v1/pilot/evidence-packages', {
      body: cleanBody({
        decision_id: decisionId,
        issuer: options.issuer,
        route_report: options.routeReport,
        security_event_limit: options.securityEventLimit,
      }),
    });
  }

  issuePermit(payload) {
    return this.request('POST', '/v1/permits/issue', { body: payload });
  }

  preparePermit(payload) {
    return this.request('POST', '/v1/permits/prepare', { body: payload });
  }

  consumePermit(payload) {
    return this.request('POST', '/v1/permits/consume', { body: payload });
  }

  exchangeToken(payload) {
    return this.request('POST', '/v1/auth/token', { body: payload });
  }

  async request(method, path, options = {}) {
    const url = new URL(`${this.baseUrl}${path}`);
    for (const [key, value] of Object.entries(options.query ?? {})) {
      url.searchParams.set(key, String(value));
    }

    const headers = new Headers({
      Accept: 'application/json',
      'User-Agent': this.userAgent,
    });
    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }
    if (options.idempotencyKey) {
      headers.set('Idempotency-Key', options.idempotencyKey);
    }

    let body;
    if (options.body !== undefined) {
      headers.set('Content-Type', 'application/json');
      body = JSON.stringify(options.body);
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      const response = await this.fetchImpl(url, {
        method,
        headers,
        body,
        signal: controller.signal,
      });
      const payload = await decodeJson(response);
      if (!response.ok) {
        const code = String(payload.error ?? payload.code ?? 'http_error');
        const message = String(payload.message ?? payload.detail ?? response.statusText);
        throw new SMERCAPIError(response.status, code, message, payload);
      }
      return payload;
    } catch (error) {
      if (error?.name === 'AbortError') {
        throw new Error(`SMERC API request timed out after ${this.timeoutMs} ms`);
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }
}

async function decodeJson(response) {
  const text = await response.text();
  if (!text) {
    return {};
  }
  const payload = JSON.parse(text);
  if (payload === null || Array.isArray(payload) || typeof payload !== 'object') {
    throw new TypeError('SMERC API returned a non-object JSON response');
  }
  return payload;
}

function cleanQuery(values) {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value !== undefined && value !== null));
}

function cleanBody(values) {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value !== undefined && value !== null));
}

function pathToken(value) {
  if (typeof value !== 'string' || value.length === 0 || /[/?#]/.test(value)) {
    throw new TypeError('path identifier must be non-empty and cannot contain path separators');
  }
  return value;
}

import { buildReviewPayload, formatLatency, formatRatio, normalizeBaseUrl } from './model.mjs';

const state = {
  apiUrl: null,
  apiKey: null,
  metrics: null,
  queue: [],
  selected: null,
  selectedAt: null,
};

const byId = (id) => document.getElementById(id);
const connectionForm = byId('connection-form');
const connectionStatus = byId('connection-status');
const metricsGrid = byId('metrics-grid');
const downloadMetrics = byId('download-metrics');
const refreshQueueButton = byId('refresh-queue');
const statusFilter = byId('status-filter');
const postureFilter = byId('posture-filter');
const queueList = byId('queue-list');
const decisionEmpty = byId('decision-empty');
const decisionDetail = byId('decision-detail');
const reviewForm = byId('review-form');
const reviewError = byId('review-error');

function setConnectionStatus(message, tone = '') {
  connectionStatus.textContent = message;
  connectionStatus.className = `connection-status ${tone}`.trim();
}

async function apiFetch(path, options = {}) {
  if (!state.apiUrl || !state.apiKey) throw new Error('Connect to the pilot API first.');
  const headers = new Headers(options.headers || {});
  headers.set('Authorization', `Bearer ${state.apiKey}`);
  if (options.body) headers.set('Content-Type', 'application/json');
  const response = await fetch(`${state.apiUrl}${path}`, { ...options, headers, redirect: 'error' });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.message || `API request failed with status ${response.status}.`);
  return payload;
}

function createMetric(label, value, denominator) {
  const element = document.createElement('div');
  element.className = 'metric';
  const strong = document.createElement('strong');
  strong.textContent = value;
  const span = document.createElement('span');
  span.textContent = label;
  const small = document.createElement('small');
  small.textContent = denominator;
  element.append(strong, span, small);
  return element;
}

function renderMetrics() {
  metricsGrid.replaceChildren();
  const report = state.metrics;
  if (!report) {
    const empty = document.createElement('p');
    empty.className = 'empty-copy';
    empty.textContent = 'No metrics loaded.';
    metricsGrid.append(empty);
    return;
  }
  const metrics = report.metrics;
  const d = report.denominators;
  metricsGrid.append(
    createMetric('Review coverage', formatRatio(metrics.decision_review_coverage), `${d.all_decisions} decisions`),
    createMetric('Agreement', formatRatio(metrics.reviewer_agreement_rate), `${d.determinate_reviews} determinate`),
    createMetric('Overrides', formatRatio(metrics.override_rate), `${d.determinate_reviews} determinate`),
    createMetric('False releases', formatRatio(metrics.false_release_rate), `${d.allow_reviews} ALLOW reviews`),
    createMetric('False constraints', formatRatio(metrics.false_constraint_rate), `${d.constrained_reviews} constrained`),
    createMetric('Useful constraints', formatRatio(metrics.useful_constraint_rate), `${d.constrained_reviews} constrained`),
    createMetric('Average latency', formatLatency(metrics.average_review_latency_ms), `${d.all_reviews} reviews`),
  );
}

function postureClass(posture) {
  return `posture-badge posture-${String(posture).toLowerCase()}`;
}

function renderQueue() {
  queueList.replaceChildren();
  if (!state.queue.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-copy';
    empty.textContent = 'No decisions match the selected filters.';
    queueList.append(empty);
    return;
  }
  for (const item of state.queue) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `queue-item${state.selected?.replay_id === item.replay_id ? ' selected' : ''}`;
    button.dataset.replayId = item.replay_id;
    const title = document.createElement('strong');
    title.textContent = item.action_id;
    const posture = document.createElement('span');
    posture.className = postureClass(item.posture);
    posture.textContent = item.posture;
    const meta = document.createElement('span');
    meta.className = 'queue-meta';
    meta.textContent = new Date(item.evaluated_at).toLocaleString();
    const reviews = document.createElement('span');
    reviews.className = 'review-count';
    reviews.textContent = `${item.review_count} review${item.review_count === 1 ? '' : 's'}`;
    button.append(title, posture, meta, reviews);
    button.addEventListener('click', () => selectDecision(item.replay_id));
    queueList.append(button);
  }
}

function fillList(id, values) {
  const list = byId(id);
  list.replaceChildren();
  for (const value of values || []) {
    const item = document.createElement('li');
    item.textContent = value;
    list.append(item);
  }
}

function renderExistingReviews(reviews) {
  const container = byId('review-list');
  container.replaceChildren();
  if (!reviews.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-copy';
    empty.textContent = 'No reviews recorded.';
    container.append(empty);
    return;
  }
  for (const review of reviews) {
    const record = document.createElement('div');
    record.className = 'review-record';
    const verdict = document.createElement('strong');
    verdict.textContent = review.verdict.toUpperCase();
    const detail = document.createElement('span');
    detail.textContent = `${review.reviewer_id} · ${new Date(review.created_at).toLocaleString()}`;
    record.append(verdict, detail);
    container.append(record);
  }
}

function configureReviewLabels(posture) {
  const isAllow = posture === 'ALLOW';
  byId('false-release').disabled = !isAllow;
  byId('false-constraint').disabled = isAllow;
  byId('useful-constraint').disabled = isAllow;
  if (!isAllow) byId('false-release').checked = false;
  if (isAllow) {
    byId('false-constraint').checked = false;
    byId('useful-constraint').checked = false;
  }
}

function renderDecision(decision, reviews) {
  decisionEmpty.hidden = true;
  decisionDetail.hidden = false;
  byId('detail-action-type').textContent = `${decision.replay.actor} · ${decision.replay.tool}`;
  byId('detail-action-id').textContent = decision.action_id;
  byId('detail-posture').textContent = decision.posture;
  byId('detail-posture').className = postureClass(decision.posture);
  byId('detail-summary').textContent = decision.plain_english_summary;
  const scoreGrid = byId('score-grid');
  scoreGrid.replaceChildren();
  for (const [name, value] of Object.entries(decision.scores || {})) {
    const score = document.createElement('div');
    score.className = 'score';
    const strong = document.createElement('strong');
    strong.textContent = Number(value).toFixed(3);
    const label = document.createElement('span');
    label.textContent = name.replaceAll('_', ' ');
    score.append(strong, label);
    scoreGrid.append(score);
  }
  fillList('reason-list', decision.reason_codes);
  fillList('control-list', decision.controls);
  renderExistingReviews(reviews);
  reviewForm.reset();
  byId('recommended-wrap').hidden = true;
  configureReviewLabels(decision.posture);
  reviewError.hidden = true;
}

async function selectDecision(replayId) {
  try {
    const [decision, reviewEnvelope] = await Promise.all([
      apiFetch(`/v1/decisions/${encodeURIComponent(replayId)}`),
      apiFetch(`/v1/decisions/${encodeURIComponent(replayId)}/reviews`),
    ]);
    state.selected = decision;
    state.selectedAt = Date.now();
    renderQueue();
    renderDecision(decision, reviewEnvelope.reviews || []);
  } catch (error) {
    setConnectionStatus(error.message, 'error');
  }
}

async function loadMetrics() {
  state.metrics = await apiFetch('/v1/pilot/metrics');
  renderMetrics();
  downloadMetrics.disabled = false;
}

async function loadQueue() {
  const query = new URLSearchParams({ status: statusFilter.value, limit: '200' });
  if (postureFilter.value) query.set('posture', postureFilter.value);
  const envelope = await apiFetch(`/v1/review-queue?${query}`);
  state.queue = envelope.decisions || [];
  renderQueue();
}

async function refreshAll() {
  setConnectionStatus('Loading…');
  await Promise.all([loadMetrics(), loadQueue()]);
  refreshQueueButton.disabled = false;
  setConnectionStatus('Connected', 'connected');
}

connectionForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const apiKey = byId('api-key').value;
    if (!apiKey) throw new Error('Bearer key is required.');
    state.apiUrl = normalizeBaseUrl(byId('api-url').value);
    state.apiKey = apiKey;
    await refreshAll();
  } catch (error) {
    state.apiKey = null;
    setConnectionStatus(error.message, 'error');
  }
});

refreshQueueButton.addEventListener('click', async () => {
  try { await refreshAll(); } catch (error) { setConnectionStatus(error.message, 'error'); }
});

statusFilter.addEventListener('change', () => loadQueue().catch((error) => setConnectionStatus(error.message, 'error')));
postureFilter.addEventListener('change', () => loadQueue().catch((error) => setConnectionStatus(error.message, 'error')));

reviewForm.addEventListener('change', (event) => {
  if (event.target.name === 'verdict') {
    byId('recommended-wrap').hidden = event.target.value !== 'override';
  }
});

reviewForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!state.selected) return;
  reviewError.hidden = true;
  const submit = byId('submit-review');
  submit.disabled = true;
  try {
    const form = new FormData(reviewForm);
    const payload = buildReviewPayload(
      {
        reviewerId: form.get('reviewerId'),
        verdict: form.get('verdict'),
        recommendedPosture: form.get('recommendedPosture'),
        falseRelease: form.get('falseRelease') === 'on',
        falseConstraint: form.get('falseConstraint') === 'on',
        usefulConstraint: form.get('usefulConstraint') === 'on',
        comment: form.get('comment'),
      },
      state.selected.posture,
      Date.now() - state.selectedAt,
    );
    await apiFetch(`/v1/decisions/${encodeURIComponent(state.selected.replay_id)}/reviews`, {
      method: 'POST',
      headers: { 'Idempotency-Key': `console-${crypto.randomUUID()}` },
      body: JSON.stringify(payload),
    });
    await Promise.all([selectDecision(state.selected.replay_id), loadMetrics(), loadQueue()]);
    setConnectionStatus('Review recorded', 'connected');
  } catch (error) {
    reviewError.textContent = error.message;
    reviewError.hidden = false;
  } finally {
    submit.disabled = false;
  }
});

downloadMetrics.addEventListener('click', () => {
  if (!state.metrics) return;
  const blob = new Blob([`${JSON.stringify(state.metrics, null, 2)}\n`], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'smerc-pilot-metrics.json';
  anchor.click();
  URL.revokeObjectURL(url);
});

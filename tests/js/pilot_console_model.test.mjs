import test from 'node:test';
import assert from 'node:assert/strict';

import {
  buildReviewPayload,
  formatLatency,
  formatRatio,
  normalizeBaseUrl,
} from '../../pilot_console/model.mjs';

test('normalizes loopback and HTTPS API URLs', () => {
  assert.equal(normalizeBaseUrl('http://127.0.0.1:8788/'), 'http://127.0.0.1:8788');
  assert.equal(normalizeBaseUrl('https://pilot.example/v1/'), 'https://pilot.example/v1');
});

test('rejects insecure remote and credential-bearing API URLs', () => {
  assert.throws(() => normalizeBaseUrl('http://pilot.example'), /HTTPS/);
  assert.throws(() => normalizeBaseUrl('https://user:secret@pilot.example'), /credentials/);
  assert.throws(() => normalizeBaseUrl('https://pilot.example?secret=value'), /query/);
});

test('formats null and measured metrics without inventing evidence', () => {
  assert.equal(formatRatio(null), 'Not measured');
  assert.equal(formatRatio(0.696), '69.6%');
  assert.equal(formatLatency(null), 'Not measured');
  assert.equal(formatLatency(1250), '1.3 sec');
});

test('builds a coherent agreement payload', () => {
  assert.deepEqual(
    buildReviewPayload(
      {
        reviewerId: 'security-1',
        verdict: 'agree',
        usefulConstraint: true,
        comment: 'Constraint matched review policy.',
      },
      'THROTTLE',
      2450.4,
    ),
    {
      reviewer_id: 'security-1',
      verdict: 'agree',
      recommended_posture: null,
      false_release: false,
      false_constraint: false,
      useful_constraint: true,
      review_latency_ms: 2450,
      comment: 'Constraint matched review policy.',
    },
  );
});

test('requires a different posture for an override', () => {
  assert.throws(
    () => buildReviewPayload(
      { reviewerId: 'security-1', verdict: 'override', recommendedPosture: 'FREEZE' },
      'FREEZE',
      10,
    ),
    /different recommended posture/,
  );
});

test('enforces posture-aware outcome labels', () => {
  assert.throws(
    () => buildReviewPayload(
      { reviewerId: 'security-1', verdict: 'agree', usefulConstraint: true },
      'ALLOW',
      10,
    ),
    /do not apply to ALLOW/,
  );
  assert.throws(
    () => buildReviewPayload(
      { reviewerId: 'security-1', verdict: 'agree', falseRelease: true },
      'DENY',
      10,
    ),
    /only to ALLOW/,
  );
});

test('rejects conflicting constraint labels', () => {
  assert.throws(
    () => buildReviewPayload(
      {
        reviewerId: 'security-1',
        verdict: 'uncertain',
        falseConstraint: true,
        usefulConstraint: true,
      },
      'THROTTLE',
      10,
    ),
    /both false and useful/,
  );
});

test('bounds review identity, comments, and latency', () => {
  assert.throws(
    () => buildReviewPayload({ reviewerId: 'name with spaces', verdict: 'agree' }, 'ALLOW', 10),
    /Reviewer ID/,
  );
  assert.throws(
    () => buildReviewPayload(
      { reviewerId: 'security-1', verdict: 'agree', comment: 'x'.repeat(501) },
      'ALLOW',
      10,
    ),
    /500/,
  );
  const payload = buildReviewPayload(
    { reviewerId: 'security-1', verdict: 'agree' },
    'ALLOW',
    999999999,
  );
  assert.equal(payload.review_latency_ms, 604800000);
});

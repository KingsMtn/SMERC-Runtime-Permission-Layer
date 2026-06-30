export const POSTURES = ["ALLOW", "THROTTLE", "FREEZE", "DENY", "ESCALATE"];

export function normalizeBaseUrl(value) {
  const url = new URL(String(value || "").trim());
  if (!['http:', 'https:'].includes(url.protocol)) {
    throw new Error('API URL must use HTTP or HTTPS.');
  }
  const loopback = ['localhost', '127.0.0.1', '::1'].includes(url.hostname);
  if (url.protocol !== 'https:' && !loopback) {
    throw new Error('Remote API URLs must use HTTPS.');
  }
  if (url.username || url.password || url.search || url.hash) {
    throw new Error('API URL cannot contain credentials, a query, or a fragment.');
  }
  return url.toString().replace(/\/$/, '');
}

export function formatRatio(value) {
  if (value === null || value === undefined) return 'Not measured';
  const percentage = Number(value) * 100;
  return `${percentage.toFixed(Number.isInteger(percentage) ? 0 : 1)}%`;
}

export function formatLatency(value) {
  if (value === null || value === undefined) return 'Not measured';
  const milliseconds = Number(value);
  if (milliseconds < 1000) return `${Math.round(milliseconds)} ms`;
  if (milliseconds < 60000) return `${(milliseconds / 1000).toFixed(1)} sec`;
  return `${(milliseconds / 60000).toFixed(1)} min`;
}

export function buildReviewPayload(input, decisionPosture, elapsedMs) {
  const reviewerId = String(input.reviewerId || '').trim();
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/.test(reviewerId)) {
    throw new Error('Reviewer ID must be a pseudonymous 1-64 character safe identifier.');
  }
  const verdict = String(input.verdict || '');
  if (!['agree', 'override', 'uncertain'].includes(verdict)) {
    throw new Error('Select agree, override, or uncertain.');
  }
  const posture = String(decisionPosture || '').toUpperCase();
  if (!POSTURES.includes(posture)) throw new Error('Decision posture is invalid.');

  let recommendedPosture = input.recommendedPosture
    ? String(input.recommendedPosture).toUpperCase()
    : null;
  if (recommendedPosture && !POSTURES.includes(recommendedPosture)) {
    throw new Error('Recommended posture is invalid.');
  }
  if (verdict === 'override' && (!recommendedPosture || recommendedPosture === posture)) {
    throw new Error('An override requires a different recommended posture.');
  }
  if (verdict === 'agree' && recommendedPosture && recommendedPosture !== posture) {
    throw new Error('Agreement cannot recommend a different posture.');
  }
  if (verdict !== 'override') recommendedPosture = null;

  const falseRelease = Boolean(input.falseRelease);
  const falseConstraint = Boolean(input.falseConstraint);
  const usefulConstraint = Boolean(input.usefulConstraint);
  if (falseRelease && posture !== 'ALLOW') {
    throw new Error('False release applies only to ALLOW decisions.');
  }
  if ((falseConstraint || usefulConstraint) && posture === 'ALLOW') {
    throw new Error('Constraint labels do not apply to ALLOW decisions.');
  }
  if (falseConstraint && usefulConstraint) {
    throw new Error('A constraint cannot be both false and useful.');
  }

  const comment = String(input.comment || '').trim();
  if (comment.length > 500) throw new Error('Comment cannot exceed 500 characters.');

  return {
    reviewer_id: reviewerId,
    verdict,
    recommended_posture: recommendedPosture,
    false_release: falseRelease,
    false_constraint: falseConstraint,
    useful_constraint: usefulConstraint,
    review_latency_ms: Math.max(0, Math.min(604800000, Math.round(Number(elapsedMs) || 0))),
    comment: comment || null,
  };
}

# Pilot Review and Metrics

SMERC can collect tenant-scoped reviewer feedback against a stored decision. This turns a shadow-mode pilot into measurable evidence without changing the original decision record.

## Review Contract

Submit one immutable review per pseudonymous reviewer and decision:

```bash
curl --request POST "$SMERC_API_URL/v1/decisions/$REPLAY_ID/reviews" \
  --header "Authorization: Bearer $SMERC_API_KEY" \
  --header "Content-Type: application/json" \
  --header "Idempotency-Key: review-$REPLAY_ID-security-1" \
  --data @examples/pilot_review.json
```

`verdict` accepts `agree`, `override`, or `uncertain`. An override must include a different `recommended_posture`. Labels are posture-aware: `false_release` applies only to `ALLOW`; `false_constraint` and `useful_constraint` apply only to non-ALLOW decisions and cannot both be true.

Use a pseudonymous reviewer identifier rather than a name or email. Comments are capped at 500 characters and should not include secrets, source code, personal data, or incident payloads.

Retrieve reviews and current metrics:

```bash
curl --header "Authorization: Bearer $SMERC_API_KEY" \
  "$SMERC_API_URL/v1/decisions/$REPLAY_ID/reviews"

curl --header "Authorization: Bearer $SMERC_API_KEY" \
  "$SMERC_API_URL/v1/pilot/metrics"
```

## Metrics

- decision review coverage
- reviewer agreement rate
- override rate
- false release rate
- false constraint rate
- useful constraint rate
- average review latency

Every rate is returned with its denominator. A rate is `null` when its denominator is zero. These are descriptive pilot measurements, not proof of accuracy, causality, customer value, or production safety.

Rate values are ratios from `0.0` through `1.0`, not preformatted percentages.

## Offline Export

Generate JSON and Markdown evidence from a pilot SQLite database:

```bash
python -m reference_engine.pilot_metrics_report \
  --audit-db smerc_audit.sqlite3 \
  --tenant design-partner \
  --output-dir pilot-metrics-output
```

The current SQLite implementation is for a controlled single-instance pilot. A production service needs external transactional storage, managed identity, retention policy, backup testing, and access monitoring.

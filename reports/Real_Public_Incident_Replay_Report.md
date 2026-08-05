# SMERC Real Public Incident Replay Report

This report replays public incident patterns through SMERC. Public source facts are real; SMERC numeric signals are analyst-assigned replay inputs.

## Summary

- Scenario count: `6`
- Public source count: `4`
- Decision difference rate: `1.0`
- Average irreversible exposure: `0.645`
- Average reversible capacity: `0.497`

## Replay Results

| Scenario | Source | Traditional | SMERC | Exposure | Capacity | Question |
|---|---|---:|---:|---:|---:|---|
| public-github-actions-runner-degradation-2026-05-05 | [GitHub Blog](https://github.blog/news-insights/company-news/github-availability-report-may-2026/) | `ALLOW` | `THROTTLE` | `0.52` | `0.599` | Should an automated runner scale-up or retry action continue at full speed while regional allocation failures are rising? |
| public-github-actions-failover-routing-2026-05-15 | [GitHub Blog](https://github.blog/news-insights/company-news/github-availability-report-may-2026/) | `ALLOW` | `THROTTLE` | `0.615` | `0.47` | Should automated failover complete before validating service discovery state and downstream orchestration dependencies? |
| public-github-auth-partial-deploy-rollback-2026-05-28 | [GitHub Status](https://www.githubstatus.com/history?page=1) | `ALLOW` | `THROTTLE` | `0.583` | `0.662` | Should a partially deployed authentication-service change continue when dependent services show elevated errors? |
| public-keepthescore-production-db-delete | [postmortems.app](https://postmortems.app/postmortem/b4b5957d-2c5f-4db4-b866-8d82da25bd93) | `ALLOW` | `DENY` | `0.983` | `0.188` | Should an automated or human-assisted database deletion proceed when backup granularity makes recent data unrecoverable? |
| public-cloudflare-dnssec-de-outage-2026-05-05 | [Cloudflare via postmortem.io index](https://postmortem.io/) | `ALLOW` | `ESCALATE` | `0.712` | `0.402` | Should DNSSEC-related changes proceed automatically when external resolution instability is detected? |
| public-mongodb-atlas-admin-api-degradation-2026-03-25 | [MongoDB Atlas via postmortem.io index](https://postmortem.io/) | `ALLOW` | `THROTTLE` | `0.456` | `0.664` | Should control-plane automation continue at normal rate while admin APIs return intermittent 503 errors? |

## Boundary

- does not prove SMERC would have prevented the public incident
- does not use private telemetry from the source organization
- does not calibrate thresholds from ground-truth customer labels
- does not replace a design-partner pilot

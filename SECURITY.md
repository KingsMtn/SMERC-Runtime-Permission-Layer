# Security Policy

## Current Status

SMERC is an MVP/reference implementation intended for controlled technical review and shadow-mode pilots. It is not currently represented as production-certified security infrastructure.

## Reporting Security Issues

Do not publish suspected vulnerabilities, secrets, or sensitive customer information in a public issue.

Use the repository owner's private GitHub contact path to report a suspected security issue and include:

- affected component
- reproduction steps
- potential impact
- suggested mitigation, if available

## Pilot Data Handling

A first pilot should provide action metadata rather than raw sensitive payloads. SMERC should not require production secrets, customer PII, private keys, raw credentials, full source-code contents, or privileged cloud credentials.

## Pilot API Controls

The pilot API defaults to refusing startup without at least one tenant-mapped bearer key. It provides:

- constant-time API-key comparison
- tenant-scoped decision storage and retrieval
- idempotency conflict detection
- bounded body and batch sizes
- allowlisted CORS rather than wildcard browser access
- no-store and content-type response headers
- opaque request identifiers

`--allow-unauthenticated` is intended only for local development. It must not be used on a network-accessible pilot deployment.

SQLite supports a controlled, single-instance pilot. It is not the target enterprise storage architecture. A multi-instance deployment requires an external transactional datastore, managed key rotation, centralized authorization, retention controls, backup testing, and operational monitoring.

Pilot reviews use pseudonymous reviewer identifiers and bounded optional comments. Do not place names, email addresses, credentials, source code, personal data, incident payloads, or other sensitive content in review fields. Review records are immutable; corrections should be handled under an approved pilot evidence procedure rather than by editing the audit database.

## GitHub Actions Remote Mode

Remote evaluation reads the bearer credential only from `SMERC_API_KEY`. The integration requires HTTPS outside loopback testing, refuses cross-origin redirects, bounds response size, validates response structure, and reuses one idempotency key across transient retries.

Do not expose the pilot secret to untrusted fork workflows. Pin the action to a reviewed commit SHA, restrict workflow permissions, use action metadata rather than sensitive payloads, and approve report-artifact retention before a live pilot.

An unavailable remote service never produces a fabricated posture. Observe and recommend modes may report `UNAVAILABLE`; enforce mode always fails closed.

## Enforcement Warning

Do not use the reference thresholds for production blocking without threat modeling, calibration, accountable approval, override procedures, and an explicit fail-open/fail-closed decision.

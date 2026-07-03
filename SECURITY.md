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

Action Language context is bounded to 16,384 canonical JSON bytes. Contract objects reject unknown fields, but `context` remains caller-defined metadata and must be treated as untrusted input by downstream log, export, and display systems. The deterministic action hash detects equal canonical requests; it is not authentication, a signature, or proof of origin.

Evidence observations are untrusted claims about outcomes. Dataset identifiers and source-quality scores do not prove provenance by themselves. A live evidence pipeline requires authenticated ingestion, append-only records, reviewer identity, source attestation, retention controls, and independent checks against metric manipulation.

The reference provenance ledger binds observations and source-artifact digests into a SHA-256 or HMAC-SHA-256 chain. Hash-only mode detects mutation only when a trusted head hash is retained independently. HMAC mode depends on confidentiality, rotation, and access control for `SMERC_EVIDENCE_HMAC_KEY`; it does not provide public-key nonrepudiation. Never commit that key or place it in action metadata.

Tenant policy files are trusted configuration. Limit write access, review threshold changes, retain prior policy hashes, and deploy policy revisions through approved change control. The reference server loads policies at startup and does not provide a remote policy-administration endpoint.

Action-bound permits are HMAC-authenticated bearer capabilities. Never log, commit, persist in build artifacts, or expose them as workflow outputs. `SMERC_PERMIT_KEYS` requires separate tenant keys of at least 32 bytes. A compromised key can mint valid-looking permits, and HMAC does not provide public nonrepudiation. The pilot limits permits to five minutes, binds them to one action, tenant, audience, decision, and policy, registers one issuance per decision/audience, and consumes them once in SQLite. Production deployment still requires HSM/KMS-backed rotation, workload identity, distributed atomic replay prevention, revocation, clock monitoring, adapter attestation, and incident procedures.

A consuming adapter's `enforced_controls` list is an assertion, not independent proof that a constraint operated. Production adapters must derive control evidence from native execution results and protect that evidence from caller manipulation.

The pilot bearer credential authorizes evaluation, permit issuance, and permit consumption for its tenant; it does not implement endpoint-level roles. Keep the credential inside one controlled integration boundary. Production deployment requires separate proposer, issuer, and executor identities with least-privilege authorization.

## Pilot API Controls

The pilot API defaults to refusing startup without at least one tenant-mapped bearer key. It provides:

- constant-time API-key comparison
- tenant-scoped decision storage and retrieval
- idempotency conflict detection
- bounded body and batch sizes
- allowlisted CORS rather than wildcard browser access
- no-store and content-type response headers
- opaque request identifiers
- optional action-bound permit issuance and atomic single-use consumption

`--allow-unauthenticated` is intended only for local development. It must not be used on a network-accessible pilot deployment.

SQLite supports a controlled, single-instance pilot. It is not the target enterprise storage architecture. A multi-instance deployment requires an external transactional datastore, managed key rotation, centralized authorization, retention controls, backup testing, and operational monitoring.

Pilot reviews use pseudonymous reviewer identifiers and bounded optional comments. Do not place names, email addresses, credentials, source code, personal data, incident payloads, or other sensitive content in review fields. Review records are immutable; corrections should be handled under an approved pilot evidence procedure rather than by editing the audit database.

The pilot review console keeps its bearer key in JavaScript memory only. It does not persist the key in browser storage or cookies and refuses non-HTTPS remote API URLs. Configure an exact console origin in `SMERC_CORS_ORIGINS`; do not use wildcard CORS. A production console still requires managed identity, RBAC, session controls, monitoring, and an approved credential lifecycle.

## GitHub Actions Remote Mode

Remote evaluation reads the bearer credential only from `SMERC_API_KEY`. The integration requires HTTPS outside loopback testing, refuses cross-origin redirects, bounds response size, validates response structure, and reuses one idempotency key across transient retries.

Do not expose the pilot secret to untrusted fork workflows. Pin the action to a reviewed commit SHA, restrict workflow permissions, use action metadata rather than sensitive payloads, and approve report-artifact retention before a live pilot.

An unavailable remote service never produces a fabricated posture. Observe and recommend modes may report `UNAVAILABLE`; enforce mode always fails closed.

## Enforcement Warning

Do not use the reference thresholds for production blocking without threat modeling, calibration, accountable approval, override procedures, and an explicit fail-open/fail-closed decision.

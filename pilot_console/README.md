# SMERC Pilot Review Console

The console is a dependency-free browser interface for a controlled SMERC shadow-mode pilot. It loads the authenticated tenant review queue, displays replay evidence, records immutable reviewer verdicts, shows denominator-aware pilot metrics, and generates stored Decision Lifecycle Ledger evidence packages for CISO review.

## Local Run

Start the API with the console origin allowlisted:

```bash
export SMERC_API_KEYS="pilot-team=replace-with-a-long-random-secret"
export SMERC_CORS_ORIGINS="http://127.0.0.1:8790"
python api_server.py --host 127.0.0.1 --port 8788 --audit-db ./smerc_audit.sqlite3
```

In another terminal:

```bash
python -m http.server 8790 --bind 127.0.0.1 --directory pilot_console
```

Open `http://127.0.0.1:8790`, enter the API URL and bearer key, and connect.

## CISO Evidence Packages

The Stored DLL evidence package panel calls `POST /v1/pilot/evidence-packages` for an existing ledger-backed decision ID. The authenticated principal must include `audit.read`. Generated packages can be downloaded as JSON for machine review or Markdown for an executive/security review packet.

Example scoped development principal:

```bash
export SMERC_API_PRINCIPALS="pilot-team:pilot-console:decisions.read+reviews.read+reviews.write+metrics.read+audit.read=development-console-secret-2026-rotate"
```

## Security Boundary

- The bearer key is held only in JavaScript memory for the current tab.
- The console does not use local storage, session storage, cookies, analytics, or third-party assets.
- Remote API URLs must use HTTPS; HTTP is accepted only for loopback development.
- Server-provided values are rendered with text nodes rather than injected HTML.
- Use pseudonymous reviewer IDs and keep sensitive data out of comments.
- The console does not expose production enforcement controls.

This is a pilot operator interface, not a production identity or authorization plane. Enterprise deployment still requires managed identity, role-based authorization, centralized audit retention, monitoring, and an approved key-rotation process.

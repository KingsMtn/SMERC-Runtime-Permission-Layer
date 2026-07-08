# Contributing To SMERC

Thank you for considering a contribution. SMERC is early, and the most valuable contributions are the ones that make it easier to test, falsify, integrate, or explain.

## Contribution Principles

- Be concrete. Prefer examples, tests, scenarios, or reproducible findings.
- Preserve restraint. SMERC should not drift toward "allow by default" when evidence is incomplete.
- Avoid hype. Do not add claims of production validation, certification, compliance, or incident reduction without evidence.
- Keep authority server-side. SDKs should call SMERC; they should not silently make their own authorization decisions.
- Document limits. Every benchmark, integration, or enforcement path should state what it does not prove.

## Useful Contribution Types

### Scenario Packs

Add realistic action scenarios in `examples/`. Strong scenarios include:

- clear action description
- existing control context
- recoverability signals
- irreversible exposure rationale
- expected review questions

### Integrations

Useful integrations should place SMERC before execution, not after the side effect has already happened.

Good integration candidates:

- AI-agent tool dispatch
- GitHub Actions
- deployment gates
- internal API gateways
- ticketing and approval workflows
- cloud automation

### SDKs

SDKs should be small, inspectable, and dependency-light where possible. They should expose API responses rather than hiding SMERC posture, replay IDs, reason codes, or controls.

### Reports And Benchmarks

Reports should distinguish:

- synthetic or proxy evidence
- shadow-mode pilot evidence
- production evidence

Do not blur those categories.

## Local Validation

Run:

```bash
python -m unittest discover -s tests -v
node --check pilot_console/app.js
node --check pilot_console/model.mjs
node --check smerc_js_sdk/client.mjs
node --check smerc_js_sdk/index.mjs
node --test tests/js/*.test.mjs
```

Generate the proxy benchmark:

```bash
python -m reference_engine.proxy_evidence_benchmark \
  examples/proxy_incident_replay_scenarios.json \
  --json-output reports/proxy_incident_replay_benchmark.json \
  --markdown-output reports/Proxy_Incident_Replay_Benchmark.md
```

## Pull Request Checklist

- The change has tests when behavior changes.
- New public claims are backed by code, reports, or clearly labeled evidence.
- Documentation states limits and assumptions.
- No secrets, private customer data, or private legal strategy are included.
- Generated reports are reproducible from committed examples.

## Security Issues

Do not open public issues for sensitive vulnerabilities. Follow `SECURITY.md`.

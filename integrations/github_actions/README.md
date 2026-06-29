# SMERC GitHub Actions Integration

The integration can evaluate a proposed action with either:

- `local`: the bundled reference engine, with no network dependency
- `remote`: the authenticated SMERC pilot API, with tenant-scoped audit persistence

Both sources return the workflow-facing postures `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE` when evaluation succeeds.

## Modes

| Mode | Decision behavior | API outage behavior |
| --- | --- | --- |
| `observe` | Report only | Report `UNAVAILABLE` unless failure policy is `fail` |
| `recommend` | Surface posture and controls | Report `UNAVAILABLE` unless failure policy is `fail` |
| `enforce` | Fail when posture matches `fail-on` | Always fail closed |

Start every pilot in `observe` mode.

## Local Evaluation

```yaml
- name: Evaluate proposed agent action locally
  id: smerc
  uses: ./integrations/github_actions
  with:
    action-file: integrations/github_actions/sample_action_request.json
    source: local
    mode: observe
    output-file: smerc-decision.json
```

Local mode expects the action shape used by `reference_engine/agent_permission_layer.py`.

## Remote Evaluation

Store the API credential as the GitHub Actions secret `SMERC_API_KEY`. Store the non-secret service URL as the repository variable `SMERC_API_URL`.

```yaml
- name: Evaluate proposed agent action through SMERC API
  id: smerc
  uses: ./integrations/github_actions
  env:
    SMERC_API_KEY: ${{ secrets.SMERC_API_KEY }}
  with:
    action-file: examples/recoverability_single_action.json
    source: remote
    api-url: ${{ vars.SMERC_API_URL }}
    tenant: platform-team
    mode: observe
    api-failure-policy: report
    request-timeout: "10"
    max-retries: "1"
    output-file: smerc-decision.json
```

Remote mode expects the recoverability action shape documented in `docs/API_Deployment_Guide.md`.

For an external repository reference, pin a commit SHA during a pilot:

```yaml
uses: KingsMtn/SMERC-Runtime-Permission-Layer/integrations/github_actions@COMMIT_SHA
```

Do not use an unpinned branch reference for an enforcement workflow.

## Remote Safety Behavior

- API keys are read only from `SMERC_API_KEY`; there is no command-line or action input for the secret.
- Non-loopback remote endpoints require HTTPS.
- Cross-origin redirects are refused so authorization headers cannot be forwarded to another host.
- Transient `429`, `500`, `502`, `503`, and `504` responses can be retried up to three times.
- One idempotency key is reused across retries.
- API responses are limited to 1 MiB and validated before a posture is accepted.
- Remote errors produce an explicit `integration_status: unavailable`; they never fabricate an authorization posture.
- Enforce mode fails closed when the API cannot return a valid decision.

The default idempotency key combines the GitHub run, attempt, job, action ID, and request hash. A caller can override it with `SMERC_IDEMPOTENCY_KEY` when coordinating retries across jobs.

## Inputs

| Input | Default | Purpose |
| --- | --- | --- |
| `action-file` | required | Structured JSON action request |
| `source` | `local` | `local` or `remote` evaluation |
| `api-url` | empty | HTTPS SMERC service URL for remote mode |
| `tenant` | empty | Optional tenant assertion |
| `mode` | `observe` | `observe`, `recommend`, or `enforce` |
| `api-failure-policy` | `report` | `report` or `fail`; enforce ignores fail-open behavior |
| `request-timeout` | `10` | API timeout from 1 to 30 seconds |
| `max-retries` | `1` | Transient retries from 0 to 3 |
| `output-file` | `smerc-decision.json` | JSON evidence report path |
| `fail-on` | `DENY,FREEZE` | Enforced postures that fail the workflow |

## Outputs

- `posture`: a SMERC posture or `UNAVAILABLE`
- `risk-score`: local risk or remote irreversible-exposure score
- `replay-id`: decision replay identifier
- `integration-status`: `evaluated` or `unavailable`
- `source`: `local` or `remote`

The action also writes a JSON report and a GitHub step summary.

## Pilot Guidance

- Use metadata rather than source code, prompts, secrets, or customer payloads.
- Do not expose the API key to workflows triggered by untrusted forks.
- Use a GitHub environment with reviewers for protected pilot secrets when appropriate.
- Upload the decision report as a workflow artifact with a retention period approved by the security owner.
- Compare SMERC results against existing approvals before enabling enforcement.

See `remote_example_workflow.yml` for a complete shadow-mode workflow.

# GitHub Deployment Adapter

This adapter is the execution boundary for one SMERC-authorized deployment. It does not infer permission from a score. In `enforce` mode it requires an action-bound permit, asks SMERC to authenticate and reserve it, applies every permit-required control, signs the resulting control evidence, atomically consumes the reservation, and only then starts the declared command.

## Security Properties

- strict JSON plan with unknown-field rejection
- command argument arrays only; no shell command strings and `shell=False`
- relative working directory confined to `GITHUB_WORKSPACE`
- explicit environment-name allowlist
- required controls fail closed when absent or unsuccessful
- permit file removal before control application or execution
- terminate then kill escalation on timeout or cancellation
- declared rollback on configured failure classes
- report contains hashes, timing, status, and identifiers; it omits raw output and bearer values

Run contract validation without a permit:

```bash
python integrations/github_deployment/deployment_adapter.py \
  --action-file examples/action_language/production_canary_release.json \
  --plan-file examples/github_deployment/execution_plan.json \
  --sparta-route-file reports/signed_sparta_route_example.json \
  --mode validate
```

Enforcement additionally requires `SMERC_EXECUTOR_TOKEN`, a matching `SMERC_CONTROL_EVIDENCE_KEY`, `--api-url`, and `--permit-token-file`. Keep the permit in an ephemeral file with restrictive permissions. Never place it in an output, log, cache, or artifact.

`issue_permit.py` performs the preceding evaluation and issuance with separate `SMERC_PROPOSER_TOKEN` and `SMERC_ISSUER_TOKEN` credentials. It creates the permit file exclusively with restrictive permissions and prints only non-secret identifiers. The protected workflow in `examples/github_deployment/protected_deployment.yml` connects the two clients.

When `--sparta-route-file` is supplied, the adapter verifies in enforce mode that the route replay ID, source posture, executable state, and declared controls match the one-time permit. A mismatch blocks before permit consumption or deployment command execution. The resulting execution report includes `smerc.sparta-execution-evidence.v1` so reviewers can follow the chain from SMERC decision to SPARTa route to native execution evidence.

## Honest Boundary

This is a pilot adapter, not a sandbox. It does not confine filesystem or network access by the declared process. A successful control command proves that the configured command exited successfully, not that an independent system verified its claim. On Windows, cancellation guarantees termination of the directly managed process but does not yet guarantee termination of every descendant. Rollback is attempted and reported; it is not guaranteed to restore state. Production use still requires hardened runners, managed identity and signing, external transactional replay state, native control verification, observability, and incident procedures.

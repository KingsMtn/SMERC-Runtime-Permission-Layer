# GitHub Deployment Adapter Operations

## What This Adds

The GitHub gate evaluates a proposed action. The deployment adapter turns an eligible decision into a bounded execution lifecycle. This closes a practical product gap: SMERC can now demonstrate that permission, controls, one-time consumption, execution, cancellation, rollback, and audit reporting occur in one ordered path.

It does not make the reference build production-certified. Use it in a controlled design-partner environment before considering enforcement.

## Protected Job Design

Use `examples/github_deployment/protected_deployment.yml` as the reviewable starting point. Configure the GitHub `production` environment with required reviewers, prevent self-review where available, restrict deployment branches or tags, and store scoped credentials as environment secrets. Use workflow concurrency so two production deployments do not proceed in parallel.

The job uses three separate SMERC authorities:

| Credential | Minimum scope | Purpose |
|---|---|---|
| `SMERC_PROPOSER_TOKEN` | `actions.evaluate` | Submit the exact action. |
| `SMERC_ISSUER_TOKEN` | `permits.issue` | Issue a short-lived capability for an eligible decision. |
| `SMERC_EXECUTOR_TOKEN` | `permits.consume` | Consume that capability at the execution boundary. |

`SMERC_CONTROL_EVIDENCE_KEY` belongs only to the configured adapter identity and audience. Do not expose issuer, executor, or evidence credentials to the proposing agent.

## Review Procedure

1. Replace the simulation commands in `examples/github_deployment/execution_plan.json` with reviewed argument arrays and rollback procedures.
2. Ensure each control that a policy may require has a native implementation in `controls`.
3. Validate the plan in CI with `mode: validate`.
4. When available, pass the SPARTa route artifact with `--sparta-route-file`.
5. Confirm the production environment approval and branch rules.
6. Confirm permit TTL is long enough for controls but short enough to limit replay opportunity.
7. Run initial trials against a non-production target.
8. Compare command outcome, rollback result, reviewer verdict, and external system state.
9. Advance from observe to recommend to limited enforcement only under the admitted evidence ceiling.

## SPARTa Route Binding

The adapter can bind an execution report to a SPARTa route report before command execution.

When `--sparta-route-file` is supplied in enforce mode, the adapter verifies:

- the route report uses the `smerc.sparta-route.v1` contract
- the route replay ID matches the one-time permit replay ID
- the route source posture matches the permit posture
- the route is executable
- every non-internal permit-required control is declared by the SPARTa route

If any check fails, the adapter returns `sparta_binding_mismatch` and stops before control execution, permit consumption, or deployment command execution.

Successful execution reports include a `sparta` section with:

- `smerc.sparta-execution-evidence.v1`
- route ID
- route report digest
- replay ID
- posture
- route state
- binding checks

This makes the GitHub pilot path easier to review as one chain: SMERC decision, SPARTa route, one-time permit, native control evidence, execution report, rollback result, and later Decision Lifecycle Ledger evidence.

## Failure Behavior

- Invalid action or plan: `BLOCKED`; no permit consumption or command.
- Permit file cannot be removed: `BLOCKED`; no control or command.
- Invalid or competing preparation: `BLOCKED`; no control, permit consumption, or command.
- Unsupported or unsuccessful required control: `BLOCKED`; the permit remains reserved and cannot trigger another execution.
- Invalid, expired, replayed, mismatched, or API-rejected permit: `BLOCKED`; no command.
- Command start failure or non-zero exit: `FAILED`; configured rollback may run.
- Deadline reached: terminate, escalate to kill, report `TIMED_OUT`, then attempt configured rollback.
- Cancellation signal: terminate, escalate to kill, report `CANCELLED`, then attempt configured rollback.

Do not treat rollback `succeeded` as proof of restored business state. Verify restoration through the target platform.

## Evidence To Collect

- permit issue, expiry, rejection, and replay rates
- required-control application and failure rates
- authorization-to-start latency
- cancellation latency and descendant-process behavior
- rollback attempt, command success, and independently verified restoration rates
- SPARTa route binding failures and missing required controls
- false release, false constraint, override, and reviewer agreement rates
- discrepancies between adapter reports and target-platform audit logs

## Current Limits

- Same-job permit handoff is protected by an ephemeral restricted file and a server-side execution reservation, not an isolated capability broker.
- Control commands and the deployment run on the same runner trust boundary.
- SQLite replay prevention is suitable only for a single-instance pilot.
- HMAC credentials are not managed KMS/HSM identities or public nonrepudiation.
- The adapter does not restrict process network or filesystem access.
- Windows terminates the directly managed process; descendant termination requires further hardening.
- GitHub environment protections are repository settings and cannot be guaranteed by this workflow file alone.
- SPARTa route binding verifies consistency of supplied artifacts; it does not prove that the supplied route was independently approved unless the route signature, key custody, and reviewer workflow are separately controlled.

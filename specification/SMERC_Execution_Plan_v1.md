# SMERC Execution Plan v1

## Purpose

`smerc.execution-plan.v1` declares exactly how one authorized action will be executed, which permit-required controls the adapter can apply, and how rollback will be attempted. It is an execution contract, not an authorization decision. A valid plan cannot execute in enforcement mode without a matching, successfully consumed `smerc.permit.v1` capability.

## Required Fields

| Field | Meaning |
|---|---|
| `version` | Fixed value `smerc.execution-plan.v1`. |
| `execution_id` | Bounded identifier used in reports and evidence references. |
| `audience` | Executor audience that must exactly match the permit. |
| `working_directory` | Relative directory resolved inside the workspace. |
| `command` | Non-empty argument array. It is never interpreted as a shell string. |
| `timeout_seconds` | Hard execution deadline from 1 through 3,600 seconds. |
| `cancel_grace_seconds` | Grace period before kill escalation, from 1 through 60 seconds. |
| `environment_allowlist` | Names that may be copied from the adapter environment. |
| `controls` | Map from control ID to a native command, timeout, and mechanism label. |
| `rollback` | A declared rollback command and the failure classes that trigger it, or `null`. |

Unknown fields are rejected. `retain_cancel_handle` is implemented internally and cannot be replaced by a caller command.

## Execution Invariants

1. Parse and validate the exact action and plan.
2. Read the permit from a bounded file and remove that file. Failure to remove it blocks execution.
3. Ask the SMERC API to authenticate the permit and atomically reserve it for this executor principal and execution ID.
4. Confirm action hash, tenant, audience, and adapter signer bindings from the verified response.
5. Apply every required control. Missing, failed, timed-out, or cancelled controls block execution.
6. Sign an action- and permit-bound control-evidence receipt.
7. Ask the SMERC API to verify the preparation and evidence, then atomically consume the permit.
8. Start the command only after the API returns `valid: true`.
9. On configured failure, timeout, or cancellation, attempt rollback and report its independent result.

## Process And Report Semantics

Process statuses are `succeeded`, `failed`, `start_failed`, `timed_out`, and `cancelled`. Top-level outcomes are `VALIDATED`, `BLOCKED`, `SUCCEEDED`, `FAILED`, `TIMED_OUT`, and `CANCELLED`.

Raw process output is consumed into `output_sha256` and `output_bytes`, then discarded. The report records hashes, timestamps, exit status, permit identifiers, control-evidence attribution, rollback status, and names of allowed environment values. It never records the values of environment variables, bearer tokens, signing keys, or raw command output.

## Non-Claims

The adapter is not a process sandbox, network policy, filesystem policy, independent control verifier, or guaranteed state restoration system. Exit code zero is evidence that the declared command completed, not proof that its external claim is true. These distinctions must remain visible in pilot interpretation.

# One-Job Runner Lifecycle v1

SMERC's one-job lifecycle is a fail-closed orchestration contract for an isolated runner. It does not provision AWS infrastructure itself.

The lifecycle requires:

- an unexpired `ACTIVE` execution envelope
- exactly one executor invocation with no automatic retry
- an exact match between the admitted tool and the executed tool
- cleanup after success or failure
- independent cleanup claims for runner destruction, credential revocation, and ephemeral-ref deletion
- portable evidence that distinguishes requested cleanup from verified cleanup

An execution is not reported as clean when any cleanup claim is missing or false. Executor failure still triggers cleanup, and the resulting failure receipt remains available for audit.

## AWS boundary

For an AWS pilot, the external provisioner should create one short-lived workload identity and one isolated compute boundary, invoke this lifecycle once, and destroy both after the operation. The provisioner must return observed cleanup facts; configuration intent alone is not cleanup evidence.

This implementation does not claim that an AWS runner was created, that IAM credentials were revoked, or that hardware isolation was provided. Those become supported claims only after a live provisioner supplies verifiable receipts.

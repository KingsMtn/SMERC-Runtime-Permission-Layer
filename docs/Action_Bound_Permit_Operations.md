# Action-Bound Permit Operations

## Configuration

Permit issuance is disabled unless a signing tenant has API principals and a permit key configured:

```powershell
$env:SMERC_API_PRINCIPALS="alpha:agent-proposer:actions.evaluate=alpha-proposer-local-secret-012345,alpha:permit-issuer:permits.issue=alpha-issuer-local-secret-01234567,alpha:deployment-executor:permits.consume=alpha-executor-local-secret-012345"
$env:SMERC_PERMIT_KEYS="alpha=alpha-permit-2026-01:alpha-local-permit-signing-secret-0123456789"
$env:SMERC_CONTROL_EVIDENCE_KEYS="alpha:deployment-executor=deployment-adapter:alpha-control-evidence-2026-01:alpha-local-control-evidence-secret-0123456789"
$env:SMERC_POLICY_DIR="examples/policies"
python api_server.py --host 127.0.0.1 --port 8788 --audit-db smerc_audit.sqlite3
```

These literal values are development-only examples. Do not reuse or commit real secrets. The signing tenant must also have an API credential and an effective `ENFORCE` policy whose evidence ceiling permits enforcement. The public example policies remain non-production references.

## Flow

1. Submit a strict action envelope to `POST /v1/language/evaluate`.
2. Retain the returned replay ID.
3. Request a permit from `POST /v1/permits/issue` with the same action, replay ID, executor audience, and a lifetime from 1 through 300 seconds.
4. Send the token to the named executor over a protected channel.
5. Immediately before the side effect, a configured adapter derives native control results and signs a short-lived control-evidence receipt.
6. The executor sends the exact action, permit token, audience, and receipt token to `POST /v1/permits/consume`.
7. SMERC verifies both bindings and atomically consumes the permit.
8. Execute only after a `200` response with `valid: true`.

The issuance body has four fields: the stored `replay_id`, the complete original `action` envelope, the executor `audience`, and `ttl_seconds`. Configured adapters consume with the exact `permit_token`, complete original `action`, same `audience`, and `control_evidence_token`. Unconfigured audiences may send `enforced_controls`, and the result is explicitly labeled `legacy_caller_assertion`. Partial action envelopes are rejected.

Tokens are bearer capabilities. Do not print them in workflow logs, commit them, place them in artifacts, or expose them as GitHub Action outputs.

Use separate scoped principals for `actions.evaluate`, `permits.issue`, and `permits.consume`. Legacy tenant keys still have all API permissions and should not be distributed to agents or untrusted workflows.

## Expected Failure Codes

| Code | Meaning |
|---|---|
| `posture_not_permittable` | The decision requires pause, denial, or human escalation. |
| `policy_not_enforceable` | The decision policy is not in `ENFORCE` mode. |
| `policy_superseded` | The active policy changed after the decision or permit. |
| `action_mismatch` | The proposed action differs from the authorized action. |
| `audience_mismatch` | A different executor attempted consumption. |
| `required_controls_missing` | The adapter did not declare every constrained control. |
| `control_evidence_required` | A configured adapter attempted the legacy assertion path. |
| `control_evidence_permit_mismatch` | The receipt belongs to another permit. |
| `permit_expired` | The bounded execution window closed. |
| `permit_already_issued` | That decision already produced a permit for the audience. |
| `permit_not_issued` | The token does not match the issuance registry. |
| `permit_already_consumed` | Replay prevention rejected a second use. |

## Pilot Boundary

This implementation is suitable for controlled, single-instance technical validation. It is not a production capability service. Signed receipts authenticate the configured adapter key but do not independently prove that native controls operated. The pilot should measure permit issuance rate, signed-receipt coverage, consumption success, expiry, replay rejection, control-application failures, and added authorization latency. See `Control_Evidence_Operations.md`.

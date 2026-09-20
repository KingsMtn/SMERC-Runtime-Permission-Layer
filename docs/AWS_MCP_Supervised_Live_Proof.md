# AWS MCP Supervised Live Proof

On September 20, 2026, SMERC evaluated an exact, read-only managed AWS MCP
`list_regions` action before an authenticated operator invoked the call. SMERC
returned `ALLOW` with `should_forward: true`, no required-evidence failures,
and the canonical reason `RECOVERABILITY_ACCEPTABLE`. The AWS MCP call then
succeeded and returned 37 Regions.

The sanitized evidence record is
`examples/aws_mcp_supervised_live_proof.json`. It stores no credentials, account
resources, or raw AWS response. The summary digest covers the region count and
the first and last Region identifiers in the observed ordered result.

## What this proves

- SMERC can evaluate the exact AWS MCP server, tool, and arguments before a call.
- The current policy allows this zero-side-effect, zero-estimated-cost read action.
- The authenticated managed AWS MCP session can execute that action successfully.
- The public artifact records the limits of the evidence alongside the result.

## What this does not prove

This was a supervised two-step proof. The managed AWS MCP endpoint was not yet
technically forced through SMERC's executor process. The record is not production
evidence, independent AWS attestation, CloudTrail correlation, or proof that a
caller with separate AWS access cannot bypass SMERC.

The next integration milestone is a trusted managed-transport executor that
accepts only the bound SMERC action, returns the result through the adapter, and
correlates the receipt with native AWS audit evidence.

# AWS Authorization-Afterlife Scenario Runner

The runner turns the merged consequence-time contracts into one reproducible reviewer path using sanitized AWS evidence already present in this repository.

It produces three outcomes:

1. A supervised read-only AWS MCP action with current authority reaches `SETTLE`.
2. A modeled authority-epoch change and acquired IAM capability expansion reaches `QUARANTINE`.
3. A controlled reversible AWS mutation combined with modeled revocation after a partial effect reaches `COMPENSATE`.

Each scenario declares one of four evidence classes: `PUBLIC_EXAMPLE`, `CONTROLLED_AWS_PROOF`, `SYNTHETIC`, or `CUSTOMER_METADATA`. Synthetic additions are stated explicitly. Controlled proof facts retain the source file digest and original boundary language.

Run:

```text
python -m reference_engine.authorization_afterlife_runner
```

Outputs:

- `reports/aws_authorization_afterlife/aws_authorization_afterlife.json`
- `reports/aws_authorization_afterlife/AWS_Authorization_Afterlife.md`

The runner uses no AWS credentials, account IDs, ARNs, raw responses, customer records, live API calls, or production execution authority. It does not convert controlled tests into customer validation or AWS attestation.

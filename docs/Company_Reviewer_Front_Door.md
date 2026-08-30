# Company Reviewer Front Door

## Purpose

This page is the shortest company-review path for SMERC.

It is for a security, platform, AI governance, cloud, or financial-services reviewer who wants to understand whether SMERC is worth testing without scheduling a sales call, sharing secrets, or connecting production systems.

## What To Do First

Pick one path:

| Reviewer | Start with | Command or link |
| --- | --- | --- |
| General AI-agent or automation reviewer | General customer evaluation | `python -m reference_engine.customer_evaluation examples/customer_eval_actions.json --pretty` |
| Cloud, SRE, platform, or infrastructure reviewer | Cloud-admin customer evaluation | `python -m reference_engine.customer_evaluation examples/cloud_admin_customer_eval_actions.json --pretty` |
| Cloud, SRE, platform, or infrastructure reviewer who wants the strongest proof artifact | Cloud Admin Proof Pack | `python -m reference_engine.cloud_admin_proof_pack --pretty` |
| Financial-services, treasury, stablecoin, payment, or tokenized-finance reviewer | Financial Runtime customer evaluation, internally called SMERC-F | `python -m reference_engine.customer_evaluation examples/smerc_f_customer_eval_actions.json --pretty` |
| Reviewer who wants to see the full assembled loop | Complete lifecycle proof | `python -m reference_engine.complete_lifecycle_proof` |

## What A Company Provides

For a real review, replace the sample file with 5 to 25 safe metadata-only actions from one workflow family.

Good workflow families:

- AI-assisted code or deployment actions
- MCP tool calls
- cloud administration changes
- security-response automation
- support or customer operations automation
- payment, refund, treasury, stablecoin, tokenized-collateral, wallet-policy, or transaction-limit actions

Use only metadata:

- action description
- actor or agent role
- tool family
- environment
- requested scope
- reversibility
- containment strength
- rollback latency
- evidence validity
- anomaly pressure
- impact scope
- cancel reliability
- authorization confidence
- hard-gate results such as identity, attestation, least privilege, typed contract, and object shape
- current reviewer or control outcome, if known

Do not include secrets, API keys, tokens, passwords, wallet keys, private keys, source code, raw customer records, raw regulated transaction payloads, AML case files, sanctions-screening data, production logs, or private prompts.

## What SMERC Returns

The output includes:

- runtime admission result
- SMERC posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`
- reason codes
- recoverability scores
- SPARTa execution route
- controls to apply before execution
- Decision Lifecycle Ledger evidence
- autonomy-budget impact
- pilot-fit recommendation

## What The Result Means

Useful result:

- SMERC finds at least one recoverability issue current controls do not explicitly capture.
- SMERC identifies a constrained path that is better than simply allowing or blocking.
- SMERC hard-stops at least one action when evidence is missing or untrusted.
- Reviewers can label whether the posture is useful, too strict, too permissive, or unclear.

For cloud, SRE, platform, DevOps, CI/CD, or AI-agent infrastructure teams, `docs/Cloud_Admin_Proof_Pack.md` is the strongest proof path. It expands the cloud-admin sample into 24 scenarios and adds cloud reason codes plus Work / Result / Impact evidence.

Weak result:

- Reviewers see no useful difference from existing IAM, OPA, CI/CD approval, ticketing, SIEM, GRC, AI gateway, or human-review controls.
- The workflow cannot be represented safely as metadata.
- The team cannot name an accountable workflow owner.
- The review burden outweighs the value of the recoverability signal.

## Where SMERC-F Fits

Financial Runtime is a domain profile of SMERC, internally called SMERC-F.

Use it when the reviewer cares about automated financial actions where reversibility, rollback, containment, and authority matter before execution:

- payment retries
- refunds
- treasury rebalancing
- stablecoin liquidity movement
- tokenized collateral movement
- wallet-policy changes
- transaction-limit changes
- reserve-status publication

SMERC-F is not AML compliance, sanctions screening, fraud detection, custody, settlement, trading, payment execution, legal advice, or production financial-control certification.

The first financial review should remain metadata-only and shadow-mode. Existing financial controls remain authoritative.

For public-data-shaped financial replay, read `docs/SMERC_F_Financial_Public_Data_Replay.md` and `docs/SMERC_F_Financial_Reason_Codes.md`. Those reports show whether the driver was low settlement reversibility, weak evidence, liquidity fragility, redemption pressure, collateral exposure, counterparty concentration, or automation velocity.

## Work / Result / Impact

Work: run safe metadata-only action examples through hard gates, recoverability scoring, SPARTa routing, ledger evidence, and pilot-fit reporting.

Result: a reviewer gets a concrete report showing where SMERC agrees with, constrains, freezes, denies, or escalates actions compared with current judgment.

Impact: the company can decide whether recoverability-before-execution is useful before granting SMERC production access, sharing sensitive data, or discussing enforcement.

## Boundary

This front door is not product-market validation. It is not production certification. It is not compliance attestation. It is not proof of incident reduction.

It is a low-risk way to answer the first serious question:

> Does recoverability-aware runtime permissioning change reviewer judgment enough to justify a bounded shadow-mode pilot?

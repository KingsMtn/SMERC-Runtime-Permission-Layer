# OpenSSF Feedback Alignment

## Purpose

This note records how external OpenSSF issue #50 feedback changed the SMERC technical framing.

The key correction is simple:

> Recoverability scoring should not be allowed to rescue a bad tool contract, bad authority boundary, missing attestation, or unexpected object shape.

SMERC should evaluate recoverability only after basic execution facts are mechanically admitted.

## What Changed

Before the feedback, SMERC already emphasized recoverability-aware runtime posture. The risk was that reviewers could read the system as:

```text
agent proposes action -> SMERC scores recoverability -> route action
```

That framing was incomplete.

The stronger runtime order is:

```text
identity and scoped workload session
-> typed tool/action contract
-> attested runtime evidence
-> least-privilege boundary
-> expected object-shape check
-> SMERC recoverability posture
-> execution routing and controls
-> Decision Lifecycle Ledger evidence
```

## Technical Interpretation

SMERC now treats the Ref-gate pattern as a hard pre-scoring admission layer for high-impact actions.

The current reference checks are:

- `typed_contract_valid`
- `attestation_valid`
- `least_privilege_confirmed`
- `object_shape_expected`

If one of those checks fails, the action is capped or rejected before recoverability can justify normal execution.

That means:

- a reversible action can still be denied if authority is wrong
- a low-risk action can still be held if the object shape is unexpected
- a confident agent can still be blocked if attestation is missing
- a recoverable action can still require review when least privilege is not proven

## Where This Exists In The Repository

Implemented or demonstrated artifacts:

- `reference_engine.ref_gated_runtime_proof`
- `reference_engine.customer_evaluation`
- `reference_engine.mcp_governance_gateway`
- `docs/Ref_Gated_Runtime_Proof_Loop.md`
- `docs/SMERC_And_The_Ref_Pattern.md`
- `docs/Runtime_Evidence_Trust_Gate.md`
- `examples/customer_eval_actions.json`
- `examples/cloud_admin_customer_eval_actions.json`
- `examples/smerc_f_customer_eval_actions.json`

## Why This Matters Commercially

This makes SMERC easier for serious reviewers to evaluate.

It avoids the weak claim that a score can make any action safe. Instead, SMERC becomes a runtime checkpoint that asks two separate questions:

1. Are the execution facts trusted enough to score?
2. If trusted, is the action recoverable enough to proceed, constrain, freeze, deny, or escalate?

That separation matters to CISOs, platform teams, and AI governance teams because it fits existing security architecture better than a standalone "AI firewall" claim.

## What This Does Not Claim

This does not prove:

- production MCP security
- prompt-injection defense
- cloud-provider certification
- compliance certification
- reduction in customer incidents
- legal or regulatory sufficiency
- complete type safety for all endpoints

It proves a clearer runtime design boundary in the public reference implementation: hard mechanical evidence gates first, recoverability scoring second, route and audit evidence third.

## Recommended Reviewer Question

The next useful external review question is:

> Are typed endpoint contracts, state-transition evidence, and pre-execution object-shape checks useful security guidance for AI-agent and MCP tool calls before recoverability scoring is added?

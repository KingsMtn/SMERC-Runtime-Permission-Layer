# IP Asset Map

This document is a business and technical map, not legal advice. Patent strategy and filing language must be reviewed by qualified intellectual property counsel.

## Strongest Candidate Mechanisms

| Mechanism | Why it matters | Current artifact |
| --- | --- | --- |
| Recoverability-weighted authorization | Scores whether an action can be undone, contained, delayed, or rolled back before allowing execution. | `reference_engine/recoverability_engine.py`, decision reports, pilot artifacts |
| Runtime Evidence Trust Gate | Separates trusted runtime metadata from agent-provided descriptions before scoring. | `docs/Runtime_Evidence_Trust_Gate.md` |
| SPARTa execution routing | Converts posture into execution behavior, controls, evidence, and adapter interpretation. | `docs/SPARTa_Router_Operations.md`, route reports |
| Decision Lifecycle Ledger | Preserves request, evidence, evaluation, override, execution, outcome, and reviewed learning record. | `docs/Decision_Lifecycle_Ledger.md` |
| Autonomy budgeting | Meters current autonomy by action count, scope, risk spend, ref-gate failures, and held/blocked attempts. | `reference_engine/autonomy_budget.py` |
| Earned autonomy | Assigns autonomy tier from historical reviewer agreement, rollback evidence, incidents, and scope discipline. | `reference_engine/earned_autonomy.py` |
| Right to continue | Evaluates authority provenance, intent integrity, consequence horizon, and collective autonomy during operation. | `reference_engine/autonomy_continuance.py` |
| MCP tool-call governance bridge | Applies recoverability and autonomy checks to tool-call sessions before forwarding or blocking. | `docs/MCP_Governance_Gateway.md` |
| SMERC-F financial-action profile | Applies the same mechanism to metadata-only automated financial-action review. | `docs/SMERC_F_Metadata_Intake_Contract.md` |

## Weak Or Broad Claims To Avoid

Avoid claiming ownership of:

- AI governance generally
- authorization systems generally
- policy engines generally
- human review generally
- audit logs generally
- fraud detection
- AML compliance
- model safety
- MCP itself
- GitHub Actions governance generally

Those areas have extensive prior art and strong obviousness risk.

## Better Claim Direction

The strongest technical story is the combination:

1. trusted metadata admission,
2. recoverability-weighted runtime posture,
3. route-to-control mapping,
4. lifecycle evidence preservation,
5. autonomy adjustment over time.

The narrower question:

> Can a runtime permission system dynamically constrain or requalify autonomous action based on recoverability, evidence provenance, intent integrity, consequence horizon, and historical earned autonomy?

That is more defensible than broad AI governance language.

## Public Disclosure Risk

The repository is public. Public disclosure can affect patent timelines and foreign rights. If patent protection is a priority, counsel should review immediately.

Do not add speculative legal claims to public pages. Keep public language product-oriented and evidence-bound.

## What To Document For Counsel

- exact input signals
- scoring formulas
- state transitions
- route-control mappings
- ledger schema
- autonomy budget thresholds
- earned autonomy tier transitions
- right-to-continue transition conditions
- MCP/GitHub/cloud/financial examples
- differences from OPA, IAM, approval workflows, AI gateways, and audit logs

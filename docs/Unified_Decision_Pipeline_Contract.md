# Unified Decision Pipeline Contract

The contract composes SMERC's distinct permission layers without collapsing them into one score:

1. Hard admission gates validate identity, delegation, current authority, recovery capability, and the non-secret evidence boundary.
2. The mathematical recoverability engine assigns a posture only after hard gates pass.
3. Execution routing turns that posture into enforceable controls.
4. Consequence-time reconciliation checks continuing authority and partial effects immediately before commitment.
5. Settlement either commits, quarantines, compensates, or denies.

A favorable mathematical score cannot override a failed hard gate. Likewise, initial execution eligibility cannot override later revocation, authority drift, incomplete settlement evidence, or compensation obligations.

This contract is a deterministic reference composition. It does not prove adapter enforcement, upstream evidence truth, customer production safety, or universal mediation.

# Consequence Reservation and Settlement

## Purpose

Delegated Continuance determines whether one agent still has authority to take its next action. Consequence Reservation and Settlement prevents many individually authorized agents, retries, or delayed tasks from collectively exceeding a shared limit.

Before execution, an agent atomically reserves cost, scope, and mutation capacity from a durable SQLite ledger. After execution, observed postconditions settle that reservation.

## Settlement States

- `RELEASED`: no consequence occurred; all reserved capacity is released.
- `CONSUMED`: the expected consequence occurred; observed capacity remains consumed.
- `RECOVERED`: cleanup is independently marked verified; scope and mutation exposure are released, but actual cost remains consumed.
- `UNSETTLED`: the outcome or cleanup cannot be proven; the original reservation remains held.
- `ESCALATED`: observed consequences exceeded expectations; the larger of reserved and observed exposure remains held.

## Safety Properties

- `BEGIN IMMEDIATE` serializes competing reservations so agents cannot double-spend the same capacity.
- A stable operation key binds retries and replacement task IDs to the original reservation.
- Reusing an operation key with changed request or contract evidence fails closed.
- Tenant and intent digests must match the signed Delegated Continuance Contract.
- An expired contract cannot reserve capacity, and the narrower child cost and scope limits remain authoritative.
- Recovery cannot be claimed without verified cleanup evidence.
- Successful rollback does not refund actual cloud spend.
- Partial cleanup remains unsettled and continues holding capacity.

## Proof Cases

The tests cover concurrent requests for the final budget capacity, task-ID retry laundering, operation-key rebinding, recovered mutations, partial cleanup, false recovery claims, and consequences exceeding the original reservation.

## Boundary

This reference ledger is not a distributed consensus system, cloud billing statement, production key store, or independently attested postcondition service. A multi-region production implementation would require transactional coordination or a strongly consistent reservation service, authenticated observation sources, retention policy, reconciliation, disaster recovery, and operator-defined consequence dimensions.

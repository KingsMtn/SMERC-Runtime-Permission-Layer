# SMERC Recovery Authority Gate Report

Generated: `2026-08-29T14:56:18+00:00`

## Summary

- Case: `RAG-001`
- Paused posture: `FREEZE`
- Unlock actor: `security-reviewer-primary`
- Unlock decision: `UNLOCK`
- Recovery path: `RECOVERY_PATH_READY`
- Unlock evidence: `UNLOCK_EVIDENCE_SUFFICIENT`

## Drivers

- `none`

## Required Next Step

Issue a short-lived action-bound permit, append DLL evidence, and continue with post-unlock monitoring.

## Work / Result / Impact

Work: evaluate whether a paused SMERC decision can be reopened by a trusted authority path.

Result: `UNLOCK`.

Impact: the same agent or workflow that caused a risky pause cannot simply unlock itself. Continuation requires verified authority, fresh recovery evidence, a bounded route, an action-bound permit, and ledger evidence.

## Plain English Summary

The recovery authority state is UNLOCK for paused posture FREEZE. The unlock actor is UNLOCK_ACTOR_VALID, evidence is UNLOCK_EVIDENCE_SUFFICIENT, and recovery path is RECOVERY_PATH_READY.

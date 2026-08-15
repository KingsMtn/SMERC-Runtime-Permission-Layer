# SMERC Action Language v1

## Purpose

SMERC Action Language is a versioned contract for asking whether an automated action may proceed and for describing the controls required before its posture can change. It makes an action replayable across agents, tools, reviewers, and enforcement points.

SMERC is called a Macro Language Model because its vocabulary governs macro-level action rather than generating micro-level prose. It does not replace an LLM, agent, IAM system, or policy engine. It carries an action proposal from those systems into a recoverability-aware permission decision.

## Contracts

An `smerc.action.v1` envelope contains six required sections:

1. `language_version`: exact contract version.
2. `action`: identity, actor, tool, target, and authority basis.
3. `signals`: risk, evidence, anomaly, and impact measurements.
4. `recoverability`: reversibility, containment, rollback, and cancellation evidence.
5. `effects`: external and sensitive-data side effects.
6. `context`: bounded JSON metadata used for replay.

The reference schema is `schemas/smerc-action-language-v1.schema.json`. Unknown contract fields are rejected by the reference compiler so misspellings cannot silently alter governance.

## Compilation

`reference_engine/action_language.py` validates and compiles the envelope into the existing recoverability engine input. Compilation is deterministic and preserves the target, authority basis, rollback method, language version, and SHA-256 action hash in replay context.

Canonicalization uses sorted JSON object keys, compact separators, ASCII escaping, and SHA-256. The hash supports equality and audit comparison; it is not a digital signature or proof of who submitted the action.

## Decision Language

An `smerc.decision.v1` response preserves the existing posture, enforcement state, scores, reason codes, controls, summary, and replay record. It adds:

- a deterministic action hash
- human-readable structured reason terms
- human-readable structured control terms
- an explicit posture transition contract

The five postures are `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, and `ESCALATE`.

## Transition Semantics

| Current posture | Eligible next posture | Requirement |
| --- | --- | --- |
| `ALLOW` | `ALLOW` | Maintain replay and cancellation controls. |
| `THROTTLE` | `ALLOW` | Satisfy generated scope, preview, rollback, rate, or checkpoint conditions. |
| `FREEZE` | `THROTTLE` | Restore evidence and recovery state before constrained execution. |
| `DENY` | None automatically | Submit a materially new request with a different action hash. |
| `ESCALATE` | `THROTTLE` | Assign an accountable reviewer and record explicit approval and rationale. |

An eligible target is not an automatic promotion. The caller must supply new evidence and request a fresh evaluation. SMERC therefore keeps restraint as the default under uncertainty.

## API

Submit a language envelope to authenticated endpoint `POST /v1/language/evaluate`. The endpoint validates, compiles, evaluates, stores, and returns the decision. Idempotency keys are tenant-scoped and bound to both endpoint and request body.

## Limits

- Scores are normalized numbers from `0.0` through `1.0`.
- Context is limited to 16,384 bytes of canonical JSON.
- The current terms and thresholds are a reference policy requiring design-partner calibration.
- The language describes governance intent; enforcement adapters must implement each returned control faithfully.

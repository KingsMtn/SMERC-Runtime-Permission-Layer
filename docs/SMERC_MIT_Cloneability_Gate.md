# SMERC MIT Cloneability Gate

Status: **long-build gate not met**

This assessment asks whether a capable company can start from the final
MIT-licensed SMERC revision, use public information, and independently recreate
the commercially important outcome. It does not treat repository size, commit
count, vocabulary, or an implementation lead as a moat.

This is an engineering and product assessment, not legal advice.

## License boundary

- Final MIT revision: `07b1fee27b573fc2affb14a15fedb50a060d0bef`
- Final MIT revision date: 2026-09-06
- Relicensing commit: `c2f53f7645e50e1982b07c5c927bc64e15d35fef`
- Comparison target: `6a59c3b131bd999e62b8fa6505e385625cf4320a`
  (main after PR #88)

The old license permits recipients of that revision to use, modify, publish,
distribute, sublicense, and sell it subject to its notice requirement. The
current license can restrict copying of later source, but it cannot by itself
make publicly described behavior expensive to reconstruct.

## Measured exposure

| Measure | Final MIT revision | Post-PR #88 main |
| --- | ---: | ---: |
| Repository files | 948 | 1,333 |
| Test-related files | 163 | 225 |
| Files mentioning reversibility | 380 | 548 |
| Files mentioning rollback | 419 | 652 |
| Files mentioning recovery | 502 | 745 |
| Files mentioning evidence | 802 | 1,162 |
| Files mentioning permits | 166 | 204 |
| Files mentioning attestation | 180 | 300 |
| Files mentioning continuance | 22 | 30 |
| Files mentioning settlement | 112 | 116 |
| Files mentioning consequence | 120 | 173 |
| Files mentioning MCP | 199 | 346 |
| Files mentioning replay | 485 | 632 |
| Files mentioning outcomes | 308 | 400 |

The post-MIT history adds 385 net files and changes 445 files, with 204,460
added lines and 329 deleted lines. Those numbers demonstrate continued work,
not defensibility. Documentation, generated evidence, examples, and tests make
raw line growth particularly unsuitable as a moat measure.

The MIT revision already disclosed the central vocabulary and substantial
implementation surface for reversibility, rollback, recovery, evidence,
permits, attestation, continuance, settlement, consequences, replay, and
outcome evaluation. A clean-room competitor would not start from zero.

## Initial gate score

Each category is scored from 0 to 5. A long build requires at least 27/35 and
no score below 3.

| Category | Current score | Reason |
| --- | ---: | --- |
| MIT reconstruction difficulty | 2 | The licensed baseline exposes most foundational concepts and a large tested implementation. |
| Competitive uniqueness | 2 | cMCP, ACLE-MCP, Salus, AgentAction, and cloud policy systems cover substantial portions. |
| Technical necessity | 3 | The authorization-to-execution and recovery-evidence gaps are real, but buyer urgency is not yet demonstrated. |
| Enforcement strength | 2 | Current proofs are principally software enforcement without a hardware-rooted production boundary. |
| Proprietary compounding asset | 1 | No private deployment corpus, customer policy network, or unique hardware integration compounds with use yet. |
| Customer urgency | 1 | Public interest and architectural feedback are not customer commitments. |
| Proof quality | 2 | Tests and AWS proofs are useful, but the decisive comparative proof remains incomplete. |
| **Total** | **13/35** | **Do not authorize a long build.** |

## Candidate that may earn continuation

The remaining candidate is a compound guarantee rather than any individual
feature:

> Release action-bound authority from a measured execution environment only
> after fresh recovery evidence and collective-consequence evaluation; preserve
> the bound through controlled delegation; and cryptographically settle the
> observed outcome or rollback against the original decision.

Hardware attestation, short-lived capabilities, runtime authorization,
rollback controls, signed receipts, and outcome logs are not independently
unique. The candidate succeeds only if their composition prevents important
failures that adjacent systems do not prevent.

## Validation sprint

The candidate receives one bounded validation sprint before further platform
expansion.

1. Build a capability matrix backed by primary evidence for cMCP, ACLE-MCP,
   Salus, AgentAction, AWS AgentCore Policy, and Azure Attestation.
2. Specify three attacks that the complete SMERC composition should stop and
   that each closest alternative does not claim to stop.
3. Give a clean-room evaluator the MIT revision and public material, but no
   later source, and estimate a tested reconstruction plan.
4. Implement one hardware-attested action path using existing confidential
   compute. Do not design custom silicon.
5. Measure bypass resistance, decision latency, stale-evidence rejection,
   authority lifetime, outcome binding, and rollback verification.
6. Obtain five interviews with platform or security engineers, three explicit
   confirmations that the gap matters, and one written pilot commitment.

## Continuation thresholds

Continue the product only when all of these are true:

- No reviewed alternative supplies the same complete guarantee.
- Clean-room reconstruction from the MIT baseline requires at least twelve
  skilled engineer-months, excluding ordinary cloud integration work.
- The proof blocks at least three relevant attacks missed by the closest
  alternatives.
- The hardware boundary prevents the host or agent from minting equivalent
  authority or fabricating a valid settlement record.
- At least one external organization commits to testing the proof.
- The revised gate score reaches 27/35 with no category below 3.

If these thresholds fail, SMERC should stop pursuing this as a standalone
platform and either narrow to a component with demonstrated demand or end the
commercial effort.

## Reproduce the repository measurements

```powershell
python tools/license_boundary_audit.py `
  07b1fee27b573fc2affb14a15fedb50a060d0bef `
  6a59c3b131bd999e62b8fa6505e385625cf4320a `
  --output reports/cloneability/license-boundary.json
```

# OpenSSF Issue #50 Response Draft

Thanks. This is useful and I agree with the direction.

My current view is that recoverability should not replace hard pre-execution gates. The runtime order should be:

```text
scoped authority / typed contract / attestation / least privilege / expected object shape
-> recoverability-aware SMERC posture
-> SPARTa route / controls
-> replayable decision evidence
```

I added a Ref-gated runtime proof loop to make that boundary explicit. The Ref gate is mechanical: typed contract valid, attestation valid, least privilege confirmed, and object shape expected. If that gate fails, SMERC scoring is capped and the action is forced toward hold/block/review behavior rather than allowing recoverability to justify normal execution.

The useful framing I take from your comment is:

- no recoverability scoring should rescue bad authority or bad shape
- the Ref should not be an AI agent
- scoped access and typed endpoints belong before governance scoring
- SMERC should govern runtime posture after mechanical evidence is admitted

The current proof loop is here:

https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/docs/Ref_Gated_Runtime_Proof_Loop.md

And the generated report is here:

https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/blob/main/reports/Ref_Gated_Runtime_Proof.md

This is still pilot-grade and local. It does not claim complete endpoint type safety, prompt-injection defense, production MCP transport, or production certification. The goal is to show the order of operations clearly: hard gates first, scoring second, route/evidence third.

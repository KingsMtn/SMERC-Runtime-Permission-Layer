# SMERC Agent Identity Gate

SMERC scores proposed actions before execution. The Agent Identity Gate adds one earlier question:

**Is this agent allowed to ask for this level of action in the first place?**

This is different from ordinary user login. In agentic systems, the actor may be an LLM agent, workflow bot, service account, automation runner, or human operator acting through automation. The same requested action can deserve a different posture depending on the actor's trust tier, credential scope, authorized tool family, autonomy level, and recent behavior.

## What It Evaluates

`reference_engine/agent_identity.py` accepts `smerc.agent-identity.v1` records with:

- agent id, name, type, provider, and owner team
- trust tier: `unverified`, `sandbox`, `standard`, `trusted`, or `critical`
- authorized tool families
- maximum autonomy level: `observe`, `recommend`, `constrain`, or `execute`
- credential scope: `none`, `read_only`, `scoped_write`, `production_write`, or `financial_or_destructive`
- recent denials, recent overrides, and recent success rate

The gate returns:

- `PASS`, `WATCH`, or `FAIL`
- identity score
- trust modifier
- reason codes
- recommended controls
- plain-English summary

## Why It Matters

Recoverability scoring should not be the only admission test. A highly recoverable action may still be wrong if the requesting agent is outside its authority. A trusted agent may be allowed to run a canary deploy while a support agent attempting bulk deletion should be frozen even if the action has a rollback story.

SMERC now separates three questions:

1. **Identity admission:** is the actor authorized for this tool family and autonomy level?
2. **Recoverability posture:** is the action recoverable enough to allow, throttle, freeze, deny, or escalate?
3. **SPARTa route:** if allowed or constrained, what execution route and controls apply?

## Runtime Behavior

When a customer evaluation includes agent identities, SMERC evaluates each action against the matching actor record.

- `PASS` keeps the request admitted for normal recoverability scoring.
- `WATCH` admits the request but records identity risk and controls.
- `FAIL` caps the result to `FREEZE` unless a stricter hard Ref-gate failure already caps it to `DENY`.

If a customer evaluation omits identities, existing metadata-only reports still work. Identity enforcement becomes active when an `agents` list is supplied.

## Example

```bash
python -m reference_engine.agent_identity examples/agent_identity_catalog.json \
  --actor release_agent \
  --tool github_actions.production_deploy \
  --autonomy execute \
  --side-effect external \
  --pretty
```

For catalog-level examples, inspect:

- `examples/agent_identity_catalog.json`
- `examples/pilot_intake_filled_examples.json`

Run:

```bash
python -m unittest tests.test_agent_identity -v
python -m reference_engine.pilot_intake_report examples/pilot_intake_filled_examples.json --pretty
```

## Evidence Boundary

This gate does not replace IAM, identity providers, PAM, workload identity, approvals, or policy-as-code. It uses their metadata as runtime evidence and converts that evidence into a replayable SMERC admission result.

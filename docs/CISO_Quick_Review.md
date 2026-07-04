# SMERC CISO Quick Review

## What Is SMERC?

SMERC is runtime permission infrastructure for AI agents. It evaluates proposed high-impact actions before execution and returns a replayable posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

## Where Does It Sit?

SMERC sits between an agent or automation system and a side-effecting tool:

```text
agent proposes action -> SMERC evaluates -> tool/workflow/reviewer responds
```

## What Risk Does It Address?

SMERC is designed for situations where AI agents or automation can:

- deploy code
- modify infrastructure
- access sensitive data
- delete records
- send external communications
- change security workflows
- trigger financial or operational processes

## What Makes It Different?

SMERC is not primarily a prompt filter. It focuses on the action boundary, where a proposed tool call or workflow action is about to create consequences.

The main distinction is the use of intermediate runtime postures and an action-bound execution contract:

- `THROTTLE`: proceed with constraints
- `FREEZE`: pause for missing confidence/context
- `ESCALATE`: route to higher-trust review

These are more operationally useful than simple allow/block decisions.

For evidence-authorized enforcement policies, eligible decisions can issue a signed permit bound to the exact action, executor audience, decision replay, policy hash, required controls, and short expiry. The pilot consumes each permit once. This makes the authorization inspectable at the execution boundary, while remaining explicit that production key management and distributed replay prevention are not yet implemented.

Scoped workload principals keep proposing agents separate from permit issuers and side-effecting executors. Decisions, reviews, permit issuance, and permit consumption retain authenticated principal attribution. The reference implementation uses static pilot secrets rather than enterprise identity federation.

Configured execution adapters must also provide a signed, short-lived control-evidence receipt before permit consumption. The receipt binds native control references to the exact permit and action. This is stronger than a caller-supplied control list, while remaining explicitly short of hardware-backed or independently verified attestation.

## What Exists Today?

- Python reference engine
- Runtime permission engine
- Example action dataset
- Unit tests
- Public demo site
- GitHub Actions integration v0.1
- Decision report artifacts and replay records
- Signed action-bound permit and single-use consumption contract
- Scoped workload identity and attributed security events
- Signed adapter control-evidence receipts
- Pilot package and validation materials

## How Would A Team Test It?

Start with the GitHub Actions integration in `observe` mode:

```yaml
uses: ./integrations/github_actions
with:
  action-file: integrations/github_actions/sample_action_request.json
  mode: observe
```

Review the decision report without blocking the existing workflow.

## What Is Not Proven Yet?

- Production risk reduction
- Buyer willingness to pay
- Threshold calibration against real enterprise workflows
- Reviewer agreement across multiple security teams
- False release and false constraint rates
- Performance at scale

## Recommended First Pilot

90-day GitHub Actions pilot:

1. Observe: score actions without blocking.
2. Recommend: surface constraints and reviewer guidance.
3. Enforce: fail or route selected high-risk postures after calibration.

## Review Links

- Public demo: `https://admirable-sorbet-9986d5.netlify.app`
- CISO review page: `https://admirable-sorbet-9986d5.netlify.app/ciso.html`
- GitHub Actions pilot page: `https://admirable-sorbet-9986d5.netlify.app/github-action.html`
- GitHub repository: `https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer`
- CISO deployment packet: `docs/CISO_Deployment_Packet.md`
- Runtime permission doc: `docs/Runtime_Permission_Infrastructure.md`
- GitHub Actions integration: `integrations/github_actions/`

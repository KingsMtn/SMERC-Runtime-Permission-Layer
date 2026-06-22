# SMERC Runtime Permission Layer

[![Tests](https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/tests.yml/badge.svg)](https://github.com/KingsMtn/SMERC-Runtime-Permission-Layer/actions/workflows/tests.yml)

## External Technical Review Edition

SMERC is runtime permission infrastructure for AI-agent actions. It evaluates a proposed action before execution and returns a replayable posture:

- `ALLOW`
- `THROTTLE`
- `FREEZE`
- `DENY`
- `ESCALATE`

The first integration is a GitHub Actions gate for AI-assisted code, deployment, and infrastructure workflows.

## Why This Repository Exists

This public repository is the external technical review edition of SMERC. It contains the implementation and documentation needed for a security, platform, or product team to determine whether SMERC is worth testing in shadow mode.

It intentionally excludes private legal drafts, patent strategy, competition submissions, investor materials, outreach records, and internal commercial planning.

## Review In 10 Minutes

1. Read `docs/CISO_Quick_Review.md`.
2. Read `docs/Security_Model.md`.
3. Inspect `reference_engine/agent_permission_layer.py`.
4. Review `integrations/github_actions/README.md`.
5. Inspect `examples/agent_permission_actions.json`.
6. Run the tests.
7. Review `pilot_package/SMERC_Shadow_Mode_Pilot_One_Pager.md`.

## What SMERC Evaluates

The reference engine accepts structured action metadata:

- action identity and description
- tool and actor
- confidence
- harm potential
- consent or authorization support
- reversibility
- external side effects
- sensitive-data involvement
- optional context

It outputs:

- runtime posture
- risk score
- confidence score
- reason codes
- recommended constraints
- replay ID and replay record

## Quick Start

Requires Python 3.10 or later. No third-party Python packages are required.

```bash
python -m reference_engine.agent_permission_layer examples/agent_permission_actions.json --pretty
python -m unittest discover -s tests
```

Run the GitHub Actions gate locally:

```bash
python integrations/github_actions/run_smerc_gate.py \
  --action-file integrations/github_actions/sample_action_request.json \
  --mode observe \
  --output-file smerc-decision.json
```

Run the optional SMERC-F financial action-governance profile:

```bash
python -m reference_engine.financial_permission_profile \
  examples/financial_action_requests.json --pretty
```

Run the SMERC-F historical-context replay suite:

```bash
python -m reference_engine.financial_replay \
  examples/financial_replay_scenarios.json \
  --report reports/SMERC_F_Replay_Report.md
```

## GitHub Actions Modes

| Mode | Behavior |
| --- | --- |
| `observe` | Score and report; never fail the workflow. |
| `recommend` | Surface posture and constraints for reviewer use. |
| `enforce` | Fail selected high-risk postures after calibration and approval. |

The recommended first deployment is `observe` mode.

## What SMERC Is Not

- Not a replacement for IAM, OPA, branch protection, code review, SIEM, or existing approvals.
- Not a prompt-injection filter.
- Not a production-certified security platform.
- Not a claim that current thresholds are already calibrated for every enterprise.
- Not intended to receive production secrets, raw customer data, or full private prompts in a first pilot.
- Not a cryptocurrency, token, trading system, custody platform, or financial product.

## Optional Domain Profile

`SMERC-F` demonstrates how the core permission engine can govern proposed treasury, settlement, liquidity, collateral, and tokenized-finance actions. It is explicitly labeled exploratory and uses synthetic examples.

See `docs/SMERC_Financial_Action_Governance.md`.

Replay method and limitations are documented in `docs/SMERC_F_Replay_Validation.md`.

## Public Review Links

- CISO review: https://admirable-sorbet-9986d5.netlify.app/ciso.html
- Interactive demo: https://admirable-sorbet-9986d5.netlify.app
- GitHub Actions pilot: https://admirable-sorbet-9986d5.netlify.app/github-action.html
- Pilot options: https://admirable-sorbet-9986d5.netlify.app/pilot.html

## Current Evidence

- Working Python reference engine
- Installable local GitHub Action
- Deterministic example action requests
- Automated tests
- Security and deployment documentation
- Public interactive demo
- Defined shadow-mode pilot

## Evidence Still Required

- live workflow pilot data
- reviewer agreement and override rates
- false release and false constraint measurements
- threshold calibration against customer workflows
- latency and operational impact measurements
- production security and legal review

## Pilot Question

> Does recoverability-aware runtime scoring change reviewer judgment in a useful and repeatable way before AI-agent actions create side effects?

SMERC should be adopted only if a controlled pilot produces evidence that the answer is yes.

## License

See `LICENSE`.


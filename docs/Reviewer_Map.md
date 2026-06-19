# SMERC Reviewer Map

## One-Line Positioning

SMERC is runtime permission infrastructure for AI agents, controlling when automated systems should allow, throttle, freeze, deny, or escalate actions.

## What This Repository Contains

This repository is not only a document archive. It contains a working reference system with:

- a Python runtime permission engine
- a reversibility-weighted authorization model
- example AI-agent action datasets
- a GitHub Actions integration
- unit tests
- a browser demo
- a public Netlify deployment
- CISO, security, deployment, and pilot review materials

## What To Review First

### For A CISO

Start with:

- `docs/CISO_Quick_Review.md`
- `docs/Security_Model.md`
- `docs/Pilot_Readiness.md`
- `integrations/github_actions/README.md`

Primary question:

> Would a security team want a shadow-mode control that scores AI-assisted code, deployment, and infrastructure actions before execution?

### For A Platform Engineer

Start with:

- `integrations/github_actions/run_smerc_gate.py`
- `integrations/github_actions/action.yml`
- `examples/agent_permission_actions.json`
- `reference_engine/agent_permission_layer.py`

Primary question:

> Can this be inserted into an existing workflow without disrupting current approvals?

### For A Product Or Partnership Reviewer

Start with:

- `README.md`
- `docs/Runtime_Permission_Infrastructure.md`
- `docs/Deployment_Model.md`
- `pilot_package/SMERC_Shadow_Mode_Pilot_One_Pager.md`

Primary question:

> Does SMERC address a real action-governance gap that is worth validating in a controlled workflow?

## Current Product Wedge

The first commercial wedge is a 90-day GitHub Actions pilot for AI-assisted code, deployment, and infrastructure workflows.

Pilot sequence:

1. `observe`: score actions and write reports without blocking.
2. `recommend`: compare SMERC postures against reviewer behavior.
3. `enforce`: fail or route selected high-risk postures after calibration.

## What SMERC Is

- Runtime permission infrastructure for AI agents and action-taking systems.
- A replayable posture engine for proposed actions.
- A way to distinguish "safe to proceed," "proceed with limits," "pause," "deny," and "send to accountable review."
- A reference architecture for evaluating recoverability before side effects occur.

## What SMERC Is Not

- Not a replacement for LLMs.
- Not a replacement for OPA, IAM, code review, branch protection, SIEM, or enterprise GRC.
- Not a safety-certified controller.
- Not a claim that every threshold is already production-calibrated.
- Not a broad claim that "AI governance" itself is new.

## Evidence Already Built

- Deterministic reference engines in Python.
- Unit tests for core decision behavior and GitHub Actions integration.
- Example AI-agent action datasets.
- Public browser demo with audit history and downloadable reports.
- A defined shadow-mode pilot package.

## Evidence Still Needed

- Real customer interview data.
- Shadow-mode pilot data from live workflows.
- Reviewer agreement and override rates.
- False release and false constraint measurements.
- Latency and workflow-disruption measurements.
- Legal and security review before production use.

## Recommended Next Step

Run one design-partner pilot in GitHub Actions shadow mode. The goal is not to prove that SMERC is universally correct. The goal is to prove whether runtime recoverability scoring changes reviewer judgment in a way security and platform teams value.

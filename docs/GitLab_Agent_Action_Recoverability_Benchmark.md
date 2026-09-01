# GitLab Agent Action Recoverability Benchmark

SMERC should be easy for a GitLab, CI/CD, or DevSecOps reviewer to understand without decoding the SMERC acronym first.

GitLab-style agent governance can ask whether an agent tool is allowed, should ask, or should be denied. SMERC asks the next execution question:

> Is this specific agent action recoverable enough to execute now?

## Why This Is Not A Distraction

This is not a separate product line. It is a proof adapter for the same SMERC runtime permission engine.

The GitLab-shaped path is useful because GitLab, CI/CD, merge requests, protected environments, project tokens, dependency remediation, MCP tool calls, and agentic coding are concrete places where the recoverability question is easy to see.

## What The Benchmark Compares

The benchmark compares:

- GitLab-style tool-governance outcomes: `ALLOW`, `ASK`, `DENY`
- SMERC runtime postures: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, `ESCALATE`

The useful deltas are:

- `GITLAB_ALLOW_SMERC_RESTRAINT`: ordinary access permits an action, but SMERC finds weak recoverability.
- `GITLAB_ASK_SMERC_STRUCTURED_ROUTE`: ordinary governance asks for confirmation, while SMERC returns a specific route, controls, and reason codes.
- `GITLAB_DENY_SMERC_NON_DENY`: ordinary governance blocks the action, while SMERC sees a possible constrained path. This is a calibration prompt, not an override.

## Run It

```bash
python -m reference_engine.gitlab_agent_action_benchmark \
  examples/gitlab_agent_action_recoverability_scenarios.json \
  --json-output reports/gitlab_agent_action_recoverability_benchmark.json \
  --markdown-output reports/GitLab_Agent_Action_Recoverability_Benchmark.md \
  --pretty
```

## Generated Outputs

- `reports/GitLab_Agent_Action_Recoverability_Benchmark.md`
- `reports/gitlab_agent_action_recoverability_benchmark.json`

## Evidence Boundary

This is a GitLab-shaped public-pattern benchmark only.

It is not a GitLab integration, GitLab endorsement, GitLab telemetry, production deployment, customer validation, or proof of incident reduction.

## Impact

The impact is search and reviewer clarity. A platform team can now inspect a familiar CI/CD and agent-governance example and see exactly where SMERC adds value:

- an authorized action can still be unrecoverable
- an approval can become stale after scope changes
- an MCP tool can be valid while its arguments are unsafe
- an agent token can be valid while the requested action has too much blast radius
- a human `ASK` state can be converted into a more precise route with controls and replay evidence

That makes SMERC easier for GitLab-style, DevSecOps, platform engineering, and AI-agent governance reviewers to test.

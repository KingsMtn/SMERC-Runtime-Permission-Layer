# SMERC Community And Partner Paths

SMERC is runtime permission infrastructure for AI-agent and automation actions. The project is seeking practical review from people who work near real execution boundaries: security teams, platform teams, AI governance teams, DevSecOps engineers, agent-framework builders, cloud operators, and researchers.

This repository is not asking reviewers to accept a broad claim. It is asking reviewers to inspect a concrete question:

> When an automated action is technically allowed, is it recoverable enough to execute now?

## Who This Is For

### Design Partners

Good design partners have real workflows where AI agents, CI/CD systems, cloud automation, internal tools, or service bots can create side effects.

Useful first pilots include:

- GitHub Actions shadow-mode scoring
- AI coding-agent pull request and deployment review
- cloud administration workflow review
- internal automation review queues
- security automation dry runs

Design partners help answer whether SMERC's recoverability scoring changes reviewer judgment in useful ways.

### Integration Partners

Integration partners help connect SMERC to toolchains where runtime permission decisions matter.

Useful integration targets include:

- CI/CD platforms
- AI-agent frameworks
- API gateways
- developer platforms
- cloud control planes
- ticketing and approval systems
- security orchestration tools

Integration partners should not treat SMERC as a replacement for IAM, policy-as-code, SIEM, EDR, code review, or deployment approvals. SMERC is an additional pre-execution recoverability layer.

### Research Reviewers

Research reviewers can help pressure-test:

- recoverability scoring assumptions
- proxy incident replay methodology
- reviewer-agreement metrics
- false-release and false-constraint definitions
- replay and audit semantics
- policy calibration methods

The current benchmark is proxy evidence only. It is useful for hypothesis testing, not production validation.

### Open-Source Contributors

Useful contributions include:

- additional scenario packs
- SDK examples
- documentation improvements
- policy-language examples
- API client tests
- replay and benchmark improvements
- security review findings
- integration adapters

## How To Engage

Use GitHub Issues or Pull Requests.

Suggested first issue titles:

- `Design partner: evaluate SMERC against GitHub Actions shadow mode`
- `Integration idea: connect SMERC to [tool/platform]`
- `Scenario contribution: [category] recoverability examples`
- `Research review: proxy benchmark assumptions`
- `Security review: [area]`

## What Good Feedback Looks Like

Good feedback is specific and testable:

- "This scenario should be `FREEZE`, not `THROTTLE`, because rollback takes hours."
- "This signal is missing: blast radius should include downstream workflow count."
- "This integration point is wrong; the decision needs to happen before tool-call dispatch."
- "This would not pass our security review until secrets, tenancy, or deployment isolation are hardened."
- "This is useful in shadow mode, but not enforce mode yet."

## What This Project Is Not Claiming

SMERC does not claim:

- to replace LLMs, AI agents, IAM, OPA, SIEM, EDR, or approval systems
- to be production-certified
- to prove incident reduction without live pilots
- to be calibrated for every enterprise
- to solve prompt injection, model safety, or identity governance by itself

SMERC currently provides a working reference engine, API, SDKs, replay/audit mechanics, GitHub integrations, proxy evidence, and pilot materials. Production adoption requires design-partner validation and hardening.

## The Collaboration Goal

The immediate goal is not broad adoption. The immediate goal is credible learning:

1. Run SMERC in shadow mode against real or realistic workflows.
2. Compare SMERC posture decisions with existing approval behavior.
3. Measure reviewer agreement, false release, false constraint, latency, and review burden.
4. Decide whether narrow enforcement is justified.

# SMERC Founder Explanation Card

## 15-Second Version

SMERC is a permission layer for AI agents. Before an agent edits code, deletes data, sends messages, moves money, or triggers a workflow, SMERC decides whether to allow, throttle, freeze, deny, or escalate the action.

## 30-Second Version

Most systems ask whether an automated action is allowed. SMERC asks a second question: if this action goes wrong, can the organization recover?

It scores reversibility, containment, rollback latency, evidence validity, anomaly pressure, and impact scope before execution. The result is a replayable decision that tells the system whether to proceed, slow down, pause, block, or route to review.

## 60-Second Version

AI agents are starting to take real actions inside companies. They can write code, trigger deployments, call APIs, move data, and interact with sensitive workflows.

The problem is that many controls still treat this as a simple allow-or-block decision. In real operations, the more important question is often recoverability: if the action is wrong, how hard is it to contain and reverse?

SMERC is runtime permission infrastructure for that action boundary. It evaluates proposed actions using structured signals, returns one of five postures, attaches reason codes and controls, and records the decision for audit and replay.

The first practical use case is GitHub Actions and deployment governance, where SMERC can score automated or AI-assisted workflows in shadow mode before any enforcement is turned on.

## What To Say When Someone Asks "Is It Built?"

Yes, there is working software. The public repository includes Python engines, schemas, an API path, audit and replay structures, action-bound permits, GitHub Actions integration, a deployment adapter, examples, tests, and CI.

It is not yet a finished hosted enterprise product. It is a pilot-grade architecture ready for technical review and design-partner testing.

## What To Say When Someone Asks "Why Not Use Existing Tools?"

Existing policy, IAM, and security tools are still needed. SMERC is not trying to replace them.

SMERC focuses on a specific missing question at runtime:

> Is this action recoverable enough to execute under current conditions?

That makes it complementary to policy engines, CI/CD approvals, identity systems, AI gateways, and security monitoring.

## What To Say When Someone Asks "What Do You Need?"

The useful next step is a design-partner pilot.

The simplest pilot is shadow-mode GitHub Actions scoring. SMERC observes proposed workflow actions, returns posture decisions and reason codes, and lets the team compare those decisions against existing reviewer judgement before any blocking is enabled.

## Words To Avoid

Avoid claiming:

- production-certified
- guaranteed safe
- replaces security teams
- replaces policy engines
- prevents all AI risk
- patented
- proven market demand

Use instead:

- pilot-grade
- runtime permission layer
- recoverability-aware authorization
- action-bound permits
- audit and replay
- design-partner validation
- controlled shadow-mode pilot


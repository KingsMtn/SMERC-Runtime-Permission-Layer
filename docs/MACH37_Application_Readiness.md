# MACH37 Application Readiness

## Current Recommendation

MACH37 should be treated as a strong future application target, but not a distraction from the next proof milestone.

The project should move toward MACH37 when SMERC can be explained as a narrow cybersecurity product with a testable pilot, not as a broad AI-governance framework.

## MACH37-Fit Version Of SMERC

SMERC is a recoverability-aware runtime permission layer for AI-agent actions.

The first product is a GitHub Actions / pull request guardian that evaluates AI-assisted software, deployment, and infrastructure actions before execution. It returns a posture, route, controls, reason codes, and a replayable evidence record.

The security problem is AI-agent blast radius:

- unauthorized or unsafe code changes
- risky deployment actions
- destructive infrastructure commands
- tool calls with weak rollback paths
- human overrides that are not evaluated later
- action logs that record what happened but not why the decision was made

## Why MACH37 Could Fit

MACH37 is relevant because SMERC is closest to cybersecurity, runtime authorization, and enterprise infrastructure.

The application should emphasize:

- CISO buyer relevance
- GitHub Actions as the first narrow wedge
- runtime governance before action execution
- recoverability scoring
- constrained authorization instead of simple allow/block
- replayable decision evidence
- security-team review workflow

The application should not emphasize:

- broad macro-language theory
- crypto or trading concepts
- benevolent AI philosophy
- speculative market size
- unvalidated patent claims
- general AI ethics language

## Application-Ready Checklist

SMERC is ready for a MACH37-style application when these are true:

- The README has a clear reviewer path.
- The public demo and GitHub repo tell the same story.
- The GitHub Actions / PR Guardian flow works locally.
- The test suite is passing.
- The CISO review package is easy to find.
- The pilot package explains observe, recommend, and enforce phases.
- The fake-customer and benchmark reports are linked from the review path.
- The project states what is not proven yet.
- At least one external reviewer has provided written feedback.
- There is a concise answer to: "Why is this not just OPA, an AI gateway, or an approval workflow?"

## Draft Application Answer

### What Is The Company Building?

SMERC is building recoverability-aware runtime permission infrastructure for AI-agent actions. It sits between AI agents, tools, code repositories, deployment workflows, APIs, and operational systems. Before an action executes, SMERC evaluates risk, recoverability, evidence quality, and execution controls, then returns a posture such as allow, throttle, freeze, deny, or escalate.

The first product is a GitHub Actions / pull request guardian for AI-assisted code, deployment, and infrastructure workflows. It runs in shadow mode first, scoring actions and producing replayable decision evidence without blocking production work.

### What Problem Does It Solve?

AI agents are gaining permission to write code, trigger workflows, change infrastructure, and call operational tools. Existing security controls often decide whether an actor is allowed to perform an action, but they do not always score whether a bad action can be recovered from before execution.

SMERC focuses on recoverability before action. It asks whether an action should proceed normally, proceed with constraints, pause for review, or be blocked because the rollback path, evidence, or containment is too weak.

### Why Now?

AI-agent tool use is moving from demos into software development, infrastructure, support, and operations. The risk is no longer only bad text output. The risk is automated action with real side effects.

Security teams need a way to govern these actions without turning every workflow into a manual approval queue. SMERC aims to preserve speed where actions are recoverable and add restraint where actions create irreversible exposure.

### What Is Built?

The public repository includes a reference engine, runtime contracts, GitHub Actions integration, PR Guardian, SPARTa route generation, action-bound permits, control-evidence receipts, Decision Lifecycle Ledger, DLL Intelligence, benchmark reports, fake-customer pilot evidence, SDKs, API contracts, and tests.

### What Is Still Unproven?

SMERC has not yet proven live customer risk reduction. The next milestone is a shadow-mode pilot where a security or platform team compares SMERC posture decisions against human reviewer labels, override rates, approval latency, and irreversible exposure patterns.

## One-Minute Pitch

SMERC is runtime permission infrastructure for AI agents.

AI agents are starting to write code, trigger deployments, change infrastructure, and call business tools. Most systems still treat this as an allow-or-block problem. SMERC adds recoverability scoring before execution.

For each proposed action, SMERC asks: if this goes wrong, can the organization contain it, roll it back, and explain why it was allowed?

The first product is a GitHub Actions and pull request guardian for AI-assisted engineering workflows. It runs in shadow mode, scores risky actions, recommends allow, throttle, freeze, deny, or escalate, and produces replayable evidence for security review.

SMERC does not replace existing security tools. It adds a recoverability-aware permission layer at the point where AI agents are about to create real operational consequences.

## Hard Question Answer

### Why Is This Not Just OPA?

OPA is strong policy-as-code infrastructure. SMERC is not trying to replace it. SMERC is focused on recoverability-aware posture decisions, execution routes, and lifecycle evidence for AI-agent actions. OPA can answer whether a policy permits an action. SMERC is designed to answer whether the action is structurally safe enough to release, constrain, pause, block, or escalate based on recoverability and evidence quality.

### Why Is This Not Just An AI Gateway?

AI gateways are useful for model access, routing, monitoring, prompt filtering, and usage controls. SMERC focuses on what happens after an agent proposes a real action: code changes, deployments, infrastructure commands, money movement, or workflow execution. The core question is not only model safety. It is action recoverability.

### Why Is This Not Just Human Approval?

Human approval can slow work and often lacks consistent evidence. SMERC can run before approval, recommend the right posture, preserve the evidence available at decision time, and later compare the outcome against the original recommendation and any override.

## Do Not Submit Until

Do not submit a MACH37 application until the application can include at least one real external-review signal.

The minimum acceptable signal is not "people liked the idea." It should be one of:

- a security reviewer identified a specific workflow they would test
- a platform team agreed the GitHub Actions shadow-mode pilot is relevant
- an AI-governance leader provided written feedback on recoverability scoring
- a design partner agreed to provide realistic action samples for scoring

Without that, the pitch is interesting but still mostly founder-generated proof.

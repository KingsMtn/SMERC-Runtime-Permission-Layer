# International Runtime Governance Learning Map

Last updated: 2026-09-15

## Purpose

This map records what SMERC can learn from public international AI safety, agent evaluation, runtime governance, and MCP control-plane work.

It is not a claim that those organizations endorse SMERC, use SMERC, need SMERC, or expose their private engines. It is a bounded engineering learning map:

> What public engine patterns should SMERC absorb so the project becomes stronger at each level we create?

## Short Finding

The field is converging around runtime controls for agentic systems:

- sandboxed execution
- tool-call control planes
- policy enforcement
- identity and trust
- audit trails
- incident response
- benchmark and red-team scoring
- disclosure boundaries for sensitive evaluations

That validates the category, but it also raises the bar. SMERC should not compete by saying "we gate actions too." SMERC should compete by making recoverability a first-class runtime signal:

> Is this action recoverable enough to execute now, with the evidence currently available?

## Engine-Level Lessons To Pull Forward

| Public source | What their engine emphasizes | What SMERC should add or strengthen | Boundary |
| --- | --- | --- | --- |
| UK AI Security Institute Inspect Sandboxing Toolkit | Agent evaluations need isolated tool execution, and isolation should be chosen by risk. Inspect separates model inference from the environment where tool calls execute and classifies sandboxing across tooling, host, and network isolation. | Add explicit environment-boundary evidence fields: `tooling_isolation`, `host_isolation`, `network_isolation`, `sandbox_escape_surface`, and `execution_environment_boundary`. Use them as recoverability inputs, not just security labels. | Do not claim SMERC is an Inspect replacement. SMERC can use the same isolation axes as decision evidence. |
| UK AI Security Institute SandboxEscapeBench | Agent sandbox escape testing needs public scenarios, private held-out tests, and layered containment so the test itself does not create real-world harm. | Add a public/private probe split to SMERC stress data: public examples for reviewers, held-out internal cases for regression checks, and clear dangerous-detail withholding. | Do not publish operational exploit steps. Use vulnerability classes and metadata-only recoverability records. |
| UK AI Security Institute MCP tool evidence | Public MCP ecosystems show rapid growth in agent tools, including high-impact and agent-generated tools. | Treat public MCP server and tool metadata as a live signal source for SMERC. Track new tool families, side-effect classes, and missing-evidence patterns. | Public MCP metadata is market signal, not customer validation. |
| UK AI Security Institute transcript analysis | Pass/fail rates hide important behavior. Transcripts reveal how agents fail, hesitate, retry, or route around controls. | Keep posture outputs, decision lifecycle ledgers, and replay reports reviewer-readable. Add transcript-derived fields only after stripping prompt content and sensitive details. | Do not ingest private transcripts without permission. Prefer derived metadata. |
| Singapore AI Verify / Project Moonshot / Agentic AI governance | Practical evaluation combines benchmarking, red teaming, baseline tests, tiered scores, and human accountability proportional to autonomy and risk. | Add simple reviewer-visible score bands beside posture: evidence sufficiency, recoverability strength, containment strength, and rollback latency tier. | Do not claim regulatory certification. Use this as presentation discipline and evaluation structure. |
| Japan AISI AI Incident Response Approach Book | AI incidents should be expected. Detective controls, business continuity, accountability, and lifecycle-wide supply-chain thinking matter because autonomous behavior can exceed conventional incident response. | Treat SMERC as both pre-execution control and incident-prevention evidence. Strengthen postcondition evidence, freeze reasons, escalation routing, and continuity impact language. | Do not imply SMERC eliminates incidents. It reduces blind execution and preserves decision evidence. |
| Canada CAISI evaluator-disclosure guidance | Evaluators should share clear, audience-specific information while withholding sensitive datasets, adversarial details, and held-out tests that could enable misuse or contamination. Synthetic examples and metadata are safer. | Make SMERC's external ask metadata-only by default. Maintain public examples, trusted reviewer packets, and private held-out regressions as separate disclosure tiers. | Never ask reviewers to post account IDs, raw logs, secrets, private prompts, production commands, or customer records. |
| EU AI Act / GPAI Code of Practice | Governance is moving toward documentation, transparency, systemic-risk practices, safety and security evidence, and corrective-action expectations. | Position SMERC as audit-supporting evidence: decision records, control mapping, non-claims, and corrective-action evidence. | Do not claim AI Act compliance or GPAI conformity without legal review and formal assessment. |
| Microsoft Agent Governance Toolkit / MCP control plane work | MCP standardizes tool execution but not necessarily governance. Control planes add policy checks, identity, audit, response inspection, trust scoring, and action interception. | Keep SMERC compatible with control-plane language, but differentiate on recoverability, missing evidence, rollback, containment, and side effects. Add adapters rather than trying to own every policy engine category. | Microsoft-style governance is adjacent and sometimes overlapping. SMERC should complement it, not pretend it does not exist. |
| Nightfall MCP Gateway and similar commercial gateways | The market is moving toward inline enforcement before tool calls, credential brokering, audit, and tool/server visibility. | Treat this as market validation for the "before action" boundary. SMERC should add recoverability scoring that an inline gateway could call before high-impact execution. | Commercial press releases are market signal, not independent proof. |

## What SMERC Should Add Next

### 1. Isolation Evidence Fields

Add or document recoverability inputs that describe where the action runs:

- `tooling_isolation`: none, restricted tools, shell, browser, code execution, privileged automation
- `host_isolation`: none, process, container, hardened container, VM, dedicated account
- `network_isolation`: none, outbound only, scoped private network, internet, production network
- `sandbox_escape_surface`: none known, docker socket, privileged container, host mount, cloud metadata access, production credentials
- `execution_environment_boundary`: local, CI runner, MCP server, cloud function, Bedrock action group, Kubernetes workload, production host

SMERC use: weaker isolation should increase required evidence before `ALLOW`, especially when rollback latency or external side effects are high.

### 2. Disclosure Tiers For Evidence

Use three tiers:

- public examples: synthetic or sanitized metadata-only records
- trusted reviewer examples: richer but still no secrets, raw logs, customer records, or production commands
- private regression cases: held-out rows used to prevent gaming and benchmark contamination

SMERC use: this keeps the project useful and visible without turning the repo into an exploit cookbook.

### 3. Reviewer Score Bands

Add reviewer-facing bands beside posture:

- evidence sufficiency: strong, partial, missing
- recoverability strength: strong, moderate, weak, unrecoverable
- containment strength: isolated, scoped, broad, unknown
- rollback latency tier: immediate, minutes, hours, unknown

SMERC use: this makes `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, and `ESCALATE` easier for external reviewers to trust.

### 4. MCP Tool Metadata Watch

Use public MCP/server/tool metadata to generate new stress rows around:

- tool definitions with hidden instruction risk
- newly introduced side-effecting tools
- tool schemas that omit rollback or containment evidence
- agent-generated tools
- cross-server confused-deputy paths

SMERC use: the public ecosystem becomes a recurring source of recoverability stress cases.

### 5. Incident-To-Recoverability Translation

For public AI-agent incidents and advisories, translate only the safe pattern:

- action family
- authority used
- external side effect
- rollback path
- containment boundary
- evidence missing at decision time
- likely SMERC posture

SMERC use: this lets the project learn from real pain without using leaked source, private logs, or proprietary details.

## Build Priority

1. Add isolation evidence fields to the recoverability metadata contract and example rows.
2. Add a disclosure-tier note to public evidence and reviewer intake docs.
3. Add reviewer score bands to customer evaluation reports.
4. Add an MCP public metadata watchlist that produces metadata-only stress rows.
5. Add an incident-to-recoverability translation template for public advisories.

## Non-Claims

This document does not claim:

- SMERC is endorsed by UK AISI, Singapore IMDA, Japan AISI, Canada CAISI, the European Commission, Microsoft, Nightfall, or any named organization.
- SMERC is equivalent to a sandbox, AI gateway, policy engine, agent framework, model evaluation framework, or incident-response program.
- Public international guidance proves customer value, acquisition value, regulatory compliance, or production readiness.
- SMERC should use leaked proprietary source code, private prompts, customer logs, or sensitive benchmark details.

## Useful Public Sources

- UK AI Security Institute Inspect Sandboxing Toolkit: https://www.aisi.gov.uk/blog/the-inspect-sandboxing-toolkit-scalable-and-secure-ai-agent-evaluations
- UK AI Security Institute Inspect sandboxing documentation: https://inspect.aisi.org.uk/sandboxing.html
- UK AI Security Institute SandboxEscapeBench: https://www.aisi.gov.uk/blog/can-ai-agents-escape-their-sandboxes-a-benchmark-for-safely-measuring-container-breakout-capabilities
- UK AI Security Institute MCP tool evidence: https://www.aisi.gov.uk/blog/how-are-ai-agents-used-evidence-from-177000-ai-agent-tools
- UK AI Security Institute transcript analysis: https://www.aisi.gov.uk/blog/transcript-analysis-for-ai-agent-evaluations
- Singapore Project Moonshot: https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/2024/sg-launches-project-moonshot
- Singapore Model AI Governance Framework for Agentic AI: https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/2026/new-model-ai-governance-framework-for-agentic-ai
- Japan AISI AI Incident Response Approach Book: https://aisi.go.jp/activity/activity_security/260109/
- Canada CAISI evaluator disclosure guidance: https://ised-isde.canada.ca/site/ised/en/canadian-artificial-intelligence-safety-institute/what-information-should-ai-evaluators-share
- EU General-Purpose AI Code of Practice: https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai
- EU AI regulatory framework: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
- Microsoft MCP control plane / Agent Governance Toolkit: https://developer.microsoft.com/blog/securing-mcp-a-control-plane-for-agent-tool-execution/
- Microsoft Agent Governance Toolkit repository: https://github.com/microsoft/agent-governance-toolkit
- Nightfall MCP Gateway: https://www.nightfall.ai/news/nightfall-launches-mcp-gateway-to-govern-ai-agents-before-they-act

## Work / Result / Impact

Work: convert public international governance, sandboxing, MCP, incident-response, and disclosure patterns into bounded SMERC build inputs.

Result: SMERC gains a stronger outside-learning loop without claiming access to private engines or copying sensitive implementation details.

Impact: the project can keep innovating at each level while staying disciplined: recoverability first, evidence-bound, metadata-safe, and honest about what remains unproven.

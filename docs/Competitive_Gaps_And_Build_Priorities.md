# Competitive Gaps And Build Priorities

SMERC should not pretend competitors are weak. Several adjacent products are stronger than SMERC in important categories today.

## What Others Do Better Today

| Category | What They Usually Do Better | Why It Matters |
|---|---|---|
| OPA and policy-as-code | Mature policy language, broad adoption, stable enforcement patterns, Kubernetes and cloud-native integrations. | CISOs already trust known policy primitives and existing platform integrations. |
| Enterprise access control | Identity lifecycle, RBAC/ABAC, SSO, SCIM, audit administration, production support. | SMERC should not compete as an identity system. |
| AI gateways | Fast insertion point for LLM calls, prompt filtering, provider routing, token controls, usage analytics. | Buyers may expect AI governance to start at the gateway layer. |
| Agent governance platforms | Agent inventory, tool-call monitoring, policy UI, workflow dashboards, SaaS deployment. | SMERC is still more technical artifact than polished enterprise product. |
| Security approval workflows | Human approval chains, ticketing, audit familiarity, established escalation paths. | Buyers may prefer extending ServiceNow, Jira, Slack, Teams, or existing GRC workflows. |
| SIEM/GRC platforms | Long-term retention, reporting, compliance workflows, alert triage, enterprise integrations. | SMERC must not claim to replace compliance or evidence-retention systems. |

## Where SMERC Has A Real Lane

SMERC is most defensible where the question is not simply identity, prompt safety, or allow/deny policy.

The lane is:

> Is this specific AI-agent or automation action recoverable enough to execute now, and what posture, controls, route, and lifecycle evidence should be preserved before side effects occur?

The strongest differentiator is the connected loop:

```text
recoverability-aware decision
-> PR/runtime review artifact
-> SPARTa route
-> Decision Lifecycle Ledger
-> DLL Intelligence
```

## Build Priorities

1. **Latency and overhead measurement**
   - Measure median, p95, and max SMERC evaluation time.
   - Measure total workflow time added in GitHub Actions.
   - Separate machine decision latency from human approval latency.

2. **Policy language maturity**
   - Keep SPL narrow, deterministic, and auditable.
   - Avoid claiming parity with OPA until grammar, validation, imports, and tooling mature.

3. **Enterprise integration depth**
   - GitHub Actions first.
   - Then one ticketing/review path such as Jira, ServiceNow, Slack, or Teams.
   - Avoid broad integration claims until a real customer path exists.

4. **Operational dashboard**
   - Show decision distribution, reviewer agreement, false release, false constraint, override rate, latency, and evidence gaps.
   - This is where a pilot becomes commercially legible.

5. **Evidence retention boundary**
   - Keep DLL as a governance memory layer.
   - Do not market it as legal recordkeeping, SIEM, GRC, or compliance retention without counsel and customer requirements.

6. **Customer-calibrated benchmarks**
   - Synthetic benchmarks are useful for demonstration.
   - Customer-context shadow-mode records are required before making risk-reduction claims.

## Recommended Positioning

SMERC should position as:

> Recoverability-aware runtime permission infrastructure for AI-agent actions.

It should not position as:

- a replacement for OPA
- a replacement for IAM
- a generic AI gateway
- a SIEM or GRC platform
- a production-certified security platform

The near-term product goal is not to beat every governance product. It is to make one painful wedge concrete: AI-assisted actions can be technically allowed but operationally unrecoverable.

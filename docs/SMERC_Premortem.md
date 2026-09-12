# SMERC Premortem

## Purpose

This premortem treats failure as something to instrument early, not something to guess about later.

The useful question is:

> If SMERC does not get traction, what evidence would have warned us early?

This document should help the project stay honest while still moving. It is not a retreat from the work. It is a map of what must be tested before the project claims market proof.

## Failure Modes

| Failure mode | Warning signal | Test now | Response |
| --- | --- | --- | --- |
| Reviewers think existing tools already cover the gap. | Feedback says IAM, OPA, Cedar, Bedrock Guardrails, SIEM, SOAR, approvals, or policy engines are enough. | Ask reviewers where recoverability-before-execution is already handled in their stack. | Narrow the claim: SMERC complements authority, content safety, detection, and approvals by testing rollback latency, evidence validity, blast radius, and action momentum before execution. |
| The framing is too abstract. | People agree in principle but cannot explain where SMERC sits or what it does. | Ask a reviewer to describe SMERC back in their own words after reading one page. | Lead with concrete phrases: authorized action, recoverability gate, rollback path, blast radius, evidence gap, throttle, freeze, escalate. |
| The proof is too synthetic. | Reviewers say the examples are interesting but not real enough. | Ask for 5 to 25 metadata-only examples from one real workflow. | Treat external metadata replacement and reviewer labels as the next proof gate before broader outreach. |
| The value is interesting but not urgent. | Feedback says "nice idea" but no one can name a painful workflow or buyer. | Ask which workflow would have justified a shadow-mode review last quarter. | Focus on urgent lanes: agentic cloud execution, cost velocity, infrastructure changes, high-impact CI/CD, and automated financial actions. |
| The product surface is unclear. | Reviewers ask whether SMERC is an SDK, GitHub Action, MCP gateway, AWS Lambda handler, Bedrock/AgentCore layer, marketplace package, or enterprise service. | Ask reviewers which deployment surface they would actually test first. | Keep the public story clear: GitHub and metadata-only review are proof paths; AWS-style cloud action governance is the Tier 2 enterprise path. |
| The licensing boundary reduces trust. | Reviewers hesitate because they cannot tell what is safe to inspect, reuse, or commercialize. | Ask whether the public review license and commercial-use page are clear enough. | Keep public review useful while stating that hosted, embedded, production, resale, or revenue-generating use requires written permission. |
| The evidence ask is too hard. | Reviewers cannot provide even safe metadata-only examples. | Ask whether the external reviewer request is too long, too sensitive, or too much work. | Reduce the ask to one workflow and 5 examples, then expand only after a reviewer engages. |
| The control appears to slow teams down. | Reviewers see SMERC as another approval queue. | Ask whether `THROTTLE`, `FREEZE`, and `ESCALATE` help them avoid blanket manual review. | Emphasize middle-state governance and shadow-mode measurement before enforcement. |
| The system overclaims. | Feedback challenges production readiness, AWS endorsement, incident reduction, compliance, or acquisition value. | Audit public docs for claims that outrun evidence. | Keep non-claims visible: pilot-grade, metadata-only, not production-certified, not AWS-endorsed, not proven to reduce incidents. |

## Current Highest-Risk Assumption

The highest-risk assumption is not that recoverability matters. The highest-risk assumption is that outside reviewers will find SMERC's framing and evidence request useful enough to provide real metadata or labels.

That is why the current best test is external feedback on:

- the metadata-only reviewer request
- whether recoverability-before-execution is a distinct control concept
- whether 5 to 25 safe examples from one workflow are realistic
- whether the posture result would change review behavior

## What Success Looks Like

Near-term success is modest:

- one external reviewer says the evidence ask is shaped correctly
- one reviewer offers a better framing
- one reviewer contributes safe metadata-only examples
- one reviewer says which posture would be useful, too strict, too loose, irrelevant, or unclear

That is stronger than another internal feature because it starts replacing belief with market evidence.

## What Failure Would Teach

If the project fails to get traction after disciplined outreach, useful lessons would include one or more of these:

- the problem belongs inside existing policy engines rather than a separate recoverability layer
- the vocabulary needs to become more concrete
- the first buyer is not AWS-style cloud infrastructure
- the proof path needs real workflow metadata before anyone will engage
- the packaging needs to become one deployable integration instead of a broad framework

None of those outcomes waste the work. They tell us what to reengineer.

## Current Action

Do not broaden outreach until the active OpenSSF ask has either produced feedback or aged enough to justify one separate targeted community test.

See:

- `docs/Public_Outreach_Status.md`
- `docs/External_Metadata_Reviewer_Request.md`
- `docs/Public_Outreach_Post_Drafts.md`


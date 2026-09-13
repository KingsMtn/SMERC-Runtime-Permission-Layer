# Public Agent Runtime Incident Learning

## Purpose

SMERC should learn from public AI-agent runtime incidents, public advisories, public vendor writeups, public security research, public message-board discussions, and public benchmark descriptions.

SMERC should not use leaked proprietary source code, copied private architecture, reverse-engineered proprietary implementation details, leaked credentials, private prompts, private logs, or data that appears to have been exposed without authorization.

This note turns that boundary into a project rule: learn from the public failure pattern, not from stolen or leaked implementation material.

## Decision

Use public reporting to improve SMERC's threat models, reason codes, metadata-only replay packs, reviewer questions, and postcondition evidence expectations.

Do not use leaked proprietary source.

Do not copy leaked logic.

Do not treat leaked material as a benchmark, dataset, implementation guide, or architectural dependency.

Do not ask reviewers to share private source, private prompts, raw logs, secrets, customer records, account identifiers, production commands, or live cloud access.

## Allowed Sources

- Public vendor advisories and documentation
- Public vulnerability disclosures
- Public security research blogs
- Public CVEs, GitHub advisories, and incident timelines
- Public benchmark papers and benchmark metadata where the license permits use
- Public issue discussions and public community threads
- Public cloud and runtime documentation
- Metadata-only examples created from observable public patterns

## Disallowed Sources

- Leaked proprietary source code
- Copied proprietary algorithms or internal architecture
- Private repository contents not intentionally published for reuse
- Secrets, credentials, tokens, account IDs, ARNs, raw logs, customer data, packet payloads, or private prompts
- Decompiled or reverse-engineered commercial code used as implementation material
- Claims that SMERC has validated against a proprietary system when it has only learned from public reporting

## Public Lessons SMERC Can Safely Use

### Agent Runtime Reality

Public agent-runtime incidents show that real agents do not fail only at the model prompt layer. They fail across tool selection, terminal execution, delegated authority, repository actions, cloud APIs, environment variables, retry loops, package scripts, and human approval assumptions.

SMERC should keep modeling the proposed action, not only the model response.

### Runtime Authorization Beyond Identity

An agent can be authenticated and still be unsafe to run a specific action at a specific moment.

SMERC should continue separating identity from recoverability: who is acting, what they are trying to do, what evidence supports it, whether the action can be bounded, and how recovery would work if the action is wrong.

### Credential And Environment-Variable Exfiltration Pressure

Agent tools often operate near secrets, environment variables, repository tokens, cloud credentials, API keys, and deployment permissions.

SMERC should treat credential exposure pressure as a recoverability and containment issue, not only a static secret-scanning issue.

### Tool-Call And Terminal Execution Risk

Tool calls, shell commands, package scripts, workflow actions, file edits, cloud commands, and deployment steps can create side effects faster than a human reviewer can understand them.

SMERC should preserve pre-execution checkpoints for actions that combine high velocity, weak rollback, broad scope, uncertain evidence, or unclear delegated authority.

### Agent Identity And Provenance

Public discussions around agent systems keep returning to provenance: which agent, harness, tool, workflow, human approval, policy bundle, or delegated identity actually caused an action.

SMERC should keep requiring evidence for agent identity, session identity, on-behalf-of authority, policy version, approval mode, and tool source before a serious action is allowed.

### Repo And Action Hijacking

An authorized automation path can be hijacked through issue content, workflow triggers, package scripts, tool descriptions, dependency behavior, or repository-side instructions.

SMERC should continue treating untrusted content, delegated tool authority, workflow triggers, and missing source trust as first-class reason-code inputs.

### Authorized But Unrecoverable Actions

The useful gap for SMERC is not "was the action allowed by policy?" but "is this action recoverable enough to execute now?"

That framing applies to AI coding agents, cloud automation, MCP tool calls, GitHub Actions, financial actions, and other high-impact workflows.

## More Than Code

The most useful lessons are not just code-level lessons.

SMERC should extract:

- operating model patterns: how agents are approved, delegated, monitored, paused, and resumed
- failure modes: where authorized automation becomes unsafe
- controls: which evidence should exist before execution and after execution
- governance questions: who can unlock a frozen action and under what proof
- product placement: where SMERC should sit between agent, tool, gateway, IAM, workflow, and cloud API
- buyer language: how security, platform, cloud, finance, and governance teams describe the pain
- evidence expectations: what serious reviewers need before they trust the claim

## Work / Result / Impact

Work: convert public incident lessons into metadata-only scenarios, reason codes, replay packs, reviewer questions, and evidence gates.

Result: SMERC becomes stronger against real agent-runtime failure patterns without copying leaked source, ingesting private data, or making unsupported validation claims.

Impact: SMERC can learn from the industry's visible failures while staying credible for public review, commercial diligence, and acquisition-minded evaluation.

## Next Build Hooks

### Public Pattern Replay Pack

Create a metadata-only replay pack from public incident patterns:

- credential access attempt during an ambiguous tool action
- terminal command with unclear rollback
- repository action triggered by untrusted content
- cloud action with weak postcondition evidence
- retry loop that increases cost or blast radius
- delegated action where the approving identity and executing identity differ

### Reason Codes

Add or map these reason codes in future runtime proof:

- `AGENT_RUNTIME_PROVENANCE_WEAK`
- `TOOL_EXECUTION_SCOPE_UNCLEAR`
- `CREDENTIAL_EXFILTRATION_PRESSURE`
- `RECOVERY_PATH_UNPROVEN`
- `DELEGATED_AUTHORITY_UNCLEAR`
- `POSTCONDITION_EVIDENCE_MISSING`

### Evidence Fields

Future metadata examples should prefer safe fields such as:

- agent family or workflow family
- tool family
- action family
- delegated authority mode
- evidence source type
- rollback path status
- credential exposure pressure
- postcondition evidence status
- expected blast-radius boundary
- reviewer label

## Boundary Statement For Reviewers

SMERC learns from public agent-runtime incidents and public security research. It does not rely on leaked proprietary source code or private customer data. The project uses public lessons to build metadata-only recoverability tests, not to copy another vendor's implementation.

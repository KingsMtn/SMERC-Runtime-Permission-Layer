# Public Agent Runtime Incident Replay

## Purpose

This replay pack converts public AI-agent runtime incident patterns into SMERC-safe metadata rows.

It answers a reviewer question:

> Can SMERC learn from real public agent-runtime failures without using leaked source code, private logs, credentials, raw prompts, or proprietary implementation details?

The answer is yes, but only through public incident-pattern data.

## Source Boundary

Use public incident-pattern data, not leaked implementation data.

Allowed sources include:

- public engineering postmortems
- public security advisories
- public vulnerability disclosures
- public threat-intelligence reports
- public cloud documentation
- public reporting about incident response blast radius

Disallowed sources include:

- leaked proprietary source code
- copied private architecture
- private prompts
- raw logs
- credentials or tokens
- customer data
- exploit payloads
- account identifiers, ARNs, packet payloads, or production commands

This replay pack follows `docs/Public_Agent_Runtime_Incident_Learning.md`.

## Public Learning Sources

The first public learning sources are:

- Anthropic engineering containment writeup: `https://www.anthropic.com/engineering/how-we-contain-claude`
- Anthropic Claude Code public security advisories: `https://github.com/anthropics/claude-code/security`
- Anthropic September 2026 threat-intelligence report: `https://www.anthropic.com/threat-intelligence-report-september-2026`
- Anthropic cybersecurity incident alignment assessment: `https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents`
- AWS Claude Platform credential-source documentation: `https://docs.aws.amazon.com/claude-platform/latest/userguide/authentication.html`
- Public reporting on overbroad leak cleanup and GitHub takedown blast radius: `https://techcrunch.com/2026/04/01/anthropic-took-down-thousands-of-github-repos-trying-to-yank-its-leaked-source-code-a-move-the-company-says-was-an-accident/`

These sources are used only for public failure shapes, source categories, and control lessons.

## Example Rows

The companion example file is:

- `examples/public_agent_runtime_incident_patterns.json`

It includes six metadata-only records:

1. credential exfiltration pressure from an agent action
2. trust-boundary bypass before user consent
3. approved-domain exfiltration through an allowed service
4. sandbox or filesystem boundary escape risk
5. overbroad remediation blast radius after leaked material cleanup
6. autonomous or semi-autonomous cyber workflow acceleration

## Reason Codes

The first reason-code set is:

- `AGENT_RUNTIME_PROVENANCE_WEAK`
- `TOOL_EXECUTION_SCOPE_UNCLEAR`
- `CREDENTIAL_EXFILTRATION_PRESSURE`
- `TRUST_BOUNDARY_BEFORE_CONSENT`
- `APPROVED_DOMAIN_CAPABILITY_GRANT`
- `SANDBOX_BOUNDARY_WEAK`
- `REMEDIATION_BLAST_RADIUS_UNBOUNDED`
- `AUTONOMOUS_WORKFLOW_VELOCITY_HIGH`
- `RECOVERY_PATH_UNPROVEN`
- `DELEGATED_AUTHORITY_UNCLEAR`
- `POSTCONDITION_EVIDENCE_MISSING`

## SMERC Posture Mapping

| Incident Pattern | Likely SMERC Posture | Why |
| --- | --- | --- |
| credential exfiltration pressure | `DENY` or `FREEZE` | Secrets and identity material are hard to recover once disclosed. |
| trust boundary before consent | `DENY` | Configuration or hooks should not execute before a trust decision. |
| approved-domain exfiltration | `FREEZE` or `DENY` | Destination allowlists can become capability grants. |
| sandbox or filesystem boundary escape | `DENY` | The action boundary is not reliable enough for execution. |
| overbroad remediation blast radius | `THROTTLE` or `ESCALATE` | Cleanup actions need scoping, dry-run evidence, and review before mass side effects. |
| autonomous workflow acceleration | `THROTTLE`, `FREEZE`, or `ESCALATE` | Speed and parallelism increase blast radius and reduce human observability. |

## Work / Result / Impact

Work: convert public agent-runtime incident lessons into safe metadata-only replay rows with source boundaries, posture mappings, and reason codes.

Result: SMERC can show that its recoverability model responds to public real-world agent failure patterns without ingesting leaked code or private data.

Impact: reviewers get a credible bridge from public incident learning to SMERC's pre-execution recoverability controls.

## What This Does Not Prove

This replay pack is not:

- proof that SMERC evaluated Anthropic's private systems
- proof that SMERC used leaked Claude Code source
- a security audit of Claude Code, Claude, Anthropic, AWS, or any third-party product
- official benchmark performance
- customer validation
- production certification
- legal, compliance, or incident-response advice

## Next Build

The next stronger implementation is a small normalizer and report that turns `examples/public_agent_runtime_incident_patterns.json` into `smerc.customer-evaluation.v1` actions, then reports posture distribution, reason-code distribution, and non-claims.

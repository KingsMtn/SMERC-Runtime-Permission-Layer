# GitHub Actions Pilot Operator Readiness

Generated: `2026-08-02T02:31:34.848833+00:00`

## Decision

- Ready for week-zero qualification: `true`
- Ready for customer observe mode: `true`
- Pilot mode: `observe`

## First Customer Question

Can we run SMERC in observe mode against one GitHub Actions workflow using metadata-only action descriptions and compare the output with reviewer judgment for 30 days?

## Required Setup Items

- one selected repository or workflow family
- security owner
- platform owner
- pilot reviewer group
- metadata-only action request file
- observe-mode workflow configuration
- artifact retention period
- weekly review cadence
- stop conditions
- day-30 go/no-go criteria

## Blockers

- None.

## Warnings

- None.

## Repository Evidence Checks

| Item | Status | Detail |
| --- | --- | --- |
| `integrations/github_actions/README.md` | `ready` | repository evidence exists |
| `integrations/github_actions/remote_example_workflow.yml` | `ready` | repository evidence exists |
| `docs/API_Deployment_Guide.md` | `ready` | repository evidence exists |
| `docs/GitHub_OIDC_Operations.md` | `ready` | repository evidence exists |
| `pilot_package/GitHub_Actions_Pilot_Launch_Runbook.md` | `ready` | repository evidence exists |
| `pilot_package/Weekly_Review_Template.md` | `ready` | repository evidence exists |
| `pilot_package/Go_No_Go_Criteria.md` | `ready` | repository evidence exists |

## Setup Checks

| Item | Status | Detail |
| --- | --- | --- |
| pilot starts in observe mode | `ready` | first customer test must not block workflow execution |
| pilot explicitly excludes production certification claims | `ready` | public and customer language must stay inside evidence boundaries |
| metadata-only approved data is defined | `ready` | pilot should score workflow metadata, not sensitive payloads |
| sensitive and regulated data exclusions are defined | `ready` | first pilot must state what not to send |
| GitHub OIDC is the preferred authentication path | `ready` | OIDC reduces static secret handling in a real workflow |
| at least one target workflow is declared | `ready` | a pilot must start with a concrete workflow |
| weekly metrics include reviewer agreement | `ready` | commercial evidence requires human comparison labels |
| weekly metrics include unavailable evaluation count | `ready` | operators need to know whether integration reliability is noisy |
| stop conditions are declared | `ready` | a bounded pilot needs explicit halt rules |
| go/no-go options are declared | `ready` | day-30 decision should not drift into unapproved enforcement |

## Evidence Boundary

Readiness only. This does not prove production suitability, incident reduction, customer demand, or regulatory compliance.

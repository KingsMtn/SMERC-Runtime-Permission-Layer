# SMERC Pilot Readiness

## Pilot Objective

Determine whether runtime permission postures improve governance of AI-assisted code, deployment, and infrastructure workflows.

Use `docs/Pilot_Evaluation_Checklist.md` and `examples/pilot_evaluation_checklist.json` as the practical design-partner checklist. The checklist is deliberately written to identify both fit and reasons to stop or narrow the pilot.

## First Pilot Scope

Recommended first scope:

- GitHub Actions
- Pull requests or workflow dispatch events
- AI-assisted code or infrastructure changes
- Shadow-mode SMERC decisions
- Existing approvals remain unchanged at first

## Pilot Phases

### Phase 1: Observe

Duration: 2-4 weeks.

SMERC scores proposed actions and writes decision reports. It does not block workflows.

Success evidence:

- decision reports generated reliably
- reviewers understand postures and reason codes
- no workflow disruption

### Phase 2: Recommend

Duration: 3-4 weeks.

SMERC decisions are reviewed against existing approval behavior.

Success evidence:

- reviewer agreement rate measured
- false constraint rate measured
- false release concerns identified
- useful constraints discovered

### Phase 3: Enforce

Duration: 2-4 weeks after approval.

Selected postures can fail or route workflows.

Initial enforcement candidates:

- `DENY`
- `FREEZE`

`ESCALATE` should route to human review rather than automatically fail until policy is calibrated.

## Success Metrics

- reviewer agreement rate
- false release rate
- false freeze or false deny rate
- approval latency impact
- percentage of high-risk actions receiving useful constraints
- number of replay records reviewed
- number of workflow changes recommended after pilot

## Required Integrations

Minimum:

- GitHub repository
- GitHub Actions workflow
- JSON action metadata file generated or supplied by workflow
- artifact upload for SMERC decision report

Optional:

- pull request comment publishing
- Slack notification
- ticket creation
- security-review queue

## Exit Criteria

The pilot is successful only if a security or platform team can identify at least one of:

- a workflow where SMERC would have reduced review uncertainty
- a high-impact action where throttle/freeze/escalate was more useful than allow/block
- a repeatable integration path for agent tool-call governance
- evidence that recoverability or runtime posture scoring maps to real operational concern


# Cloud Automation Guardrails

SMERC can be evaluated as a recoverability-aware checkpoint for cloud automation and infrastructure actions.

The practical question is:

> Even if this cloud action is authorized, is it recoverable enough to execute now?

## Where It Fits

SMERC is designed to sit after existing identity, policy, CI/CD, and approval controls but before execution.

Relevant workflows include:

- infrastructure-as-code changes,
- Terraform or deployment plans,
- GitHub Actions cloud deployments,
- Kubernetes resource changes,
- IAM permission changes,
- network and firewall updates,
- backup retention changes,
- database migrations,
- destructive cloud-resource operations,
- automated remediation actions.

## Why Cloud Admin Is a Strong Next Lane

Cloud platforms already have authorization, policy, logging, and monitoring. The gap is that an authorized change can still be operationally unsafe if:

- rollback latency is high,
- backup evidence is incomplete,
- blast radius is broad,
- cancellation is unreliable,
- containment is weak,
- the action disables observability or recovery,
- a human reviewer cannot reconstruct why the action moved.

SMERC adds recoverability scoring before the action creates side effects.

Internally, the reference implementation uses named layers for the same flow:

- signal and evidence intake, called SPARK,
- recoverability decision, called SMERC,
- execution routing and control translation, called SPARTa,
- decision lifecycle evidence, called DLL.

Those names are secondary. Cloud and platform reviewers should first understand the plain-language flow: collect evidence, score recoverability, route execution, and preserve replay evidence.

## Example SMERC Inputs

Cloud-admin events can be represented with the existing Action Language or self-service pilot bundle:

- `base_action_risk`
- `reversibility`
- `containment_strength`
- `rollback_latency`
- `evidence_validity`
- `anomaly_pressure`
- `impact_scope`
- `cancel_reliability`
- `authorization_confidence`
- `external_side_effect`
- `sensitive_data`

## Example Decisions

| Cloud action | Likely SMERC concern | Possible posture |
| --- | --- | --- |
| Delete a production database table | destructive, slow rollback, sensitive data | `DENY` |
| Apply a 5 percent canary deploy | scoped, reversible, observable | `ALLOW` or `THROTTLE` |
| Change IAM admin permissions | high blast radius, privilege impact | `FREEZE` or `ESCALATE` |
| Rotate a secret with tested rollback | recoverable but sensitive | `THROTTLE` |
| Disable logging during incident response | weak evidence and recovery visibility | `DENY` or `FREEZE` |

## Pilot Shape

The first cloud-admin pilot should be shadow-mode only:

1. Select one workflow family, such as GitHub Actions deployments or Terraform plans.
2. Provide 10 to 25 non-secret sample actions.
3. Run the Self-Service Pilot Connector or customer action intake.
4. Compare SMERC posture against current approval decisions.
5. Measure reviewer agreement, false release candidates, useful constraints, latency, and evidence gaps.
6. Continue only if workflow owners find the recoverability signal useful.

## Existing Artifacts

- `reference_engine/self_service_pilot_connector.py`
- `examples/self_service_pilot_bundle.json`
- `docs/Self_Service_Pilot_Connector.md`
- `reports/Self_Service_Pilot_Connector_Report.md`
- `reference_engine/action_language.py`
- `docs/GitHub_Actions_Pilot_Operator_Quickstart.md`
- `pilot_package/First_Pilot_Path.md`

## Evidence Boundary

This is a pilot direction, not a production cloud-security claim. SMERC does not replace IAM, OPA, cloud-native policy, CI/CD approvals, CSPM, CNAPP, SIEM, SRE review, incident response, or human accountability.

SMERC should be tested as an additional recoverability-aware runtime permission signal before high-impact automated cloud actions execute.

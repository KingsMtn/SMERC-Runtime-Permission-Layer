# Technical Diligence Index

This index is for strategic reviewers, platform teams, security architects, and potential design partners who need to inspect SMERC without reading the entire repository.

## 15-Minute Path

1. Read `docs/Public_Review_Snapshot.md`.
2. Read `docs/CISO_Security_Architect_15_Minute_Review.md`.
3. Inspect the current CI badge in `README.md`.
4. Run the developer quickstart in `docs/Developer_Quickstart.md`.
5. Review one generated report in `reports/`.

## Core Runtime

- `reference_engine/agent_permission_layer.py`
- `reference_engine/recoverability_engine.py`
- `reference_engine/sparta_router.py`
- `reference_engine/runtime_evidence_trust.py`
- `reference_engine/autonomy_budget.py`
- `reference_engine/earned_autonomy.py`
- `reference_engine/autonomy_continuance.py`

## Primary Pilot Path

- `pilot_package/First_Pilot_Path.md`
- `docs/GitHub_Actions_Pilot_Operator_Quickstart.md`
- `reference_engine/github_actions_pilot_readiness.py`
- `integrations/github_actions/`
- `reports/GitHub_Actions_Pilot_Readiness.md`

## MCP / Tool-Call Governance

- `docs/MCP_Governance_Gateway.md`
- `docs/MCP_Tool_Governance.md`
- `docs/MCP_Proxy_Runner.md`
- `docs/MCP_Transport_Proxy.md`
- `docs/MCP_Tool_Risk_Scanner.md`
- `docs/Ref_Gated_Runtime_Proof_Loop.md`
- `reference_engine/ref_gated_runtime_proof.py`
- `reports/Ref_Gated_Runtime_Proof.md`

## Execution Routing And Controls

- `docs/SPARTa_Router_Operations.md`
- `docs/SPARTa_v2_Execution_Adapter_Framework.md`
- `docs/SPARTa_Adapter_Conformance.md`
- `docs/Control_Mapping_Library.md`
- `docs/Action_Bound_Permit_Operations.md`
- `docs/Control_Evidence_Operations.md`

## Decision Memory And Audit

- `docs/Decision_Lifecycle_Ledger.md`
- `docs/DLL_Intelligence.md`
- `docs/Governance_Report_Generator.md`
- `docs/Pilot_Ledger_Intake.md`
- `docs/Pilot_Ledger_Metrics.md`

## Autonomy Governance

- `docs/Autonomy_Health_Framework.md`
- `docs/Autonomy_Budgeting_Framework.md`
- `docs/Earned_Autonomy_Framework.md`
- `docs/Autonomy_Continuance_Framework.md`

## Financial-Action Profile

- `docs/SMERC_F_Metadata_Intake_Contract.md`
- `docs/SMERC_F_Fortune_500_Financial_Services_Review.md`
- `docs/SMERC_F_Pilot_Evidence_Packet.md`
- `docs/SMERC_F_Financial_Source_Ingestion.md`
- `docs/SMERC_F_Financial_Public_Data_Replay.md`

## Claims Boundary

SMERC is pilot-grade. It is not production-certified, compliance-attested, independently security-audited, customer-validated for incident reduction, or a replacement for IAM, policy-as-code, AI gateways, SIEM, SOAR, GRC, code review, or human accountability.

## Diligence Questions

- Does recoverability scoring change reviewer judgment?
- Does the evidence trust gate reject weak metadata correctly?
- Are route controls clear enough for native tool adapters?
- Does the ledger preserve useful audit evidence without overcollecting sensitive data?
- Does autonomy budgeting reduce risky independence without blocking useful automation?
- Can the system run in shadow mode with acceptable latency and low operational burden?

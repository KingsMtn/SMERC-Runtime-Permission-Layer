# Technical Diligence Index

This index is for strategic reviewers, platform teams, security architects, and potential design partners who need to inspect SMERC without reading the entire repository.

## 15-Minute Path

1. Read `docs/Public_Review_Snapshot.md`.
2. Read `docs/Company_Reviewer_Front_Door.md`.
3. Read `docs/CISO_Security_Architect_15_Minute_Review.md`.
4. Read `docs/AI_Readable_Reviewer_Bundle.md`.
5. Read `docs/External_Signal_And_Competitive_Review.md`.
6. Inspect the current CI badge in `README.md`.
7. Run the developer quickstart in `docs/Developer_Quickstart.md`.
8. Review one generated report in `reports/`.

## Core Runtime

- `reference_engine/agent_permission_layer.py`
- `reference_engine/recoverability_engine.py`
- `reference_engine/sparta_router.py`
- `reference_engine/complete_lifecycle_proof.py`
- `reference_engine/runtime_evidence_trust.py`
- `reference_engine/autonomy_budget.py`
- `reference_engine/earned_autonomy.py`
- `reference_engine/autonomy_continuance.py`
- `reference_engine/recovery_authority_gate.py`

## Competitive And External Signal

- `docs/AI_Readable_Reviewer_Bundle.md`
- `examples/ai_reviewer_bundle.json`
- `docs/External_Signal_And_Competitive_Review.md`
- `docs/Accelerator_And_Adjacent_Company_Map.md`
- `docs/Public_Action_Governance_Benchmark.md`
- `docs/Public_Benchmark_Ingestion.md`
- `docs/Serious_Report_Performance.md`
- `docs/Customer_Owned_Metadata_Request.md`
- `docs/Competitive_Gaps_And_Build_Priorities.md`
- `reports/Competitive_Proof_Parity_Report.md`
- `reports/Public_Action_Governance_Benchmark.md`
- `reports/Public_Benchmark_Ingestion_Report.md`
- `reports/Serious_Report_Performance.md`
- `reports/Customer_Owned_Metadata_Request.md`
- `reports/Runtime_Governance_Benchmark.md`

## Primary Pilot Path

- `docs/Company_Reviewer_Front_Door.md`
- `pilot_package/First_Pilot_Path.md`
- `docs/GitHub_Actions_Pilot_Operator_Quickstart.md`
- `docs/Cloud_Admin_Proof_Pack.md`
- `docs/Cloud_Metadata_Connector.md`
- `docs/Public_Benchmark_Ingestion.md`
- `docs/Serious_Report_Performance.md`
- `docs/Customer_Owned_Metadata_Request.md`
- `reference_engine/github_actions_pilot_readiness.py`
- `reference_engine/cloud_admin_proof_pack.py`
- `reference_engine/cloud_metadata_connector.py`
- `reference_engine/public_benchmark_ingestion.py`
- `reference_engine/serious_report_performance.py`
- `reference_engine/customer_owned_metadata_request.py`
- `integrations/github_actions/`
- `reports/GitHub_Actions_Pilot_Readiness.md`
- `reports/cloud_admin_proof_pack/Cloud_Admin_Proof_Pack.md`
- `reports/Cloud_Metadata_Connector_Report.md`
- `reports/Public_Benchmark_Ingestion_Report.md`
- `reports/Serious_Report_Performance.md`
- `reports/Customer_Owned_Metadata_Request.md`

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
- `docs/Postcondition_Evidence.md`
- `reference_engine/postcondition_evidence.py`

## Decision Memory And Audit

- `docs/Decision_Lifecycle_Ledger.md`
- `docs/DLL_Intelligence.md`
- `docs/Complete_Lifecycle_Proof.md`
- `docs/Governance_Report_Generator.md`
- `docs/Pilot_Ledger_Intake.md`
- `docs/Pilot_Ledger_Metrics.md`
- `reports/Postcondition_Evidence_Report.md`

## Complete Lifecycle Proof

- `docs/Complete_Lifecycle_Proof.md`
- `reference_engine/complete_lifecycle_proof.py`
- `examples/complete_lifecycle/lifecycle_case.json`
- `reports/complete_lifecycle/Complete_Lifecycle_Proof_Report.md`
- `reports/complete_lifecycle/complete_lifecycle_proof.json`

Work: connect runtime admission, SMERC recoverability scoring, SPARTa routing, Recovery Authority Gate, action-bound permits, execution result, and DLL evidence.

Result: the reference case returns `COMPLETE` with a paused initial action, verified unlock, constrained continuation, verified permit, synthetic execution success, and valid ledger.

Impact: a reviewer can inspect the whole governance lifecycle instead of reading disconnected module pages.

## Autonomy Governance

- `docs/Autonomy_Health_Framework.md`
- `docs/Autonomy_Budgeting_Framework.md`
- `docs/Earned_Autonomy_Framework.md`
- `docs/Autonomy_Continuance_Framework.md`
- `docs/Recovery_Authority_Gate.md`

## Pause And Unlock Governance

- `reference_engine/recovery_authority_gate.py`
- `examples/recovery_authority/unlock_request.json`
- `reports/Recovery_Authority_Gate_Report.md`
- `reports/recovery_authority_gate_report.json`

## Financial-Action Profile

- `docs/SMERC_F_Metadata_Intake_Contract.md`
- `docs/SMERC_F_Fortune_500_Financial_Services_Review.md`
- `docs/SMERC_F_Pilot_Evidence_Packet.md`
- `docs/SMERC_F_Financial_Source_Ingestion.md`
- `docs/SMERC_F_Financial_Public_Data_Replay.md`
- `docs/SMERC_F_Financial_Reason_Codes.md`

Work: replay public-data-shaped financial actions through SMERC-F and attach financial reason codes.

Result: records show current control outcome, SMERC-F posture, exposure, capacity, reason codes, and Work / Result / Impact explanation.

Impact: financial-services reviewers can inspect whether recoverability adds useful pre-execution judgment without treating SMERC-F as AML, sanctions, custody, settlement, or payment software.

## Claims Boundary

SMERC is pilot-grade. It is not production-certified, compliance-attested, independently security-audited, customer-validated for incident reduction, or a replacement for IAM, policy-as-code, AI gateways, SIEM, SOAR, GRC, code review, or human accountability.

## Diligence Questions

- Does recoverability scoring change reviewer judgment?
- Does the evidence trust gate reject weak metadata correctly?
- Are route controls clear enough for native tool adapters?
- Does the ledger preserve useful audit evidence without overcollecting sensitive data?
- Does autonomy budgeting reduce risky independence without blocking useful automation?
- Can the system run in shadow mode with acceptable latency and low operational burden?

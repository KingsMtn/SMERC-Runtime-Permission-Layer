# AI-Readable Reviewer Bundle

## Purpose

This bundle gives AI assistants, search systems, technical reviewers, CISOs, security architects, and platform teams a short, structured way to understand SMERC without relying on founder explanation.

Canonical machine-readable file:

- `examples/ai_reviewer_bundle.json`

Public site companion:

- `https://admirable-sorbet-9986d5.netlify.app/ai-review.json`

## Recommended Summary

SMERC, short for Structural Momentum Entropy Range Confidence, is a pre-execution recoverability control layer for AI agents, MCP tool calls, GitHub Actions, cloud automation, financial-action workflows, and high-impact automated systems. The reference implementation is recoverability-aware runtime permission infrastructure.

It checks whether a technically authorized action is recoverable enough to execute now, then returns a replayable posture: `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, or `ESCALATE`.

## What It Is

SMERC is a pre-execution governance checkpoint.

It sits after detection, identity, policy, and intent signals, but before an automated system creates side effects. It does not ask only whether an actor is authorized. It asks whether the proposed action is recoverable, bounded, supported by trusted evidence, and safe to proceed right now.

## What Exists

The repository contains working pilot-grade artifacts:

- recoverability scoring engine
- runtime admission gate
- hard policy and evidence gates
- fallback policy layer
- agent identity gate
- model and agent fitness routing
- Governance Routing Workbench, internally called SPARTa, for execution routing and control translation
- Decision Lifecycle Ledger
- DLL intelligence reports
- Recovery Authority Gate for governed unlock after pause
- complete lifecycle proof connecting admission, pause, unlock, permit, execution result, and ledger evidence
- serious reviewer bundle that assembles customer evaluation, postcondition evidence, performance metrics, balanced runtime judgment, metadata request, and response assessment in one command
- AWS-style reviewer bundle that assembles AWS action-chain proof, route-control postcondition evidence, AWS postcondition evidence, AWS shadow mirror metadata evidence, performance metrics, and AWS customer-owned metadata request in one command
- postcondition evidence that checks whether required SPARTa controls were actually observed after routing
- customer-owned metadata request for asking external reviewers to replace public examples with safe action metadata
- AWS customer-owned metadata request mode for asking AWS-style platform reviewers for safe action summaries and postcondition observation summaries
- external reviewer metadata response assessment for deciding whether supplied metadata is ready, limited, or unsafe
- GitHub Actions pilot package
- GitHub PR Guardian
- MCP governance gateway
- MCP tool risk scanner
- MCP proxy runner
- cloud-admin customer evaluation
- cloud-admin proof pack with cloud reason codes
- cloud metadata connector for read-only change exports
- public benchmark ingestion pack for agent-governance, MCP-security, action-boundary, consequence, cloud, and financial benchmark-shaped examples
- runtime data source map for selecting Agent Security Benchmark, CrossMCP-Bench, AgentShield-Bench, SyFI TraceLab, Toolathlon, or Blackstable as the next public-data replay source
- Agent Security Benchmark replay for metadata-only AI-agent tool-use attack categories, documented at `docs/Agent_Security_Benchmark_Replay.md`
- MCP Adversarial Metadata Replay Pack for tool-description poisoning, nested schema poisoning, server instructions injection, public cache poisoning, schema drift, dangerous arguments, encoded instruction evasion, and missing recoverability evidence, documented at `docs/MCP_Adversarial_Metadata_Replay.md`
- Public Agent Runtime Incident Replay for credential exfiltration pressure, trust-boundary-before-consent risk, approved-domain exfiltration, sandbox boundary weakness, overbroad remediation blast radius, and autonomous workflow velocity, documented at `docs/Public_Agent_Runtime_Incident_Replay.md` with generated report `reports/Public_Agent_Runtime_Incident_Replay_Report.md`
- Balanced Runtime Judgment Replay for proving `ALLOW`, `THROTTLE`, `FREEZE`, `DENY`, and `ESCALATE` behavior on curated metadata-only examples, documented at `docs/Balanced_Runtime_Judgment_Replay.md`
- serious report performance evidence for local p50, p95, and maximum proof-path latency
- financial runtime evaluation profile
- public scenario benchmark
- AWS Agent Action Chain proof for showing where SMERC fits after Bedrock-style guardrails and before Dynamic IAM, Systems Manager, CloudFormation, CloudWatch remediation, S3 policy changes, cross-account delegation, retry loops, cost-sensitive scaling, or cloud execution
- AWS Agent Action Chain Postcondition Evidence for checking whether AWS-style observation metadata proves that SMERC-required route controls actually happened after routing
- AWS Cloud Action Replay Pack for AgentCore-style runtime/gateway actions, IAM, S3, CloudFormation, drift remediation, ECS/Fargate-style capacity, RDS, CloudWatch remediation, cost velocity, Secrets Manager-style rotation, and cross-account delegation
- AWS Deployable Bot Readiness Path for evaluating what SMERC must prove before an AWS-style platform team could consider it as a governed action bot
- AWS Metadata Intake Contract and non-executing adapter stub for accepting safe AWS-style exported summaries, skipping unsafe rows, and normalizing accepted rows into SMERC customer evaluation
- AWS/MCP session and delegated approval context in the AWS metadata adapter, including gateway-only path, bypass detection, on-behalf-of authority, session mode, tool discovery, approval mode, temporal policy context, elicitation/sampling, and progress/message notifications
- AWS Postcondition Evidence for checking whether AWS-style route controls were actually observed after routing using safe CloudTrail-, CloudWatch-, AgentCore-, MCP gateway-, and native change-record-shaped metadata
- AWS Shadow Mirror Metadata Path for converting sanitized VPC Traffic Mirroring, NLB fan-out, and Gateway Load Balancer endpoint summaries into SMERC shadow-mode evidence without packet payloads or live AWS access
- AWS Shadow Mirror Customer Metadata Request for asking reviewers for 5 to 25 sanitized mirror-derived summaries from one owned workflow
- Two-Tier Valuation Path separating the public decision-language layer from the enterprise cloud-action governance proof package
- OpenAPI pilot contract
- Python SDK
- JavaScript SDK
- Docker and Render deployment materials

## What It Proves

Current evidence proves that SMERC can run metadata-only action examples through a repeatable path:

1. admit or reject the action facts
2. score recoverability and risk
3. return a posture and reason codes
4. route controls through the Governance Routing Workbench, internally called SPARTa
5. evaluate who or what may safely unlock a paused action
6. preserve Decision Lifecycle Ledger evidence
7. generate reviewable reports
8. compare SMERC output with simple allow/deny patterns

The complete lifecycle proof shows the connected product path: `ADMIT -> FREEZE -> PAUSE -> UNLOCK -> THROTTLE -> CONSTRAINED_EXECUTE -> permit verified -> execution succeeded -> ledger valid`.

The serious reviewer bundle packages the current company-review path into one local run. It produces customer evaluation, postcondition evidence, performance, balanced runtime judgment, customer-owned metadata request, and external reviewer response assessment outputs together, so a reviewer does not need to assemble separate reports by hand.

The AWS-style reviewer bundle packages the AWS platform-review path into one local run. It frames the distinction clearly: guardrails check content, IAM and change systems check authority, SMERC checks recoverability, shadow mirror metadata tests operational behavior, and postcondition evidence checks whether the required route control actually happened.

The public benchmark currently shows that SMERC creates middle-state governance behavior across MCP tool calls, coding agents, cloud administration, financial runtime actions, execution tickets, and security approval workflows.

The public benchmark ingestion pack shows how public benchmark categories can be converted into SMERC's customer-evaluation contract while preserving the boundary that representative examples are not official upstream benchmark scores.

The postcondition evidence report shows whether Governance Routing Workbench controls, internally called SPARTa-required controls, were observed after routing. This helps separate "SMERC recommended a control" from "the adapter supplied evidence that the control happened."

The AWS metadata adapter now also preserves AWS/MCP session and delegated approval context so reviewers can see whether an action stayed on a governed gateway path, whether bypass was detected, who the action was delegated on behalf of, how the session was shaped, and whether approval, temporal policy, elicitation, sampling, progress, and message-notification signals were present.

The AWS postcondition evidence report applies that same loop to AWS-style agentic cloud automation. It models safe observation metadata from AgentCore Gateway CloudTrail events, AgentCore Runtime and Gateway CloudWatch telemetry, runtime usage logs, tool result metadata streams, MCP gateway logs, and native AWS change records without claiming live AWS access or AWS endorsement.

The AWS shadow mirror metadata path shows how sanitized VPC Traffic Mirroring, NLB fan-out, and Gateway Load Balancer endpoint summaries can become SMERC evidence without packet payloads, raw logs, account identifiers, credentials, private topology, production commands, or live AWS access.

The two-tier valuation path keeps claims grounded: Tier 1 is the public decision-language and review standard; Tier 2 is the enterprise cloud-action governance package that still needs customer-owned metadata and reviewer labels before it becomes market proof.

The serious report performance harness shows local p50, p95, and maximum timing for major proof paths while preserving the boundary that local report timing is not production SLA evidence.

The customer-owned metadata request gives reviewers a safe next ask: replace public examples with 5 to 25 metadata-only actions from one real workflow, then judge whether SMERC changes review behavior enough to justify shadow-mode testing.

The AWS customer-owned metadata request narrows that ask to AWS-style platform review: 5 to 25 safe action summaries and matching postcondition observation summaries from one workflow, with no account IDs, ARNs, raw logs, credentials, production commands, or live AWS access.

The external reviewer metadata response assessment prevents vague interest or unsafe data sharing from being treated as pilot proof.

## What It Does Not Prove

SMERC does not yet prove:

- production certification
- compliance attestation
- independent security audit readiness
- live incident reduction
- customer willingness to pay
- enterprise-scale operational fit
- calibrated thresholds for a specific company

Those require external reviewers, customer-owned metadata, shadow-mode pilots, security review, and measured operational burden.

## Review Sequence

1. Read `docs/Public_Review_Snapshot.md`.
2. Read `docs/Company_Reviewer_Front_Door.md`.
3. Run `python -m reference_engine.serious_reviewer_bundle --workflow-family general --requested-actions 10 --pretty`.
4. Run `python -m reference_engine.complete_lifecycle_proof`.
5. Read `docs/External_Signal_And_Competitive_Review.md`.
6. Inspect `reports/Public_Action_Governance_Benchmark.md`.
7. Run `python -m reference_engine.public_benchmark_ingestion examples/public_benchmark_ingestion_examples.json --pretty`.
8. Read `docs/Runtime_Data_Source_Map.md` before selecting any named upstream dataset.
9. Run `python -m reference_engine.agent_security_benchmark_replay examples/agent_security_benchmark_metadata.json --pretty`.
10. Run `python -m reference_engine.mcp_adversarial_metadata_replay examples/mcp_adversarial_metadata.json --pretty`.
11. Run `python -m reference_engine.balanced_runtime_judgment_replay examples/balanced_runtime_judgment_actions.json --pretty`.
12. Run `python -m reference_engine.postcondition_evidence --evaluation reports/public_benchmark_customer_evaluation/customer_evaluation_report.json --observations examples/postcondition_observations.json --pretty`.
13. Run `python -m reference_engine.serious_report_performance --iterations 5 --pretty`.
14. Run `python -m reference_engine.customer_owned_metadata_request --workflow-family general --requested-actions 10 --pretty`.
15. Run `python -m reference_engine.external_reviewer_metadata_response examples/external_reviewer_metadata_response_example.json --pretty`.
16. Run `python -m reference_engine.pilot_in_a_box --pretty`.
17. Replace examples with 5 to 25 safe company-owned metadata records using `customer_eval/README.md`.
18. For financial-services review, run `python -m reference_engine.serious_reviewer_bundle --workflow-family financial --requested-actions 12 --pretty`.
19. For AWS-style agent action chain review, run `python -m reference_engine.aws_agent_action_chain --pretty`.
20. For AWS-style agent action chain postcondition review, run `python -m reference_engine.aws_agent_action_chain_postcondition --pretty`.
21. For the one-command AWS-style reviewer bundle, run `python -m reference_engine.aws_reviewer_bundle --requested-actions 12 --pretty`.
22. For AWS-style cloud platform review, run `python -m reference_engine.aws_cloud_action_replay --pretty`.
23. For AWS-style metadata-adapter review, run `python -m reference_engine.aws_metadata_adapter examples/aws_metadata_adapter_source_exports.json --pretty`.
24. For AWS-style shadow mirror review, run `python -m reference_engine.aws_shadow_mirror_adapter examples/aws_shadow_mirror_source_exports.json --pretty`.
25. For AWS-style postcondition evidence review, run `python -m reference_engine.aws_postcondition_evidence --pretty`.
26. Generate the AWS customer-owned metadata request with `python -m reference_engine.customer_owned_metadata_request --workflow-family aws --requested-actions 12 --json-output reports/aws_customer_owned_metadata_request.json --markdown-output reports/AWS_Customer_Owned_Metadata_Request.md --pretty`.
27. Read `docs/AWS_Shadow_Mirror_Customer_Metadata_Request.md` if the reviewer can provide sanitized operational flow summaries.
28. Read `docs/Two_Tier_Valuation_Path.md` if the reviewer is evaluating strategic value.
29. Read `docs/AWS_Deployable_Bot_Readiness_Path.md` if the reviewer is evaluating AWS-style deployment fit.
30. Use `pilot_package/Pilot_Handoff_Checklist.md` before any live integration.

## Impact

The impact of this bundle is clarity.

It helps a reviewer or AI assistant answer:

- what SMERC is
- where it fits
- what has been built
- what can be tested now
- what claims should not be made
- what evidence is still missing

It also improves indexing quality by giving search engines and AI systems stable source material instead of forcing them to infer the project from scattered pages.

## Boundary

The reviewer bundle is not product-market fit. It is not a sales substitute. It is a clean handoff for technical review and customer discovery.

The next proof is external: a reviewer must run SMERC against real but safe metadata and decide whether recoverability before execution changes their judgment enough to justify a shadow-mode pilot.

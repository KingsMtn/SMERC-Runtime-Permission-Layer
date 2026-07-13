# SMERC Governance Report Generator

The SMERC Governance Report Generator creates a replayable review package from existing SMERC artifacts.

It does not create new evidence. It assembles and cross-checks:

- a SMERC decision
- a signed or unsigned SPARTa route report
- a control mapping report
- a Decision Lifecycle Ledger record

The purpose is to help CISOs, security architects, platform engineers, and pilot reviewers inspect whether a governed action is coherent from request through route, controls, and lifecycle record.

## Why It Exists

Without a single report, reviewers have to jump across JSON files, Markdown reports, examples, and test output. That makes SMERC look like a collection of parts instead of a connected governance system.

This generator shows the system flow:

1. SMERC returns a posture.
2. SPARTa converts the posture into a route.
3. Control mapping explains native mechanisms and evidence requirements.
4. DLL records the governed lifecycle.
5. The report cross-checks whether those artifacts agree.

## Example

```bash
python -m reference_engine.governance_report examples/governance_report/github_actions_governance_bundle.json --pretty --json-output reports/governance_report_example.json --markdown-output reports/Governance_Report_Example.md
```

The generated report includes:

- executive summary
- artifact digests
- posture and route state
- control mapping status
- DLL validity
- cross-check results
- known limits
- recommended next action

## Cross-Checks

The current generator checks:

- decision posture matches route source posture
- decision replay ID matches route replay ID
- route controls are mapped or documented as route-level controls
- control mapping has no missing required controls
- DLL hash chain is valid

Failed cross-checks block the report from being used as pilot approval evidence.

## Limits

This report is a pilot review artifact. It is not production certification, compliance attestation, or proof that live incidents are reduced. A real deployment still needs validated adapters, scoped identity, operational monitoring, security review, and external pilot data.

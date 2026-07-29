# Customer Metadata Validation

## Purpose

Customer metadata validation checks whether prospect-specific pilot inputs are ready to generate a core pilot package.

It protects against:

- unreplaced public sample organizations
- unconfirmed substitution checklist items
- too few or too many action examples
- review-only prospects being treated as pilot-ready
- sample metrics being used as customer evidence
- invalid pilot handoff input

## Run

```bash
python -m reference_engine.customer_metadata_validator --pretty
```

Generated outputs:

```text
reports/Customer_Metadata_Validation_Report.md
reports/customer_metadata_validation_report.json
```

For a prospect-specific package:

```bash
python -m reference_engine.customer_metadata_validator \
  --checklist customer_working/customer_metadata_substitution_checklist.json \
  --prospect-route customer_working/prospect_route.json \
  --customer-intake customer_working/customer_action_intake.json \
  --pilot-handoff customer_working/pilot_handoff.json \
  --pretty
```

Only generate a customer-specific core pilot package after this validation returns:

```text
ready_for_customer_package: true
```

## Boundary

This validation does not prove customer demand, pilot success, production safety, incident reduction, compliance, or approval for enforcement.
